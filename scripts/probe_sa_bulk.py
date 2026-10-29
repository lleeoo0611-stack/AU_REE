#!/usr/bin/env python3
"""Read-only South Australia bulk export and WFS diagnostics (NO commodity screening)."""
import json,re,requests,xml.etree.ElementTree as ET,pathlib
from urllib.parse import urljoin
OUT=pathlib.Path("work/sa_probe");OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session();S.headers.update({"User-Agent":"Australian-REE-academic-inventory/1.0"})
RESULT=[]
def probe(name,url,params=None,save=False):
    try:
        r=S.get(url,params=params,timeout=(12,45),allow_redirects=True)
        body=r.content
        item={"name":name,"status":r.status_code,"type":r.headers.get("Content-Type"),"length":len(body),"url":r.url.split("?")[0],"prefix":r.text[:600] if r.encoding or "xml" in (r.headers.get("content-type") or "") else ""}
        if save and len(body)<3_000_000:(OUT/(name+".txt")).write_bytes(body)
        RESULT.append(item)
        print(name,json.dumps(item,ensure_ascii=False),flush=True)
        return r
    except Exception as e:
        item={"name":name,"error":str(e)[:300]};RESULT.append(item);print(name,json.dumps(item),flush=True)
        return None
page=probe("sa_bulk_index","https://dem-sdp.s3-ap-southeast-2.amazonaws.com/index.html",save=True)
if page is not None:
    text=page.text
    links=re.findall(r'(?i)(?:href|src)\\s*=\\s*[\x22\x27]([^\x22\x27]+)',text)
    print("sa_index_links",json.dumps(links[:80]),flush=True)
    print("sa_index_excerpts",re.sub(r'\\s+',' ',text)[:1500],flush=True)
bucket=probe("sa_s3_listing","https://dem-sdp.s3-ap-southeast-2.amazonaws.com/",params={"list-type":"2","max-keys":"1000"},save=True)
if bucket is not None and bucket.status_code==200:
    print("S3_KEYS",re.findall(r'<Key>([^<]+)</Key>',bucket.text)[:80],flush=True)
sites=[
 ("SA_PROJECT","https://services.sarig.sa.gov.au/vector/south_australia_mining_projects/wfs","south_australia_mining_projects:developing_projects___minerals"),
 ("SA_MINDEP","https://services.sarig.sa.gov.au/vector/mines_and_mineral_deposits/wfs","mines_and_mineral_deposits:all_mines_and_mineral_deposits"),
 ("SA_CRITICAL","https://services.sarig.sa.gov.au/vector/south_australian_critical_minerals/wfs","south_australian_critical_minerals:rare_earth_elements")
]
for name,url,typename in sites:
    cap=probe(name+"_caps",url,{"service":"WFS","request":"GetCapabilities","version":"1.1.0"},save=True)
    if cap is not None and cap.ok:
        try:
            root=ET.fromstring(cap.content);print(name,"cap_root",root.tag,flush=True)
        except Exception as e:print(name,"cap_parse_error",str(e),flush=True)
    for style,params in [
       ("basic",{"service":"WFS","version":"2.0.0","request":"GetFeature","typeNames":typename,"count":"1"}),
       ("csv",{"service":"WFS","version":"2.0.0","request":"GetFeature","typeNames":typename,"count":"1","outputFormat":"csv"}),
       ("v11",{"service":"WFS","version":"1.1.0","request":"GetFeature","typeName":typename,"maxFeatures":"1","outputFormat":"text/csv"})
    ]:
        probe(name+"_"+style,url,params,save=True)
(OUT/"summary.json").write_text(json.dumps(RESULT,indent=2,ensure_ascii=False),encoding="utf8")
