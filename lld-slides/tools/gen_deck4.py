#!/usr/bin/env python3
"""Generate deck4.md ("Cracking the LLD Interview") from slide specs, blueprint style.

Specs come from tools/deck4_specs.json (produced by the deck4 build workflow).
Each topic renders as an anatomy/design slide (code + ROLES/FRAMEWORK + key points); slugs
in INTERACTIVE additionally get a full-width live Vue component slide. Components are wired
incrementally — anything not yet in INTERACTIVE just shows its static anatomy slide.
"""
import json, html, re
from pathlib import Path

HERE = Path(__file__).resolve().parent   # lld-slides/tools
ROOT = HERE.parent                       # lld-slides

SPECS = json.load(open(HERE / 'deck4_specs.json'))
d = {s['slug']: s for s in SPECS}

METHOD = ['ood-approach', 'machine-coding-approach', 'identifying-entities',
          'writing-clean-code', 'choosing-design-patterns', 'handling-concurrency']
GAMES = ['tic-tac-toe', 'snake-and-ladder', 'minesweeper', 'chess']
DSSEARCH = ['lru-cache', 'bloom-filter', 'search-autocomplete', 'search-engine']

# slugs whose slide gets a bespoke interactive component (in addition to the anatomy slide).
# Populated as components are built + verified; everything else falls back to the static slide.
INTERACTIVE = {
    'ood-approach': 'OodInterviewCockpit',
    'machine-coding-approach': 'MachineCodingClock',
    'identifying-entities': 'EntityModelingLab',
    'writing-clean-code': 'RefactorLab',
    'choosing-design-patterns': 'PatternDiagnosisBench',
    'handling-concurrency': 'SeatBookingRaceSim',
    'tic-tac-toe': 'TicTacToeEngine',
    'snake-and-ladder': 'SnakeLadderBoard',
    'minesweeper': 'MinesweeperBoard',
    'chess': 'ChessBoardPlayground',
    'lru-cache': 'LruCacheBoard',
    'bloom-filter': 'BloomFilterLab',
    'search-autocomplete': 'TrieTypeaheadExplorer',
    'search-engine': 'InvertedIndexSearchBoard',
}


def esc(s):
    # HTML-escape text that lands inside HTML (key points/roles can contain <, >, &, e.g. Map<id, val>)
    return html.escape(str(s), quote=False)


def kpts(slug, cls="bp-dim text-sm"):
    items = ''.join(f"<li>{esc(k)}</li>" for k in d[slug]['keyPoints'])
    return f'<ul class="kpts {cls}">{items}</ul>'


def roles(slug):
    items = []
    for p in d[slug].get('participants', []):
        if ' (' in p and p.endswith(')'):
            name, desc = p.split(' (', 1)
            items.append(f'<li><b>{esc(name)}</b> <span class="bp-dim">{esc(desc[:-1])}</span></li>')
        else:
            items.append(f'<li><b>{esc(p)}</b></li>')
    return '<ul class="roles">' + ''.join(items) + '</ul>'


def notes(slug):
    x = d[slug]
    rw = ' · '.join(x.get('realWorld', []))
    parts = ['Key points: ' + ' | '.join(x['keyPoints']), f"Problem: {x.get('problem', '')}"]
    if rw:
        parts.append(f"Real-world: {rw}")
    if x.get('gotcha'):
        parts.append(f"Gotcha: {x['gotcha']}")
    body = '\n\n'.join(parts).replace('--', '––')  # keep HTML comment valid
    return f"\n<!--\n{body}\n-->\n"


def anatomy_slide(slug):
    x = d[slug]
    label = 'FRAMEWORK' if x.get('kind') == 'method' else 'ROLES'
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{esc(x['oneLiner'])}</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
{x['python'].strip()}
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">{label}</div>
{roles(slug)}

<div class="bp-eyebrow mb-2">KEY POINTS</div>
{kpts(slug)}

</div>
</div>
{notes(slug)}"""


def live_slide(slug):
    x = d[slug]
    comp = INTERACTIVE[slug]
    idea = x['interactive']['idea']
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{esc(idea)}</div>

<{comp} />
"""


