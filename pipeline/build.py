#!/usr/bin/env python3
"""Gera carousel.html a partir de um content.json.
Uso: python3 pipeline/build.py content.json [saida.html]
Roda a partir da raiz do repo (usa assets/ relativo)."""
import base64, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def b64(p):
    with open(p, "rb") as fh:
        return base64.b64encode(fh.read()).decode()

def asset(*p):
    return os.path.join(ROOT, "assets", *p)

def main():
    cj = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "content.json")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "carousel.html")
    with open(cj) as fh:
        C = json.load(fh)

    pal = {
        "P": "#1B3A6B", "PL": "#6E9BDC", "PD": "#0A1834",
        "LB": "#F3EFE8", "LR": "#E4DCCF", "DB": "#0B1730",
    }
    pal.update(C.get("palette", {}))
    handle = C["brand"]["handle"]
    initial = C["brand"].get("initial", "M")

    bc900 = b64(asset("fonts", "bc900.woff2"))
    pj400 = b64(asset("fonts", "pj400.woff2"))
    pj500 = b64(asset("fonts", "pj500.woff2"))
    pj700 = b64(asset("fonts", "pj700.woff2"))
    pj800 = b64(asset("fonts", "pj800.woff2"))
    logo_w = b64(asset("logo_white.png"))
    logo_n = b64(asset("logo_navy.png"))

    def photo(name):
        # procura no banco fixo (fotos/) e nas baixadas da internet (_net/)
        path = asset("fotos", name)
        if not os.path.exists(path):
            alt = asset("_net", name)
            if os.path.exists(alt):
                path = alt
        ext = "png" if name.lower().endswith("png") else "jpeg"
        return f"data:image/{ext};base64,{b64(path)}"

    GRAIN = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>"

    total = 1 + len(C["slides"])

    def brandbar(cls):
        return (f'<div class="brand-bar {cls}"><span>Powered by Content Machine</span>'
                f'<span>{handle}</span><span>2026 &reg;</span></div>')

    def prog(cls, n):
        pct = round(n / total * 100)
        return (f'<div class="prog {cls}"><div class="prog-track"><div class="prog-fill" '
                f'style="width:{pct}%"></div></div><div class="prog-num">{n}/{total}</div></div>')

    parts = []
    # CAPA
    capa = C["capa"]
    type_badge = ""
    if capa.get("type_label"):
        type_badge = (f'<div class="capa-type-badge2"><span class="capa-type-label">'
                      f'{capa["type_label"]}</span><span class="capa-date">'
                      f'{capa.get("date","")}</span></div>')
    parts.append(f"""
<div class="slide slide-capa" id="slide-1">
  <div class="capa-bg" style="background-image:url('{photo(capa["image"])}')"></div>
  <div class="capa-grad"></div>
  <div class="accent-bar"></div>
  <div class="brand-bar on-dark"><span>Powered by Content Machine</span><span>{handle}</span><span>2026 &reg;</span></div>
  {type_badge}
  <div class="capa-headline-area">
    <img class="capa-logo" src="data:image/png;base64,{logo_w}" alt="logo">
    <div class="capa-headline">{capa["headline"]}</div>
  </div>
  <div class="grain"></div>
</div>""")

    # SLIDES INTERNOS
    for i, s in enumerate(C["slides"], start=2):
        layout = s["layout"]
        if layout == "cta":
            parts.append(f"""
<div class="slide slide-cta on-light" id="slide-{i}">
  <div class="accent-bar"></div>
  {brandbar('on-light')}
  <div class="content">
    <div class="cta-bridge">{s["bridge"]}</div>
    <div class="cta-headline">{s["headline"]}</div>
    <div class="cta-kbox">
      <div class="cta-kinstr">{s.get("kinstr","Pra n&atilde;o perder a pr&oacute;xima:")}</div>
      <div class="cta-kword">{s["kword"]}</div>
      <div class="cta-kbenefit">{s.get("kbenefit","")}</div>
    </div>
    <div class="cta-footer">
      <img class="cta-logo" src="data:image/png;base64,{logo_n}" alt="logo">
    </div>
  </div>
  {prog('on-light', i)}
  <div class="grain"></div>
</div>""")
        elif layout == "grad":
            imgbg = ""
            if s.get("image"):
                imgbg = (f'<div class="slide-img-bg" style="background-image:url(\'{photo(s["image"])}\')"></div>'
                         f'<div class="grad-img-overlay"></div>')
            parts.append(f"""
<div class="slide slide-grad on-grad{' with-img' if s.get('image') else ''}" id="slide-{i}">
  {imgbg}
  <div class="accent-bar on-grad"></div>
  {brandbar('on-grad')}
  <div class="content">
    <div class="tag">{s.get("tag","")}</div>
    <div class="grad-h1">{s["h1"]}</div>
    <div class="grad-body">{s["body"]}</div>
  </div>
  {prog('on-grad', i)}
  <div class="grain"></div>
</div>""")
        else:  # dark | light
            cls = "slide-dark on-dark" if layout == "dark" else "slide-light on-light"
            hcls = "dark-h1" if layout == "dark" else "light-h1"
            bcls = "dark-body" if layout == "dark" else "light-body"
            imgbg = ""
            withimg = ""
            if s.get("image"):
                imgbg = (f'<div class="slide-img-bg" style="background-image:url(\'{photo(s["image"])}\')"></div>'
                         f'<div class="slide-img-overlay"></div>')
                withimg = " with-img"
            parts.append(f"""
<div class="slide {cls}{withimg}" id="slide-{i}">
  {imgbg}
  <div class="accent-bar"></div>
  {brandbar('on-dark' if layout=='dark' else 'on-light')}
  <div class="content">
    <div class="tag">{s.get("tag","")}</div>
    <div class="{hcls}">{s["h1"]}</div>
    <div class="{bcls}">{s["body"]}</div>
  </div>
  {prog('on-dark' if layout=='dark' else 'on-light', i)}
  <div class="grain"></div>
</div>""")

    slides_html = "\n".join(parts)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>Carrossel {C.get("date","")}</title>
