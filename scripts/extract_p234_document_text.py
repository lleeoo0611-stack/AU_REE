"""Extract full PDF pages / HTML text as review aids, never auto-approve scope."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/p234_document_text"


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1
        if tag in {"p", "br", "div", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="+", type=Path)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for manifest in args.manifests:
        for doc in json.loads(manifest.read_text(encoding="utf-8")):
            if "archive_path" not in doc:
                continue
            path = ROOT / doc["archive_path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != doc["sha256"]:
                raise ValueError("Original document checksum mismatch")
            try:
                if doc["format"] == "pdf":
                    reader = PdfReader(path)
                    pages = [p.extract_text() or "" for p in reader.pages]
                elif doc["format"] == "html":
                    html = VisibleText()
                    html.feed(path.read_text(encoding="utf-8", errors="replace"))
                    pages = [re.sub(r"[ \t]+", " ", "".join(html.parts))]
                else:
                    pages = []
                result = {**doc, "pages": pages}
                (OUT / (doc["document_id"] + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(doc["document_id"], len(pages), sum(len(x) for x in pages), flush=True)
            except Exception as exc:
                print(doc["document_id"], "TEXT_EXTRACTION_FAILED", str(exc), flush=True)


if __name__ == "__main__":
    main()
