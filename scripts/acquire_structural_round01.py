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
    if meta.exists():
        record = json.loads(meta.read_text(encoding='utf-8'))
        # A source ID identifies one immutable URL/publication/review scope.
        # Metadata cannot be carried over silently to a changed URL or group.
        for key in ('source_id', 'url', 'format', 'publication_date', 'review_group_ids'):
            if record.get(key) != item.get(key):
                raise ValueError('source contract changed; assign a new source_id: ' + item['source_id'])
        if not path.exists():
            if record.get('access_status') == 'ORIGINAL_BYTES_LOCAL':
                raise FileNotFoundError('archived original missing: ' + item['source_id'])
            # A failed source remains a documented access hold; retry only
            # with an independently curated new source ID.
            return record
        if record.get('access_status') != 'ORIGINAL_BYTES_LOCAL':
            raise ValueError('orphaned original contradicts access status: ' + item['source_id'])
        raw = path.read_bytes()
        if (hashlib.sha256(raw).hexdigest() != record.get('sha256')
                or len(raw) != record.get('byte_count')):
            raise ValueError('archived bytes/hash/size changed: ' + item['source_id'])
        return record
    if path.exists():
        # Do not silently fetch over an archived PDF/HTML whose metadata was
        # deleted or lost; preserve bytes for independent recovery.
        raise FileExistsError('archived original lacks manifest: ' + item['source_id'])
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
