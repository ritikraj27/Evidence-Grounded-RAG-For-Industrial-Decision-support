import urllib.request, json
ids=["arXiv:2501.11551","arXiv:2507.21502","arXiv:2510.24476","arXiv:2312.10997","arXiv:2404.16130",
 "arXiv:2401.15884","arXiv:2401.17043","arXiv:2401.15391","arXiv:2406.13629","arXiv:2212.08037",
 "arXiv:2407.01449","arXiv:2310.11511","arXiv:2309.15217","arXiv:2305.14627","arXiv:2302.09664",
 "arXiv:2005.11401","arXiv:2107.03382","arXiv:2410.05779","arXiv:2408.03314","arXiv:2401.15391"]
url="https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,venue,externalIds,authors,abstract,citationCount"
data=json.dumps({"ids":ids}).encode()
req=urllib.request.Request(url,data=data,headers={"Content-Type":"application/json","User-Agent":"mtp-verify/1.0"})
res=json.loads(urllib.request.urlopen(req,timeout=90).read())
for i,p in zip(ids,res):
    if p is None:
        print(f"[MISS] {i}   <-- NOT FOUND")
    else:
        au=", ".join(a["name"] for a in (p.get("authors") or [])[:3])
        print(f"[OK]   {i} | {p.get('year')} | {p.get('venue') or 'n/a'}")
        print(f"       {p.get('title')}")
        print(f"       {au} | cites={p.get('citationCount')} | DOI={ (p.get('externalIds') or {}).get('DOI','-') }")
