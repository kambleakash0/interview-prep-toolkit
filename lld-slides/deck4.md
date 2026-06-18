---
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

---
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

---
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

---
layout: default
class: section-slide
---

<div class="ghost-num">01</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 01</div>
  <h1>The Interview Method</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">how to drive the room</span></div>
</div>

---

## How to Approach OOD Interviews

<div class="bp-dim bp-mono text-sm mb-3">A repeatable 5-step framework — clarify, find entities, design classes, place patterns, walk use cases — that turns any "Design X" prompt into a defensible class diagram.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod
from enum import Enum

class VoteType(Enum):
    UPVOTE = 1
    DOWNVOTE = -1

# Step 3: shared verbs -> interfaces (Question, Answer implement both)
class Votable(ABC):
    @abstractmethod
    def vote(self, user: "User", vt: VoteType) -> None: ...

# Step 4: Strategy swaps reputation rules without touching core classes
class ReputationStrategy(ABC):
    @abstractmethod
    def delta(self, vt: VoteType, is_question: bool) -> int: ...

class StandardReputation(ReputationStrategy):
    def delta(self, vt, is_question):
        if vt == VoteType.UPVOTE: return 5 if is_question else 10
        return -2

# Step 5: walk the use case + trap the edge cases
def vote(self, voter: "User", vt: VoteType) -> None:
    if voter.id == self.author.id:
        raise ValueError("no self-voting")
    if voter.id in self.votes:
        raise ValueError("no duplicate voting")
    self.votes[voter.id] = Vote(voter, vt)
    self.score += self.rep.delta(vt, self.is_question)
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">FRAMEWORK</div>
<ul class="roles"><li><b>Step 1 Clarify Requirements</b> <span class="bp-dim">ask first, scope via four buckets</span></li><li><b>Step 2 Identify Core Entities</b> <span class="bp-dim">nouns -&gt; 4-6 things</span></li><li><b>Step 3 Design Classes &amp; Interfaces</b> <span class="bp-dim">cardinality, composition vs association, Facade manager</span></li><li><b>Step 4 Apply Design Patterns</b> <span class="bp-dim">Strategy, Observer; never name-drop</span></li><li><b>Step 5 Walk Use Cases &amp; Edge Cases</b> <span class="bp-dim">trace vote, trap edge cases</span></li><li><b>StackOverflow</b> <span class="bp-dim">central Facade manager / entry-point API</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Time-box: Clarify 3-5m -&gt; Entities 3-5m -&gt; Classes 20-25m -&gt; Patterns 5-7m -&gt; Use Cases 5-10m</li><li>Step 1 scope first: features, actors, constraints, concurrency — never assume</li><li>Step 2 nouns -&gt; 4-6 entities; verbs -&gt; interfaces (Commentable, Votable)</li><li>Step 3 composition vs association, then add central Facade manager (Deck-3 Facade + Singleton)</li><li>Step 4 state What/Why/How; Strategy for reputation, Observer for notifications, State for status (Deck-3)</li><li>Step 5 trace vote flow (Vote -&gt; Strategy -&gt; Observer); edge cases: self-vote, dup, empty, floor</li></ul>

</div>
</div>

<!--
Key points: Time-box: Clarify 3-5m -> Entities 3-5m -> Classes 20-25m -> Patterns 5-7m -> Use Cases 5-10m | Step 1 scope first: features, actors, constraints, concurrency — never assume | Step 2 nouns -> 4-6 entities; verbs -> interfaces (Commentable, Votable) | Step 3 composition vs association, then add central Facade manager (Deck-3 Facade + Singleton) | Step 4 state What/Why/How; Strategy for reputation, Observer for notifications, State for status (Deck-3) | Step 5 trace vote flow (Vote -> Strategy -> Observer); edge cases: self-vote, dup, empty, floor

Problem: "Design Stack Overflow" is open-ended and the clock is 45-60 minutes. Candidates freeze, build unrequested features, or pattern-drop. Without a framework the session has no shape and no defensible deliverable.

Real-world: Stack Overflow Q&A core design · any FAANG 'Design X' OOD round (parking lot, elevator, vending machine)

Gotcha: Skipping Step 1 to look fast: you build unrequested features and run out of clock. Clarify scope first, then narrate every class decision aloud — the verbal reasoning is half the grade.
-->

---

## How to Approach OOD Interviews

<div class="bp-dim bp-mono text-sm mb-3">Drive one Stack Overflow design through all 5 steps on a clickable step-rail, with a running time-budget clock.</div>

<OodInterviewCockpit />

---

## How to Approach Machine-Coding Interviews

<div class="bp-dim bp-mono text-sm mb-3">Run the 60-90 min round on a clock: cap design at 15-20%, then build bottom-up to a codebase that actually RUNS.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from enum import Enum

class VoteType(Enum):          # adjective/state -> enum
    UPVOTE = 1
    DOWNVOTE = -1

class Question:                # noun -> model class
    def vote(self, voter, vote_type):          # verb -> method
        if voter.id == self.author.id:
            raise ValueError("Cannot vote on your own question")
        if voter.id in self.votes:             # Map dedup: O(1)
            raise ValueError("Already voted")
        self.votes[voter.id] = Vote(voter, vote_type)
        self.author.update_reputation(5 if vote_type is VoteType.UPVOTE else -2)

class StackOverflow:           # the manager: single entry point (Facade)
    def __init__(self):
        self.users: dict[int, User] = {}       # in-memory repo
        self.questions: dict[int, Question] = {}

    def ask_question(self, user, title, body, tag_names):
        if not title or not title.strip():     # validate at the boundary
            raise ValueError("Question title cannot be empty")
        q = Question(user, title, body, [Tag(n) for n in tag_names])
        self.questions[q.id] = q               # register + auto-inc id
        user.add_question(q)
        return q
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">FRAMEWORK</div>
<ul class="roles"><li><b>Clarify (3-5m): I/O format, validate?, graded tests, limits; MUST/NICE list</b></li><li><b>Quick Design (5-10m): noun-verb-adjective; 5-7 classes, Map-vs-List, enum-vs-boolean</b></li><li><b>Skeleton (10-15m): model fields + constructors so it COMPILES by minute 10</b></li><li><b>Core Impl (40-50m): bottom-up enums -&gt; models -&gt; service -&gt; Main; TODO-skip</b></li><li><b>Edge Cases &amp; Test (20-25m): boundary, null/empty, dup, auth, state, order; fix now</b></li><li><b>Manager/Service StackOverflow</b> <span class="bp-dim">Facade entry point, in-memory Map&lt;id, entity&gt;</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Clock: Clarify 3-5m -&gt; Quick Design 5-10m -&gt; Skeleton 10-15m -&gt; Core 40-50m -&gt; Edge &amp; Test 20-25m; design &lt;= 15-20%</li><li>Noun-verb-adjective: nouns -&gt; classes, verbs -&gt; methods, adjectives/states -&gt; enums</li><li>Add one manager/service Facade entry point; in-memory Map&lt;id, entity&gt; stores (Repository-ish)</li><li>Map by ID for lookup/dedup (O(1)), List for order; enums over boolean params</li><li>Skeleton compiles by minute 10, then bottom-up enums -&gt; models -&gt; service -&gt; Main; Main is test harness</li><li>Harden by category: boundary, null/empty, dup, auth, state, order; TODO-skip, never trade validation</li></ul>

