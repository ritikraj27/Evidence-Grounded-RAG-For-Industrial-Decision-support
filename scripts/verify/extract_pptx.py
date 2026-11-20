import sys, zipfile, re, xml.etree.ElementTree as ET
A="{http://schemas.openxmlformats.org/drawingml/2006/main}"
p=sys.argv[1]
z=zipfile.ZipFile(p)
names=sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$",n)],
             key=lambda n:int(re.search(r"(\d+)",n.split("/")[-1]).group(1)))
print(f"### {p} -> {len(names)} slides")
for n in names:
    root=ET.fromstring(z.read(n))
    txt=[]
    for sp in root.iter():
        if sp.tag.endswith("}txBody"):
            for para in sp.iter(f"{A}p"):
                s="".join(t.text or "" for t in para.iter(f"{A}t"))
                if s.strip(): txt.append(s.strip())
    # notes
    num=int(re.search(r"(\d+)",n.split("/")[-1]).group(1))
    notes=""
    npath=f"ppt/notesSlides/notesSlide{num}.xml"
    if npath in z.namelist():
        nr=ET.fromstring(z.read(npath))
        nt=[]
        for para in nr.iter(f"{A}p"):
            s="".join(t.text or "" for t in para.iter(f"{A}t"))
            if s.strip() and s.strip()!="‹#›": nt.append(s.strip())
        if nt: notes=" [NOTES: "+" | ".join(nt)[:300]+"]"
    print(f"\n--- SLIDE {num} ---")
    print("\n".join(txt)[:2200])
    if notes: print(notes)
