# Máquina de Carrosséis — Consultoria Metamorfose

Pipeline automático de carrosséis virais pra Instagram (metodologia BrandsDecoded v4), rodado por uma rotina cloud do Claude Code todo dia às 7h (America/Recife).

## Estrutura
- `prompts/` — system prompt + 6 arquivos da metodologia BrandsDecoded
- `assets/fotos/` — **banco fixo de fotos da marca** (jogue mais fotos aqui)
- `assets/fonts/` — Barlow Condensed + Plus Jakarta Sans (.woff2)
- `assets/logo_white.png` / `logo_navy.png` — logo Metamorfose
- `pipeline/build.py` — gera `carousel.html` a partir de `content.json`
- `pipeline/export.js` — exporta cada slide em PNG 1080×1350 (Playwright)
- `content.json` — molde/exemplo do dia
- `RUNNER.md` — a tarefa diária que a rotina executa
- `output/YYYY-MM-DD/` — entregas diárias

## Rodar manual
```bash
python3 pipeline/build.py content.json carousel.html
npm i playwright sharp && npx playwright install chromium
node pipeline/export.js carousel.html slides
```

## Adicionar fotos ao banco
Coloque `.jpg`/`.png` em `assets/fotos/` e commite. O agente passa a escolher entre elas.
