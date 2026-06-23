#!/usr/bin/env python3
"""Baixa imagens da internet por tema (licença livre p/ uso comercial).
Uso: python3 pipeline/fetch_images.py "termo de busca" [N=3] [prefixo=net]
Salva em assets/_net/ e imprime os nomes salvos (1 por linha) p/ usar no content.json.

Fonte principal: Openverse (Creative Commons, sem chave).
Opcional: se a env PEXELS_API_KEY existir, usa Pexels (qualidade melhor).
"""
import json, os, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "_net")
UA = "Mozilla/5.0 (MaquinaCarrosseis/1.0)"


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def pexels(query, n, key):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": n, "orientation": "portrait"})
    data = json.loads(get(url, {"Authorization": key}))
    return [(p["src"]["large2x"], "jpg") for p in data.get("photos", [])][:n]


def openverse(query, n):
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
        "q": query, "license_type": "commercial", "license": "cc0,pdm",
        "size": "large", "page_size": max(n * 2, 6), "mature": "false"})
    data = json.loads(get(url))
    out = []
    for it in data.get("results", []):
        u = it.get("url")
        if not u:
            continue
        ext = "png" if u.lower().split("?")[0].endswith("png") else "jpg"
        out.append((u, ext))
    return out


def main():
    query = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    prefix = sys.argv[3] if len(sys.argv) > 3 else "net"
    os.makedirs(OUT, exist_ok=True)

    key = os.environ.get("PEXELS_API_KEY")
    candidates = []
    try:
        candidates = pexels(query, n, key) if key else openverse(query, n)
    except Exception as e:
        sys.stderr.write(f"fonte primaria falhou: {e}\n")
    if not candidates:
        try:
            candidates = openverse(query, n)
        except Exception as e:
            sys.stderr.write(f"openverse falhou: {e}\n")

    saved = []
    for i, (u, ext) in enumerate(candidates, 1):
        if len(saved) >= n:
            break
        name = f"{prefix}-{i}.{ext}"
        try:
            blob = get(u)
            if len(blob) < 5000:   # provavelmente erro/placeholder
                continue
            with open(os.path.join(OUT, name), "wb") as fh:
                fh.write(blob)
            saved.append(name)
        except Exception as e:
            sys.stderr.write(f"falha baixando {u}: {e}\n")

    for s in saved:
        print(s)
    if not saved:
        sys.stderr.write("NENHUMA imagem baixada — use o banco fixo de assets/fotos/\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
