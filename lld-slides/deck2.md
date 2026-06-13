---
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

---
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

---
layout: default
class: section-slide
---

<div class="ghost-num">01</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 01</div>
  <h1>Design Principles</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">DRY · KISS · YAGNI</span><span class="bp-chip">Law of Demeter</span></div>
</div>

---

## DRY Principle

<div class="bp-dim bp-mono text-sm mb-3">Every piece of knowledge should exist in exactly one place in your system.</div>

<DryExtract />

---

## Keep It Simple, Stupid

<div class="bp-dim bp-mono text-sm mb-3">Simpler code is more readable, maintainable, and has fewer bugs than unnecessarily complex solutions.</div>

<KissToggle />

---

## YAGNI

<div class="bp-dim bp-mono text-sm mb-3">Don't build features or add complexity until you actually need them.</div>

<YagniPrune />

---

## Law of Demeter

<div class="bp-dim bp-mono text-sm mb-3">Only talk to your immediate friends; never reach through objects to get what you want.</div>

<DemeterChain />

---

## Separation of Concerns

<div class="bp-dim bp-mono text-sm mb-3">Split a system into distinct parts, each responsible for exactly one concern.</div>

<LayerFlow />

---

## Coupling & Cohesion

<div class="bp-dim bp-mono text-sm mb-3">Aim for low coupling between modules and high cohesion within each module.</div>

<CouplingToggle />

---

## Composing Objects

<div class="bp-dim bp-mono text-sm mb-3">Favor composition (has-a) over inheritance (is-a) — assemble behavior from small parts.</div>

<ComposeSwap />

---
layout: default
class: section-slide
---

<div class="ghost-num">02</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 02</div>
  <h1>SOLID Principles</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">S · O · L · I · D</span></div>
</div>

---

## Single Responsibility Principle

<div class="bp-dim bp-mono text-sm mb-3">A class should have one reason to change and do one thing well.</div>

<SrpSplit />

---

## Open-Closed Principle

<div class="bp-dim bp-mono text-sm mb-3">Software should be open for extension but closed for modification through abstraction.</div>

<OcpPlugin />

---

## Liskov Substitution Principle

<div class="bp-dim bp-mono text-sm mb-3">Subtypes must be safely substitutable for base types without breaking behavior.</div>

<LspSwap />

---

## Interface Segregation

<div class="bp-dim bp-mono text-sm mb-3">No client should be forced to depend on methods it does not use — split fat interfaces.</div>

<IspToggle />

---

## Dependency Inversion Principle

<div class="bp-dim bp-mono text-sm mb-3">Depend on abstractions, not implementations</div>

<DipInvert />

---
layout: default
class: section-slide
---

<div class="ghost-num">03</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 03</div>
  <h1>UML Diagrams</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">structure & behavior</span></div>
</div>

---

## Class Diagram: Structure & Relationships

<div class="bp-dim bp-mono text-sm mb-3">Static view of classes, attributes, methods, and relationships in object-oriented design.</div>

<div class="grid grid-cols-[2fr_3fr] gap-6 items-center">
<div class="min-w-0">

<ul class="kpts bp-dim text-sm"><li>Three compartments: name, attributes, methods</li><li>Visibility markers: + public, - private, # protected</li><li>Six relationship types from dependency to realization</li><li>Association and composition model "has-a" connections</li></ul>

</div>
<div class="min-w-0">

```mermaid {scale: 0.62}
classDiagram
    class BankAccount {
        -accountNumber: String
        -balance: double
        +deposit(amount: double): void
        +withdraw(amount: double): boolean
        +getBalance(): double
    }
    class Customer {
        -customerId: String
        -name: String
        -accounts: List~BankAccount~
    }
    Customer "1" --> "*" BankAccount : owns
```

</div>
</div>

---

## Use Case Diagram

<div class="bp-dim bp-mono text-sm mb-3">Shows actors and their system goals; maps requirements before design begins</div>

<div class="grid grid-cols-[2fr_3fr] gap-6 items-center">
<div class="min-w-0">

<ul class="kpts bp-dim text-sm"><li>Actor initiates or supports interaction from outside</li><li>Use case is complete goal ending with meaningful result</li><li>System boundary encloses functionality; actors outside</li><li>Associate actors to use cases with solid lines</li></ul>

</div>
<div class="min-w-0">

```mermaid {scale: 0.9}
flowchart LR
  C([Customer]) --> U1([Browse movies])
  C --> U2([Book ticket])
  C --> U3([Cancel ticket])
```

</div>
</div>

---

## Sequence Diagrams

<div class="bp-dim bp-mono text-sm mb-3">Visualizes message interactions between objects in temporal order to trace system behavior.</div>

<SequencePlay />

---

## Activity Diagrams: Mapping Workflows

<div class="bp-dim bp-mono text-sm mb-3">Shows the sequence of activities, decisions, and parallel paths in a workflow process.</div>

<ActivityRun />

---

## State Machine Diagrams

<div class="bp-dim bp-mono text-sm mb-3">Shows how objects change states in response to events; models object lifecycles and state-driven behavior.</div>

<StateMachine />

---
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

---
layout: end
---

<div class="text-center">
  <div class="bp-eyebrow mb-3">END OF DECK 2</div>
  <h1>Questions?</h1>
  <div class="bp-dim bp-mono mt-3">Foundations &rarr; Principles &rarr; Patterns &rarr; Interviews</div>
</div>