</div>
</div>

<!--
Key points: Clock: Clarify 3-5m -> Quick Design 5-10m -> Skeleton 10-15m -> Core 40-50m -> Edge & Test 20-25m; design <= 15-20% | Noun-verb-adjective: nouns -> classes, verbs -> methods, adjectives/states -> enums | Add one manager/service Facade entry point; in-memory Map<id, entity> stores (Repository-ish) | Map by ID for lookup/dedup (O(1)), List for order; enums over boolean params | Skeleton compiles by minute 10, then bottom-up enums -> models -> service -> Main; Main is test harness | Harden by category: boundary, null/empty, dup, auth, state, order; TODO-skip, never trade validation

Problem: Candidates over-design and run out of time, hitting minute 50 with 500 lines that do not compile. Machine coding scores what runs, not what you describe, so you need a time-boxed pipeline that keeps the project compiling from minute 10 and trades extra features for working validation.

Real-world: Flipkart / PhonePe / Atlassian / Uber machine-coding rounds · 60-90 min timed IDE build of a real system (parking lot, Stack Overflow, food delivery)

Gotcha: Over-designing: detailed UML and every signature upfront burns the clock. Sketch 5-7 classes, start coding, refactor as you discover issues; never trade input validation for one more feature.
-->

---

## How to Approach Machine-Coding Interviews

<div class="bp-dim bp-mono text-sm mb-3">Drive the 90-minute clock: classify words into classes/methods/enums, watch the skeleton make it compile, trip the edge-case guards.</div>

<MachineCodingClock />

---

## Identifying Entities & Modeling Relationships

<div class="bp-dim bp-mono text-sm mb-3">Before you reach for a pattern, mine the prompt: nouns become candidate entities, verbs become behavior, then pin a typed relationship and a multiplicity on every pair.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from enum import Enum
from dataclasses import dataclass, field

# Prompt: "A parking lot has levels; each level has spots.
# A vehicle parks in a spot; status is free or occupied."

class SpotStatus(Enum):          # fixed categorical set -> enum
    FREE = "free"
    OCCUPIED = "occupied"

@dataclass
class Spot:                      # has identity + behavior -> entity
    spot_id: str                 # "spot number" is data -> attribute
    status: SpotStatus = SpotStatus.FREE

@dataclass
class Level:                     # owns spots; spots die with level
    levels_id: str
    spots: list[Spot] = field(default_factory=list)   # composition 1..*

@dataclass
class ParkingLot:                # aggregates levels (1..*)
    levels: list[Level] = field(default_factory=list)

    def park(self, v: "Vehicle") -> Spot | None:      # verb -> method
        for lvl in self.levels:
            for s in lvl.spots:
                if s.status is SpotStatus.FREE:
                    s.status = SpotStatus.OCCUPIED
                    return s
        return None
# "available", "display board", "ticket print" -> discard / attribute
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">FRAMEWORK</div>
<ul class="roles"><li><b>Mine nouns &amp; verbs</b> <span class="bp-dim">nouns -&gt; entities, verbs -&gt; methods</span></li><li><b>Filter candidates</b> <span class="bp-dim">entity vs attribute vs enum vs discard</span></li><li><b>Promote to enums</b> <span class="bp-dim">fold fixed value sets into Enum</span></li><li><b>Type each relationship</b> <span class="bp-dim">inheritance / composition / aggregation / association</span></li><li><b>Set multiplicity</b> <span class="bp-dim">1 / 0..* / 1..* per end; many-to-many -&gt; link entity</span></li><li><b>Validate the model</b> <span class="bp-dim">ownership, invariants, patterns emerge</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Mine first: nouns -&gt; entities, verbs -&gt; methods; before classes/patterns</li><li>Filter: merge synonyms, identity+behavior -&gt; entity, data -&gt; attribute, fixed sets -&gt; enum, drop UI/IO</li><li>Type each edge: inheritance (is-a), composition (part dies), aggregation (part outlives), association (uses)</li><li>Pin multiplicity 1 / 0..* / 1..*; many-to-many -&gt; link entity (Booking links User, Show)</li><li>Composition over inheritance: varying behavior -&gt; Strategy/State; trees -&gt; Composite; creation -&gt; Factory; broadcast -&gt; Observer</li><li>Clean model makes patterns emerge: OOAD prerequisite, not a pattern</li></ul>

</div>
</div>

<!--
Key points: Mine first: nouns -> entities, verbs -> methods; before classes/patterns | Filter: merge synonyms, identity+behavior -> entity, data -> attribute, fixed sets -> enum, drop UI/IO | Type each edge: inheritance (is-a), composition (part dies), aggregation (part outlives), association (uses) | Pin multiplicity 1 / 0..* / 1..*; many-to-many -> link entity (Booking links User, Show) | Composition over inheritance: varying behavior -> Strategy/State; trees -> Composite; creation -> Factory; broadcast -> Observer | Clean model makes patterns emerge: OOAD prerequisite, not a pattern

Problem: Candidates jump straight to classes and patterns. Without a domain model, you get tight coupling, god classes, and forced patterns. The fix is a systematic noun/verb extraction pass that filters words into entities, attributes, enums, or noise, then types every relationship and sets its multiplicity, so the structure (and the patterns) fall out naturally.

Real-world: parking lot levels/spots/vehicles · movie booking User-Show-Booking link entity

Gotcha: This is OOAD/domain modeling, not a GoF pattern. The patterns list is a cross-reference, not the subject. The deeper trap is over-modeling: promoting a plain attribute (ticket number) to its own entity, or building a deep is-a tree where a single collaborator field would do.
-->

---

## Identifying Entities & Modeling Relationships

<div class="bp-dim bp-mono text-sm mb-3">Words to entities to a typed, multiplicity-labeled relationship graph, on one fixed prompt.</div>

<EntityModelingLab />

---

## Writing Clean, Extensible Code

<div class="bp-dim bp-mono text-sm mb-3">Your interview code is read more than it is run; win on names, single responsibilities, and a seam where the next requirement drops in as a new class, not an edited method.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

# DIRTY: every new type edits this tested method (closed for extension)
def process(kind, amount):
    if kind == "credit":   ...   # charge card
    elif kind == "debit":  ...
    elif kind == "upi":    ...
    else: raise ValueError(kind)  # add GiftCard -> edit here

# CLEAN: new behavior = new class; the seam stays untouched (Open/Closed)
class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: int) -> "Receipt": ...

class CreditCard(PaymentMethod):
    def pay(self, amount): return charge(self.token, amount)

class GiftCard(PaymentMethod):              # added, nothing edited
    def pay(self, amount): return redeem(self.code, amount)

class Processor:
    def __init__(self, method: PaymentMethod):  # inject the abstraction
        self._method = method
    def run(self, amount: int):
        if amount <= 0:                     # guard clause, fail fast
            raise InvalidAmount(amount)
        return self._method.pay(amount)     # polymorphism, no if/elif
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">FRAMEWORK</div>
<ul class="roles"><li><b>Names</b> <span class="bp-dim">intention-revealing identifiers</span></li><li><b>Responsibilities</b> <span class="bp-dim">SRP: one reason to change</span></li><li><b>Seam / Open-Closed</b> <span class="bp-dim">interface + registry for new types</span></li><li><b>Dependency Injection</b> <span class="bp-dim">pass abstraction, never a concrete</span></li><li><b>Polymorphism over conditionals</b> <span class="bp-dim">Strategy/State replace switch</span></li><li><b>Guard clauses</b> <span class="bp-dim">validate at boundary, flat happy path</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Code = communication: clear names, small methods, domain-shaped structure</li><li>One responsibility per class (SRP), one job per method; 'and' -&gt; split</li><li>Extensibility = Open/Closed seam: new type -&gt; new class, not new switch branch</li><li>Program to interface, inject it: depend on PaymentMethod (Strategy, DI)</li><li>Polymorphism or registry lookup over type/state conditionals (Strategy, State, Factory)</li><li>Guard clauses + domain errors over nesting; fail fast, flat happy path; don't gold-plate</li></ul>

