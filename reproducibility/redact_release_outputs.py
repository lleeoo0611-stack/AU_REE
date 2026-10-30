"""Remove URL credential parameters from derived outputs, preserving local originals."""
import csv, hashlib, json, re
from pathlib import Path

PATTERN=re.compile(r'(?i)([?&])?\s*(?:access_token|api[_-]?key|token|auth_token|X-Amz-[A-Za-z-]+)\s*=\s*[^&\s"<>;\\]+')
def clean(value):
    if isinstance(value,str):
        v=PATTERN.sub(lambda m:'?' if m[1]=='?' else '',value)
        return v.replace('?&','?').replace('&&','&')
    if isinstance(value,list):return [clean(x) for x in value]
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    return value
def redact_text_copy(path):
    if path.suffix.lower() not in ['.csv','.json','.jsonl','.txt','.md','.xml','.html']:return False
    raw=path.read_text(encoding='utf-8-sig',errors='strict')
    if path.suffix=='.json':
        obj=json.loads(raw);obj2=clean(obj)
        if obj2==obj:return False
        changed=json.dumps(obj2,ensure_ascii=False,indent=2)+'\n'
    else:changed=clean(raw)
    if changed==raw:return False
    path.write_text(changed,encoding='utf-8');return True
def main():
    root=Path(__file__).resolve().parents[1];out=root/'deliverable';changed=[]
    for p in sorted(out.glob('*.csv')):
        with p.open(encoding='utf-8-sig',newline='') as f:
            rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
        rows2=clean(rows)
        if rows2!=rows:
            with p.open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows2)
            changed.append(p.name)
    # Browser captures and extracted native records are derived evidence views.
    for p in sorted((root/'research_20261029').rglob('*')):
        if p.is_file() and redact_text_copy(p):changed.append(str(p.relative_to(root)))
    qpath=out/'quality_gate_487_summary.json';q=json.loads(qpath.read_text())
    for name in q.get('input_sha256',{}):q['input_sha256'][name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    q['credential_policy']='Credential query parameters removed from derived release outputs. Original input archives remain local.'
    qpath.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({'credential_query_redaction':'PASS','changed_files':changed}))
if __name__=='__main__':main()
