"""Resolve old GEMIS handles through official DSpace discover + ORIGINAL bundle.

Require an exact preserved handle, retain the item metadata and filename,
download ORIGINAL content only. Discovery matches never approve Project scope.
"""
import concurrent.futures
import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from acquire_p234_primary_documents import ROOT, OUT, fetch, inventory

API = "https://geoscience.nt.gov.au/gemis/server/api"


def get(url):
    with urllib.request.urlopen(url, timeout=25) as response:
        return json.load(response)


def resolve(url, targets):
    number = re.search(r"/(?:handle|bitstream)/1/(\d+)", url).group(1)
    query = urllib.parse.quote('handle:"1/' + number + '"')
    discovery = get(API + "/discover/search/objects?query=" + query)
    found = discovery.get("_embedded", {}).get("searchResult", {}).get("_embedded", {}).get("objects", [])
    items = [x["_embedded"]["indexableObject"] for x in found if x["_embedded"]["indexableObject"].get("handle") == "1/" + number]
    if len(items) != 1:
        raise ValueError("Expected unique exact handle: " + number)
    item = items[0]
    bundles = get(item["_links"]["bundles"]["href"] + "?size=100")["_embedded"]["bundles"]
    files = []
    for bundle in bundles:
        if bundle["name"] != "ORIGINAL":
            continue
        files += get(bundle["_links"]["bitstreams"]["href"] + "?size=100")["_embedded"].get("bitstreams", [])
    expected_file = urllib.parse.unquote(url.rsplit("/", 1)[-1]) if "/bitstream/" in url else None
    pdfs = [x for x in files if x["name"].lower().endswith(".pdf") and
            (expected_file is None or x["name"].casefold() == expected_file.casefold())]
    if expected_file and not pdfs:
        raise ValueError("Exact original filename absent: " + expected_file)
    records = []
    for original in pdfs:
        record = fetch(original["_links"]["content"]["href"], targets)
        record.update({"replaces_legacy_url": url, "official_handle": item["handle"],
                       "official_item_uuid": item["uuid"], "official_item_title": item["name"],
                       "official_item_metadata": item["metadata"], "original_filename": original["name"],
                       "original_bundle": "ORIGINAL"})
        records.append(record)
    return records


def main():
    records = []
    urls = {u: ids for u, ids in inventory().items() if "geoscience.nt.gov.au" in u}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(resolve, u, ids): u for u, ids in urls.items()}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                found = future.result()
                records += found
                print(url, [(x["original_filename"], x["status"]) for x in found], flush=True)
            except Exception as exc:
                records.append({"requested_url": url, "status": "RESOLUTION_FAILED", "error": str(exc)})
                print(url, str(exc), flush=True)
    path = OUT / "gemis_originals_manifest.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(sorted(records, key=lambda x: x["requested_url"]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
