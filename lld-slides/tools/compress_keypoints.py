#!/usr/bin/env python3
"""Replace keyPoints with terser wording (same count + order per pattern).
Only keyPoints are touched; participants/everything else is left as-is."""
import json

NEW = {
 "singleton": [
   "Hide the constructor; one cached instance behind an accessor",
   "One shared instance — every caller's writes are seen everywhere",
   "Guard the first build with a lock + re-check (thread-safe)",
   "Use for one owner of shared state; else inject dependencies",
 ],
 "builder": [
   "Each setter mutates scratch state and returns self; build() emits the product",
   "No nulls for skipped fields; any order; validation in build()",
   "Use for many optional fields or an immutable product",
   "Add a field = one new method, no constructor churn",
 ],
 "factory-method": [
   "Creator calls an overridable factory method inside shared logic",
   "Client codes to the Product interface, never a concrete class",
   "New variant = new Creator + Product pair, no edits",
   "Use when the subclass decides the type within a shared workflow",
 ],
 "abstract-factory": [
   "One factory returns a whole matched family of products",
   "Swap the family by swapping one factory; client untouched",
   "Use when products must vary together and never mix",
   "Unlike Factory Method (one product), it makes a related set",
 ],
 "prototype": [
   "clone() returns an independent copy — no constructor or class name",
   "Skips heavy init; defaults live in one template you copy",
   "Use for many similar instances, or when you hold only an interface",
   "Shallow copy shares nested state — deep-copy to isolate clones",
 ],
 "adapter": [
   "Adapter implements Target, wraps Adaptee, translates each call",
   "Client and adaptee stay untouched and decoupled",
   "Prefer object adapters (composition) over class adapters",
   "Use to fit a legacy or third-party API to your contract",
 ],
 "facade": [
   "One object fronts the subsystems and sequences their calls",
   "Clients depend only on the facade; subsystems stay swappable",
   "Use for a multi-step workflow many callers invoke the same way",
   "Adds convenience, not restriction — subsystems stay usable directly",
 ],
 "decorator": [
   "Wraps the same interface, adding work before/after delegating inward",
   "Features stack at runtime; one class per feature, not per combo",
   "Use for optional, stackable add-ons (compression, encryption, logging)",
   "Order matters: the outermost layer runs first in, last out",
 ],
 "composite": [
   "Leaf and Composite share one Component interface; no type checks",
   "A Composite holds children and delegates to them — arbitrary nesting",
   "Operations recurse: leaves return a value, composites aggregate",
   "Use when data is a tree and one op runs on a node or subtree",
 ],
 "proxy": [
   "Same interface as the real subject; intercepts before delegating",
   "Add lazy loading, access control, caching, or logging transparently",
   "Variants: virtual, protection, remote, caching, smart",
   "Use when direct access is costly or risky",
 ],
 "bridge": [
   "Abstraction holds an implementor and delegates the low-level work",
   "M+N classes, not M*N; either side swaps independently",
   "Use for two orthogonal axes that must combine freely",
   "Wire the implementor by composition; reassign it at runtime",
 ],
 "flyweight": [
   "Split state: intrinsic (shared, immutable) vs extrinsic (passed in)",
   "A factory caches by intrinsic key and reuses the instance",
   "Memory stays roughly flat as the object count explodes",
   "Use for huge object counts differing by a few context values",
 ],
 "strategy": [
   "One interface, many implementations; the context holds one",
   "New behavior = new class (Open/Closed), each testable alone",
   "Swap at runtime via setter — the context delegates blindly",
   "Use for variants of one operation, no scattered conditionals",
 ],
 "iterator": [
   "The collection hands back a cursor with has_next/next",
   "Storage and traversal vary independently; many walks at once",
   "One API across structures, or many orders without client edits",
   "The client loop is identical — only the iterator changes",
 ],
 "observer": [
   "Subject keeps a list of observers and calls update() on change",
   "Subject and observers vary independently; new listener, no edits",
   "Observers subscribe / unsubscribe at runtime",
   "Use when one change must fan out to many swappable consumers",
 ],
 "command": [
   "An action becomes an object (receiver + execute/undo) — passable data",
   "Invoker depends only on Command; new action = new class",
   "Undo/history for free: keep executed commands on a stack",
   "Use for queuing, scheduling, macros, or rollback",
 ],
 "state": [
   "Context forwards each call to its state; states swap the next state",
   "Each mode's rules in one class — no sprawling conditionals",
   "Use when an object has a few modes with different allowed actions",
   "Unlike Strategy: states know and trigger each other",
 ],
 "template-method": [
   "A template method runs a fixed step sequence; subclasses fill steps",
   "Shared workflow in one place; new variant = one subclass",
   "Use when many implementations share a recipe but vary a few steps",
   "Inheritance: the base owns control flow, steps can't be reordered",
 ],
 "chain-of-responsibility": [
   "Each handler holds the next; it handles or forwards the request",
   "Sender and receivers decoupled; reorder or insert without edits",
   "Two flavors: first-capable stops, or every handler contributes",
   "Use when the right handler is decided at runtime",
 ],
 "visitor": [
   "accept(visitor) calls back the matching visit() — double dispatch, no isinstance ladders",
   "New operation = new visitor; the element hierarchy never changes",
   "Use when element types are stable but operations keep growing",
   "Each operation lives in one testable visitor, not scattered",
 ],
 "mediator": [
   "Components report to one mediator instead of calling peers",
   "Loosely coupled — each depends only on the mediator",
   "Use for a tight cluster whose interactions keep sprawling",
   "Unlike Observer: the mediator orchestrates, not just broadcasts",
 ],
 "memento": [
   "Originator packs its private fields into a Memento and unpacks them",
   "Caretaker stacks Mementos and triggers save/restore, opaque to it",
   "New state changes only Originator + Memento; caretaker untouched",
   "Use for undo/redo, checkpoints, rollback with encapsulated snapshots",
 ],
 "null-object": [
   "A Null variant implements the interface with no-op / safe-default methods",
   "Callers skip null guards; the happy path stays readable",
   "Stateless — share one immutable singleton",
   "Use when absence is normal; avoid when missing means a bug",
 ],
 "repository": [
   "Domain depends on a repository interface, not on SQL",
   "Swap the store (memory, SQL, Mongo) without touching callers",
   "Tests run against an in-memory repo — no database",
   "One place maps rows to objects",
 ],
 "mvc": [
   "Model holds state and rules; never draws",
   "View renders the model; never mutates it",
   "Controller turns input into model updates",
   "Model notifies views on change (observer underneath)",
 ],
 "dependency-injection": [
   "Pass collaborators in; don't build them inside",
   "Depend on an abstraction, not a concrete class",
   "Swap real for fake to test in isolation",
   "A container wires the graph once",
 ],
 "specification": [
   "Each rule is an object with is_satisfied(item)",
   "Compose with and / or / not into bigger rules",
   "Reuse one spec for filtering, validation, and queries",
   "Name the rule once; read it like a sentence",
 ],
 "game-loop": [
   "One loop: input -> update(dt) -> render, repeating",
   "Update by elapsed time, not frame count",
   "Render rate can vary; simulation stays stable",
   "A fixed timestep catches up with extra updates",
 ],
 "thread-pool": [
   "A fixed set of workers pulls from one queue",
   "Bounded concurrency: at most N run at once",
   "Reuse threads — no per-task create/destroy",
   "Extra work waits in the queue (back-pressure)",
 ],
 "producer-consumer": [
   "A bounded buffer sits between producers and consumers",
   "Producer blocks when full; consumer when empty",
   "The buffer absorbs bursts and applies back-pressure",
   "Sides scale independently — add more of either",
 ],
}

for path in ['tools/deck3_specs.json', 'tools/deck3_additional_specs.json']:
    data = json.load(open(path))
    changed = 0
    for s in data:
        slug = s['slug']
        if slug in NEW:
            old = s['keyPoints']
            new = NEW[slug]
            if len(old) != len(new):
                print(f"  SKIP {slug}: count {len(old)} -> {len(new)} mismatch")
                continue
            s['keyPoints'] = new
            changed += 1
    json.dump(data, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f"{path}: updated {changed} patterns")

missing = [k for k in NEW if k not in {s['slug'] for s in json.load(open('tools/deck3_specs.json'))} | {s['slug'] for s in json.load(open('tools/deck3_additional_specs.json'))}]
print("NEW slugs not found:", missing or "none")
