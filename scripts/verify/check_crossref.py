import urllib.request, urllib.parse, json, time
def cr(q,label):
    url="https://api.crossref.org/works?"+urllib.parse.urlencode({"query.bibliographic":q,"rows":3,"select":"DOI,title,author,container-title,volume,page,issued,type"})
    req=urllib.request.Request(url,headers={"User-Agent":"mtp-verify/1.0 (mailto:ritik@example.com)"})
    try:
        items=json.loads(urllib.request.urlopen(req,timeout=60).read())["message"]["items"]
    except Exception as e:
        print(f"[ERR] {label}: {e}"); return
    print(f"=== {label} ===")
    if not items: print("   NO RESULTS"); return
    for it in items:
        t=" ".join((it.get("title") or ["?"])[0].split())
        ct=(it.get("container-title") or ["-"])[0]
        au=", ".join(f"{a.get('given','')} {a.get('family','')}".strip() for a in (it.get("author") or [])[:3])
        yr=(it.get("issued",{}).get("date-parts") or [[None]])[0][0]
        print(f"  DOI:{it.get('DOI')}")
        print(f"    {t[:100]}")
        print(f"    {ct} | vol {it.get('volume')} p{it.get('page')} | {yr} | {au}")
    print()

cr("Dynamic RAG with hybrid retrieval robust LLMs hallucination prevention Neurocomputing","A: Decian Neurocomputing 2026")
cr("Empowering LLMs by hybrid retrieval-augmented generation domain-centric Q&A smart manufacturing","B: Wan AdvEngInform")
cr("Retrieval augmented generation-driven information retrieval and question answering in construction management","C: Wu AdvEngInform")
cr("Hallucination mitigation for retrieval-augmented large language models A review Mathematics","D: Zhang&Zhang Mathematics 2025")
cr("Detecting hallucinations in large language models using semantic entropy Nature","E: Farquhar Nature 2024")