<style>
@font-face{{font-family:'Barlow Condensed';font-weight:900;font-display:block;src:url(data:font/woff2;base64,{bc900}) format('woff2');}}
@font-face{{font-family:'Plus Jakarta Sans';font-weight:400;font-display:block;src:url(data:font/woff2;base64,{pj400}) format('woff2');}}
@font-face{{font-family:'Plus Jakarta Sans';font-weight:500;font-display:block;src:url(data:font/woff2;base64,{pj500}) format('woff2');}}
@font-face{{font-family:'Plus Jakarta Sans';font-weight:700;font-display:block;src:url(data:font/woff2;base64,{pj700}) format('woff2');}}
@font-face{{font-family:'Plus Jakarta Sans';font-weight:800;font-display:block;src:url(data:font/woff2;base64,{pj800}) format('woff2');}}
:root{{--P:{pal['P']};--PL:{pal['PL']};--PD:{pal['PD']};--LB:{pal['LB']};--LR:{pal['LR']};--DB:{pal['DB']};
--G:linear-gradient(160deg,{pal['PD']} 0%,{pal['P']} 55%,#4E7AC0 100%);
--F-HEAD:'Barlow Condensed',sans-serif;--F-BODY:'Plus Jakarta Sans',sans-serif;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#1a1a1a;font-family:var(--F-BODY);padding:40px 0;}}
.toolbar{{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:999;}}
.toolbar button{{background:var(--P);color:#fff;border:none;border-radius:8px;padding:12px 22px;font-weight:700;font-size:14px;cursor:pointer;}}
.stage{{display:flex;flex-direction:column;align-items:center;gap:20px;}}
.stage.preview{{flex-direction:row;flex-wrap:wrap;justify-content:center;gap:18px;max-width:1480px;margin:0 auto;}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;flex-shrink:0;}}
.stage.preview .slide{{transform:scale(.32);transform-origin:top left;margin:0 -734px -918px 0;}}
.grain{{position:absolute;inset:0;z-index:3;pointer-events:none;background-image:url("{GRAIN}");background-size:200px 200px;opacity:0.05;mix-blend-mode:overlay;}}
.slide-dark .grain,.slide-grad .grain,.slide-capa .grain{{opacity:0.07;mix-blend-mode:soft-light;}}
.accent-bar{{position:absolute;top:0;left:0;right:0;height:7px;z-index:30;background:var(--G);}}
.accent-bar.on-grad{{background:rgba(255,255,255,0.18);}}
.brand-bar{{position:absolute;top:7px;left:0;right:0;padding:32px 56px 0;display:flex;justify-content:space-between;align-items:center;z-index:20;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;font-size:14px;}}
.brand-bar.on-light{{color:rgba(15,13,12,0.45);}}
.brand-bar.on-dark{{color:rgba(255,255,255,0.55);}}
.brand-bar.on-grad{{color:rgba(255,255,255,0.6);}}
.prog{{position:absolute;bottom:0;left:0;right:0;padding:0 56px 36px;z-index:20;display:flex;align-items:center;gap:16px;}}
.prog-track{{flex:1;height:3px;border-radius:2px;overflow:hidden;}}
.prog-fill{{height:100%;border-radius:2px;}}
.prog-num{{font-size:15px;font-weight:600;}}
.on-light .prog-track{{background:rgba(0,0,0,0.08);}} .on-light .prog-fill{{background:var(--P);}} .on-light .prog-num{{color:rgba(0,0,0,0.3);}}
.on-dark .prog-track{{background:rgba(255,255,255,0.12);}} .on-dark .prog-fill{{background:#fff;}} .on-dark .prog-num{{color:rgba(255,255,255,0.3);}}
.on-grad .prog-track{{background:rgba(255,255,255,0.2);}} .on-grad .prog-fill{{background:#fff;}} .on-grad .prog-num{{color:rgba(255,255,255,0.4);}}
.tag{{font-size:14px;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:26px;}}
.on-light .tag{{color:var(--P);}} .on-dark .tag{{color:var(--PL);}} .on-grad .tag{{color:rgba(255,255,255,0.75);}}
.content{{position:absolute;top:120px;left:56px;right:56px;bottom:90px;display:flex;flex-direction:column;justify-content:flex-end;z-index:5;}}
.slide-capa{{background:#000;}}
.capa-bg{{position:absolute;inset:0;background-size:cover;background-position:center 20%;background-repeat:no-repeat;}}
.capa-grad{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(10,24,52,0.30) 0%,rgba(10,24,52,0.05) 22%,rgba(10,24,52,0.20) 42%,rgba(10,24,52,0.70) 58%,rgba(10,24,52,0.94) 78%,rgba(10,24,52,0.99) 100%);}}
.capa-type-badge2{{position:absolute;top:80px;left:56px;z-index:25;display:flex;align-items:center;gap:14px;}}
.capa-type-label{{background:var(--P);color:#fff;padding:9px 20px;font-size:13px;font-weight:800;letter-spacing:3px;text-transform:uppercase;border-radius:5px;}}
.capa-date{{font-size:15px;font-weight:500;color:rgba(255,255,255,0.6);}}
.capa-headline-area{{position:absolute;bottom:120px;left:0;right:0;padding:0 56px;z-index:10;}}
.capa-logo{{height:104px;width:auto;display:block;margin-bottom:38px;opacity:0.97;}}
.cta-logo{{height:92px;width:auto;display:block;opacity:0.9;}}
.capa-headline{{font-family:var(--F-HEAD);font-size:104px;font-weight:900;line-height:0.92;letter-spacing:-3px;text-transform:uppercase;color:#fff;}}
.capa-headline em{{color:var(--PL);font-style:normal;}}
.slide-dark{{background:var(--DB);}}
.dark-h1{{font-family:var(--F-HEAD);font-size:78px;font-weight:900;line-height:0.97;letter-spacing:-2px;text-transform:uppercase;color:#fff;margin-bottom:34px;}}
.dark-h1 em{{color:var(--PL);font-style:normal;}}
.dark-body{{font-size:37px;font-weight:400;line-height:1.5;letter-spacing:-0.2px;color:rgba(255,255,255,0.6);}}
.dark-body strong{{color:#fff;font-weight:700;}}
.slide-light{{background:var(--LB);}}
.light-h1{{font-family:var(--F-HEAD);font-size:74px;font-weight:900;line-height:1.0;letter-spacing:-1.5px;text-transform:uppercase;color:var(--DB);margin-bottom:30px;}}
.light-h1 em{{color:var(--P);font-style:normal;}}
.light-body{{font-size:37px;font-weight:400;line-height:1.55;letter-spacing:-0.2px;color:rgba(15,13,12,0.62);}}
.light-body strong{{color:var(--DB);font-weight:800;}}
.slide-grad{{background:var(--G);}}
.grad-h1{{font-family:var(--F-HEAD);font-size:88px;font-weight:900;line-height:0.95;letter-spacing:-2px;text-transform:uppercase;color:#fff;margin-bottom:36px;}}
.grad-body{{font-size:37px;font-weight:400;line-height:1.55;letter-spacing:-0.2px;color:rgba(255,255,255,0.78);}}
.grad-body strong{{color:#fff;font-weight:800;}}
.slide-img-bg{{position:absolute;inset:0;background-size:cover;background-position:center;z-index:0;}}
.slide-img-overlay{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(6,14,32,0.82) 0%,rgba(6,14,32,0.72) 30%,rgba(6,14,32,0.78) 60%,rgba(6,14,32,0.93) 100%);z-index:1;}}
.grad-img-overlay{{position:absolute;inset:0;background:linear-gradient(165deg,rgba(10,24,52,0.86) 0%,rgba(27,58,107,0.82) 50%,rgba(91,138,212,0.78) 100%);z-index:1;}}
.slide-cta{{background:var(--LB);}}
.cta-bridge{{font-size:37px;font-weight:500;line-height:1.5;letter-spacing:-0.2px;color:rgba(15,13,12,0.55);margin-bottom:44px;}}
.cta-bridge strong{{color:var(--DB);font-weight:800;}}
.cta-headline{{font-family:var(--F-HEAD);font-size:84px;font-weight:900;line-height:0.95;letter-spacing:-2px;text-transform:uppercase;color:var(--DB);margin-bottom:38px;}}
.cta-headline em{{color:var(--P);font-style:normal;}}
.cta-kbox{{background:#fff;border:3px solid rgba(27,58,107,0.15);border-radius:20px;padding:40px 48px;margin-bottom:30px;box-shadow:0 8px 30px rgba(10,24,52,0.06);}}
.cta-kinstr{{font-size:21px;font-weight:500;color:rgba(15,13,12,0.45);margin-bottom:12px;}}
.cta-kword{{font-family:var(--F-HEAD);font-size:88px;font-weight:900;color:var(--P);letter-spacing:-2px;line-height:1;margin-bottom:14px;}}
.cta-kbenefit{{font-size:22px;font-weight:500;line-height:1.5;color:rgba(15,13,12,0.5);}}
.cta-footer{{display:flex;align-items:center;gap:16px;}}
</style></head>
<body>
<div class="toolbar"><button onclick="document.querySelector('.stage').classList.toggle('preview')">Preview / Tamanho Real</button></div>
<div class="stage">
{slides_html}
</div></body></html>"""

    with open(out, "w") as fh:
        fh.write(html)
    print("OK", out, len(html), "bytes,", total, "slides")

if __name__ == "__main__":
    main()