</div>
</div>

<!--
Key points: Code = communication: clear names, small methods, domain-shaped structure | One responsibility per class (SRP), one job per method; 'and' -> split | Extensibility = Open/Closed seam: new type -> new class, not new switch branch | Program to interface, inject it: depend on PaymentMethod (Strategy, DI) | Polymorphism or registry lookup over type/state conditionals (Strategy, State, Factory) | Guard clauses + domain errors over nesting; fail fast, flat happy path; don't gold-plate

Problem: Candidates ship working code that solves the prompt but rots the moment the interviewer says "now add X." A fat if/elif on a type or state forces edits to tested core logic for every new case, and anemic objects with public fields leak invariants. The grader is judging structure, naming, and extensibility, not just a passing run, so the candidate who cannot absorb a new requirement without rewriting loses the signal even with a correct first pass.

Real-world: payment methods (credit / debit / UPI / gift card) · discount rules and notification channels added without touching the engine

Gotcha: Don't gold-plate a 45-minute problem: apply the Open/Closed seam at the one axis the prompt actually flexes, not a pattern for every class.
-->

---

## Writing Clean, Extensible Code

<div class="bp-dim bp-mono text-sm mb-3">Click 'Add: GiftCard' and watch DIRTY grow another if/elif branch while CLEAN snaps a new Strategy card onto the registry shelf with zero core lines changed.</div>

<RefactorLab />

---

## Choosing the Right Design Pattern

<div class="bp-dim bp-mono text-sm mb-3">Don't hunt for places to use a pattern; name the design pain first, then reach for the pattern that dissolves it -- and say the tradeoff out loud.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
SMELL_TO_PATTERN = {
    # symptom keyword            -> pattern, one-line discriminator
    "growing if/else on a type":  ("Strategy", "caller picks the algorithm"),
    "behavior changes by phase":  ("State",    "object drives its own transitions"),
    "new Concrete() scattered":   ("Factory",  "hide WHICH class is built"),
    "telescoping constructors":   ("Builder",  "hide HOW it's assembled"),
    "one change updates many":    ("Observer", "fan-out via subscribe/notify"),
    "wrap to add behavior live":  ("Decorator","compose at runtime, not subclass"),
    "tree of part/whole":         ("Composite","treat leaf and group uniformly"),
    "3rd-party API mismatch":     ("Adapter",  "translate the wrong interface"),
}

def diagnose(symptom: str) -> str:
    pattern, why = SMELL_TO_PATTERN[symptom]
    return f"symptom={symptom!r} -> {pattern} ({why})"

def justify(symptom, pattern, benefit, cost) -> str:
    # the sentence the interviewer is listening for
    return f"I see {symptom}, so I add {pattern} to {benefit}, accepting {cost}."

# YAGNI: when duplication has a single axis, skip the pattern.
def shipping_cost(method, weight):       # plain function beats Strategy here
    return {"air": 9, "ground": 4}[method] * weight
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">FRAMEWORK</div>
<ul class="roles"><li><b>Symptom</b> <span class="bp-dim">named design pain: creation, behavior, fan-out, structure, API</span></li><li><b>Smell-to-family map</b> <span class="bp-dim">routes symptom to GoF family</span></li><li><b>Discriminator</b> <span class="bp-dim">one-line splitter for trap pairs</span></li><li><b>Justification sentence</b> <span class="bp-dim">symptom -&gt; pattern -&gt; benefit -&gt; cost</span></li><li><b>YAGNI guardrail</b> <span class="bp-dim">rejects pattern when if/else suffices</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Problem-first, not pattern-first: name the smell it removes</li><li>5 smells -&gt; families: messy creation -&gt; Factory/Abstract Factory/Builder; varying/switching behavior -&gt; Strategy/State; one change fans out -&gt; Observer; rigid tree/wrapping/mismatched API -&gt; Composite/Decorator/Adapter/Facade</li><li>Say it: 'see &lt;symptom&gt;, add &lt;pattern&gt; for &lt;benefit&gt;, accept &lt;cost&gt;'</li><li>Strategy vs State: caller picks algorithm vs object drives own transitions</li><li>Factory vs Builder: hides WHICH class vs HOW it's assembled</li><li>YAGNI: if/else or plain function often wins; second axis of change justifies abstraction</li></ul>

</div>
</div>

<!--
Key points: Problem-first, not pattern-first: name the smell it removes | 5 smells -> families: messy creation -> Factory/Abstract Factory/Builder; varying/switching behavior -> Strategy/State; one change fans out -> Observer; rigid tree/wrapping/mismatched API -> Composite/Decorator/Adapter/Facade | Say it: 'see <symptom>, add <pattern> for <benefit>, accept <cost>' | Strategy vs State: caller picks algorithm vs object drives own transitions | Factory vs Builder: hides WHICH class vs HOW it's assembled | YAGNI: if/else or plain function often wins; second axis of change justifies abstraction

Problem: Candidates either force patterns into trivial code or avoid them and ship rigid conditionals. Interviewers score design judgement, not pattern trivia: the question is never "which pattern do you know?" but "what hurts, and what removes that pain at an acceptable cost?"

Real-world: narrating a design decision in a machine-coding round · refactoring a God-class if/else during a live interview

Gotcha: Pattern-evangelism backfires: forcing Strategy onto a two-line lookup signals poor judgement. The simplest thing that removes the pain wins; let a real second axis of change earn the abstraction.
-->

---

## Choosing the Right Design Pattern

<div class="bp-dim bp-mono text-sm mb-3">Click a real interview code smell, watch it route through a decision node to the pattern that cures it -- then flip Trap mode to disambiguate the near-misses.</div>

<PatternDiagnosisBench />

---

## Handling Concurrency Scenarios

<div class="bp-dim bp-mono text-sm mb-3">Get the single-threaded logic correct first, then name the race condition and lock exactly the read-modify-write span — nothing more.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import threading

