# interview-prep-toolkit

Materials for technical-interview prep. Each topic lives in its own folder.

## Contents

| Folder | What it is | Start here |
| --- | --- | --- |
| [`lld-slides/`](lld-slides/) | Interactive **Low-Level Design** teaching decks, built with Slidev | [`lld-slides/README.md`](lld-slides/README.md) |

More topics will be added over time.

## Quickstart — LLD slides

Requires [Node.js](https://nodejs.org) **20.12+** and [pnpm](https://pnpm.io) (enable the bundled one with `corepack enable pnpm`).

```bash
cd lld-slides
pnpm install
pnpm dev      # Deck 1 (Foundations) — also: pnpm dev2, dev3, dev4
```

Each deck opens at http://localhost:3030. Full instructions, the deck list, and keyboard shortcuts are in [`lld-slides/README.md`](lld-slides/README.md).
