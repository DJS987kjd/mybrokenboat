#!/usr/bin/env python3
import re,json,glob,os,sys
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"site");err=0;titles={};descs={};n=0
for f in glob.glob(f"{OUT}/**/*.html",recursive=True):
    h=open(f).read();n+=1;rel=f[len(OUT):]
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
        try: json.loads(b)
        except Exception as x: print("JSON-LD FAIL",rel,x);err+=1
    for a in re.findall(r'href="(/[^"#]*)"',h):
        t=OUT+a+("index.html" if a.endswith("/") else "")
        if not os.path.exists(t): print("BROKEN",rel,a);err+=1
    for k,d in (("<title>(.*?)</title>",titles),('name="description" content="(.*?)"',descs)):
        v=re.search(k,h).group(1); 
        if v in d: print("DUP",rel,v);err+=1
        d[v]=rel
    for need in ("When in doubt, see a marine mechanic","/disclaimer/",'rel="canonical" href="https://mybrokenboat.com','og:title'):
        if need not in h: print("MISSING",need,rel);err+=1
for u in re.findall(r"<loc>https://mybrokenboat.com(.*?)</loc>",open(f"{OUT}/sitemap.xml").read()):
    if not os.path.exists(OUT+u+"index.html"): print("SITEMAP BROKEN",u);err+=1
print(f"{n} html pages, {err} errors");sys.exit(1 if err else 0)
