# julia here. Pen Library

Public, filterable library of Julia's fountain pens, served at https://pens.juliahere.com via GitHub Pages.
Companion to the Ink Library (https://ink.juliahere.com, repo Jwilde624/ink-library).

- `index.html` – the page; pen data lives in the `<script id="pen-data">` block.
- `photos/b-*.json` – pen photo bundles keyed by Notion page id; `manifest.json` maps each pen page to its Notion image.
- `tools/` – scripts used by the weekly refresh (`build_pens.py`, `pencrop.py`, `dl.py`, `mkbatch.py`).

Only pens marked Active or For Sale in Notion are published. Cost, purchase date and store are never published.