class SeatManager:           # Singleton: the contended registry
    def __init__(self):
        self._lock = threading.Lock()
        self._booked = set()

    # BEFORE: race condition — check-then-act is not atomic
    def book_unsafe(self, seat_id, user):
        if seat_id not in self._booked:   # both threads pass
            self._booked.add(seat_id)     # both write -> double-book
            return True
        return False

    # AFTER: guard only the read-modify-write critical section
    def book(self, seat_id, user):
        with self._lock:                  # smallest span, not whole flow
            if seat_id in self._booked:
                return False              # loser fails cleanly
            self._booked.add(seat_id)
            return True
    # notify waitlist / persist OUTSIDE the lock (Observer)
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">FRAMEWORK</div>
<ul class="roles"><li><b>Trigger detection</b> <span class="bp-dim">which of 3 ways concurrency entered</span></li><li><b>Logic-first sequencing</b> <span class="bp-dim">correct single-threaded before locks</span></li><li><b>Race-condition naming</b> <span class="bp-dim">non-atomic check-then-act on shared state</span></li><li><b>Critical-section scoping</b> <span class="bp-dim">minimal read-modify-write span to guard</span></li><li><b>Tool selection</b> <span class="bp-dim">Lock vs CAS vs concurrent collection vs per-resource</span></li><li><b>Trade-off narration</b> <span class="bp-dim">granularity, lock-ordering deadlock, optimistic vs pessimistic</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Arrives 3 ways: stated, asked, or self-raised — self-raise signals seniority</li><li>Single-threaded correct first, sync second — never thread-safe from line one</li><li>Name it: race condition, check-then-act (read free -&gt; write booked) not atomic</li><li>Critical section = smallest read-modify-write span; method-wide lock kills throughput</li><li>Pick tool: Lock, atomic CAS, concurrent collection, per-resource locks — GIL doesn't make check-then-act atomic</li><li>Deck 3 patterns: Singleton DCL manager, Strategy lock-vs-CAS, State AVAILABLE-&gt;HELD-&gt;BOOKED, Observer waitlist notify</li></ul>

</div>
</div>

<!--
Key points: Arrives 3 ways: stated, asked, or self-raised — self-raise signals seniority | Single-threaded correct first, sync second — never thread-safe from line one | Name it: race condition, check-then-act (read free -> write booked) not atomic | Critical section = smallest read-modify-write span; method-wide lock kills throughput | Pick tool: Lock, atomic CAS, concurrent collection, per-resource locks — GIL doesn't make check-then-act atomic | Deck 3 patterns: Singleton DCL manager, Strategy lock-vs-CAS, State AVAILABLE->HELD->BOOKED, Observer waitlist notify

Problem: Mid-level-and-up interviews probe whether your design survives concurrent access. The classic trap is check-then-act on shared mutable state ("seat is free, so book it"): two threads both pass the check and double-book. Candidates either ignore it, or over-correct by locking the whole method and tanking throughput.

Real-world: seat/ticket booking and inventory decrement · payment idempotency and double-charge guards

Gotcha: Don't lock the whole method — the teaching point is the small critical section. And don't trust the GIL: compound check-then-act still races; guard it explicitly.
-->

---

## Handling Concurrency Scenarios

<div class="bp-dim bp-mono text-sm mb-3">Interleave two threads to double-book a seat, then flip the lock and watch the critical section serialize.</div>

<SeatBookingRaceSim />

---
layout: default
class: section-slide
---

<div class="ghost-num">02</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 02</div>
  <h1>Games & Puzzles</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">state, rules, turns</span></div>
</div>

---

## Tic Tac Toe

<div class="bp-dim bp-mono text-sm mb-3">A 3x3 board where pluggable WinningStrategies detect victory and Observers update a shared scoreboard, so every new feature is a new class, never an edit.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class WinningStrategy(ABC):
    @abstractmethod
    def check_win(self, board, row, col, symbol): ...

class RowWinningStrategy(WinningStrategy):
    def check_win(self, board, row, col, symbol):
        return all(board.cell(row, c).symbol == symbol
                   for c in range(board.size))

class DiagonalWinningStrategy(WinningStrategy):
    def check_win(self, board, row, col, symbol):
        n = board.size
        main = all(board.cell(i, i).symbol == symbol for i in range(n))
        anti = all(board.cell(i, n-1-i).symbol == symbol for i in range(n))
        return main or anti          # anti-diag col = size-1-i

class Game:                          # owns Board, uses strategies+observers
    def make_move(self, row, col):
        with self._lock:
            if self.status != GameStatus.IN_PROGRESS:  # 1 reject if over
                raise InvalidMove("game over")
            if not self.board.is_empty(row, col):       # 2 validate
                raise InvalidMove("occupied")
            sym = self.current.symbol
            self.board.place(row, col, sym)             # 3 place
            if any(s.check_win(self.board, row, col, sym)  # 4 check wins
                   for s in self.strategies):
                self.status = (GameStatus.WINNER_X if sym is Symbol.X
                               else GameStatus.WINNER_O)
                return self._notify()                   # observers fire
            if self.board.is_full():                    # 5 draw
                self.status = GameStatus.DRAW
                return self._notify()
            self.idx = (self.idx + 1) % 2               # 6 switch turn
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Symbol / GameStatus</b> <span class="bp-dim">enums: cell value; one-way game state</span></li><li><b>Board</b> <span class="bp-dim">owns 9 Cells; place/is_empty/is_full + bounds, no rules</span></li><li><b>WinningStrategy</b> <span class="bp-dim">interface: check_win; Row/Column/Diagonal impls</span></li><li><b>GameObserver</b> <span class="bp-dim">interface: update on terminal; Scoreboard implements</span></li><li><b>Game</b> <span class="bp-dim">orchestrator: owns Board, iterates strategies, notifies</span></li><li><b>TicTacToeSystem</b> <span class="bp-dim">Singleton Facade: owns Scoreboard, wires games</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Split Board (grid: place/is_full/bounds) from Cell (one Symbol) by SRP — reusable, win-highlight home</li><li>Enums for safety: Symbol(X/O/EMPTY) + one-way GameStatus state machine, terminal states never revert</li><li>Strategy (Deck 3) for wins: Row/Column/Diagonal check_win; Game iterates list, FourCorners = +1 class</li><li>Observer (Deck 3) decouples game-end: Game notifies on terminal; Scoreboard records, Game unaware</li><li>Singleton + Facade (Deck 3): TicTacToeSystem owns Scoreboard, wires observers, hides Game/Board/Cell</li><li>make_move spine: reject-if-over -&gt; validate -&gt; place -&gt; check wins -&gt; draw -&gt; switch; lock it</li></ul>

</div>
</div>

<!--
Key points: Split Board (grid: place/is_full/bounds) from Cell (one Symbol) by SRP — reusable, win-highlight home | Enums for safety: Symbol(X/O/EMPTY) + one-way GameStatus state machine, terminal states never revert | Strategy (Deck 3) for wins: Row/Column/Diagonal check_win; Game iterates list, FourCorners = +1 class | Observer (Deck 3) decouples game-end: Game notifies on terminal; Scoreboard records, Game unaware | Singleton + Facade (Deck 3): TicTacToeSystem owns Scoreboard, wires observers, hides Game/Board/Cell | make_move spine: reject-if-over -> validate -> place -> check wins -> draw -> switch; lock it

Problem: Win detection has three rules (row, column, diagonal) plus future variants; the scoreboard must persist across games. Inline if-checks and direct scoreboard calls make Game a rigid god-class that you edit for every new rule or listener.

Real-world: web multiplayer game server (concurrent make_move on a shared Game) · grid-based games reusing Board: Connect Four, Battleship · pluggable rule engines where each rule is a Strategy · event listeners (analytics, replay recorder) added as Observers without touching the subject

Gotcha: Concurrency: without a lock on make_move, two web threads both read current_player_index=0, both place using the same symbol, and the turn counter wraps - corrupting the board. The lock makes each move atomic. Don't conflate WinningStrategy (checks wins) with the AI extension's MoveStrategy (picks moves) - two different Strategy uses.
-->

---

## Tic Tac Toe

