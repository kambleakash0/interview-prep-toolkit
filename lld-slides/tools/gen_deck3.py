#!/usr/bin/env python3
"""Generate deck3.md (Design Patterns) from refined slide specs, blueprint style.

Specs come from tools/deck3_specs.json (produced by the deck3 extraction workflow).
Every pattern renders as a rich static slide (code + diagram + key points) unless its
slug is in INTERACTIVE, in which case a bespoke living Vue component is used instead.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent   # lld-slides/tools
ROOT = HERE.parent                       # lld-slides

SPECS = json.load(open(HERE / 'deck3_specs.json'))
SPECS += json.load(open(HERE / 'deck3_additional_specs.json'))
d = {s['slug']: s for s in SPECS}

CREATIONAL = ['singleton', 'builder', 'factory-method', 'abstract-factory', 'prototype']
STRUCTURAL = ['adapter', 'facade', 'decorator', 'composite', 'proxy', 'bridge', 'flyweight']
BEHAVIORAL = ['strategy', 'iterator', 'observer', 'command', 'state',
              'template-method', 'chain-of-responsibility', 'visitor', 'mediator', 'memento']
ADDITIONAL = ['null-object', 'repository', 'mvc', 'dependency-injection',
              'specification', 'game-loop', 'thread-pool', 'producer-consumer']

# slugs whose slide is a bespoke interactive/animated component instead of code+diagram.
# Populated incrementally as components are built; everything else falls back to a static slide.
INTERACTIVE = {
    'singleton': 'SingletonInstancePool',
    'builder': 'FluentBuilderChain',
    'factory-method': 'FactoryMethodDialogForge',
    'abstract-factory': 'FamilySwitchBench',
    'prototype': 'PrototypeCloneForge',
    'adapter': 'AdapterPlugTranslator',
    'facade': 'FacadeOrchestrationStage',
    'decorator': 'DecoratorOnionStack',
    'composite': 'CompositeTreeAggregator',
    'proxy': 'ProxyGatekeeperPlayground',
    'bridge': 'BridgeMatrixWirer',
    'flyweight': 'FlyweightGlyphPool',
    'strategy': 'StrategySwapBench',
    'iterator': 'IteratorCursorWalk',
    'observer': 'ObserverBroadcastBoard',
    'command': 'CommandUndoStackPlayground',
    'state': 'StatePlayerMachine',
    'template-method': 'TemplateMethodPipeline',
    'chain-of-responsibility': 'ApprovalChainTracer',
    'visitor': 'VisitorDoubleDispatchTracer',
    'mediator': 'MediatorStarTopology',
    'memento': 'MementoUndoStack',
    'null-object': 'NullObjectCallTracer',
    'repository': 'RepositorySwapStore',
    'mvc': 'MvcRoundTrip',
    'dependency-injection': 'DependencyInjector',
    'specification': 'SpecificationComposer',
    'game-loop': 'GameLoopTicker',
    'thread-pool': 'ThreadPoolDispatcher',
    'producer-consumer': 'ProducerConsumerBuffer',
}

# ---- diagram curation (mirrors gen_deck2) ----
EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿️←-⇿⬀-⯿]')
KNOWN_MERMAID = ('classDiagram', 'sequenceDiagram', 'stateDiagram', 'flowchart',
                 'graph', 'erDiagram', 'journey', 'mindmap', 'gantt', 'pie')
SCALE = {'classDiagram': 0.6, 'sequenceDiagram': 0.78, 'stateDiagram-v2': 0.74,
         'stateDiagram': 0.74, 'flowchart': 0.74, 'graph': 0.74}


def clean_mermaid(s):
    out = []
    for ln in s.split('\n'):
        st = ln.strip()
        if st.startswith('style ') or st.startswith('classDef ') or ':::' in ln:
            continue
        out.append(EMOJI.sub('', ln).rstrip())
    return '\n'.join([l for l in out if l.strip()]).strip()


def diagram_for(slug, scale=None):
    x = d[slug]
    raw = clean_mermaid(x['diagram'])
    first = raw.split('\n', 1)[0].strip()
    if not any(first.startswith(k) for k in KNOWN_MERMAID):
        raw = (x.get('diagramType', '').strip() or 'classDiagram') + '\n' + raw
    sc = scale or SCALE.get(x.get('diagramType', '').strip(), 0.7)
    return f"```mermaid {{scale: {sc}}}\n{raw}\n```"


def kpts(slug, cls="bp-dim text-xs"):
    items = ''.join(f"<li>{k}</li>" for k in d[slug]['keyPoints'])
    return f'<ul class="kpts {cls}">{items}</ul>'


def notes(slug):
    x = d[slug]
    rw = ' · '.join(x.get('realWorld', []))
    parts = ['Key points: ' + ' | '.join(x['keyPoints']), f"Problem: {x['problem']}"]
    if rw:
        parts.append(f"Real-world: {rw}")
    if x.get('gotcha'):
        parts.append(f"Gotcha: {x['gotcha']}")
    body = '\n\n'.join(parts)
    return f"\n<!--\n{body}\n-->\n"


def roles(slug):
    items = []
    for p in d[slug].get('participants', []):
        if ' (' in p and p.endswith(')'):
            name, desc = p.split(' (', 1)
            items.append(f'<li><b>{name}</b> <span class="bp-dim">{desc[:-1]}</span></li>')
        else:
            items.append(f'<li><b>{p}</b></li>')
    return '<ul class="roles">' + ''.join(items) + '</ul>'

def pattern_slide(slug):
    x = d[slug]
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{x['oneLiner']}</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
{x['python'].strip()}
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
{roles(slug)}

<div class="bp-eyebrow mb-2">KEY POINTS</div>
{kpts(slug, "bp-dim text-sm")}

</div>
</div>
{notes(slug)}"""


