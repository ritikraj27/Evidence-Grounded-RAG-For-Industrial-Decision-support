import urllib.request, json
ids=["arXiv:2605.05244","arXiv:2610.28340","arXiv:2604.20854","arXiv:2603.21172",
     "arXiv:2604.27914","arXiv:2411.08891","arXiv:2411.06037","arXiv:2403.14403",
     "arXiv:2305.06983","arXiv:2403.10081","arXiv:2406.15927","arXiv:2207.05221",
     "arXiv:2405.01563","arXiv:2311.08298","arXiv:2310.01798","arXiv:1806.03822"]
url="https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,venue,citationCount,authors"
req=urllib.request.Request(url,data=json.dumps({"ids":ids}).encode(),headers={"Content-Type":"application/json","User-Agent":"v/1"})
for i,p in zip(ids,json.loads(urllib.request.urlopen(req,timeout=90).read())):
    if not p: print(f"[MISS] {i}"); continue
    print(f"[OK] {i} | {p.get('year')} | {p.get('venue') or 'n/a'} | cites={p.get('citationCount')}")
    print(f"     {p.get('title')}")