def emit(slug):
    if slug in INTERACTIVE:
        return anatomy_slide(slug) + '\n' + live_slide(slug)
    return anatomy_slide(slug)


def section(num, title, chips):
    chiphtml = ''.join(f'<span class="bp-chip">{esc(c)}</span>' for c in chips)
    return f"""---
layout: default
class: section-slide
---

<div class="ghost-num">{num}</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE {num}</div>
  <h1>{title}</h1>
  <div class="flex gap-3 mt-6">{chiphtml}</div>
</div>
"""


# ---- scaffolding ----
HEAD = """---
theme: default
colorSchema: dark
title: Cracking the LLD Interview
info: |
  LLD for friends — Deck 4: Cracking the LLD Interview
  The Method · Games & Puzzles · Data Structures & Search
fonts:
  sans: Inter
  mono: Fira Code
  weights: '300,400,500,600,700'
lineNumbers: false
transition: slide-left
mdc: true
drawings:
  enabled: true
---

<div class="bp-eyebrow mb-4" v-motion :initial="{ x: -40, opacity: 0 }" :enter="{ x: 0, opacity: 1, transition: { delay: 80 } }">LOW-LEVEL DESIGN · DECK 4</div>

<div v-motion :initial="{ y: 36, opacity: 0 }" :enter="{ y: 0, opacity: 1, transition: { delay: 180 } }">

# Cracking the LLD Interview

</div>

<div class="text-2xl bp-dim mt-2 mb-8 bp-mono" v-motion :initial="{ y: 24, opacity: 0 }" :enter="{ y: 0, opacity: 1, transition: { delay: 320 } }">First the method, then the machine — drive any LLD round, then watch it on real problems.</div>

<div class="flex gap-3" v-motion :initial="{ opacity: 0 }" :enter="{ opacity: 1, transition: { delay: 480 } }">
  <span class="bp-chip">01 · The Method</span>
  <span class="bp-chip">02 · Games & Puzzles</span>
  <span class="bp-chip">03 · Data Structures & Search</span>
</div>

<div class="abs-br m-6 bp-dim text-sm">
  press <span class="bp-key">space</span> to advance · <span class="bp-key">o</span> for overview
</div>
"""

INTRO = """---
layout: default
---

## How this deck works

<div class="bp-dim bp-mono text-sm mb-5">Decks 1-3 gave you the vocabulary. This one turns it into interview performance: a repeatable method, then eight problems worked end-to-end.</div>

<div class="grid grid-cols-3 gap-3">
<div class="bp-card bp-card--cyan" v-click="1">
  <div class="text-3xl bp-mono bp-glow-text">6</div>
  <div class="text-xl mt-1">The Method</div>
  <div class="bp-dim text-sm mt-2">How to drive an OOD or machine-coding round — clarify, model, place patterns, handle concurrency.</div>
</div>
<div class="bp-card bp-card--blue" v-click="2">
  <div class="text-3xl bp-mono">8</div>
  <div class="text-xl mt-1">Worked case studies</div>
  <div class="bp-dim text-sm mt-2">Each problem as a design/anatomy slide <b>and</b> a full-width live demo you can drive.</div>
</div>
<div class="bp-card bp-card--violet" v-click="3">
  <div class="text-3xl bp-mono">3</div>
  <div class="text-xl mt-1">Patterns in the wild</div>
  <div class="bp-dim text-sm mt-2">Strategy, State, Observer keep recurring — Deck 3 cashed out in real designs.</div>
</div>
</div>

<div v-click="4" class="mt-8 grid grid-cols-3 gap-6 bp-dim text-sm">
  <div><span class="bp-mono" style="color:var(--bp-cyan)">Method first.</span> A defensible class diagram beats a clever one you can't explain.</div>
  <div><span class="bp-mono" style="color:var(--bp-cyan)">Then apply it.</span> Games, then data-structure designs, each in idiomatic Python.</div>
  <div><span class="bp-mono" style="color:var(--bp-cyan)">Drive the demo.</span> Every case study ships a clickable, living component.</div>
</div>
"""

