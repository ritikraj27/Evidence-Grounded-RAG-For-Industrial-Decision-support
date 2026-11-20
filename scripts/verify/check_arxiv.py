import urllib.request, urllib.parse, xml.etree.ElementTree as ET, time, sys
API="https://export.arxiv.org/api/query"
A="{http://www.w3.org/2005/Atom}"
ids=["2501.11551","2507.21502","2510.24476","2312.10997","2404.16130","2401.15884",
     "2401.17043","2401.15391","2406.13629","2212.08037","2407.01449","2310.11511",
     "2309.15217","2305.14627","2302.09664","2005.11401","2107.03382","2404.16130"]
q=urllib.parse.urlencode({"id_list":",".join(ids),"max_results":len(ids)})
req=urllib.request.Request(API+"?"+q,headers={"User-Agent":"mtp-verify/1.0"})
root=ET.fromstring(urllib.request.urlopen(req,timeout=60).read())
found={}
for e in root.findall(A+"entry"):
    eid=e.find(A+"id").text.rsplit("/",1)[-1]
    t=" ".join(e.find(A+"title").text.split())
    d=e.find(A+"published").text[:10]
    au=[a.find(A+"name").text for a in e.findall(A+"author")]
    found[eid]=(d,t,au)
for i in ids:
    if i in found:
        d,t,au=found[i]
        print(f"[OK]   {i} | {d} | {t[:105]}")
        print(f"       authors: {', '.join(au[:3])}{' ...' if len(au)>3 else ''} ({len(au)} authors)")
    else:
        print(f"[MISS] {i}  <-- NOT FOUND in arXiv")