<div class="bp-dim bp-mono text-sm mb-3">Play the board and watch every move flow through make_move while pluggable strategy chips fire and a decoupled Observer pushes the win to the Singleton scoreboard.</div>

<TicTacToeEngine />

---

## Snake & Ladder

<div class="bp-dim bp-mono text-sm mb-3">Model a turn-based board game where the board is just a position-to-position map, so one O(1) lookup resolves snakes and ladders identically.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC
from collections import deque
import random

class BoardEntity(ABC):
    def __init__(self, start, end):
        self.start, self.end = start, end

class Snake(BoardEntity):
    def __init__(self, start, end):
        if start <= end: raise ValueError("head must be above tail")
        super().__init__(start, end)

class Ladder(BoardEntity):
    def __init__(self, start, end):
        if start >= end: raise ValueError("bottom must be below top")
        super().__init__(start, end)

class Board:
    def __init__(self, size, entities):
        self.size = size
        self.jumps = {e.start: e.end for e in entities}
    def get_final_position(self, pos):
        return self.jumps.get(pos, pos)          # O(1), snake==ladder

class Game:                                      # Facade: callers use play()
    def take_turn(self, p):
        roll = self.dice.roll()
        nxt = p.position + roll
        if nxt > self.board.size: return          # overshoot -> skip
        if nxt == self.board.size:
            self.winner, self.status = p, "FINISHED"; return
        p.position = self.board.get_final_position(nxt)
        if roll == 6: self.take_turn(p)           # extra turn
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>GameStatus</b> <span class="bp-dim">enum: NOT_STARTED / RUNNING / FINISHED, no DRAW</span></li><li><b>Player</b> <span class="bp-dim">name + mutable position, starts at 0</span></li><li><b>BoardEntity / Snake / Ladder</b> <span class="bp-dim">base + fail-fast start vs end subclasses</span></li><li><b>Dice</b> <span class="bp-dim">configurable min/max, roll() returns random</span></li><li><b>Board</b> <span class="bp-dim">size + dict{start:end}; resolves both in one lookup</span></li><li><b>Game + Game.Builder</b> <span class="bp-dim">owns board/dice/player-deque; chained setters -&gt; validated build()</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>No cells stored: just dict{start:end}; get_final_position(p)=map.get(p,p) is O(1), snakes/ladders alike</li><li>BoardEntity base unifies Snake (start&gt;end) / Ladder (start&lt;end); ctor fail-fasts -&gt; bad config dies at build</li><li>Turn rotation = deque: pop front, take turn, append back; scales to any N, zero branching</li><li>Rules in take_turn: overshoot 100 skip; hit 100 win; else apply map; roll 6 -&gt; recursive extra (unbounded risk)</li><li>Builder (Deck-3) assembles Game via chained set_board/set_players/set_dice; build() validates all three</li><li>Game is a Facade (Deck-3): callers only play(); dice/board/queue/win-detect hidden behind one entry</li></ul>

</div>
</div>

<!--
Key points: No cells stored: just dict{start:end}; get_final_position(p)=map.get(p,p) is O(1), snakes/ladders alike | BoardEntity base unifies Snake (start>end) / Ladder (start<end); ctor fail-fasts -> bad config dies at build | Turn rotation = deque: pop front, take turn, append back; scales to any N, zero branching | Rules in take_turn: overshoot 100 skip; hit 100 win; else apply map; roll 6 -> recursive extra (unbounded risk) | Builder (Deck-3) assembles Game via chained set_board/set_players/set_dice; build() validates all three | Game is a Facade (Deck-3): callers only play(); dice/board/queue/win-detect hidden behind one entry

Problem: A 10x10 board with configurable snakes/ladders, N players in round-robin, dice 1-6 (roll-6 grants an extra turn), and exact-land-to-win. Naive designs store 100 cell objects and branch on "is this a snake or a ladder?" everywhere. The board has no per-cell content worth storing, and snake-vs-ladder is the same operation (jump start->end) with opposite direction, so the type split is noise.

Real-world: board-game engines / digital tabletop apps · round-robin scheduling with a player/job deque · rule-table lookups (position->effect maps) over branchy if/else chains

Gotcha: Recursive take_turn on a roll of 6 is unbounded: a streak of sixes can blow the stack. Cap consecutive sixes or loop instead of recurse, and note exact-land-to-win means overshoot skips rather than caps the position.
-->

---

## Snake & Ladder

<div class="bp-dim bp-mono text-sm mb-3">Play the board live: a token climbs ladders and slides down snakes via one map lookup you can watch light up.</div>

<SnakeLadderBoard />

---

## Minesweeper

<div class="bp-dim bp-mono text-sm mb-3">A grid of Cell state machines where the first click is always safe, mines are scattered after it, and revealing a zero-count cell floods outward to its numbered border.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from enum import Enum

class State(Enum): HIDDEN=0; REVEALED=1; FLAGGED=2

class Cell:
    def __init__(self): self.state=State.HIDDEN; self.mine=False; self.adj=0

class Board:
    def __init__(self, rows, cols, mines, place):
        self.rows, self.cols, self.mines, self.place = rows, cols, mines, place
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.armed = False; self.revealed = 0

    def reveal(self, r, c):                       # returns opened cells
        if not self.armed:                        # first click: defer + carve
            self.place(self, safe=(r, c)); self.armed = True
        cell = self.grid[r][c]
        if cell.state != State.HIDDEN: return []
        if cell.mine: cell.state = State.REVEALED; return [(r, c, "BOOM")]
        opened, q = [], [(r, c)]                   # iterative flood-fill
        while q:
            cr, cc = q.pop()
            cur = self.grid[cr][cc]
            if cur.state != State.HIDDEN: continue
            cur.state = State.REVEALED; self.revealed += 1; opened.append((cr, cc))
            if cur.adj == 0: q += self.neighbors(cr, cc)  # stop at numbered cells
        return opened

    def won(self): return self.revealed == self.rows*self.cols - self.mines
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Cell</b> <span class="bp-dim">State machine: is_mine + adjacent_count + HIDDEN/REVEALED/FLAGGED</span></li><li><b>Board</b> <span class="bp-dim">grid owner: reveal cascade, neighbor scan, derived won/lost</span></li><li><b>MinePlacementStrategy</b> <span class="bp-dim">scatters mines after first click, carves safe zone</span></li><li><b>BoardFactory</b> <span class="bp-dim">builds configured Board from Difficulty preset</span></li><li><b>Game</b> <span class="bp-dim">orchestrates turns + GameStatus IN_PROGRESS/WON/LOST</span></li><li><b>StatsTracker</b> <span class="bp-dim">Observer: rolls up games/wins/losses on game-over</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Cell State machine: HIDDEN -&gt; REVEALED (terminal) or HIDDEN &lt;-&gt; FLAGGED; flagged = reveal-immune (Deck-3 State)</li><li>Defer mines to first reveal via MinePlacementStrategy: carve safe zone, compute 0-8 counts (Strategy)</li><li>0-count reveal triggers iterative flood-fill (queue, not recursion); stops at numbers, no stack blow-up</li><li>Win/loss DERIVED each turn (revealed == total - mines, or mine revealed) — no desyncing flag</li><li>Difficulty presets (EASY/MEDIUM/HARD) are config from BoardFactory, not subclasses (Factory Method)</li><li>StatsTracker observes game-over: rolls up games/wins/losses (Observer)</li></ul>

</div>
</div>