AGENDA = """---
layout: default
---

## The path

<div class="grid grid-cols-3 gap-3 mt-6">
<div class="bp-card bp-card--cyan" v-click="1">
  <div class="text-3xl bp-mono bp-glow-text">01</div>
  <div class="text-xl mt-1">The Method</div>
  <div class="bp-dim text-sm mt-2">OOD approach · Machine coding · Identifying entities · Clean code · Choosing patterns · Concurrency</div>
</div>
<div class="bp-card bp-card--blue" v-click="2">
  <div class="text-3xl bp-mono">02</div>
  <div class="text-xl mt-1">Games & Puzzles</div>
  <div class="bp-dim text-sm mt-2">Tic Tac Toe · Snake & Ladder · Minesweeper · Chess</div>
</div>
<div class="bp-card bp-card--violet" v-click="3">
  <div class="text-3xl bp-mono">03</div>
  <div class="text-xl mt-1">Data Structures & Search</div>
  <div class="bp-dim text-sm mt-2">LRU Cache · Bloom Filter · Autocomplete · Search Engine</div>
</div>
</div>

<div v-click="4" class="mt-10 text-center bp-dim bp-mono text-sm">
  1 method &middot; 8 worked designs &middot; patterns you'll reach for in every round &rarr;
</div>
"""

RECAP = """---
layout: default
---

<div class="bp-eyebrow mb-2">DECK 4 · RECAP</div>

## Your interview toolkit

<div class="grid grid-cols-3 gap-3 mt-6">
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">01</span> The Method</div>
    <ul class="recap-list">
      <li>Clarify scope before classes</li>
      <li>Nouns&rarr;classes, verbs&rarr;methods</li>
      <li>Patterns solve pains; guard the critical section</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">02</span> Games & Puzzles</div>
    <ul class="recap-list">
      <li>Tic Tac Toe &middot; Snake & Ladder</li>
      <li>Minesweeper &middot; Chess</li>
      <li>State machines + polymorphic rules</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">03</span> Data Structures & Search</div>
    <ul class="recap-list">
      <li>LRU Cache &middot; Bloom Filter</li>
      <li>Autocomplete &middot; Search Engine</li>
      <li>The right structure beats fancy patterns</li>
    </ul>
  </div>
</div>

<div v-click class="mt-10 text-center bp-mono bp-dim">Next &rarr; <span style="color:var(--bp-cyan)">Stateful systems &amp; management designs</span></div>

<style>
.recap-card .recap-head { font-size: 1.25rem; color: #fff; margin-bottom: .8rem; }
.recap-card .recap-head .bp-mono { color: var(--bp-cyan); margin-right: .4rem; }
.recap-list { list-style: none; padding: 0; margin: 0; }
.recap-list li { position: relative; padding-left: 1.5rem; margin: .5rem 0; color: var(--bp-dim); font-size: .9rem; }
.recap-list li::before { content: ''; position: absolute; left: .2rem; top: .3em; width: 6px; height: 11px; border: solid var(--bp-good); border-width: 0 2px 2px 0; transform: rotate(45deg); }
</style>
"""

END = """---
layout: end
---

<div class="text-center">
  <div class="bp-eyebrow mb-3">END OF DECK 4</div>
  <h1>Questions?</h1>
  <div class="bp-dim bp-mono mt-3">Foundations &rarr; Principles &rarr; Patterns &rarr; Interviews</div>
</div>
"""

parts = [HEAD, INTRO, AGENDA]
parts.append(section('01', 'The Interview Method', ['how to drive the room']))
for s in METHOD:
    parts.append(emit(s))
parts.append(section('02', 'Games & Puzzles', ['state, rules, turns']))
for s in GAMES:
    parts.append(emit(s))
parts.append(section('03', 'Data Structures & Search', ['the right structure wins']))
for s in DSSEARCH:
    parts.append(emit(s))
parts.append(RECAP)
parts.append(END)

doc = '\n'.join(parts)
open(ROOT / 'deck4.md', 'w').write(doc)
allslugs = METHOD + GAMES + DSSEARCH
n_inter = sum(1 for s in allslugs if s in INTERACTIVE)
print(f"wrote deck4.md | slides ~{doc.count(chr(10) + '---' + chr(10)) + 1} | interactive {n_inter}/{len(allslugs)}")
