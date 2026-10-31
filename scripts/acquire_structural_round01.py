"""Fetch explicitly curated sources once; retain originals locally, publish manifests.

Network acquisition is opt-in and never part of the offline mother pipeline.
No third-party original is committed. Failed retrievals are recorded, not negatives.
"""
import argparse
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'inputs/source_review_20261101/structural_round01_sources.json'
ARCHIVE = ROOT / 'work/structural_round01/originals'
MANIFEST = ROOT / 'inputs/source_review_20261101/structural_round01_access_manifest.json'


def fetch(item):
    import requests
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    path = ARCHIVE / (item['source_id'] + '.bin')
    meta = path.with_suffix('.json')
    if meta.exists() and not path.exists():
        # A failed source is reopened by a new, explicitly curated source ID.
        return dict(json.loads(meta.read_text(encoding='utf-8')), **item)
    if path.exists() and meta.exists():
        record = json.loads(meta.read_text(encoding='utf-8'))
        if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('archived bytes changed: ' + item['source_id'])
        return dict(record, **item)
    result = dict(item, retrieved_at=datetime.now(timezone.utc).isoformat(),
                  archive_path=path.relative_to(ROOT).as_posix(), sha256='', byte_count=0)
    try:
        session = requests.Session()
        session.trust_env = False
        started = time.monotonic()
        response = session.get(item['url'], timeout=(10, 15), stream=True)
        result.update(http_status=response.status_code, final_url=response.url,
                      content_type=response.headers.get('Content-Type', ''))
        response.raise_for_status()
        chunks = []
        for chunk in response.iter_content(128 * 1024):
            if time.monotonic() - started > 50:
                raise ValueError('bounded retrieval time exceeded; new locator needed to reopen')
            chunks.append(chunk)
            if sum(map(len, chunks)) > 80 * 1024 * 1024:
                raise ValueError('bounded retrieval size exceeded; use specific report pages')
        raw = b''.join(chunks)
        if item.get('format') == 'pdf' and not raw.startswith(b'%PDF'):
            raise ValueError('expected PDF; received another representation')
        path.write_bytes(raw)
        result.update(access_status='ORIGINAL_BYTES_LOCAL', sha256=hashlib.sha256(raw).hexdigest(),
                      byte_count=len(raw))
    except (requests.RequestException, ValueError) as exc:
        result.update(access_status='SOURCE_UNAVAILABLE', error=str(exc)[:350])
    meta.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', required=True)
    args = parser.parse_args()
    items = json.loads(INPUT.read_text(encoding='utf-8'))
    assert len({x['source_id'] for x in items}) == len(items)
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fetch, items))
    MANIFEST.write_bytes((json.dumps(rows, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    for r in rows:
        print(r['source_id'], r['access_status'], r['byte_count'])


if __name__ == '__main__':
    main()
