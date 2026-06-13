#!/usr/bin/env python3
"""Generate deck2.md (Principles & UML) from extracted content, blueprint style."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # lld-slides

# NOTE: this input is an ephemeral extraction artifact from the original build and is
# NOT present in this repo. Regenerate/port it before re-running gen_deck2 (deck2.md is
# otherwise hand-maintained). Output path below is repo-relative.
d = json.load(open('/tmp/deck2_content.json'))

# The 3 lessons that are paywalled on the source course are authored here from
# first principles (these are standard, well-known design principles — original
# explanations and examples, not the source course's text).
AUTHORED = {
    'soc': {
        'slug': 'soc', 'type': 'principle', 'title': 'Separation of Concerns',
        'oneLiner': 'Split a system into distinct parts, each responsible for exactly one concern.',
        'keyPoints': ['Each layer owns a single concern', 'Layers talk via clear interfaces',
                      'Change one concern, leave the rest', 'Basis of layered & MVC designs'],
        'python': 'class OrderRepository:        # data\n    def save(self, order): ...\n\n'
                  'class OrderService:           # logic\n    def __init__(self, repo):\n'
                  '        self.repo = repo\n    def place(self, order):\n        self.repo.save(order)\n\n'
                  'class OrderController:        # presentation\n    def __init__(self, service):\n'
                  '        self.service = service\n    def handle(self, req):\n'
                  '        self.service.place(req.order)',
        'diagram': 'flowchart TB\n  P[Presentation] --> S[Business logic]\n  S --> R[Data access]\n  R --> DB[(Database)]',
        'diagramType': 'flowchart', 'exercise': '',
    },
    'coupling-and-cohesion': {
        'slug': 'coupling-and-cohesion', 'type': 'principle', 'title': 'Coupling & Cohesion',
        'oneLiner': 'Aim for low coupling between modules and high cohesion within each module.',
        'keyPoints': ['Low coupling: modules change independently', 'High cohesion: one module, one job',
                      'Couple through abstractions, not internals', 'Together: easy to change & test'],
        'python': 'from abc import ABC, abstractmethod\n\nclass PaymentGateway(ABC):      # the seam\n'
                  '    @abstractmethod\n    def charge(self, amount): ...\n\n'
                  'class OrderService:             # cohesive: ordering only\n'
                  '    def __init__(self, gateway: PaymentGateway):\n        self.gateway = gateway  # low coupling\n'
                  '    def checkout(self, cart):\n        self.gateway.charge(cart.total)',
        'diagram': 'classDiagram\n  class OrderService {\n    +place_order()\n    +cancel_order()\n  }\n'
                   '  class PaymentGateway {\n    <<interface>>\n    +charge(amount)\n  }\n'
                   '  OrderService --> PaymentGateway : one seam',
        'diagramType': 'classDiagram', 'exercise': '',
    },
    'composing-objects': {
        'slug': 'composing-objects', 'type': 'principle', 'title': 'Composing Objects',
        'oneLiner': 'Favor composition (has-a) over inheritance (is-a) — assemble behavior from small parts.',
        'keyPoints': ['Build behavior by combining objects', 'Avoid deep, rigid inheritance trees',
                      'Swap parts at runtime', 'Delegate instead of subclassing'],
        'python': 'class Engine:\n    def start(self):\n        return "engine on"\n\n'
                  'class GPS:\n    def route(self, dest):\n        return f"routing to {dest}"\n\n'
                  'class Car:                      # has-a, not is-a\n    def __init__(self):\n'
                  '        self.engine = Engine()\n        self.gps = GPS()\n    def drive(self, dest):\n'
                  '        self.engine.start()\n        return self.gps.route(dest)',
        'diagram': 'classDiagram\n  class Car {\n    +drive(dest)\n  }\n  class Engine {\n    +start()\n  }\n'
                   '  class GPS {\n    +route(dest)\n  }\n  Car *-- Engine\n  Car *-- GPS',
        'diagramType': 'classDiagram', 'exercise': '',
    },
}
d.update(AUTHORED)

# ---- diagram curation ----
EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿️←-⇿⬀-⯿]')

def clean_mermaid(s: str) -> str:
    out = []
    for ln in s.split('\n'):
        st = ln.strip()
        if st.startswith('style ') or st.startswith('classDef ') or ':::' in ln:
            continue
        out.append(EMOJI.sub('', ln).rstrip())
    return '\n'.join([l for l in out if l.strip()]).strip()

# replace clearly-broken / weak diagrams
DIAGRAM_OVERRIDE = {
    'dry': "flowchart TB\n  A[AuthService] --> V\n  P[PaymentService] --> V\n  M[MessagingService] --> V\n  V([\"EmailValidator<br/>single source of truth\"])",
    'kiss': "flowchart TB\n  R[New requirement] --> Q{Abstraction<br/>needed now?}\n  Q -->|no| S[One small function]\n  Q -->|yes| A[Add it then, not before]",
    'yagni': "classDiagram\n  class PasswordValidator {\n    +is_valid(password) bool\n  }",
    'use-case-diagram': "flowchart LR\n  C([Customer]) --> U1([Browse movies])\n  C --> U2([Book ticket])\n  C --> U3([Cancel ticket])",
    'state-machine-diagram': "stateDiagram-v2\n  [*] --> Idle\n  Idle --> Playing: play()\n  Playing --> Paused: pause()\n  Playing --> Stopped: stop()\n  Paused --> Playing: resume()\n  Paused --> Stopped: stop()\n  Stopped --> Idle: reset()\n  Stopped --> [*]",
}

KNOWN_MERMAID = ('classDiagram', 'sequenceDiagram', 'stateDiagram', 'flowchart',
                 'graph', 'erDiagram', 'journey', 'mindmap', 'gantt', 'pie')

SCALE = {'classDiagram': 0.62, 'sequenceDiagram': 0.82, 'stateDiagram-v2': 0.78,
         'stateDiagram': 0.78, 'flowchart': 0.8, 'graph': 0.8}

def diagram_for(slug):
    x = d[slug]
    raw = DIAGRAM_OVERRIDE.get(slug) or x['diagram']
    raw = clean_mermaid(raw)
    # safety: ensure the diagram declares its type on the first line
    first = raw.split('\n', 1)[0].strip()
    if not any(first.startswith(k) for k in KNOWN_MERMAID):
        raw = (x.get('diagramType', '').strip() or 'flowchart TB') + '\n' + raw
    sc = SCALE.get(x.get('diagramType', '').strip(), 0.8)
    if slug in DIAGRAM_OVERRIDE and slug == 'kiss':
        sc = 0.85
    if slug in DIAGRAM_OVERRIDE and slug == 'use-case-diagram':
        sc = 0.9
    return f"```mermaid {{scale: {sc}}}\n{raw}\n```"

def kpts(slug, cls="bp-dim text-xs"):
    items = ''.join(f"<li>{k}</li>" for k in d[slug]['keyPoints'])
    return f'<ul class="kpts {cls}">{items}</ul>'

def principle_slide(slug):
    x = d[slug]
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{x['oneLiner']}</div>

<div class="grid grid-cols-2 gap-6 items-start">
<div class="min-w-0">

```python
{x['python'].strip()}
```

</div>
<div class="min-w-0">

{diagram_for(slug)}

{kpts(slug)}

</div>
</div>
"""

