#!/usr/bin/env python3
"""Build My Broken Boat static site from library/*.md -> site/. No deps."""
import re, json, html, os, glob, shutil, datetime
ROOT=os.path.dirname(os.path.abspath(__file__)); LIB=f"{ROOT}/library"; OUT=f"{ROOT}/site"
BASE="https://mybrokenboat.com"; NAME="My Broken Boat"; TAG="Outboard Help"
TODAY=datetime.date.today().isoformat()
Q={ # slug: (question H1, group, related)
"01-wont-crank":("Why won't my outboard crank when I turn the key?","Won't start",["21-kill-switch-lanyard","16-battery-charging","02-cranks-wont-fire"]),
"02-cranks-wont-fire":("Why does my outboard crank but not start?","Won't start",["15-primer-bulb","20-spark-plug-fouling","22-choke-enrichment"]),
"03-starts-then-dies":("Why does my outboard start and then die?","Won't start",["15-primer-bulb","11-carb-gummed-after-storage","04-rough-idle"]),
"04-rough-idle":("Why does my outboard idle rough or surge?","Runs poorly",["11-carb-gummed-after-storage","20-spark-plug-fouling","12-ethanol-fuel-issues"]),
"05-stalls-under-throttle":("Why does my outboard bog or stall when I throttle up?","Runs poorly",["10-water-in-fuel","15-primer-bulb","08-loss-of-power-wont-plane"]),
"06-no-telltale-stream":("Why is there no tell-tale (pee) stream from my outboard?","Overheating & cooling",["07-overheating-alarm","26-water-pump-impeller","14-spring-startup","25-submerged-motor"]),
"07-overheating-alarm":("Why is my outboard overheating or sounding the alarm?","Overheating & cooling",["06-no-telltale-stream","26-water-pump-impeller","27-warning-horn-beeping","19-excessive-smoke","08-loss-of-power-wont-plane"]),
"08-loss-of-power-wont-plane":("Why has my outboard lost power or won't plane?","Runs poorly",["09-prop-cavitation-ventilation","05-stalls-under-throttle","17-trim-tilt","27-warning-horn-beeping"]),
"09-prop-cavitation-ventilation":("Why does my prop slip, ventilate, or cavitate?","Runs poorly",["08-loss-of-power-wont-plane","17-trim-tilt","18-shifting-problems"]),
"10-water-in-fuel":("How do I tell if there's water in my outboard fuel?","Fuel problems",["12-ethanol-fuel-issues","05-stalls-under-throttle","03-starts-then-dies","27-warning-horn-beeping"]),
"11-carb-gummed-after-storage":("How do I fix a carburetor gummed up after storage?","Fuel problems",["12-ethanol-fuel-issues","14-spring-startup","04-rough-idle"]),
"12-ethanol-fuel-issues":("What problems does ethanol (E10) fuel cause in outboards?","Fuel problems",["10-water-in-fuel","11-carb-gummed-after-storage","13-winterizing"]),
"13-winterizing":("How do I winterize an outboard motor?","Seasonal care",["14-spring-startup","24-gear-oil-milky","12-ethanol-fuel-issues","26-water-pump-impeller"]),
"14-spring-startup":("How do I start my outboard after winter storage?","Seasonal care",["13-winterizing","11-carb-gummed-after-storage","16-battery-charging"]),
"15-primer-bulb":("Why won't my primer bulb firm up?","Fuel problems",["03-starts-then-dies","02-cranks-wont-fire","10-water-in-fuel"]),
"16-battery-charging":("Why is my outboard battery not charging?","Electrical & controls",["01-wont-crank","17-trim-tilt","14-spring-startup"]),
"17-trim-tilt":("Why isn't my power trim/tilt working?","Electrical & controls",["16-battery-charging","09-prop-cavitation-ventilation","08-loss-of-power-wont-plane"]),
"18-shifting-problems":("Why is my outboard hard to shift or not shifting?","Electrical & controls",["24-gear-oil-milky","09-prop-cavitation-ventilation","01-wont-crank"]),
"19-excessive-smoke":("Why is my outboard smoking so much?","Runs poorly",["20-spark-plug-fouling","22-choke-enrichment","07-overheating-alarm"]),
"20-spark-plug-fouling":("Why do my outboard spark plugs keep fouling?","Runs poorly",["19-excessive-smoke","22-choke-enrichment","02-cranks-wont-fire"]),
"21-kill-switch-lanyard":("Is my kill switch or lanyard stopping my outboard?","Electrical & controls",["01-wont-crank","02-cranks-wont-fire","03-starts-then-dies"]),
"22-choke-enrichment":("How do I fix outboard choke or enrichment problems?","Won't start",["02-cranks-wont-fire","20-spark-plug-fouling","11-carb-gummed-after-storage"]),
"23-pull-start-recoil":("Why won't my outboard pull-start cord work?","Won't start",["02-cranks-wont-fire","22-choke-enrichment","21-kill-switch-lanyard"]),
"24-gear-oil-milky":("Why is my outboard gear oil milky?","Seasonal care",["18-shifting-problems","13-winterizing","25-submerged-motor"]),
"25-submerged-motor":("What do I do if my outboard was submerged?","Emergencies",["24-gear-oil-milky","06-no-telltale-stream","16-battery-charging"]),
"26-water-pump-impeller":("How often should I replace my outboard water pump impeller?","Overheating & cooling",["06-no-telltale-stream","07-overheating-alarm","13-winterizing"]),
"27-warning-horn-beeping":("Why is my outboard beeping?","Electrical & controls",["07-overheating-alarm","10-water-in-fuel","16-battery-charging"]),
}
GROUPS=["Won't start","Runs poorly","Overheating & cooling","Fuel problems","Electrical & controls","Seasonal care","Emergencies"]
e=html.escape
def inline(s):
    s=e(s,quote=False)
    s=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",s); s=re.sub(r"(?<!\*)\*([^*]+)\*",r"<em>\1</em>",s)
    s=re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",r'<a href="\2" rel="nofollow noopener">\1</a>',s)
    s=re.sub(r'(?<![">])(https?://[^\s<]+)',r'<a href="\1" rel="nofollow noopener">\1</a>',s)
    return s
