#!/usr/bin/env python3
"""Baixa imagens da internet por tema (licença livre p/ uso comercial).
Uso: python3 pipeline/fetch_images.py "termo de busca" [N=3] [prefixo=net]
Salva em assets/_net/ e imprime os nomes salvos (1 por linha) p/ usar no content.json.

Fonte principal: Openverse (Creative Commons, sem chave).
Opcional: se a env PEXELS_API_KEY existir, usa Pexels (qualidade melhor).

Variedade: cada busca pega uma PÁGINA aleatória e embaralha os resultados, então
o mesmo tema rende fotos diferentes a cada dia (não repete fundo).

Também exporta `fetch(query, n, prefix)` p/ o build.py chamar direto.
"""
import json, os, random, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "_net")
UA = "Mozilla/5.0 (MaquinaCarrosseis/1.0)"


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def pexels(query, n, key):
    # página aleatória p/ variar o resultado dia a dia
    page = random.randint(1, 8)
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": max(n * 3, 9), "page": page, "orientation": "portrait"})
    data = json.loads(get(url, {"Authorization": key}))
    out = [(p["src"]["large2x"], "jpg") for p in data.get("photos", [])]
    random.shuffle(out)
    return out


def openverse(query, n):
    # página aleatória + page_size folgado p/ ter de onde embaralhar
    page = random.randint(1, 6)
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
        "q": query, "license_type": "commercial", "license": "cc0,pdm",
        "size": "large", "page_size": max(n * 4, 12), "page": page, "mature": "false"})
    data = json.loads(get(url))
    out = []
    seen = set()
    for it in data.get("results", []):
        u = it.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        ext = "png" if u.lower().split("?")[0].endswith("png") else "jpg"
        out.append((u, ext))
    random.shuffle(out)
    return out


def fetch(query, n=3, prefix="net"):
    """Baixa até n imagens do tema. Retorna lista de nomes salvos em assets/_net/.
    Lista vazia = falhou (sem rede / sem resultado)."""
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
    # query longa rende poucos resultados no Openverse — tenta versões mais curtas
    if not candidates:
        words = query.split()
        for short in ([" ".join(words[:2])] if len(words) > 2 else []) + ([words[0]] if len(words) > 1 else []):
            try:
                candidates = openverse(short, n)
                if candidates:
                    sys.stderr.write(f"query reduzida p/ '{short}'\n")
                    break
            except Exception as e:
                sys.stderr.write(f"openverse '{short}' falhou: {e}\n")

    saved = []
    idx = 0
    for u, ext in candidates:
        if len(saved) >= n:
            break
        idx += 1
        name = f"{prefix}-{idx}.{ext}"
        try:
            blob = get(u)
            if len(blob) < 5000:   # provavelmente erro/placeholder
                idx -= 1
                continue
            with open(os.path.join(OUT, name), "wb") as fh:
                fh.write(blob)
            saved.append(name)
        except Exception as e:
            idx -= 1
            sys.stderr.write(f"falha baixando {u}: {e}\n")
    return saved


def main():
    query = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    prefix = sys.argv[3] if len(sys.argv) > 3 else "net"
    saved = fetch(query, n, prefix)
    for s in saved:
        print(s)
    if not saved:
        sys.stderr.write("NENHUMA imagem baixada — use o banco fixo de assets/fotos/\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