def uml_slide(slug):
    x = d[slug]
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{x['oneLiner']}</div>

<div class="grid grid-cols-[2fr_3fr] gap-6 items-center">
<div class="min-w-0">

{kpts(slug, "bp-dim text-sm")}

</div>
<div class="min-w-0">

{diagram_for(slug)}

</div>
</div>
"""

def placeholder_slide(title, slug):
    return f"""---

## {title}

<PremiumPlaceholder />
"""

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
title: Principles & UML
info: |
  LLD for friends — Deck 2: Principles & UML
  Design Principles · SOLID · UML
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

<div class="bp-eyebrow mb-4" v-motion :initial="{ x: -40, opacity: 0 }" :enter="{ x: 0, opacity: 1, transition: { delay: 80 } }">LOW-LEVEL DESIGN · DECK 2</div>

<div v-motion :initial="{ y: 36, opacity: 0 }" :enter="{ y: 0, opacity: 1, transition: { delay: 180 } }">

# Principles &amp; UML

</div>

<div class="text-2xl bp-dim mt-2 mb-8 bp-mono" v-motion :initial="{ y: 24, opacity: 0 }" :enter="{ y: 0, opacity: 1, transition: { delay: 320 } }">The rules that keep designs clean — and how to draw them.</div>

<div class="flex gap-3" v-motion :initial="{ opacity: 0 }" :enter="{ opacity: 1, transition: { delay: 480 } }">
  <span class="bp-chip">01 · Design Principles</span>
  <span class="bp-chip">02 · SOLID</span>
  <span class="bp-chip">03 · UML</span>
</div>

<div class="abs-br m-6 bp-dim text-sm">
  press <span class="bp-key">space</span> to advance · <span class="bp-key">o</span> for overview
</div>
"""