def parse(path):
    lines=open(path).read().splitlines(); d={"title":lines[0].lstrip("# ").strip(),"sections":[],"intro":[]}
    cur=None
    for l in lines[1:]:
        if l.startswith("## "): cur={"h":l[3:].strip(),"items":[],"kind":None,"text":[]}; d["sections"].append(cur); continue
        m=re.match(r"\s*(\d+\.|[-*])\s+(.*)",l)
        tgt=cur if cur else None
        if m and tgt is not None: tgt["kind"]=tgt["kind"] or ("ol" if m.group(1)[0].isdigit() else "ul"); tgt["items"].append(m.group(2))
        elif l.strip():
            (tgt["text"] if tgt else d["intro"]).append(l.strip())
    return d
def plain(s): return re.sub(r"[*_`]|\[([^\]]+)\]\([^)]+\)",r"\1",s)
def sec(d,key):
    for s in d["sections"]:
        if s["h"].lower().startswith(key): return s
CSS=""".newsletter{background:#fff;border:1px solid #dde5ec;border-radius:8px;padding:1rem;margin-top:2rem}.newsletter input[type=email]{padding:.5rem;font:inherit;min-width:16rem}.newsletter button{padding:.5rem 1rem;font:inherit;background:#0b3954;color:#fff;border:0;border-radius:4px}.fine{font-size:.85rem;opacity:.8}
*{box-sizing:border-box}body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1b2733;background:#f7f9fb}
a{color:#0b5fa5}header{background:#0b3954;color:#fff}header .w{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4rem 1.2rem;padding:.8rem 1rem}
header a{color:#fff;text-decoration:none}.brand{font-weight:800;font-size:1.3rem}.tag{opacity:.8;font-size:.95rem}nav{margin-left:auto;display:flex;gap:1rem;font-size:.95rem}
.w{max-width:52rem;margin:0 auto;padding:1rem}h1{line-height:1.25;font-size:1.7rem}h2{margin-top:1.8rem;font-size:1.25rem;border-bottom:2px solid #dde5ec}
.answer{background:#e8f3fb;border-left:5px solid #0b5fa5;padding:.8rem 1rem;border-radius:4px}.safety{background:#fff6e0;border:1px solid #f0c36d;padding:.7rem 1rem;border-radius:6px;font-size:.93rem;margin:1rem 0}
.placeholder{border:2px dashed #999;padding:1rem;border-radius:6px;background:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem}
.card{background:#fff;border:1px solid #dde5ec;border-radius:8px;padding:.6rem 1rem}.card ul{padding-left:1.1rem}.src{font-size:.88rem;word-break:break-all}
footer{border-top:1px solid #dde5ec;margin-top:2rem;font-size:.88rem;color:#555}input,textarea,button{font:inherit;padding:.4rem;width:100%;max-width:30rem}button{width:auto}"""
SAFETY='<aside class="safety" role="note"><strong>Safety first:</strong> General information only, not a substitute for your owner\'s manual or a qualified technician. Gasoline vapor is explosive; work safely. In danger on the water? Call the Coast Guard (VHF 16). <strong>When in doubt, see a marine mechanic.</strong> <a href="/disclaimer/">Read the full disclaimer</a>.</aside>'
def page(path,title,desc,body,ld=None,ogtype="website"):
    url=BASE+path; lds="".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False).replace("</","<\\/")}</script>' for x in (ld or []))
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary"><link rel="stylesheet" href="/style.css">{lds}</head><body>
<header><div class="w"><a class="brand" href="/">{NAME}</a><span class="tag">{TAG}</span><nav><a href="/">Problems</a><a href="/about/">About</a><a href="/newsletter/">Newsletter</a><a href="/contact/">Contact</a></nav></div></header>
<main class="w">{SAFETY}{body}</main><footer><div class="w">&copy; {datetime.date.today().year} {NAME} &middot; {TAG} &middot; <a href="/disclaimer/">Disclaimer</a> &middot; <a href="/about/">About</a> &middot; <a href="/contact/">Contact</a><br>When in doubt, see a marine mechanic. Brand names are trademarks of their owners; no affiliation implied.</div></footer></body></html>"""
    f=OUT+path+("index.html" if path.endswith("/") else ""); os.makedirs(os.path.dirname(f),exist_ok=True); open(f,"w").write(h)
NEWS='<section class="newsletter" id="newsletter"><h2>Get free outboard tips by email</h2><p>A short seasonal email with common fixes. No spam. Unsubscribe anytime.</p><form method="post" action="/api/subscribe"><label for="nl-email">Email</label> <input id="nl-email" type="email" name="email" required autocomplete="email" maxlength="254"><input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px"> <button type="submit">Subscribe</button></form><p class="fine">We\'ll email you a link to confirm. You\'re only added after you click it.</p></section>'
def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); open(f"{OUT}/style.css","w").write(CSS)
    probs={}
    for p in sorted(glob.glob(f"{LIB}/[0-9]*.md")):
        slug=os.path.basename(p)[:-3]; d=parse(p); d["mod"]=datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat(); probs[slug]=d
    pages=[]
    for slug,d in probs.items():
        q,grp,rel=Q[slug]; path=f"/problems/{slug[3:]}/"; d["path"]=path; d["q"]=q
    for slug,d in probs.items():
        q,grp,rel=Q[slug]; symptom=next((plain(x).replace("Symptom:","").strip() for x in d["intro"] if "Symptom" in x),"")
        causes=sec(d,"likely"); fixes=sec(d,"safe"); mech=sec(d,"call"); srcs=sec(d,"sources")
        cl=[plain(x) for x in (causes["items"] if causes else [])][:3]
        fx=[plain(x) for x in fixes["items"]]
        ans=(f"Most often: {', '.join(c[0].lower()+c[1:] for c in cl)}. " if cl else "")+f"Start here: {fx[0]} If that doesn't fix it, work through the checks below, and see a marine mechanic if you're unsure."
        qa=sec(d,"quick answer")
        if qa and qa["text"]: ans=plain(" ".join(qa["text"]))
        d["answer"]=ans
        body=f"<h1>{e(q)}</h1><p><em>{e(d['title'])}</em>{(' &middot; Symptom: '+e(symptom)) if symptom else ''}</p><p class=\"answer\"><strong>Quick answer:</strong> {e(ans)}</p>"
        for s in d["sections"]:
            if s is srcs or s is qa: continue
            body+=f"<h2>{e(s['h'])}</h2>"
            for t in s["text"]: body+=f"<p>{inline(t)}</p>"
            if s["items"]: body+=f"<{s['kind']}>"+"".join(f"<li>{inline(i)}</li>" for i in s["items"])+f"</{s['kind']}>"
        surls=[re.search(r"https?://\S+",x).group(0) for x in (srcs["items"] if srcs else []) if re.search(r"https?://\S+",x)]
        if srcs: body+='<h2>Sources</h2><ul class="src">'+"".join(f"<li>{inline(i)}</li>" for i in srcs["items"])+"</ul>"+"".join(f"<p class=\"src\">{inline(t)}</p>" for t in srcs["text"] if "Private draft" not in t)
        body+="<p><em>Values not stated here are model-specific; check your owner's manual.</em></p>"
        body+='<h2>Related problems</h2><ul>'+"".join(f'<li><a href="{probs[r]["path"]}">{e(probs[r]["q"])}</a></li>' for r in rel)+"</ul>"
        desc=(ans[:150].rsplit(" ",1)[0]+"…") if len(ans)>155 else ans
        url=BASE+d["path"]
        ld=[{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}}]},
            {"@context":"https://schema.org","@type":"HowTo","name":d["title"],"description":ans,"step":[{"@type":"HowToStep","position":i+1,"text":t} for i,t in enumerate(fx)],
             **({"tool":[{"@type":"HowToTool","name":plain(sec(d,'parts')['text'][0] if sec(d,'parts')['text'] else '')}]} if sec(d,"parts") else {}),"citation":surls,"url":url},
            {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":d["title"],"item":url}]}]
        page(d["path"],f"{q} | {NAME}",desc,body,ld,"article"); pages.append((d["path"],q,ans))
    # home
    body=f"<h1>Outboard motor troubleshooting: what's wrong with my boat motor?</h1><p>Plain-English fixes for common outboard problems, organized by symptom. Each page gives a quick answer, likely causes, safe owner checks, parts, and when to call a pro, with sources.</p><div class=\"grid\">"
    for g in GROUPS:
        body+=f'<section class="card"><h2>{e(g)}</h2><ul>'+"".join(f'<li><a href="{d["path"]}">{e(d["q"])}</a></li>' for s,d in probs.items() if Q[s][1]==g)+"</ul></section>"
    body+="</div>"+NEWS
    org={"@context":"https://schema.org","@type":"Organization","name":NAME,"url":BASE+"/","slogan":TAG}
    web={"@context":"https://schema.org","@type":"WebSite","name":NAME,"alternateName":f"{NAME}: {TAG}","url":BASE+"/","publisher":{"@type":"Organization","name":NAME}}
    page("/",f"{NAME}: {TAG}. Outboard Motor Troubleshooting","Free, plain-English outboard motor troubleshooting by symptom: won't start, overheating, fuel problems, rough idle and more, with sources.",body,[org,web])
    dl=open(f"{LIB}/DISCLAIMER-draft.md").read().splitlines()[1:]
    db="<h1>Disclaimer</h1>"+"".join((f"<li>{inline(l[2:])}</li>" if l.startswith("- ") else f"<p>{inline(l)}</p>") for l in dl if l.strip() and "[If affiliate" not in l)
    db=re.sub(r"(<li>.*</li>)",r"<ul>\1</ul>",db,flags=re.S).replace(" [If affiliate links are added, disclose them here.]","")
    db+=f"<p><em>Last updated {TODAY}.</em></p>"
    page("/disclaimer/",f"Disclaimer | {NAME}","Safety and liability disclaimer for My Broken Boat's outboard troubleshooting information.",db)
    page("/about/",f"About | {NAME}","About My Broken Boat: simple, sourced outboard motor troubleshooting for boat owners.",
      "<h1>What is My Broken Boat?</h1><p>My Broken Boat (Outboard Help) collects common outboard motor fixes from owner's manuals and manufacturer resources and explains them in plain English, so you can try the safe, simple checks first and know when it's time for a pro.</p><p>Every page lists its sources. Specs vary by make, model, and year, so your owner's manual always wins. We don't sell parts, and the site has no ads, affiliate links, or tracking.</p>"+NEWS)
    page("/contact/",f"Contact | {NAME}","Ask My Broken Boat a simple outboard troubleshooting question.",
      '<h1>How do I ask an outboard question?</h1><p>Tell us your motor\'s make, model, year, and what it\'s doing. We answer simple troubleshooting questions.</p><section class="placeholder" id="contact-form"><!-- PLACEHOLDER: contact form. Not connected to any service; see README.md --><h2>Contact form (coming soon)</h2><p>The question form isn\'t active yet. Please check back soon.</p><form onsubmit="return false" aria-disabled="true"><label>Email<br><input type="email" disabled></label><br><label>Motor make/model/year<br><input disabled></label><br><label>What\'s happening?<br><textarea rows="5" disabled></textarea></label><br><button disabled>Send (not active)</button></form></section>')
    page("/newsletter/",f"Newsletter | {NAME}","Sign up for free seasonal outboard motor tips from My Broken Boat.",
      "<h1>Want outboard tips by email?</h1><p>Every so often we send a short email with the most common outboard problems people are asking about and how to fix them.</p><p id=\"nl-err\" hidden>Something went wrong or that link expired. Please try again.</p><script>if(location.search.includes('error'))document.getElementById('nl-err').hidden=false</script>"+NEWS)
    page("/newsletter/check-email/",f"Check your email | {NAME}","Confirm your My Broken Boat newsletter signup from your inbox.",
      "<h1>Check your email</h1><p>We sent you a confirmation link. Click it to finish signing up. If you don't see it, check spam.</p><p><a href=\"/\">Back to problems</a></p>")
    page("/newsletter/confirmed/",f"You're subscribed | {NAME}","Your My Broken Boat newsletter subscription is confirmed.",
      "<h1>You're subscribed</h1><p>Thanks! You'll get our next email. Every email has an unsubscribe link.</p><p><a href=\"/\">Back to problems</a></p>")
    allp=["/","/about/","/contact/","/disclaimer/","/newsletter/"]+[p for p,_,_ in pages]
    mods={d["path"]:d["mod"] for d in probs.values()}; newest=max(list(mods.values())+[datetime.date.fromtimestamp(os.path.getmtime(__file__)).isoformat()])
    open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"  <url><loc>{BASE}{p}</loc><lastmod>{mods.get(p,newest)}</lastmod></url>\n" for p in allp)+"</urlset>\n")
    open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /newsletter/check-email/\nDisallow: /newsletter/confirmed/\n\nSitemap: {BASE}/sitemap.xml\n")
    llm=f"# {NAME}\n\n> {TAG}: free, plain-English troubleshooting for common outboard boat motor problems. Each page has a short quick answer, likely causes, safe owner checks, parts/tools, when to call a marine mechanic, and source citations. General information only; specs are model-specific, so follow the owner's manual. When in doubt, see a marine mechanic.\n\n"
    for g in GROUPS:
        llm+=f"## {g}\n\n"+"".join(f"- [{q}]({BASE}{p}): {a}\n" for p,q,a in pages if Q["%s"%[s for s,d in probs.items() if d['path']==p][0]][1]==g)+"\n"
    llm+=f"## Site\n\n- [Disclaimer]({BASE}/disclaimer/)\n- [About]({BASE}/about/)\n- [Contact]({BASE}/contact/)\n"
    open(f"{OUT}/llms.txt","w").write(llm)
    print(f"built {len(allp)} pages")
if __name__=="__main__": main()
