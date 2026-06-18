# LLD Teaching Decks

Four interactive slide decks for teaching **Low-Level Design** — built with [Slidev](https://sli.dev). Every concept is a live, clickable demo (animated diagrams, steppable state machines, runnable-looking flows) in a dark "blueprint" theme, with Python examples throughout.

## What's inside

| Deck | Run with | Covers |
| --- | --- | --- |
| **1 - Foundations** | `pnpm dev` | LLD intro, OOP fundamentals, class relationships |
| **2 - Principles & UML** | `pnpm dev2` | Design principles, SOLID, UML diagrams |
| **3 - Design Patterns** | `pnpm dev3` | All 30 patterns: Creational, Structural, Behavioral, Additional |
| **4 - Cracking the LLD Interview** | `pnpm dev4` | The interview method, then worked case studies: games, data structures & search |

Each pattern/concept/case study gets a code slide plus a full-width interactive component you can click through. Practice prompts live alongside the decks in [`deck1_exercises.md`](deck1_exercises.md) and [`deck2_exercises.md`](deck2_exercises.md).

## Prerequisites

- [Node.js](https://nodejs.org) 20.12+ (required by Slidev 52)
- [pnpm](https://pnpm.io) — enable the bundled one with `corepack enable pnpm`, or install via `npm install -g pnpm`

## Getting started

```bash
pnpm install     # installs Slidev + Vue (versions pinned by pnpm-lock.yaml)

pnpm dev         # Deck 1 - Foundations
pnpm dev2        # Deck 2 - Principles & UML
pnpm dev3        # Deck 3 - Design Patterns
pnpm dev4        # Deck 4 - Cracking the LLD Interview
```

Each command opens the deck at **http://localhost:3030**.

> [!TIP]
> Run one deck at a time. To run two at once, start the second on another port: `pnpm exec slidev deck2.md --port 3031`.

## Navigating the slides

| Key / action | Does |
| --- | --- |
| `Space` or `->` | Next step / slide |
| `<-` / `Up` | Back |
| `o` | Slide overview (jump anywhere) |
| `f` | Fullscreen |
| click the buttons / toggles | Drive the live demos (step, play, swap, reset) |

Most pattern slides come in pairs: an **anatomy** slide (code + roles + key points) followed by a **live** slide where the interactive component sits — play with the controls there.

## Building & exporting (optional)

```bash
pnpm build3                       # static SPA for Deck 3 -> dist/deck3
pnpm add -D playwright-chromium   # one-time, needed only for PDF export
pnpm export3                      # PDF of Deck 3
```

(`build`/`export`, `build2`/`export2`, and `build4`/`export4` do the same for Decks 1, 2, and 4.)

## Tech stack

- **[Slidev](https://sli.dev)** — Markdown-driven slides on Vite + Vue
- **[Vue 3](https://vuejs.org)** — the interactive components in [`components/`](components/)
- **[Mermaid](https://mermaid.js.org)** — diagrams
- Custom blueprint theme in [`styles/`](styles/) + [`setup/`](setup/)

> [!NOTE]
> The teaching content is derived from the [AlgoMaster Low-Level Design course](https://algomaster.io/learn/lld). Explanations, code, and interactive components here are reworked/original; full credit for the underlying curriculum goes to AlgoMaster.
