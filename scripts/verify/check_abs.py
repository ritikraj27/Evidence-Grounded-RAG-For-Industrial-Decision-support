import urllib.request, urllib.parse, xml.etree.ElementTree as ET, time
A="{http://www.w3.org/2005/Atom}"
def fetch(ids, tries=5):
    for t in range(tries):
        try:
            url="https://export.arxiv.org/api/query?"+urllib.parse.urlencode({"id_list":",".join(ids),"max_results":len(ids)})
            req=urllib.request.Request(url,headers={"User-Agent":"mtp-verify/1.0"})
            return ET.fromstring(urllib.request.urlopen(req,timeout=60).read())
        except Exception as e:
            print(f"  retry {t+1}: {e}"); time.sleep(8*(t+1))
    return None
root=fetch(["2507.21502","2510.24476","2407.01449","2501.11551"])
if root is None: raise SystemExit("arXiv unavailable")
for e in root.findall(A+"entry"):
    eid=e.find(A+"id").text.rsplit("/",1)[-1]
    t=" ".join(e.find(A+"title").text.split())
    pub=e.find(A+"published").text[:10]; upd=e.find(A+"updated").text[:10]
    com=e.find(A+"comment")
    jr=e.find("{http://arxiv.org/schemas/atom}journal_ref")
    doi=e.find("{http://arxiv.org/schemas/atom}doi")
    au=[a.find(A+"name").text for a in e.findall(A+"author")]
    print(f"--- {eid} ---")
    print(f"TITLE : {t}")
    print(f"AUTHORS ({len(au)}): {'; '.join(au)}")
    print(f"published {pub} | updated {upd}")
    if com is not None: print(f"COMMENT: {' '.join(com.text.split())}")
    if jr is not None: print(f"JOURNAL_REF: {' '.join(jr.text.split())}")
    if doi is not None: print(f"DOI: {doi.text}")
    print()