def interactive_slide(slug):
    x = d[slug]
    comp = INTERACTIVE[slug]
    idea = x['interactive']['idea']
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{idea}</div>

<{comp} />
"""


def emit(slug):
    # interactive patterns get TWO slides: the code/anatomy slide, then the live component.
    if slug in INTERACTIVE:
        return pattern_slide(slug) + '\n' + interactive_slide(slug)
    return pattern_slide(slug)


def section(num, title, chips):
    chiphtml = ''.join(f'<span class="bp-chip">{c}</span>' for c in chips)
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


# ---- assemble ----
HEAD = """---
theme: default
colorSchema: dark
title: Design Patterns
info: |
  LLD for friends — Deck 3: Design Patterns
  Creational · Structural · Behavioral · Additional
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

<div class="bp-eyebrow mb-4" v-motion :initial="{ x: -40, opacity: 0 }" :enter="{ x: 0, opacity: 1, transition: { delay: 80 } }">LOW-LEVEL DESIGN · DECK 3</div>

<div v-motion :initial="{ y: 36, opacity: 0 }" :enter="{ y: 0, opacity: 1, transition: { delay: 180 } }">

# Design Patterns

</div>

<div class="text-2xl bp-dim mt-2 mb-8 bp-mono" v-motion :initial="{ y: 24, opacity: 0 }" :enter="{ y: 0, opacity: 1, transition: { delay: 320 } }">Named, reusable solutions to the problems that keep coming back.</div>

<div class="flex gap-3" v-motion :initial="{ opacity: 0 }" :enter="{ opacity: 1, transition: { delay: 480 } }">
  <span class="bp-chip">01 · Creational</span>
  <span class="bp-chip">02 · Structural</span>
  <span class="bp-chip">03 · Behavioral</span>
  <span class="bp-chip">04 · Additional</span>
</div>

<div class="abs-br m-6 bp-dim text-sm">
  press <span class="bp-key">space</span> to advance · <span class="bp-key">o</span> for overview
</div>
"""

INTRO = """---
layout: default
---

## What are design patterns?

<div class="bp-dim bp-mono text-sm mb-5">Battle-tested templates for how objects are made, composed, and made to collaborate — not code you copy, but shapes you reach for.</div>

<div class="grid grid-cols-4 gap-3">
<div class="bp-card bp-card--cyan" v-click="1">
  <div class="text-3xl bp-mono bp-glow-text">5</div>
  <div class="text-xl mt-1">Creational</div>
  <div class="bp-dim text-sm mt-2">How objects get <b>made</b> — decouple code from concrete construction.</div>
</div>
<div class="bp-card bp-card--blue" v-click="2">
  <div class="text-3xl bp-mono">7</div>
  <div class="text-xl mt-1">Structural</div>
  <div class="bp-dim text-sm mt-2">How objects <b>compose</b> — assemble bigger structures without rigid coupling.</div>
</div>
<div class="bp-card bp-card--violet" v-click="3">
  <div class="text-3xl bp-mono">10</div>
  <div class="text-xl mt-1">Behavioral</div>
  <div class="bp-dim text-sm mt-2">How objects <b>interact</b> — assign responsibility and flow control cleanly.</div>
</div>
<div class="bp-card bp-card--green" v-click="4">
  <div class="text-3xl bp-mono">8</div>
  <div class="text-xl mt-1">Additional</div>
  <div class="bp-dim text-sm mt-2">Beyond the GoF — patterns you meet wiring real systems.</div>
</div>
</div>