<!--
Key points: Cell State machine: HIDDEN -> REVEALED (terminal) or HIDDEN <-> FLAGGED; flagged = reveal-immune (Deck-3 State) | Defer mines to first reveal via MinePlacementStrategy: carve safe zone, compute 0-8 counts (Strategy) | 0-count reveal triggers iterative flood-fill (queue, not recursion); stops at numbers, no stack blow-up | Win/loss DERIVED each turn (revealed == total - mines, or mine revealed) — no desyncing flag | Difficulty presets (EASY/MEDIUM/HARD) are config from BoardFactory, not subclasses (Factory Method) | StatsTracker observes game-over: rolls up games/wins/losses (Observer)

Problem: Players need a board that never blows up on the first click, auto-opens the obvious empty region, and reliably knows when the game is won or lost. The naive approach (place mines at construction, store a mutable won flag, recurse blindly) breaks first-click-safety, lets state desync, and stack-overflows on a 30x16 hard board.

Real-world: sweeping classic Minesweeper · any reveal-cascade grid puzzle (flood fill)

Gotcha: Placing mines at construction breaks first-click-safety, and a recursive cascade blows the stack on a 30x16 board - defer placement and flood iteratively, then derive win/loss instead of storing a flag that can desync.
-->

---

## Minesweeper

<div class="bp-dim bp-mono text-sm mb-3">Play it live, flip on Reveal internals, and watch the first click carve a safe zone before mines scatter and the cascade floods out.</div>

<MinesweeperBoard />

---

## Chess

<div class="bp-dim bp-mono text-sm mb-3">A polymorphic rules engine: six piece subclasses each generate their own moves, then a referee layer filters them by simulating the board to reject any move that leaves your king in check.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Piece(ABC):
    def __init__(self, color): self.color, self.moved = color, False
    @abstractmethod
    def get_moves(self, board, src): ...   # Strategy hook

class Bishop(Piece):
    DIRS = [(1,1),(1,-1),(-1,1),(-1,-1)]
    def get_moves(self, board, src):
        moves = []
        for dr, dc in self.DIRS:           # ray-walk until blocked
            r, c = src.r+dr, src.c+dc
            while board.in_bounds(r, c):
                tgt = board[r][c]
                if tgt is None: moves.append((r, c))
                else:
                    if tgt.color != self.color: moves.append((r, c))
                    break                  # sliding pieces need path clearance
                r, c = r+dr, c+dc
        return moves

class RuleEngine:
    def legal_moves(self, board, src):
        piece = board[src.r][src.c]
        cands = piece.get_moves(board, src)
        return [m for m in cands if not self._leaves_king_in_check(board, src, m)]

    def _leaves_king_in_check(self, board, src, dst):
        undo = board.apply(src, dst)        # simulate on the real board
        bad = board.is_attacked(board.king_sq(src_color := board[dst].color))
        board.revert(undo)                  # roll back -> Move is reversible
        return bad
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Piece</b> <span class="bp-dim">abstract; declares get_moves — Strategy hook</span></li><li><b>King/Queen/Rook/Bishop/Knight/Pawn</b> <span class="bp-dim">concrete pieces; sliders ray-walk, Pawn stateful</span></li><li><b>Board</b> <span class="bp-dim">8x8 grid; apply/revert Move, is_attacked, king_sq</span></li><li><b>Move</b> <span class="bp-dim">from, to, piece, captured, flags — reversible Command + history unit</span></li><li><b>RuleEngine / MoveValidator</b> <span class="bp-dim">filters via simulate-then-check; detects check/mate/stalemate</span></li><li><b>Game</b> <span class="bp-dim">alternates turns, applies moves, drives GameState</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Two-layer validation: piece-local geometry + path vs global 'leaves king in check?'</li><li>Each Piece computes own moves (Strategy + Template Method) — Open/Closed, engine untouched</li><li>Check = simulate on board copy, scan enemy moves for king square, revert. Mate = check + 0 moves; stalemate = no check + 0 moves</li><li>Pins free: simulate-then-check already rejects king-exposing moves</li><li>Special moves stateful: castling reads flags + attacks, en passant prev Move, promotion on back rank</li><li>Move (from, to, piece, captured, flags) = reversible Command — history, en passant, undo</li></ul>

</div>
</div>

<!--
Key points: Two-layer validation: piece-local geometry + path vs global 'leaves king in check?' | Each Piece computes own moves (Strategy + Template Method) — Open/Closed, engine untouched | Check = simulate on board copy, scan enemy moves for king square, revert. Mate = check + 0 moves; stalemate = no check + 0 moves | Pins free: simulate-then-check already rejects king-exposing moves | Special moves stateful: castling reads flags + attacks, en passant prev Move, promotion on back rank | Move (from, to, piece, captured, flags) = reversible Command — history, en passant, undo

Problem: Chess has six pieces with different movement geometry, stateful special moves (castling, en passant, promotion), and global constraints (you cannot leave your own king in check) that no single piece can decide alone. Conflating piece-local geometry with global legality produces a buggy validator and a god-class board.

Real-world: online chess engines (lichess/chess.com move validation) · game-replay and analysis tooling driven by move history · any turn-based board game with per-actor move rules and a global win-condition checker

Gotcha: Sliding pieces (Bishop/Rook/Queen) must stop at the first blocker — path clearance — while the Knight jumps. Forgetting clearance, or validating geometry without the simulate-then-check pass (which also handles pins for free), is the classic interview failure.
-->

---

## Chess

<div class="bp-dim bp-mono text-sm mb-3">Click a piece and watch the Strategy layer emit moves while the referee greys out the ones that would leave your king in check.</div>

<ChessBoardPlayground />

---
layout: default
class: section-slide
---

<div class="ghost-num">03</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 03</div>
  <h1>Data Structures & Search</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">the right structure wins</span></div>
</div>

---

## LRU Cache

<div class="bp-dim bp-mono text-sm mb-3">Pair a dict with a doubly linked list so lookup, recency-bump, and eviction all stay O(1) — the textbook lesson that the right data structures beat fancy patterns.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
class Node:
    def __init__(self, key, value):
        self.key, self.value = key, value
        self.prev = self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head, self.tail = Node(None, None), Node(None, None)
        self.head.next, self.tail.prev = self.tail, self.head

    def add_first(self, n):           # insert after dummy head (MRU)
        n.prev, n.next = self.head, self.head.next
        self.head.next.prev = self.head.next = n

    def remove(self, n):              # O(1): splice neighbours
        n.prev.next, n.next.prev = n.next, n.prev

    def move_to_front(self, n):
        self.remove(n); self.add_first(n)

    def remove_last(self):            # node just before dummy tail (LRU)
        if self.tail.prev is self.head: return None
        last = self.tail.prev; self.remove(last); return last

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map, self.list = capacity, {}, DoublyLinkedList()

    def get(self, key):
        node = self.map.get(key)
        if node is None: return None
        self.list.move_to_front(node)
        return node.value

    def put(self, key, value):
        if key in self.map:
            node = self.map[key]; node.value = value
            self.list.move_to_front(node); return
        if len(self.map) == self.cap:
            lru = self.list.remove_last()
            if lru: del self.map[lru.key]   # node.key needed here
        node = Node(key, value)
        self.list.add_first(node); self.map[key] = node
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Node</b> <span class="bp-dim">key, value, prev, next; stores own key</span></li><li><b>DoublyLinkedList</b> <span class="bp-dim">add_first, remove, move_to_front, remove_last — O(1)</span></li><li><b>dict key-&gt;Node</b> <span class="bp-dim">O(1) node-pointer lookup</span></li><li><b>LRUCache</b> <span class="bp-dim">capacity, map, list; coordinates both, evicts</span></li><li><b>Dummy head/tail sentinels</b> <span class="bp-dim">Null Object, erase edge cases</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Two O(1) needs: key-&gt;node lookup (dict) + recency order (DLL); compose both</li><li>Dict maps key -&gt; *node ref*, not value -&gt; jump straight to node, no traversal</li><li>Head = MRU, tail = LRU; access = move_to_front, overflow = remove_last, both O(1)</li><li>Dummy head/tail sentinels (Null Object) kill empty/first/last edge cases</li><li>Node stores own key so eviction can do del map[node.key]</li><li>Composition + Encapsulation, NO Strategy/Observer/Singleton; one Lock for thread-safety</li></ul>