AGENDA = """---
layout: default
---

## The path

<div class="grid grid-cols-3 gap-4 mt-6">
<div class="bp-card bp-card--cyan" v-click="1">
  <div class="text-3xl bp-mono bp-glow-text">01</div>
  <div class="text-xl mt-1">Design Principles</div>
  <div class="bp-dim text-sm mt-2">DRY · KISS · YAGNI · Law of Demeter · …</div>
</div>
<div class="bp-card" v-click="2">
  <div class="text-3xl bp-mono">02</div>
  <div class="text-xl mt-1">SOLID</div>
  <div class="bp-dim text-sm mt-2">the five object-design principles</div>
</div>
<div class="bp-card bp-card--violet" v-click="3">
  <div class="text-3xl bp-mono">03</div>
  <div class="text-xl mt-1">UML</div>
  <div class="bp-dim text-sm mt-2">class · use-case · sequence · activity · state</div>
</div>
</div>

<div v-click="4" class="mt-12 text-center bp-dim bp-mono text-sm">
  3 modules · principles you'll cite in every review &rarr;
</div>
"""

RECAP = """---
layout: default
---

<div class="bp-eyebrow mb-2">DECK 2 · RECAP</div>

## You now know

<div class="grid grid-cols-3 gap-4 mt-6">
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">01</span> Principles</div>
    <ul class="recap-list">
      <li>DRY · KISS · YAGNI</li>
      <li>Demeter · separation</li>
      <li>coupling, cohesion, composition</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">02</span> SOLID</div>
    <ul class="recap-list">
      <li>SRP · OCP · LSP</li>
      <li>ISP · DIP</li>
      <li>the design backbone</li>
    </ul>
  </div>
  <div class="bp-card recap-card" v-click>
    <div class="recap-head"><span class="bp-mono bp-glow-text">03</span> UML</div>
    <ul class="recap-list">
      <li>class · use-case</li>
      <li>sequence · activity</li>
      <li>state machine</li>
    </ul>
  </div>
</div>

<div v-click class="mt-10 text-center bp-mono bp-dim">Next &rarr; <span style="color:var(--bp-cyan)">Deck 3 · Design Patterns</span></div>

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
  <div class="bp-eyebrow mb-3">END OF DECK 2</div>
  <h1>Questions?</h1>
  <div class="bp-dim bp-mono mt-3">Foundations &rarr; Principles &rarr; Patterns &rarr; Interviews</div>
</div>
"""

KPTS_STYLE = """
<style>
.kpts { list-style: none; padding: 0; margin: .6rem 0 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .35rem 0; line-height: 1.4; }
.kpts li::before { content: '▸'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
"""

# slugs whose slide is a bespoke interactive/animated component instead of code+diagram
INTERACTIVE = {
    'dry': 'DryExtract',
    'kiss': 'KissToggle',
    'yagni': 'YagniPrune',
    'lod': 'DemeterChain',
    'soc': 'LayerFlow',
    'coupling-and-cohesion': 'CouplingToggle',
    'composing-objects': 'ComposeSwap',
    'srp': 'SrpSplit',
    'ocp': 'OcpPlugin',
    'lsp': 'LspSwap',
    'isp': 'IspToggle',
    'dip': 'DipInvert',
    'state-machine-diagram': 'StateMachine',
    'sequence-diagram': 'SequencePlay',
    'activity-diagram': 'ActivityRun',
}

def interactive_slide(slug, comp):
    x = d[slug]
    return f"""---

## {x['title']}

<div class="bp-dim bp-mono text-sm mb-3">{x['oneLiner']}</div>

<{comp} />
"""

def emit(slug, kind):
    if slug in INTERACTIVE:
        return interactive_slide(slug, INTERACTIVE[slug])
    return uml_slide(slug) if kind == 'uml' else principle_slide(slug)

parts = [HEAD, AGENDA]
parts.append(section('01', 'Design Principles', ['DRY · KISS · YAGNI', 'Law of Demeter']))
for s in ['dry', 'kiss', 'yagni', 'lod']:
    parts.append(emit(s, 'p'))
for s in ['soc', 'coupling-and-cohesion', 'composing-objects']:
    parts.append(emit(s, 'p'))
parts.append(section('02', 'SOLID Principles', ['S · O · L · I · D']))
for s in ['srp', 'ocp', 'lsp', 'isp', 'dip']:
    parts.append(emit(s, 'p'))
parts.append(section('03', 'UML Diagrams', ['structure & behavior']))
for s in ['class-diagram', 'use-case-diagram', 'sequence-diagram', 'activity-diagram', 'state-machine-diagram']:
    parts.append(emit(s, 'uml'))
parts.append(RECAP)
parts.append(END)

doc = '\n'.join(parts)
open(ROOT / 'deck2.md', 'w').write(doc)
print("wrote deck2.md  | slides ~", doc.count('\n---\n') + 1)