<div v-click="5" class="mt-8 grid grid-cols-3 gap-6 bp-dim text-sm">
  <div><span class="bp-mono" style="color:var(--bp-cyan)">A shared vocabulary.</span> Say "use a Strategy" and the team pictures the same shape.</div>
  <div><span class="bp-mono" style="color:var(--bp-cyan)">A design, not a library.</span> Each pattern is a set of roles and how they relate.</div>
  <div><span class="bp-mono" style="color:var(--bp-cyan)">30 in idiomatic Python.</span> Each with a runnable example and a live demo.</div>
</div>
"""

AGENDA = """---
layout: default
---

## The path

<div class="grid grid-cols-4 gap-3 mt-6">
<div class="bp-card bp-card--cyan" v-click="1">
  <div class="text-3xl bp-mono bp-glow-text">01</div>
  <div class="text-xl mt-1">Creational</div>
  <div class="bp-dim text-sm mt-2">Singleton · Builder · Factory Method · Abstract Factory · Prototype</div>
</div>
<div class="bp-card bp-card--blue" v-click="2">
  <div class="text-3xl bp-mono">02</div>
  <div class="text-xl mt-1">Structural</div>
  <div class="bp-dim text-sm mt-2">Adapter · Facade · Decorator · Composite · Proxy · Bridge · Flyweight</div>
</div>
<div class="bp-card bp-card--violet" v-click="3">
  <div class="text-3xl bp-mono">03</div>
  <div class="text-xl mt-1">Behavioral</div>
  <div class="bp-dim text-sm mt-2">Strategy · Iterator · Observer · Command · State · Template · CoR · Visitor · Mediator · Memento</div>
</div>
<div class="bp-card bp-card--green" v-click="4">
  <div class="text-3xl bp-mono">04</div>
  <div class="text-xl mt-1">Additional</div>
  <div class="bp-dim text-sm mt-2">Null Object · Repository · MVC · DI · Specification · Game Loop · Thread Pool · Producer-Consumer</div>
</div>
</div>

<div v-click="5" class="mt-10 text-center bp-dim bp-mono text-sm">
  4 modules · 30 patterns you'll reach for in every design &rarr;
</div>
"""

RECAP = """---
layout: default
---

<div class="bp-eyebrow mb-2">DECK 3 · RECAP</div>

## Your pattern toolkit

<div class="grid grid-cols-4 gap-3 mt-6">
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">01</span> Creational</div>
    <ul class="recap-list">
      <li>Singleton · Builder</li>
      <li>Factory Method</li>
      <li>Abstract Factory · Prototype</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">02</span> Structural</div>
    <ul class="recap-list">
      <li>Adapter · Facade</li>
      <li>Decorator · Composite</li>
      <li>Proxy · Bridge · Flyweight</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">03</span> Behavioral</div>
    <ul class="recap-list">
      <li>Strategy · Iterator · Observer</li>
      <li>Command · State · Template · CoR</li>
      <li>Visitor · Mediator · Memento</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">04</span> Additional</div>
    <ul class="recap-list">
      <li>Null Object · Repository</li>
      <li>MVC · DI · Specification</li>
      <li>Game Loop · Thread Pool · Producer-Consumer</li>
    </ul>
  </div>
</div>

<div v-click class="mt-10 text-center bp-mono bp-dim">Next &rarr; <span style="color:var(--bp-cyan)">Interview case studies</span></div>

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
  <div class="bp-eyebrow mb-3">END OF DECK 3</div>
  <h1>Questions?</h1>
  <div class="bp-dim bp-mono mt-3">Foundations &rarr; Principles &rarr; Patterns &rarr; Interviews</div>
</div>
"""

parts = [HEAD, INTRO, AGENDA]
parts.append(section('01', 'Creational Patterns', ['how objects are made']))
for s in CREATIONAL:
    parts.append(emit(s))
parts.append(section('02', 'Structural Patterns', ['how objects compose']))
for s in STRUCTURAL:
    parts.append(emit(s))
parts.append(section('03', 'Behavioral Patterns', ['how objects interact']))
for s in BEHAVIORAL:
    parts.append(emit(s))
parts.append(section('04', 'Additional Patterns', ['beyond the GoF 23']))
for s in ADDITIONAL:
    parts.append(emit(s))
parts.append(RECAP)
parts.append(END)

doc = '\n'.join(parts)
open(ROOT / 'deck3.md', 'w').write(doc)
allslugs = CREATIONAL + STRUCTURAL + BEHAVIORAL + ADDITIONAL
n_inter = sum(1 for s in allslugs if s in INTERACTIVE)
print(f"wrote deck3.md | slides ~{doc.count(chr(10) + '---' + chr(10)) + 1} | interactive {n_inter}/{len(allslugs)}")
