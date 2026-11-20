import urllib.request, urllib.parse, json
def oa(doi=None, title=None):
    if doi: q=urllib.parse.urlencode({"filter":f"doi:{doi}"})
    else: q=urllib.parse.urlencode({"search":title,"per-page":3})
    url="https://api.openalex.org/works?"+q+"&mailto=ritik@example.com"
    req=urllib.request.Request(url,headers={"User-Agent":"mtp-verify/1.0"})
    try:
        d=json.loads(urllib.request.urlopen(req,timeout=60).read())
    except Exception as e:
        print(f"[ERR] {doi or title}: {e}"); return
    for w in d.get("results",[])[:3]:
        print(f"  * {w.get('title')}")
        print(f"    year={w.get('publication_year')} type={w.get('type')} doi={w.get('doi')} cites={w.get('cited_by_count')}")
        loc=(w.get("primary_location") or {}).get("source") or {}
        print(f"    venue={loc.get('display_name')}  host={(loc.get('source') or {}).get('host_organization_name')}")
        auths=[]
        for a in (w.get("authorships") or [])[:6]:
            inst=[i.get("display_name") for i in (a.get("institutions") or [])]
            auths.append(f"{a.get('author',{}).get('display_name')}[{','.join([i for i in inst if i]) or '-'}]")
        print(f"    authors: {'; '.join(auths)}")
        print()
    if not d.get("results"): print("  NO RESULTS\n")

print("### arXiv:2507.21502 (claimed 'Microsoft') ###")
oa(doi="https://arxiv.org/abs/2507.21502")
print("### ColPali venue check ###")
oa(doi="https://arxiv.org/abs/2407.01449")