</div>
</div>

<!--
Key points: Two O(1) needs: key->node lookup (dict) + recency order (DLL); compose both | Dict maps key -> *node ref*, not value -> jump straight to node, no traversal | Head = MRU, tail = LRU; access = move_to_front, overflow = remove_last, both O(1) | Dummy head/tail sentinels (Null Object) kill empty/first/last edge cases | Node stores own key so eviction can do del map[node.key] | Composition + Encapsulation, NO Strategy/Observer/Singleton; one Lock for thread-safety

Problem: A fixed-size cache must answer get/put in O(1) AND know which entry is least recently used so it can evict on overflow. A dict alone gives O(1) lookup but no order, so eviction degrades to O(n); a plain list gives order but O(n) to find a node. Neither structure alone suffices.

Real-world: CPU/page caches and OS memory management · CDN and web-server response caches · functools.lru_cache (Python's stdlib decorator) · database buffer pools

Gotcha: Forgetting to store the key in the Node makes eviction O(n) — you can't tell the dict which key to delete. Also: get must count as usage and bump to MRU, not just read.
-->

---

## LRU Cache

<div class="bp-dim bp-mono text-sm mb-3">Fire put/get on a capacity-3 cache and watch move_to_front slide nodes and a capacity overflow evict the tail.</div>

<LruCacheBoard />

---

## Bloom Filter

<div class="bp-dim bp-mono text-sm mb-3">A probabilistic membership filter that trades a tunable false-positive rate for massive space savings by fanning each element across k hash-derived bits.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import math, threading

class BloomFilterConfig:
    def __init__(self, n: int, p: float):
        self.bit_array_size = math.ceil(-(n * math.log(p)) / (math.log(2) ** 2))
        self.num_hash_functions = max(1, round((self.bit_array_size / n) * math.log(2)))

class BloomFilter:                       # coordinator; Builder sets n, p, strategy
    def __init__(self, cfg, strategy):
        self._cfg, self._strategy = cfg, strategy
        self._bits = [False] * cfg.bit_array_size
        self._lock = threading.Lock()

    def add(self, element: str) -> None:
        with self._lock:                 # all k bits set atomically
            for seed in range(self._cfg.num_hash_functions):
                self._bits[self._strategy.hash(element, seed, len(self._bits))] = True

    def might_contain(self, element: str) -> bool:
        with self._lock:
            for seed in range(self._cfg.num_hash_functions):
                if not self._bits[self._strategy.hash(element, seed, len(self._bits))]:
                    return False         # one 0 => definitely not present
            return True                  # all set => maybe present
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>HashStrategy</b> <span class="bp-dim">hash(element, seed, size) -&gt; bit; Strategy pattern</span></li><li><b>MurmurHashStrategy / FNVHashStrategy / DJB2HashStrategy</b> <span class="bp-dim">interchangeable algos</span></li><li><b>BitArray</b> <span class="bp-dim">fixed-size bits; set/get/clear</span></li><li><b>BloomFilterConfig</b> <span class="bp-dim">immutable; computes m, k from n, p</span></li><li><b>BloomFilter</b> <span class="bp-dim">coordinator: BitArray + config + HashStrategy, locks ops</span></li><li><b>BloomFilter.Builder</b> <span class="bp-dim">required n, optional rate/strategy; validates</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Asymmetric: maybe present (false positive), never false negative</li><li>add -&gt; set k bits; might_contain -&gt; all k set, early-return False on 0</li><li>k hashes = one algo, seeds 0..k-1 make them independent (Strategy, Deck 3)</li><li>Params computed: m = -(n*ln p)/(ln2)^2, k = (m/n)*ln2; 1M @ 1% -&gt; ~1.14MB, 7 hashes</li><li>Layers: HashStrategy, BitArray, Config (immutable), BloomFilter, Builder (Deck 3)</li><li>One mutex on add/might_contain -&gt; atomic k bits, no half-written false negative; no delete</li></ul>

</div>
</div>

<!--
Key points: Asymmetric: maybe present (false positive), never false negative | add -> set k bits; might_contain -> all k set, early-return False on 0 | k hashes = one algo, seeds 0..k-1 make them independent (Strategy, Deck 3) | Params computed: m = -(n*ln p)/(ln2)^2, k = (m/n)*ln2; 1M @ 1% -> ~1.14MB, 7 hashes | Layers: HashStrategy, BitArray, Config (immutable), BloomFilter, Builder (Deck 3) | One mutex on add/might_contain -> atomic k bits, no half-written false negative; no delete

Problem: Tracking 10M URLs in a HashSet for a safe-browsing check costs hundreds of MB. We want the same "is this in the set?" answer using a fraction of the space, accepting a rare "maybe" we never lose a "yes".

Real-world: URL blacklist / safe-browsing membership check · DB read-path filter to skip expensive disk lookups for absent keys

Gotcha: Standard Bloom filters cannot delete: clearing shared bits could yank bits a still-present element relies on, breaking the no-false-negatives guarantee. Use a Counting Bloom filter (out of scope) when deletion is required.
-->

---

## Bloom Filter

<div class="bp-dim bp-mono text-sm mb-3">Drive add/check on a live 32-bit board, force a false positive, and slide k and FP-rate to watch m recompute and collisions shrink.</div>

<BloomFilterLab />

---

## Search Autocomplete (Typeahead)

<div class="bp-dim bp-mono text-sm mb-3">A Trie walks the prefix once in O(L), then a pluggable ranking Strategy picks the top-N completions from its subtree.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod
from heapq import nlargest

class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_word = False
        self.frequency = 0

class RankingStrategy(ABC):
    @abstractmethod
    def rank(self, cands, k): ...  # -> [(word, freq)]

class FrequencyRanking(RankingStrategy):
    def rank(self, cands, k):
        return nlargest(k, cands, key=lambda c: (c[1], c[0]))

class AlphabeticalRanking(RankingStrategy):
    def rank(self, cands, k):
        return sorted(cands)[:k]

class AutocompleteSystem:                      # Facade
    def __init__(self, ranker, limit=10):
        self.root, self.ranker, self.limit = TrieNode(), ranker, limit

    def insert(self, word):
        node = self.root
        for ch in word.lower():
            node = node.children.setdefault(ch, TrieNode())
        node.is_word, node.frequency = True, node.frequency + 1

    def suggest(self, prefix, k=None):
        node = self.root
        for ch in prefix.lower():              # O(L) walk
            if ch not in node.children:
                return []
            node = node.children[ch]
        cands = self._collect(node, prefix.lower())
        return self.ranker.rank(cands, k or self.limit)

    def _collect(self, node, path):            # DFS / Iterator
        out = [(path, node.frequency)] if node.is_word else []
        for ch, child in node.children.items():
            out += self._collect(child, path + ch)
        return out
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>TrieNode</b> <span class="bp-dim">children map + is_word + frequency; Composite node</span></li><li><b>AutocompleteSystem</b> <span class="bp-dim">Facade: owns Trie root, ranker, default limit</span></li><li><b>RankingStrategy</b> <span class="bp-dim">ABC: swappable ranking contract</span></li><li><b>FrequencyRanking / AlphabeticalRanking</b> <span class="bp-dim">concrete Strategies over candidates</span></li><li><b>insert() / suggest()</b> <span class="bp-dim">write bumps freq; read O(L) walk then rank</span></li><li><b>_collect()</b> <span class="bp-dim">DFS Iterator over completions under prefix</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Trie spine: node per char, O(L) walk to prefix, DFS-collect subtree -- size-independent, shared prefixes save memory</li><li>Ranking = Strategy (Deck 3): Alphabetical/Frequency swappable, Trie untouched</li><li>Frequency learned on insert: bump counter at terminal node; node holds word + freq</li><li>Top-N bounded: heapq.nlargest(k) partial sort, not full subtree sort</li><li>AutocompleteSystem = Facade over Trie + ranker + limit; children form Composite, DFS = Iterator</li><li>Normalize up-front: lowercase insert/query, English-only; delete/update out of scope</li></ul>

</div>
</div>

<!--
Key points: Trie spine: node per char, O(L) walk to prefix, DFS-collect subtree –– size-independent, shared prefixes save memory | Ranking = Strategy (Deck 3): Alphabetical/Frequency swappable, Trie untouched | Frequency learned on insert: bump counter at terminal node; node holds word + freq | Top-N bounded: heapq.nlargest(k) partial sort, not full subtree sort | AutocompleteSystem = Facade over Trie + ranker + limit; children form Composite, DFS = Iterator | Normalize up-front: lowercase insert/query, English-only; delete/update out of scope

Problem: As a user types, suggest the best-matching completions in real time. A flat list or HashMap-of-prefixes scales with dictionary size; we need prefix lookup that costs O(prefix length) regardless of how many words exist, plus ranking the interviewer can reconfigure (alphabetical vs frequency) and a configurable result limit.

Real-world: Google / YouTube search box typeahead · IDE code completion · e-commerce product search suggestions

Gotcha: Don't fully sort the whole subtree –– it can be huge; collect then heapq.nlargest(k). Per-node cached top-k is a precompute trade-off; mention it as an extension but keep the core simple.
-->

---

## Search Autocomplete (Typeahead)

<div class="bp-dim bp-mono text-sm mb-3">Type a prefix, watch the O(L) Trie walk and subtree DFS, then toggle the ranking Strategy to re-rank in place.</div>

<TrieTypeaheadExplorer />

---

## Simple Search Engine

<div class="bp-dim bp-mono text-sm mb-3">Flip the document-to-word map inside out into an inverted index, then rank the hits by term frequency.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import math, re
from collections import defaultdict

class Tokenizer:
    def tokenize(self, text):
        return re.findall(r"[a-z0-9]+", text.lower())

class InvertedIndex:
    def __init__(self):
        self.postings = defaultdict(lambda: defaultdict(int))  # term->{doc:freq}
        self.docs = set()

    def add(self, doc_id, terms):
        self.docs.add(doc_id)
        for t in terms:
            self.postings[t][doc_id] += 1

class TfIdfRanking:                      # Strategy: swap for TermFrequencyRanking
    def score(self, idx, term, doc_id):
        tf = idx.postings[term][doc_id]
        idf = math.log(len(idx.docs) / (1 + len(idx.postings[term])))
        return tf * idf

class SearchEngine:                      # Facade over tokenizer + index + ranker
    def __init__(self, ranking):
        self.tok, self.idx, self.rank = Tokenizer(), InvertedIndex(), ranking

    def index(self, doc_id, text):
        self.idx.add(doc_id, self.tok.tokenize(text))

    def search(self, query):
        scores = defaultdict(float)
        for term in self.tok.tokenize(query):
            for doc_id in self.idx.postings.get(term, {}):
                scores[doc_id] += self.rank.score(self.idx, term, doc_id)
        return sorted(scores, key=scores.get, reverse=True)
```

</div>
<div class="min-w-0 kpcol">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Tokenizer</b> <span class="bp-dim">text -&gt; lowercase term stream; shared</span></li><li><b>InvertedIndex</b> <span class="bp-dim">term -&gt; postings docId:freq; O(1)-lookup core</span></li><li><b>Posting</b> <span class="bp-dim">one docId:freq cell in postings list</span></li><li><b>RankingStrategy</b> <span class="bp-dim">pluggable scorer: TermFrequency vs TfIdf</span></li><li><b>SearchEngine</b> <span class="bp-dim">Facade over tokenizer + index + strategy</span></li><li><b>SearchResult</b> <span class="bp-dim">docId + relevance score, returned sorted</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Inverted index: term -&gt; postings (docId, freq); lookup O(1), no full scan</li><li>One Tokenizer for index + query (split + lowercase); shared vocabulary</li><li>Ranking = pluggable Strategy: swap TF for TF-IDF/BM25, index untouched</li><li>SearchEngine is a Facade over tokenizer + index + strategy; walk postings via Iterator</li><li>Multi-word: union/intersect postings, then strategy scores + sorts descending</li><li>Non-goals: in-memory, exact case-insensitive, no crawl/stem/stop-word/fuzzy</li></ul>

</div>
</div>

<!--
Key points: Inverted index: term -> postings (docId, freq); lookup O(1), no full scan | One Tokenizer for index + query (split + lowercase); shared vocabulary | Ranking = pluggable Strategy: swap TF for TF-IDF/BM25, index untouched | SearchEngine is a Facade over tokenizer + index + strategy; walk postings via Iterator | Multi-word: union/intersect postings, then strategy scores + sorts descending | Non-goals: in-memory, exact case-insensitive, no crawl/stem/stop-word/fuzzy

Problem: Searching a corpus by scanning every document on each query is O(corpus) per lookup and does not scale. We need fast keyword lookup, case-insensitive matching, and relevance ranking, while keeping ranking swappable and the wiring hidden behind a clean facade.

Real-world: Elasticsearch / Lucene segment indexes · in-app full-text document search

Gotcha: Forgetting to reuse one tokenizer: if query and corpus normalize differently, exact matches silently miss. Also, term-frequency alone over-rewards long documents - reach for TF-IDF/BM25 once relevance matters.
-->

---

## Simple Search Engine

<div class="bp-dim bp-mono text-sm mb-3">Index preset docs, fire queries, watch postings light up and result bars re-rank as you toggle TF vs TF-IDF.</div>

<InvertedIndexSearchBoard />

---
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

---
layout: end
---

<div class="text-center">
  <div class="bp-eyebrow mb-3">END OF DECK 4</div>
  <h1>Questions?</h1>
  <div class="bp-dim bp-mono mt-3">Foundations &rarr; Principles &rarr; Patterns &rarr; Interviews</div>
</div>
