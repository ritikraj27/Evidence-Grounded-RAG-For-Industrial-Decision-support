import urllib.request, json, urllib.parse
ids=["DOI:10.1016/j.aei.2025.103212","DOI:10.1016/j.aei.2025.103158","DOI:10.1016/j.neucom.2026.134911",
     "DOI:10.1016/j.neucom.2026.134357","DOI:10.3390/math13050856","DOI:10.1038/s41586-024-07421-0",
     "DOI:10.1145/3701228","DOI:10.18653/v1/2020.emnlp-main.550","DOI:10.1145/3618407.3620365"]
url="https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,venue,abstract,authors,externalIds,citationCount"
req=urllib.request.Request(url,data=json.dumps({"ids":ids}).encode(),headers={"Content-Type":"application/json","User-Agent":"v/1"})
for i,p in zip(ids,json.loads(urllib.request.urlopen(req,timeout=90).read())):
    if not p: print(f"[MISS] {i}"); continue
    print(f"--- {i} | {p.get('year')} | {p.get('venue')} | cites={p.get('citationCount')}")
    print(f"    {p.get('title')}")
    au=", ".join(a['name'] for a in (p.get('authors') or [])[:3]); print(f"    {au}")
    ab=(p.get('abstract') or 'NO ABSTRACT IN S2')
    print("    ABS: "+ab.replace("\n"," ")[:1400])
    print()
