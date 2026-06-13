#!/usr/bin/env python3
"""Author the 7 paywalled 'Additional Patterns' specs from scratch (original content)
and write tools/deck3_additional_specs.json in the same schema as deck3_specs.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent   # lld-slides/tools

SPECS = [
{
 "slug": "repository", "title": "Repository", "category": "Additional Patterns",
 "oneLiner": "Hide data access behind a collection-like interface so the domain never sees SQL or an ORM.",
 "problem": "When services build queries inline, persistence details leak everywhere and the domain becomes impossible to test without a database. A Repository gives the domain one in-memory-looking API and keeps storage swappable.",
 "keyPoints": [
   "Domain depends on a repository interface, not on SQL or a driver",
   "Swap the backing store (memory, SQL, Mongo) without touching callers",
   "Tests run against an in-memory repo — no database needed",
   "One place owns mapping rows to objects",
 ],
 "python": "from abc import ABC, abstractmethod\n\n\nclass OrderRepository(ABC):\n    @abstractmethod\n    def add(self, order): ...\n    @abstractmethod\n    def get(self, oid): ...\n\n\nclass InMemoryOrders(OrderRepository):\n    def __init__(self):\n        self._db = {}\n    def add(self, order):\n        self._db[order.id] = order\n    def get(self, oid):\n        return self._db.get(oid)\n\n\nclass OrderService:\n    def __init__(self, repo: OrderRepository):\n        self.repo = repo            # depends on the interface\n    def place(self, order):\n        self.repo.add(order)        # no SQL in the domain",
 "participants": ["Repository (interface, e.g. OrderRepository)", "ConcreteRepository (InMemoryOrders / SqlOrders)", "Client (OrderService, talks to the interface)", "Entity (Order)"],
 "diagram": "classDiagram\n  class OrderRepository {\n    <<interface>>\n    +add(order)\n    +get(oid)\n  }\n  class InMemoryOrders\n  class OrderService\n  OrderRepository <|.. InMemoryOrders\n  OrderService --> OrderRepository",
 "diagramType": "classDiagram",
 "interactive": {
   "componentName": "RepositorySwapStore",
   "idea": "The domain calls the same repository interface; swapping the backing store changes where data lives, never the caller.",
   "mechanic": "Layout: a Domain box on the left issuing two fixed call lines (repo.add(order), repo.get(42)), a Repository interface node in the middle, and a backing-store panel on the right. A segmented toggle Store [InMemory | SQL | Mongo] picks the concrete store; the store panel relabels (dict / TABLE orders / collection orders) but the Domain box and its call lines never change, with a pinned 'domain edits: 0' badge. Save animates a token from Domain along the wire into the active store, where a row '#42' appears with an insert flash; Fetch sends a token to the store and a return token carries '#42' back to the Domain which shows the loaded order. Switching the store re-skins the store panel with a short 'same interface, different backend' caption. Reset clears rows.",
 },
 "realWorld": ["Spring Data / JPA repositories", "Django's ORM manager and the repository layer on top of it", "SQLAlchemy session wrapped in a domain repository"],
 "gotcha": "Don't let the repository balloon into a god-object with a method per query; keep it focused on one aggregate, and avoid leaking ORM query objects back through the interface.",
},
{
 "slug": "mvc", "title": "MVC", "category": "Additional Patterns",
 "oneLiner": "Split a UI into Model (data), View (presentation), and Controller (input) so each owns exactly one job.",
 "problem": "When data, rendering, and input handling tangle together, every change risks the others and nothing is reusable. MVC routes input one way — Controller to Model to View — so concerns stay separate.",
 "keyPoints": [
   "Model holds state and rules; it never draws",
   "View renders the model; it never mutates it",
   "Controller turns input into model updates",
   "Model notifies views on change (observer under the hood)",
 ],
 "python": "class Model:\n    def __init__(self):\n        self.count = 0\n        self._views = []\n    def attach(self, view):\n        self._views.append(view)\n    def increment(self):\n        self.count += 1\n        for v in self._views:\n            v.render(self.count)\n\n\nclass View:\n    def render(self, count):\n        print(f\"[View] count = {count}\")\n\n\nclass Controller:\n    def __init__(self, model):\n        self.model = model\n    def on_click(self):\n        self.model.increment()      # input -> model",
 "participants": ["Model (state + notify)", "View (render only)", "Controller (input -> model)", "User"],
 "diagram": "classDiagram\n  class Model\n  class View\n  class Controller\n  Controller --> Model : updates\n  Model --> View : notifies\n  View --> Controller : input",
 "diagramType": "classDiagram",
 "interactive": {
   "componentName": "MvcRoundTrip",
   "idea": "Input flows Controller to Model to View in a one-way loop; each part owns one job and never reaches into the others.",
   "mechanic": "Three labeled columns: View (shows 'count = N' plus a +1 button), Controller (on_click), Model (count, observers). Each node has idle / active states. Clicking +1 (or Step) runs a round-trip token: View emits an input token to Controller (lights 'handle'), Controller to Model (lights 'mutate: count++'), Model fans a notify token back to View (lights 'render') and the count increments; each hop ~450ms with a pulse on the touched node. Play auto-fires three clicks. A 'show data flow' toggle draws the three directional arrows (View to Controller input, Controller to Model command, Model to View notify) so the one-way cycle is explicit. Reset sets count to 0.",
 },
 "realWorld": ["Django and Rails (MVC / MVT web stacks)", "iOS UIKit view controllers", "classic Swing / desktop UIs"],
 "gotcha": "Beware the 'fat controller' or 'massive view controller' where logic creeps in; keep business rules in the model and presentation in the view.",
},
{
 "slug": "dependency-injection", "title": "Dependency Injection", "category": "Additional Patterns",
 "oneLiner": "Hand a class its dependencies from outside instead of constructing them inside, so they can be swapped.",
 "problem": "A class that news-up its own collaborators is welded to them — you can't substitute a fake in a test or a different implementation in production. Injecting dependencies makes the seam explicit and swappable.",
 "keyPoints": [
   "Pass collaborators in (constructor/setter); don't build them inside",
   "Depend on an abstraction, not a concrete class",
   "Swap real for fake to test in isolation",
   "A container or composition root wires the graph once",
 ],
 "python": "from abc import ABC, abstractmethod\n\n\nclass Mailer(ABC):\n    @abstractmethod\n    def send(self, to, body): ...\n\n\nclass SmtpMailer(Mailer):\n    def send(self, to, body):\n        print(f\"SMTP -> {to}\")\n\n\nclass FakeMailer(Mailer):           # swap in for tests\n    def __init__(self):\n        self.sent = []\n    def send(self, to, body):\n        self.sent.append(to)\n\n\nclass Signup:\n    def __init__(self, mailer: Mailer):   # injected, not constructed\n        self.mailer = mailer\n    def register(self, email):\n        self.mailer.send(email, \"welcome\")",
 "participants": ["Service (depends on an abstraction)", "Dependency interface (Mailer)", "Real / Fake implementations", "Injector / composition root"],
 "diagram": "classDiagram\n  class Mailer {\n    <<interface>>\n    +send(to, body)\n  }\n  class SmtpMailer\n  class FakeMailer\n  class Signup\n  Mailer <|.. SmtpMailer\n  Mailer <|.. FakeMailer\n  Signup --> Mailer",
 "diagramType": "classDiagram",
 "interactive": {
   "componentName": "DependencyInjector",
   "idea": "A dependency built inside a class is welded in; injected from outside, the same slot accepts a real or a fake at will.",
   "mechanic": "A Service box (Signup) with one dependency slot labeled mailer, and a primary toggle Wiring [new inside | injected]. NEW-INSIDE: the slot shows 'SmtpMailer()' welded with a lock glyph, the external provider chips are greyed and unclickable, and a red 'hard to test' tag shows. INJECTED: the lock opens, three provider chips outside the Service become active — SmtpMailer, FakeMailer, NullMailer — and clicking one plugs it into the slot (slot relabels, a wire from provider to slot lights). A 'register(\"a@b.com\")' Run button fires: injected+Smtp shows 'SMTP -> a@b.com', injected+Fake shows 'captured: [a@b.com] (no real email)' to prove isolation, new-inside always hits SMTP. A pinned 'Service code changed: 0' counter underscores the class is never edited. Reset returns to new-inside.",
 },
 "realWorld": ["Spring's IoC container", "Angular's injector", "pytest fixtures / FastAPI Depends"],
 "gotcha": "DI is a technique, not a framework requirement; over-using a magic container can hide the object graph. For small programs, plain constructor injection is enough.",
},
{
 "slug": "specification", "title": "Specification", "category": "Additional Patterns",
 "oneLiner": "Wrap a business rule in a small predicate object you can combine with and / or / not.",
 "problem": "Validation and selection rules duplicated across queries, UI, and services drift out of sync. A Specification captures one rule as a reusable object, and composes with others instead of copy-pasting boolean logic.",
 "keyPoints": [
   "Each rule is an object with is_satisfied(item)",
   "Compose with and / or / not into bigger rules",
   "Reuse the same spec for filtering, validation, and queries",
   "Name the rule once; read it like a sentence",
 ],
 "python": "from abc import ABC, abstractmethod\n\n\nclass Spec(ABC):\n    @abstractmethod\n    def is_satisfied(self, item): ...\n    def __and__(self, other):\n        return AndSpec(self, other)\n\n\nclass AndSpec(Spec):\n    def __init__(self, a, b):\n        self.a, self.b = a, b\n    def is_satisfied(self, item):\n        return self.a.is_satisfied(item) and self.b.is_satisfied(item)\n\n\nclass IsActive(Spec):\n    def is_satisfied(self, u):\n        return u.active\n\n\nclass IsPremium(Spec):\n    def is_satisfied(self, u):\n        return u.tier == \"premium\"\n\n\nrule = IsActive() & IsPremium()\n# [u for u in users if rule.is_satisfied(u)]",
 "participants": ["Specification (interface, is_satisfied)", "Leaf specs (IsActive, IsPremium)", "Composite specs (And / Or / Not)", "Candidate item"],
 "diagram": "classDiagram\n  class Spec {\n    <<interface>>\n    +is_satisfied(item)\n  }\n  class IsActive\n  class IsPremium\n  class AndSpec\n  Spec <|.. IsActive\n  Spec <|.. IsPremium\n  Spec <|.. AndSpec\n  AndSpec --> Spec",
 "diagramType": "classDiagram",
 "interactive": {
   "componentName": "SpecificationComposer",
   "idea": "Business rules are tiny predicate objects; compose them with AND / OR / NOT and the live filter updates instantly.",
   "mechanic": "Top: a builder strip of three spec chips — isActive, isPremium, notBanned — each a toggle (on/off) with an AND/OR connector control between them and a NOT toggle on notBanned. The composed predicate renders live as text, e.g. 'isActive AND isPremium AND NOT banned'. Below: a list of 5 user cards, each showing attributes (active?, tier, banned?). As specs toggle, every card re-evaluates with a ~150ms stagger: satisfying cards turn solid green with a check, failing cards dim and label the first failing clause. A 'matches: K / 5' counter updates. Switching a connector between AND and OR re-filters and recolors. Reset turns all specs on.",
 },
 "realWorld": ["Domain-Driven Design specification objects", "rule engines / eligibility checks", "query builders that AND/OR criteria"],
 "gotcha": "For a single trivial check a plain function is simpler; reach for Specification when rules are reused, combined, or need to be named and tested on their own.",
},
{
 "slug": "game-loop", "title": "Game Loop", "category": "Additional Patterns",
 "oneLiner": "Run forever: process input, update the world by elapsed time, render — decoupled from wall-clock speed.",
 "problem": "If game logic is driven by the rendering rate, the world runs faster on fast machines and stutters on slow ones. A game loop separates 'how fast we draw' from 'how far time advanced', keeping play consistent.",
 "keyPoints": [
   "One loop: input -> update(dt) -> render, repeating",
   "Update by elapsed time (dt), not by frame count",
   "Rendering rate can vary; simulation stays stable",
   "A fixed timestep catches up with extra updates",
 ],
 "python": "import time\n\n\nclass Game:\n    def __init__(self):\n        self.running = True\n        self.x = 0\n    def process_input(self): ...\n    def update(self, dt):\n        self.x = (self.x + 1) % 10\n    def render(self):\n        print(f\"frame: x={self.x}\")\n    def run(self):\n        last = time.time()\n        while self.running:\n            now = time.time()\n            dt = now - last\n            last = now\n            self.process_input()\n            self.update(dt)\n            self.render()",
 "participants": ["Game loop (the while)", "Input stage", "Update stage (advances by dt)", "Render stage"],
 "diagram": "flowchart LR\n  I[process_input] --> U[update by dt]\n  U --> R[render]\n  R --> I",
 "diagramType": "flowchart",
 "interactive": {
   "componentName": "GameLoopTicker",
   "idea": "One loop forever: process input, update the world by dt, render — decoupled from wall-clock so play stays smooth.",
   "mechanic": "Left: a small play field with a dot entity that steps on every update, bouncing within a track. Center: a three-phase cycle drawn as nodes input -> update -> render with a token advancing one node per ~120ms tick; completing render increments a frame counter. Controls: Play (auto-runs the loop so the token cycles and the dot animates), Pause, Step (one full tick), Reset. A 'fixed timestep' toggle: when ON, a deliberately slow frame fires two update nodes before one render with a 'catch-up' badge, showing updates are time-based not frame-based. Live readouts: frames N, updates M. The loop visibly never stops until Pause.",
 },
 "realWorld": ["every game engine (Unity, Unreal, Godot main loop)", "physics simulations", "animation / render loops (requestAnimationFrame)"],
 "gotcha": "A naive loop that updates once per render couples simulation to frame rate; use a fixed timestep (or multiply by dt) so behavior is the same on fast and slow machines.",
},
{
 "slug": "thread-pool", "title": "Thread Pool", "category": "Additional Patterns",
 "oneLiner": "Keep a fixed crew of worker threads pulling tasks from a shared queue instead of spawning one per task.",
 "problem": "Spawning a thread per task is expensive and unbounded — thousands of tasks can exhaust the machine. A thread pool reuses a fixed number of workers and queues the overflow, capping concurrency.",
 "keyPoints": [
   "A fixed set of workers pulls from one task queue",
   "Bounded concurrency: at most N run at once",
   "Reuse threads — no per-task create/destroy cost",
   "Extra work waits in the queue, applying back-pressure",
 ],
 "python": "from concurrent.futures import ThreadPoolExecutor\nimport time\n\n\ndef work(n):\n    time.sleep(0.1)         # pretend it is slow\n    return n * n\n\n\n# a fixed crew of 3 threads, shared queue under the hood\nwith ThreadPoolExecutor(max_workers=3) as pool:\n    futures = [pool.submit(work, i) for i in range(8)]\n    for f in futures:\n        print(f.result())\n# 8 tasks submitted; only 3 run at once, the rest queue",
 "participants": ["Thread pool / executor", "Worker threads (fixed N)", "Task queue", "Client (submits tasks)"],
 "diagram": "flowchart LR\n  C[submit] --> Q[(task queue)]\n  Q --> W1[worker 1]\n  Q --> W2[worker 2]\n  Q --> W3[worker 3]",
 "diagramType": "flowchart",
 "interactive": {
   "componentName": "ThreadPoolDispatcher",
   "idea": "A fixed crew of workers pulls tasks from a shared queue; only N run at once while the rest wait in line.",
   "mechanic": "Layout: a Task queue column on the left (FIFO of pending task chips T1..Tn), a pool of exactly 3 Worker lanes in the middle (each idle, or running a task with a shrinking progress bar), and a Done tray on the right. Controls: 'submit task' (enqueues one chip), 'submit 5', Play/Pause (workers auto-pull), Step, Reset. On each pull an idle worker grabs the front queue chip (it slides into the lane), runs ~700ms with a progress bar, then drops into Done and the worker returns to idle to pull the next. At most 3 run simultaneously — extra tasks visibly wait. Live counters: queued K, running R (<=3), done D. Bounded concurrency (never more than 3 active bars) is the point.",
 },
 "realWorld": ["Java's ExecutorService", "Python's ThreadPoolExecutor / Gunicorn workers", "web-server request worker pools"],
 "gotcha": "Sizing matters: too few workers starves throughput, too many thrash the CPU or exhaust connections; and a slow task can block a worker, so keep tasks bounded or use a separate pool.",
},
{
 "slug": "producer-consumer", "title": "Producer-Consumer", "category": "Additional Patterns",
 "oneLiner": "Decouple producers from consumers with a bounded buffer; each side blocks when it's full or empty.",
 "problem": "When a fast producer feeds a slow consumer directly, one waits on the other and they're tightly coupled. A bounded buffer between them smooths bursts and lets each run at its own pace, blocking only at the limits.",
 "keyPoints": [
   "A bounded buffer sits between producers and consumers",
   "Producer blocks when full; consumer blocks when empty",
   "The buffer absorbs bursts and applies back-pressure",
   "Sides scale independently — add more of either",
 ],
 "python": "import queue, threading, time\n\nbuffer = queue.Queue(maxsize=5)   # bounded buffer\n\n\ndef producer():\n    for i in range(10):\n        buffer.put(i)             # blocks when full\n        time.sleep(0.05)\n\n\ndef consumer():\n    while True:\n        item = buffer.get()       # blocks when empty\n        print(\"consumed\", item)\n        buffer.task_done()\n\n\nthreading.Thread(target=producer).start()\nthreading.Thread(target=consumer, daemon=True).start()",
 "participants": ["Producer (puts items)", "Bounded buffer / queue", "Consumer (takes items)", "Blocking condition (full / empty)"],
 "diagram": "flowchart LR\n  P[Producer] --> B[(bounded buffer)]\n  B --> C[Consumer]",
 "diagramType": "flowchart",
 "interactive": {
   "componentName": "ProducerConsumerBuffer",
   "idea": "A bounded buffer decouples a producer from a consumer; each blocks when the buffer is full or empty.",
   "mechanic": "Center: a bounded buffer of 5 slots that fill left-to-right. Left: a Producer with a 'produce' button and an auto toggle; right: a Consumer with a 'consume' button and an auto toggle. Produce pushes a numbered item into the next free slot (slide-in + fill); consume pops the oldest from the front (slide-out), FIFO. States: producing into a full buffer flips the Producer to a pulsing 'BLOCKED (full)' badge and adds nothing; consuming an empty buffer shows the Consumer 'BLOCKED (empty)'. Auto mode runs producer and consumer on different intervals (producer faster) so the buffer visibly fills and back-pressures. Live readouts: buffer K/5, produced P, consumed C. Reset empties the buffer.",
 },
 "realWorld": ["Kafka / RabbitMQ message queues", "logging with an async buffered handler", "OS pipes and bounded channels (Go channels)"],
 "gotcha": "An unbounded buffer just hides the imbalance until memory runs out; keep it bounded so back-pressure is real, and size it for expected burstiness.",
},
]

out = HERE / "deck3_additional_specs.json"
json.dump(SPECS, open(out, "w"), indent=2, ensure_ascii=False)
print(f"wrote {len(SPECS)} authored specs -> {out}")
for s in SPECS:
    py_ok = bool(s["python"]) and "\n" in s["python"]
    print(f"  {s['slug']:<22} {s['interactive']['componentName']:<26} py:{s['python'].count(chr(10))+1}L  ol:{len(s['oneLiner'])}")
