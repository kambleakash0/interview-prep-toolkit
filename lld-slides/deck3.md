---
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

---
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

---
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

---
layout: default
class: section-slide
---

<div class="ghost-num">01</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 01</div>
  <h1>Creational Patterns</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">how objects are made</span></div>
</div>

---

## Singleton

<div class="bp-dim bp-mono text-sm mb-3">Guarantee a class has exactly one instance and hand every caller that same shared object.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import threading


class Settings:
    """A single shared config store, created exactly once."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:                 # guard the first creation
                if cls._instance is None:   # re-check inside the lock
                    cls._instance = super().__new__(cls)
                    cls._instance.values = {}
        return cls._instance


if __name__ == "__main__":
    a = Settings()
    a.values["theme"] = "dark"

    b = Settings()                          # no new object is built
    print("same object:", a is b)           # True
    print("b sees a's write:", b.values["theme"])  # dark
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Singleton</b> <span class="bp-dim">holds the cached instance and the access point</span></li><li><b>Client</b> <span class="bp-dim">requests the instance instead of constructing one</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Hide the constructor; one cached instance behind an accessor</li><li>One shared instance — every caller's writes are seen everywhere</li><li>Guard the first build with a lock + re-check (thread-safe)</li><li>Use for one owner of shared state; else inject dependencies</li></ul>

</div>
</div>

<!--
Key points: Hide the constructor; one cached instance behind an accessor | One shared instance — every caller's writes are seen everywhere | Guard the first build with a lock + re-check (thread-safe) | Use for one owner of shared state; else inject dependencies

Problem: Some resources must exist only once (a logger, a config store, a connection pool); spinning up duplicates wastes resources or splits state into inconsistent copies. Singleton funnels all access through one shared instance so everyone reads and writes the same object.

Real-world: Python's logging module returns the same root logger via logging.getLogger(); the module object itself is effectively a singleton. · Database/HTTP connection pools (e.g. SQLAlchemy engines, requests sessions) shared app-wide so connections are reused rather than recreated. · OS-level coordinators like a print spooler or a process-wide configuration/registry that must reflect one consistent state.

Gotcha: Singleton smuggles in global mutable state, which couples callers to it and makes unit tests bleed into each other (one test's writes leak into the next). When you mainly need 'one instance per app run,' prefer creating it once and injecting it as a dependency instead of reaching for a global accessor.
-->

---

## Singleton

<div class="bp-dim bp-mono text-sm mb-3">Every call to the accessor returns the one cached object; the first call builds it, every later call reuses it, and a lock keeps concurrent callers from building a second.</div>

<SingletonInstancePool />

---

## Builder

<div class="bp-dim bp-mono text-sm mb-3">Assemble a complex object field by field through a fluent chain, then freeze it with one build() call.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Pizza:
    def __init__(self, size, toppings, crust):
        self.size, self.toppings, self.crust = size, toppings, crust

    def __str__(self):
        tops = ", ".join(self.toppings) or "no toppings"
        return f"{self.size} {self.crust}-crust pizza with {tops}"


class PizzaBuilder(ABC):
    def __init__(self):
        self._size, self._crust, self._toppings = "medium", "thin", []

    def size(self, s): self._size = s; return self
    def crust(self, c): self._crust = c; return self
    def add(self, topping): self._toppings.append(topping); return self

    @abstractmethod
    def build(self): ...


class StandardPizzaBuilder(PizzaBuilder):
    def build(self):
        return Pizza(self._size, self._toppings, self._crust)


pizza = (StandardPizzaBuilder()
         .size("large").crust("stuffed")
         .add("mushroom").add("olive").build())
print(pizza)  # large stuffed-crust pizza with mushroom, olive
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Product</b> <span class="bp-dim">Pizza</span></li><li><b>Builder</b> <span class="bp-dim">PizzaBuilder, abstract</span></li><li><b>ConcreteBuilder</b> <span class="bp-dim">StandardPizzaBuilder</span></li><li><b>Director</b> <span class="bp-dim">optional</span></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Each setter mutates scratch state and returns self; build() emits the product</li><li>No nulls for skipped fields; any order; validation in build()</li><li>Use for many optional fields or an immutable product</li><li>Add a field = one new method, no constructor churn</li></ul>

</div>
</div>

<!--
Key points: Each setter mutates scratch state and returns self; build() emits the product | No nulls for skipped fields; any order; validation in build() | Use for many optional fields or an immutable product | Add a field = one new method, no constructor churn

Problem: Objects with many optional fields force you into telescoping constructors or long positional argument lists where one misplaced None silently corrupts state. Builder lets callers set only what they need, by name, in any order.

Real-world: Python stdlib http.client and requests/urllib3 assemble requests via incremental configuration before sending. · SQLAlchemy and Django ORM querysets chain .filter().order_by().limit() then materialize on execution, mirroring builder semantics. · Java's StringBuilder and Lombok @Builder, plus protobuf message builders, are canonical fluent builders.

Gotcha: Do not reach for Builder when an object has few fields and no optional/ordering complexity. A dataclass with defaults or keyword-only arguments is simpler and clearer; a builder there is ceremony that hides a one-line constructor.
-->

---

## Builder

<div class="bp-dim bp-mono text-sm mb-3">A builder accumulates mutable scratch state across chained calls and only materializes an immutable, frozen product when build() is invoked.</div>

<FluentBuilderChain />

---

## Factory Method

<div class="bp-dim bp-mono text-sm mb-3">A base class owns the workflow but defers "which object to build" to its subclasses.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class HtmlButton(Button):
    def render(self) -> str:
        return "<button>Click</button>"


class NativeButton(Button):
    def render(self) -> str:
        return "[ Click ]"


class Dialog(ABC):
    @abstractmethod
    def create_button(self) -> Button:  # factory method
        ...

    def render(self) -> str:            # shared workflow
        return f"Dialog -> {self.create_button().render()}"


class WebDialog(Dialog):
    def create_button(self) -> Button:
        return HtmlButton()


class DesktopDialog(Dialog):
    def create_button(self) -> Button:
        return NativeButton()


for dialog in (WebDialog(), DesktopDialog()):
    print(dialog.render())
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Product</b> <span class="bp-dim">Button</span></li><li><b>ConcreteProduct</b> <span class="bp-dim">HtmlButton, NativeButton</span></li><li><b>Creator</b> <span class="bp-dim">Dialog</span></li><li><b>ConcreteCreator</b> <span class="bp-dim">WebDialog, DesktopDialog</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Creator calls an overridable factory method inside shared logic</li><li>Client codes to the Product interface, never a concrete class</li><li>New variant = new Creator + Product pair, no edits</li><li>Use when the subclass decides the type within a shared workflow</li></ul>

</div>
</div>

<!--
Key points: Creator calls an overridable factory method inside shared logic | Client codes to the Product interface, never a concrete class | New variant = new Creator + Product pair, no edits | Use when the subclass decides the type within a shared workflow

Problem: A growing if/else or switch that picks which concrete class to instantiate couples your core logic to every type and must be edited for each new one. Factory Method removes that central branching so adding a type means adding a class, not touching existing code.

Real-world: Python's logging module: Logger.makeRecord() is a factory method subclasses override to produce custom LogRecord objects. · Django's class-based views override get_queryset()/get_form_class() so the base dispatch flow builds the right object per view. · Java's java.util.Collection.iterator() and Calendar.getInstance(), where subclasses/locales decide the concrete returned type.

Gotcha: Do not reach for it when you only have one product type or a stable, small set; spinning up a Creator subclass per Product adds class explosion. A plain Simple Factory or even direct construction is often enough, and in Python passing the class/callable as an argument frequently beats an inheritance hierarchy.
-->

---

## Factory Method

<div class="bp-dim bp-mono text-sm mb-3">The Creator subclass you pick decides which Product the one shared render() workflow produces, while the workflow steps themselves never change.</div>

<FactoryMethodDialogForge />

---

## Abstract Factory

<div class="bp-dim bp-mono text-sm mb-3">One factory hands you a whole matched family of objects, so you never wire incompatible parts together.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Connection(ABC):
    @abstractmethod
    def dsn(self) -> str: ...

class Dialect(ABC):
    @abstractmethod
    def paginate(self, limit: int) -> str: ...

class PgConn(Connection):
    def dsn(self): return "postgres://localhost/app"
class PgDialect(Dialect):
    def paginate(self, limit): return f"LIMIT {limit}"

class MyConn(Connection):
    def dsn(self): return "mysql://localhost/app"
class MyDialect(Dialect):
    def paginate(self, limit): return f"LIMIT {limit} OFFSET 0"

class DBFactory(ABC):
    @abstractmethod
    def connection(self) -> Connection: ...
    @abstractmethod
    def dialect(self) -> Dialect: ...

class PostgresFactory(DBFactory):
    def connection(self): return PgConn()
    def dialect(self): return PgDialect()

class MySQLFactory(DBFactory):
    def connection(self): return MyConn()
    def dialect(self): return MyDialect()

def run(factory: DBFactory):
    print(factory.connection().dsn(), "|", factory.dialect().paginate(10))

run(PostgresFactory())   # postgres://localhost/app | LIMIT 10
run(MySQLFactory())      # mysql://localhost/app | LIMIT 10 OFFSET 0
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>AbstractFactory</b></li><li><b>ConcreteFactory</b></li><li><b>AbstractProduct</b></li><li><b>ConcreteProduct</b></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>One factory returns a whole matched family of products</li><li>Swap the family by swapping one factory; client untouched</li><li>Use when products must vary together and never mix</li><li>Unlike Factory Method (one product), it makes a related set</li></ul>

</div>
</div>

<!--
Key points: One factory returns a whole matched family of products | Swap the family by swapping one factory; client untouched | Use when products must vary together and never mix | Unlike Factory Method (one product), it makes a related set

Problem: When several objects must come from the same variant (same OS theme, same DB engine, same channel), scattered conditionals let callers accidentally pair a Postgres connection with a MySQL dialect. Abstract Factory makes such mismatches structurally impossible.

Real-world: GUI toolkits that swap an entire look-and-feel family (Java Swing pluggable Look and Feel, Qt styles). · SQLAlchemy / JDBC dialect-and-driver pairs selected per database engine so connection and SQL generation stay consistent. · Cloud SDK provider clients (boto3 session, terraform providers) that vend a coherent family of service objects for one backend.

Gotcha: Adding a brand-new product type forces a change to the factory interface and every concrete factory; if your product set is stable but variants are few, a plain Factory Method or simple config map is lighter.
-->

---

## Abstract Factory

<div class="bp-dim bp-mono text-sm mb-3">Picking one factory locks every product to the same variant; the client code never changes.</div>

<FamilySwitchBench />

---

## Prototype

<div class="bp-dim bp-mono text-sm mb-3">Create new objects by cloning a ready-made instance instead of rebuilding them from scratch.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import copy
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def clone(self) -> "Shape": ...


class Rectangle(Shape):
    def __init__(self, w, h, style):
        self.w, self.h, self.style = w, h, style  # style is a mutable dict

    def clone(self) -> "Shape":
        return copy.deepcopy(self)  # deep copy so nested style isn't shared

    def __repr__(self):
        return f"Rectangle({self.w}x{self.h}, {self.style})"


template = Rectangle(4, 2, {"fill": "blue", "border": 1})  # prototype

a = template.clone()
b = template.clone()
b.w = 8
b.style["fill"] = "red"  # mutating b leaves template + a untouched

print(template)  # Rectangle(4x2, {'fill': 'blue', 'border': 1})
print(a)         # Rectangle(4x2, {'fill': 'blue', 'border': 1})
print(b)         # Rectangle(8x2, {'fill': 'red', 'border': 1})
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Prototype</b> <span class="bp-dim">abstract clone interface</span></li><li><b>ConcretePrototype</b> <span class="bp-dim">implements clone</span></li><li><b>Client</b></li><li><b>PrototypeRegistry</b> <span class="bp-dim">optional, keyed templates</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>clone() returns an independent copy — no constructor or class name</li><li>Skips heavy init; defaults live in one template you copy</li><li>Use for many similar instances, or when you hold only an interface</li><li>Shallow copy shares nested state — deep-copy to isolate clones</li></ul>

</div>
</div>

<!--
Key points: clone() returns an independent copy — no constructor or class name | Skips heavy init; defaults live in one template you copy | Use for many similar instances, or when you hold only an interface | Shallow copy shares nested state — deep-copy to isolate clones

Problem: Re-running expensive or intricate construction logic for every near-identical object is slow and repetitive, and it leaks setup details to the caller. External copying also breaks when fields are private or the concrete class is hidden behind an interface.

Real-world: Python stdlib copy.copy / copy.deepcopy and the __copy__ / __deepcopy__ hooks objects implement. · JavaScript structuredClone and object spread used to duplicate configured objects. · Game engines and editors cloning a configured entity/template (e.g. Unity Instantiate of a prefab) instead of rebuilding it.

Gotcha: Default shallow clones share nested mutable objects, so editing one clone silently mutates the original and every other clone; deep-copy any mutable inner state. Skip Prototype for cheap, stateless objects where a plain constructor is clearer.
-->

---

## Prototype

<div class="bp-dim bp-mono text-sm mb-3">A clone copies scalar values outright but, by default, only copies the reference to nested mutable state, the deep-vs-shallow trap at the heart of Prototype.</div>

<PrototypeCloneForge />

---
layout: default
class: section-slide
---

<div class="ghost-num">02</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 02</div>
  <h1>Structural Patterns</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">how objects compose</span></div>
</div>

---

## Adapter

<div class="bp-dim bp-mono text-sm mb-3">Wrap an incompatible class so it speaks the interface your client already expects.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class TempSensor(ABC):              # Target
    @abstractmethod
    def read_celsius(self) -> float: ...

class FahrenheitProbe:              # Adaptee (incompatible API)
    def __init__(self, f): self._f = f
    def get_fahrenheit(self) -> float: return self._f

class ProbeAdapter(TempSensor):     # Adapter
    def __init__(self, probe: FahrenheitProbe):
        self._probe = probe
    def read_celsius(self) -> float:
        return round((self._probe.get_fahrenheit() - 32) * 5 / 9, 1)

def report(sensor: TempSensor):     # Client knows only Target
    print(f"{sensor.read_celsius()} C")

report(ProbeAdapter(FahrenheitProbe(98.6)))   # 37.0 C
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Target</b></li><li><b>Adaptee</b></li><li><b>Adapter</b></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Adapter implements Target, wraps Adaptee, translates each call</li><li>Client and adaptee stay untouched and decoupled</li><li>Prefer object adapters (composition) over class adapters</li><li>Use to fit a legacy or third-party API to your contract</li></ul>

</div>
</div>

<!--
Key points: Adapter implements Target, wraps Adaptee, translates each call | Client and adaptee stay untouched and decoupled | Prefer object adapters (composition) over class adapters | Use to fit a legacy or third-party API to your contract

Problem: A class you must use (legacy code, a vendor SDK) has the right behavior but the wrong method names, parameters, or return types. You can't edit either side, yet they must work together.

Real-world: Python io.TextIOWrapper adapts a raw byte stream into a text interface; collections.abc mixins adapt minimal methods into full container APIs. · Java's java.io.InputStreamReader adapts a byte InputStream to a character Reader, and Arrays.asList adapts an array to the List interface. · Wrapping a third-party payment or SDK client (Stripe, a legacy gateway) behind your own service interface.

Gotcha: Don't reach for Adapter when you also need to add behavior or restrict the API: that's Decorator or Facade. An adapter only translates an existing interface; piling logic into it turns it into a hard-to-test god class.
-->

---

## Adapter

<div class="bp-dim bp-mono text-sm mb-3">The adapter is a translator socket: the client's plug shape never changes, only the adapter converts it to fit the foreign appliance.</div>

<AdapterPlugTranslator />

---

## Facade

<div class="bp-dim bp-mono text-sm mb-3">Wrap a tangle of subsystems behind one clean entry point so clients call a single method, not five.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Subsystem(ABC):
    @abstractmethod
    def run(self) -> None: ...


class Encoder(Subsystem):
    def run(self): print("Encoder: transcoding to H.264")


class Subtitler(Subsystem):
    def run(self): print("Subtitler: burning captions")


class Uploader(Subsystem):
    def run(self): print("Uploader: pushing to CDN")


class PublishFacade:                        # Facade
    def __init__(self):
        self._steps = [Encoder(), Subtitler(), Uploader()]

    def publish(self, title: str) -> None:  # one simple entry point
        print(f"Publishing '{title}'...")
        for step in self._steps:
            step.run()
        print("Done: live on CDN")


PublishFacade().publish("intro.mp4")        # client touches only the facade
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Facade</b></li><li><b>Subsystem</b></li><li><b>ConcreteSubsystem</b></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>One object fronts the subsystems and sequences their calls</li><li>Clients depend only on the facade; subsystems stay swappable</li><li>Use for a multi-step workflow many callers invoke the same way</li><li>Adds convenience, not restriction — subsystems stay usable directly</li></ul>

</div>
</div>

<!--
Key points: One object fronts the subsystems and sequences their calls | Clients depend only on the facade; subsystems stay swappable | Use for a multi-step workflow many callers invoke the same way | Adds convenience, not restriction — subsystems stay usable directly

Problem: A simple task often means orchestrating several low-level components in the right order, with every caller duplicating that choreography and coupling tightly to internals. Facade hides that complexity behind one high-level interface so clients stop juggling moving parts.

Real-world: Python requests library: requests.get() is a facade over urllib3 connection pools, sessions, and socket handling · SLF4J logging facade presents one API in front of multiple backend implementations such as Logback or log4j · Docker CLI: a single docker run orchestrates image pull, container create, network setup, and start

Gotcha: Do not let the facade swell into a god object that grows a method for every caller's whim; keep it a thin coordinator. If clients need fine-grained control, leave the subsystems directly accessible rather than tunneling everything through one bloated interface.
-->

---

## Facade

<div class="bp-dim bp-mono text-sm mb-3">A facade turns one client call into an ordered cascade of subsystem calls, while the client stays unaware of the count or sequence.</div>

<FacadeOrchestrationStage />

---

## Decorator

<div class="bp-dim bp-mono text-sm mb-3">Wrap an object in look-alike layers that each add one behavior, stackable in any order at runtime.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class DataSource(ABC):
    @abstractmethod
    def write(self, data: str) -> str: ...


class FileSource(DataSource):
    def write(self, data: str) -> str:
        return data


class SourceDecorator(DataSource):
    def __init__(self, wrapped: DataSource):
        self._wrapped = wrapped


class Compressed(SourceDecorator):
    def write(self, data: str) -> str:
        return f"zip({self._wrapped.write(data)})"


class Encrypted(SourceDecorator):
    def write(self, data: str) -> str:
        return f"enc({self._wrapped.write(data)})"


pipeline = Encrypted(Compressed(FileSource()))
print(pipeline.write("report"))  # enc(zip(report))
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Component</b> <span class="bp-dim">DataSource</span></li><li><b>ConcreteComponent</b> <span class="bp-dim">FileSource</span></li><li><b>Decorator</b> <span class="bp-dim">SourceDecorator</span></li><li><b>ConcreteDecorator</b> <span class="bp-dim">Compressed, Encrypted</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Wraps the same interface, adding work before/after delegating inward</li><li>Features stack at runtime; one class per feature, not per combo</li><li>Use for optional, stackable add-ons (compression, encryption, logging)</li><li>Order matters: the outermost layer runs first in, last out</li></ul>

</div>
</div>

<!--
Key points: Wraps the same interface, adding work before/after delegating inward | Features stack at runtime; one class per feature, not per combo | Use for optional, stackable add-ons (compression, encryption, logging) | Order matters: the outermost layer runs first in, last out

Problem: Subclassing every optional-feature combination explodes into 2^n classes and locks the choice in at compile time. Decorator lets you bolt on responsibilities one layer at a time without touching the original class.

Real-world: Python's functools.lru_cache and @property wrap a callable/attribute to add caching or access control without changing it. · Java I/O streams: BufferedInputStream and GZIPInputStream wrap a base InputStream to layer buffering and compression. · WSGI/ASGI and Express middleware stacks wrap a handler so each layer adds auth, logging, or compression around the request.

Gotcha: Decorators preserve only the shared interface, so a client that reaches for the concrete type's extra methods or runs isinstance checks on the wrapped object will break; deep wrapping also makes stack traces and debugging harder to follow.
-->

---

## Decorator

<div class="bp-dim bp-mono text-sm mb-3">A decorated object is an onion: each layer wraps the core, and a call dives in through every layer, then unwinds back out.</div>

<DecoratorOnionStack />

---

## Composite

<div class="bp-dim bp-mono text-sm mb-3">Treat a single object and a whole tree of objects through one interface, so recursion just works.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def cost(self) -> float: ...
    @abstractmethod
    def show(self, depth=0): ...

class Item(Node):                       # Leaf
    def __init__(self, name, price):
        self.name, self.price = name, price
    def cost(self):
        return self.price
    def show(self, depth=0):
        print("  " * depth + f"- {self.name}: ${self.price}")

class Box(Node):                        # Composite
    def __init__(self, name):
        self.name, self.children = name, []
    def add(self, node):
        self.children.append(node); return self
    def cost(self):
        return sum(c.cost() for c in self.children)
    def show(self, depth=0):
        print("  " * depth + f"+ {self.name}/")
        for c in self.children:
            c.show(depth + 1)

cart = Box("cart").add(Item("pen", 2)).add(
    Box("kit").add(Item("tape", 3)).add(Item("glue", 5)))
cart.show()
print("total:", cart.cost())           # total: 10
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Component</b> <span class="bp-dim">Node</span></li><li><b>Leaf</b> <span class="bp-dim">Item</span></li><li><b>Composite</b> <span class="bp-dim">Box</span></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Leaf and Composite share one Component interface; no type checks</li><li>A Composite holds children and delegates to them — arbitrary nesting</li><li>Operations recurse: leaves return a value, composites aggregate</li><li>Use when data is a tree and one op runs on a node or subtree</li></ul>

</div>
</div>

<!--
Key points: Leaf and Composite share one Component interface; no type checks | A Composite holds children and delegates to them — arbitrary nesting | Operations recurse: leaves return a value, composites aggregate | Use when data is a tree and one op runs on a node or subtree

Problem: Modeling part-whole hierarchies (files/folders, org charts, UI trees) forces clients into type checks and casts to tell leaves apart from containers. Adding a new node type means touching every operation.

Real-world: The HTML/DOM and most UI toolkits (Tkinter, Qt, React) where a container widget and a single widget share a render/layout interface · Filesystem trees in os.walk and pathlib.Path, where a directory and a file expose the same traversal surface · AST node trees in Python's ast module, where a node and its child subtrees are visited uniformly

Gotcha: Putting child-management methods (add/remove) on the shared Component interface forces leaves to implement no-op or throwing versions, breaking type safety; either keep them only on Composite (safer) or accept the uniformity-vs-safety tradeoff deliberately. Also avoid Composite for flat or non-recursive data, where it adds indirection for no gain.
-->

---

## Composite

<div class="bp-dim bp-mono text-sm mb-3">A composite returns the same answer whether you query one leaf or an entire subtree, because cost() recurses down and sums back up through identical Component calls.</div>

<CompositeTreeAggregator />

---

## Proxy

<div class="bp-dim bp-mono text-sm mb-3">A stand-in sharing the real object's interface that intercepts calls to control or defer access.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Vault(ABC):
    @abstractmethod
    def read(self, key: str) -> str: ...

class RealVault(Vault):
    def read(self, key: str) -> str:
        print(f"[RealVault] decrypting secret for {key!r}")
        return f"secret::{key}"

class VaultProxy(Vault):
    def __init__(self, role: str):
        self.role = role
        self._real = None              # RealVault built lazily

    def read(self, key: str) -> str:
        if self.role != "admin":
            return f"DENIED ({self.role})"
        if self._real is None:         # virtual: defer creation
            self._real = RealVault()
        return self._real.read(key)    # protection + delegation

guest, admin = VaultProxy("guest"), VaultProxy("admin")
print(guest.read("db_password"))       # blocked, RealVault never built
print(admin.read("db_password"))       # builds RealVault, then delegates
print(admin.read("api_token"))         # reuses the same RealVault
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Subject</b> <span class="bp-dim">Vault</span></li><li><b>RealSubject</b> <span class="bp-dim">RealVault</span></li><li><b>Proxy</b> <span class="bp-dim">VaultProxy</span></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Same interface as the real subject; intercepts before delegating</li><li>Add lazy loading, access control, caching, or logging transparently</li><li>Variants: virtual, protection, remote, caching, smart</li><li>Use when direct access is costly or risky</li></ul>

</div>
</div>

<!--
Key points: Same interface as the real subject; intercepts before delegating | Add lazy loading, access control, caching, or logging transparently | Variants: virtual, protection, remote, caching, smart | Use when direct access is costly or risky

Problem: A real object may be expensive to build, remote, or sensitive, yet clients call it directly with no chance to defer loading, check permissions, or add caching. Baking that policy into the object itself bloats it and breaks single responsibility.

Real-world: Python's weakref.proxy and multiprocessing manager proxies that stand in for objects living elsewhere · ORM lazy relations like SQLAlchemy or Django, where related rows load only when an attribute is first touched · Reverse proxies such as Nginx and API gateways that gate, cache, and route requests to backend services

Gotcha: A proxy must keep the exact same interface as the real subject; if it adds parameters (like a user role) to method signatures it breaks substitutability, so inject that context through the constructor instead. Also avoid stacking many proxies blindly, since each adds an indirection layer that can hide latency and complicate debugging.
-->

---

## Proxy

<div class="bp-dim bp-mono text-sm mb-3">The proxy is a gate in front of an expensive real object, deciding per-call whether to deny, build-then-delegate, or reuse, while lazy creation and access control stay visible.</div>

<ProxyGatekeeperPlayground />

---

## Bridge

<div class="bp-dim bp-mono text-sm mb-3">Split one class into two hierarchies (what vs how) and wire them with composition so each varies freely.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Channel(ABC):                          # Implementor
    @abstractmethod
    def deliver(self, text: str) -> None: ...

class EmailChannel(Channel):                 # ConcreteImplementor
    def deliver(self, text): print(f"[email] {text}")

class SmsChannel(Channel):                   # ConcreteImplementor
    def deliver(self, text): print(f"[sms] {text}")

class Notification(ABC):                     # Abstraction
    def __init__(self, channel: Channel):
        self.channel = channel               # the bridge
    @abstractmethod
    def send(self, msg: str) -> None: ...

class Alert(Notification):                   # RefinedAbstraction
    def send(self, msg): self.channel.deliver(f"ALERT: {msg}")

alert = Alert(EmailChannel())
alert.send("disk full")                      # [email] ALERT: disk full
alert.channel = SmsChannel()                 # rewire same object at runtime
alert.send("disk full")                      # [sms] ALERT: disk full
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Abstraction</b></li><li><b>RefinedAbstraction</b></li><li><b>Implementor</b></li><li><b>ConcreteImplementor</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Abstraction holds an implementor and delegates the low-level work</li><li>M+N classes, not M*N; either side swaps independently</li><li>Use for two orthogonal axes that must combine freely</li><li>Wire the implementor by composition; reassign it at runtime</li></ul>

</div>
</div>

<!--
Key points: Abstraction holds an implementor and delegates the low-level work | M+N classes, not M*N; either side swaps independently | Use for two orthogonal axes that must combine freely | Wire the implementor by composition; reassign it at runtime

Problem: When a class varies along two independent axes, subclassing every combination explodes into M x N rigid classes. Bridge keeps the two axes as separate hierarchies linked by a reference, so each grows on its own.

Real-world: Python logging: a Logger (abstraction) emits records through pluggable Handlers and Formatters (implementors), so log routing varies independently of call sites. · JDBC / Python DB-API: application code calls one cursor/connection abstraction while the concrete driver (PostgreSQL, MySQL, SQLite) is the swappable implementor. · GUI and rendering toolkits where device-independent drawing abstractions delegate to platform-specific render backends (e.g. Skia/Cairo behind a canvas API).

Gotcha: Do not reach for Bridge when there is only one implementation or a single axis of change; the extra indirection just adds ceremony. It also differs from Adapter in intent: Adapter retrofits an incompatible interface after the fact, while Bridge is designed up front to let two hierarchies evolve in parallel.
-->

---

## Bridge

<div class="bp-dim bp-mono text-sm mb-3">The abstraction and implementation are independent axes joined by one swappable reference, so combinations come from wiring rather than from new classes.</div>

<BridgeMatrixWirer />

---

## Flyweight

<div class="bp-dim bp-mono text-sm mb-3">Share one immutable object across thousands of look-alikes; pass the per-instance bits in at call time.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Glyph(ABC):                          # Flyweight
    @abstractmethod
    def stamp(self, row, col): ...

class Letter(Glyph):                       # ConcreteFlyweight: intrinsic state
    def __init__(self, char, font, color):
        self.char, self.font, self.color = char, font, color
    def stamp(self, row, col):             # extrinsic state passed in
        print(f"{self.char}@({row},{col}) [{self.font}/{self.color}]")

class GlyphPool:                           # FlyweightFactory
    _cache = {}
    @classmethod
    def get(cls, char, font, color):
        key = (char, font, color)
        if key not in cls._cache:
            cls._cache[key] = Letter(char, font, color)
        return cls._cache[key]

page = [GlyphPool.get(c, "Mono", "black") for c in "level"]
for col, g in enumerate(page):
    g.stamp(0, col)
print(f"{len(page)} chars, {len(GlyphPool._cache)} flyweights")
assert page[1] is page[3]                  # both 'e' share one instance
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Flyweight</b> <span class="bp-dim">abstract role</span></li><li><b>ConcreteFlyweight</b> <span class="bp-dim">stores intrinsic state</span></li><li><b>FlyweightFactory</b> <span class="bp-dim">caches and shares instances</span></li><li><b>Client</b> <span class="bp-dim">holds extrinsic state, passes it in</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Split state: intrinsic (shared, immutable) vs extrinsic (passed in)</li><li>A factory caches by intrinsic key and reuses the instance</li><li>Memory stays roughly flat as the object count explodes</li><li>Use for huge object counts differing by a few context values</li></ul>

</div>
</div>

<!--
Key points: Split state: intrinsic (shared, immutable) vs extrinsic (passed in) | A factory caches by intrinsic key and reuses the instance | Memory stays roughly flat as the object count explodes | Use for huge object counts differing by a few context values

Problem: Spawning millions of near-identical objects burns memory and GC time because each one re-stores the same heavy data. Flyweight keeps a single shared copy of the repeated state and supplies the unique part externally.

Real-world: Python interns small ints (-5..256) and short strings, returning the same cached object for equal values. · Java's Integer.valueOf / Boolean caching and the JVM string pool share immutable instances. · Game and UI engines share textures, glyph atlases, and sprite/tile types across thousands of placed instances.

Gotcha: Only works when shared state is immutable and truly repeated; if the intrinsic data must mutate per instance, or there are few distinct combinations, the factory and key-hashing overhead outweighs any memory savings.
-->

---

## Flyweight

<div class="bp-dim bp-mono text-sm mb-3">One shared glyph instance can back many on-screen characters; the factory reuses instead of allocating, so the grid grows but the pool barely does.</div>

<FlyweightGlyphPool />

---
layout: default
class: section-slide
---

<div class="ghost-num">03</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 03</div>
  <h1>Behavioral Patterns</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">how objects interact</span></div>
</div>

---

## Strategy

<div class="bp-dim bp-mono text-sm mb-3">Wrap each interchangeable algorithm in its own object so the caller can swap behavior at runtime.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def quote(self, subtotal: float) -> float: ...

class NoDiscount(PricingStrategy):
    def quote(self, subtotal): return subtotal

class PercentOff(PricingStrategy):
    def __init__(self, pct): self.pct = pct
    def quote(self, subtotal): return subtotal * (1 - self.pct / 100)

class Cart:                       # Context
    def __init__(self, pricing: PricingStrategy):
        self.pricing = pricing
    def total(self, subtotal):
        return round(self.pricing.quote(subtotal), 2)

cart = Cart(NoDiscount())
print(cart.total(100))            # 100
cart.pricing = PercentOff(20)     # swap algorithm at runtime
print(cart.total(100))            # 80.0
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Strategy</b> <span class="bp-dim">abstract interface</span></li><li><b>ConcreteStrategy</b> <span class="bp-dim">e.g. NoDiscount, PercentOff</span></li><li><b>Context</b> <span class="bp-dim">e.g. Cart</span></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>One interface, many implementations; the context holds one</li><li>New behavior = new class (Open/Closed), each testable alone</li><li>Swap at runtime via setter — the context delegates blindly</li><li>Use for variants of one operation, no scattered conditionals</li></ul>

</div>
</div>

<!--
Key points: One interface, many implementations; the context holds one | New behavior = new class (Open/Closed), each testable alone | Swap at runtime via setter — the context delegates blindly | Use for variants of one operation, no scattered conditionals

Problem: One class tries to do a job many ways, so it grows a sprawling if/else chain that you must reopen and risk breaking every time a new variant appears. Strategy moves each variant into its own object so behavior is selected, not branched.

Real-world: Python's sorted() and list.sort() take a key= callable - a comparison strategy injected at call time. · Django/Werkzeug password hashers and DRF authentication classes are pluggable strategies selected by configuration. · matplotlib backends and gzip/lzma compressors expose interchangeable algorithm objects behind one interface.

Gotcha: For one or two simple variants a plain function, a dict of callables, or a lambda is lighter than a class hierarchy; full Strategy classes only pay off when variants carry their own state or proliferate. Also remember the client must still know enough to choose the right strategy.
-->

---

## Strategy

<div class="bp-dim bp-mono text-sm mb-3">The context is a fixed pipe that never changes; only the plugged-in algorithm rewrites the output, so you can hot-swap behavior at runtime without touching the context.</div>

<StrategySwapBench />

---

## Iterator

<div class="bp-dim bp-mono text-sm mb-3">Walk a collection element by element through a uniform cursor, never touching its internal storage.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Iterator(ABC):
    @abstractmethod
    def has_next(self) -> bool: ...
    @abstractmethod
    def next(self): ...


class Shelf:                       # ConcreteAggregate
    def __init__(self):
        self._books = []

    def add(self, title):
        self._books.append(title)

    def iterator(self) -> Iterator:
        return ShelfIterator(self._books)


class ShelfIterator(Iterator):     # ConcreteIterator: owns the position
    def __init__(self, books):
        self._books, self._pos = books, 0

    def has_next(self) -> bool:
        return self._pos < len(self._books)

    def next(self):
        item = self._books[self._pos]
        self._pos += 1
        return item


shelf = Shelf()
for t in ("Dune", "Hyperion", "Neuromancer"):
    shelf.add(t)

it = shelf.iterator()              # client never sees the list
while it.has_next():
    print(it.next())
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Iterator</b> <span class="bp-dim">interface</span></li><li><b>ConcreteIterator</b> <span class="bp-dim">ShelfIterator</span></li><li><b>Aggregate</b> <span class="bp-dim">interface</span></li><li><b>ConcreteAggregate</b> <span class="bp-dim">Shelf</span></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>The collection hands back a cursor with has_next/next</li><li>Storage and traversal vary independently; many walks at once</li><li>One API across structures, or many orders without client edits</li><li>The client loop is identical — only the iterator changes</li></ul>

</div>
</div>

<!--
Key points: The collection hands back a cursor with has_next/next | Storage and traversal vary independently; many walks at once | One API across structures, or many orders without client edits | The client loop is identical — only the iterator changes

Problem: Letting clients reach into a collection's raw list leaks its structure, breaks encapsulation, and bakes one traversal style into client code. Iterator hands out a cursor object so the collection keeps control of how it is walked.

Real-world: Python's iterator protocol: __iter__ and __next__ power every for-loop, with itertools building lazy iterators on top · Java's java.util.Iterator and Iterable returned by collections; C++ STL begin/end iterators · Database cursors and paginated API clients that stream rows or pages without loading the whole result set

Gotcha: Mutating the collection while an iterator is mid-traversal causes skipped elements or stale reads; many languages throw ConcurrentModificationException. Also skip the full pattern when the language already gives you native iteration (Python's for-loop) and you need no custom ordering.
-->

---

## Iterator

<div class="bp-dim bp-mono text-sm mb-3">A cursor is a separate object with its own position that advances over a collection without exposing the underlying array, and swapping the cursor changes the order while the client loop stays fixed.</div>

<IteratorCursorWalk />

---

## Observer

<div class="bp-dim bp-mono text-sm mb-3">A subject broadcasts its state changes to any number of subscribers without knowing who they are.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, temperature: float) -> None: ...


class WeatherStation:  # Subject
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def subscribe(self, obs: Observer) -> None:
        self._observers.append(obs)

    def unsubscribe(self, obs: Observer) -> None:
        self._observers.remove(obs)

    def set_temperature(self, temp: float) -> None:
        for obs in self._observers:  # broadcast to all
            obs.update(temp)


class PhoneDisplay(Observer):
    def update(self, temperature: float) -> None:
        print(f"Phone: now {temperature}C")


class Logger(Observer):
    def update(self, temperature: float) -> None:
        print(f"Logger: recorded {temperature}C")


station = WeatherStation()
phone, logger = PhoneDisplay(), Logger()
station.subscribe(phone)
station.subscribe(logger)
station.set_temperature(21.5)   # both react
station.unsubscribe(logger)
station.set_temperature(23.0)   # only phone reacts
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Subject</b> <span class="bp-dim">Observable</span></li><li><b>Observer</b> <span class="bp-dim">interface</span></li><li><b>ConcreteSubject</b></li><li><b>ConcreteObserver</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Subject keeps a list of observers and calls update() on change</li><li>Subject and observers vary independently; new listener, no edits</li><li>Observers subscribe / unsubscribe at runtime</li><li>Use when one change must fan out to many swappable consumers</li></ul>

</div>
</div>

<!--
Key points: Subject keeps a list of observers and calls update() on change | Subject and observers vary independently; new listener, no edits | Observers subscribe / unsubscribe at runtime | Use when one change must fan out to many swappable consumers

Problem: When one object's state must drive several others, hardwiring those dependents into it creates tight coupling and forces edits every time a new reactor appears. Observer lets the source publish changes while listeners attach and detach freely.

Real-world: GUI/event systems: DOM addEventListener, Qt signals and slots, JavaScript EventTarget. · Reactive streams and state: RxJS Observables, Redux store subscribe, Vue/Svelte reactivity. · Backend pub/sub and messaging: Django signals, Kafka/Redis pub-sub topics, asyncio event callbacks.

Gotcha: Naive synchronous notification can cause cascading or reentrant updates and lapsed-listener memory leaks; a slow or throwing observer also blocks the rest, so consider error isolation, async dispatch, or weak references.
-->

---

## Observer

<div class="bp-dim bp-mono text-sm mb-3">A subject's state change fans out as a notification wave that reaches only the currently subscribed observers, making selective broadcast visible.</div>

<ObserverBroadcastBoard />

---

## Command

<div class="bp-dim bp-mono text-sm mb-3">Wrap a request as a first-class object so you can store, queue, log, and undo it.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class Account:                       # Receiver
    def __init__(self): self.balance = 0
    def add(self, n): self.balance += n

class Deposit(Command):              # ConcreteCommand
    def __init__(self, acct, amount):
        self.acct, self.amount = acct, amount
    def execute(self): self.acct.add(self.amount)
    def undo(self): self.acct.add(-self.amount)

class Teller:                        # Invoker
    def __init__(self): self.history = []
    def run(self, cmd):
        cmd.execute()
        self.history.append(cmd)
    def undo(self):
        if self.history: self.history.pop().undo()

acct, teller = Account(), Teller()
teller.run(Deposit(acct, 100))
teller.run(Deposit(acct, 50))
print(acct.balance)   # 150
teller.undo()
print(acct.balance)   # 100
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Command</b> <span class="bp-dim">interface</span></li><li><b>ConcreteCommand</b></li><li><b>Receiver</b></li><li><b>Invoker</b></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>An action becomes an object (receiver + execute/undo) — passable data</li><li>Invoker depends only on Command; new action = new class</li><li>Undo/history for free: keep executed commands on a stack</li><li>Use for queuing, scheduling, macros, or rollback</li></ul>

</div>
</div>

<!--
Key points: An action becomes an object (receiver + execute/undo) — passable data | Invoker depends only on Command; new action = new class | Undo/history for free: keep executed commands on a stack | Use for queuing, scheduling, macros, or rollback

Problem: When callers invoke actions directly, every trigger point gets hard-wired to a specific receiver and method. You cannot queue, replay, log, or reverse those actions because they live as method calls, not data.

Real-world: GUI frameworks: Swing Action and the QAction/QUndoStack in Qt back menu items, toolbar buttons, and editor undo/redo. · Task and job queues such as Celery or java.util.concurrent Runnable, where a unit of work is shipped as an object to run later. · Database and migration systems with up()/down() steps, e.g. Alembic or Rails migrations, which are reversible commands.

Gotcha: Do not reach for it on trivial one-off calls: a class per action is overkill versus a plain function or lambda, and reliable undo() means every command must correctly capture and restore prior state.
-->

---

## Command

<div class="bp-dim bp-mono text-sm mb-3">A command is data on a stack: execute pushes a card, undo pops it, and effects reverse in exact opposite order.</div>

<CommandUndoStackPlayground />

---

## State

<div class="bp-dim bp-mono text-sm mb-3">Swap an object's behavior by swapping the state object it delegates to, instead of branching on a flag.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def push(self, player): ...


class Locked(State):
    def push(self, player):
        print("Locked: press play first")


class Playing(State):
    def push(self, player):
        print("Pausing"); player.state = Paused()


class Paused(State):
    def push(self, player):
        print("Resuming"); player.state = Playing()


class Player:                       # the Context
    def __init__(self):
        self.state = Locked()

    def push(self):                 # same call; current state decides behavior
        self.state.push(self)


p = Player()
p.push()                            # Locked: press play first
p.state = Paused()                  # unlock into a usable state
p.push()                            # Resuming -> now Playing
p.push()                            # Pausing  -> now Paused
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>State</b> <span class="bp-dim">abstract role</span></li><li><b>ConcreteState</b> <span class="bp-dim">Locked, Playing, Paused</span></li><li><b>Context</b> <span class="bp-dim">Player</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Context forwards each call to its state; states swap the next state</li><li>Each mode's rules in one class — no sprawling conditionals</li><li>Use when an object has a few modes with different allowed actions</li><li>Unlike Strategy: states know and trigger each other</li></ul>

</div>
</div>

<!--
Key points: Context forwards each call to its state; states swap the next state | Each mode's rules in one class — no sprawling conditionals | Use when an object has a few modes with different allowed actions | Unlike Strategy: states know and trigger each other

Problem: An object that behaves differently per mode accumulates a giant if/else or switch in every method. Adding a mode means editing them all, and each mode's rules end up scattered everywhere.

Real-world: TCP connection lifecycle (LISTEN, ESTABLISHED, CLOSED) where each state handles packets differently · Editor/workflow tools: a document moving through Draft, Review, Published with per-stage allowed actions · Game and UI character controllers (idle, running, jumping) driven by per-state update logic

Gotcha: Overkill for two simple modes or a fixed linear sequence; for a handful of values a plain enum is clearer than a class explosion. Also decide who owns transitions (states vs. context) and avoid duplicating that logic in both.
-->

---

## State

<div class="bp-dim bp-mono text-sm mb-3">A media player whose single Push button does something completely different depending on which state object is currently wired into the context.</div>

<StatePlayerMachine />

---

## Template Method

<div class="bp-dim bp-mono text-sm mb-3">Lock an algorithm's step order in a base class; let subclasses fill in only the steps that vary.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Beverage(ABC):
    def prepare(self):                # template method: fixed skeleton
        self.boil_water()
        self.brew()                   # abstract step
        self.pour_in_cup()
        if self.wants_condiments():   # hook: optional branch
            self.add_condiments()

    def boil_water(self):
        print("Boiling water")

    def pour_in_cup(self):
        print("Pouring into cup")

    def wants_condiments(self):       # hook with default
        return True

    @abstractmethod
    def brew(self): ...
    @abstractmethod
    def add_condiments(self): ...


class Tea(Beverage):
    def brew(self): print("Steeping the tea")
    def add_condiments(self): print("Adding lemon")
    def wants_condiments(self): return False   # override hook


class Coffee(Beverage):
    def brew(self): print("Dripping coffee")
    def add_condiments(self): print("Adding sugar and milk")


for drink in (Tea(), Coffee()):
    print(f"-- {type(drink).__name__} --")
    drink.prepare()
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>AbstractClass</b> <span class="bp-dim">defines template method + abstract steps + hooks</span></li><li><b>Template Method</b> <span class="bp-dim">fixed-order algorithm skeleton</span></li><li><b>ConcreteClass</b> <span class="bp-dim">implements abstract steps, may override hooks</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>A template method runs a fixed step sequence; subclasses fill steps</li><li>Shared workflow in one place; new variant = one subclass</li><li>Use when many implementations share a recipe but vary a few steps</li><li>Inheritance: the base owns control flow, steps can't be reordered</li></ul>

</div>
</div>

<!--
Key points: A template method runs a fixed step sequence; subclasses fill steps | Shared workflow in one place; new variant = one subclass | Use when many implementations share a recipe but vary a few steps | Inheritance: the base owns control flow, steps can't be reordered

Problem: When several variants share the same multi-step workflow but differ in a few steps, copying the whole sequence into each class duplicates logic and lets the order silently drift apart. Template Method captures the skeleton once and exposes only the variable steps.

Real-world: Python unittest.TestCase: the framework calls setUp, the test method, then tearDown in a fixed order you fill in. · Django class-based views: dispatch() drives the request lifecycle and you override get()/post() steps. · java.io.InputStream.read(byte[]) and Collections.sort delegating to your Comparable/compareTo step.

Gotcha: Deep step hierarchies and many protected hooks create fragile base-class coupling; if variants differ wholesale rather than per-step, prefer Strategy (composition) so behavior can change at runtime without subclassing.
-->

---

## Template Method

<div class="bp-dim bp-mono text-sm mb-3">The base class runs an immutable step pipeline while subclasses only swap the variable steps and toggle one hook.</div>

<TemplateMethodPipeline />

---

## Chain of Responsibility

<div class="bp-dim bp-mono text-sm mb-3">Pass a request along a line of handlers until one decides to handle it.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
class Approver:
    def __init__(self, name, limit):
        self.name, self.limit = name, limit
        self._next = None

    def then(self, nxt):
        self._next = nxt
        return nxt  # fluent chaining: returns the link just added

    def approve(self, amount):
        if amount <= self.limit:
            print(f"{self.name} approved ${amount:,}")
        elif self._next:
            self._next.approve(amount)          # forward down the chain
        else:
            print(f"${amount:,} exceeds all limits; escalate manually")


lead = Approver("Lead", 1_000)
lead.then(Approver("Director", 10_000)).then(Approver("VP", 100_000))

for amt in (500, 5_000, 250_000):
    lead.approve(amt)
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Handler</b> <span class="bp-dim">abstract Approver</span></li><li><b>ConcreteHandler</b> <span class="bp-dim">Lead, Director, VP</span></li><li><b>Client</b> <span class="bp-dim">builds the chain and sends the request</span></li><li><b>Request</b> <span class="bp-dim">the amount passed along the chain</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Each handler holds the next; it handles or forwards the request</li><li>Sender and receivers decoupled; reorder or insert without edits</li><li>Two flavors: first-capable stops, or every handler contributes</li><li>Use when the right handler is decided at runtime</li></ul>

</div>
</div>

<!--
Key points: Each handler holds the next; it handles or forwards the request | Sender and receivers decoupled; reorder or insert without edits | Two flavors: first-capable stops, or every handler contributes | Use when the right handler is decided at runtime

Problem: A single sender shouldn't hard-code which receiver handles each case, and the processing logic shouldn't collapse into one tangled block of nested if-else branches. Chain of Responsibility decouples the sender from the receiver and lets each step be added, removed, or reordered independently.

Real-world: Web framework middleware pipelines (Express, ASP.NET Core, Java Servlet filters) where each layer handles or passes the request. · Python's logging module: a LogRecord propagates up through parent loggers and their handlers. · GUI/event systems and exception handling that bubble an event or error up a hierarchy until something consumes it.

Gotcha: If no handler accepts the request and there's no terminal/default handler, it silently falls off the end and nothing happens; long or misordered chains also hurt debuggability since you can't tell up front who will respond. Avoid it when exactly one known receiver always handles the request and a direct call is simpler.
-->

---

## Chain of Responsibility

<div class="bp-dim bp-mono text-sm mb-3">A request token travels down a row of handler cards, each deciding to forward or handle, until one accepts or the token falls off the end into escalation.</div>

<ApprovalChainTracer />

---

## Visitor

<div class="bp-dim bp-mono text-sm mb-3">Bolt new operations onto a fixed class hierarchy without ever touching those classes again.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def accept(self, v): ...

class Num(Node):
    def __init__(self, value): self.value = value
    def accept(self, v): return v.num(self)

class Add(Node):
    def __init__(self, left, right): self.left, self.right = left, right
    def accept(self, v): return v.add(self)

class Visitor(ABC):
    @abstractmethod
    def num(self, n): ...
    @abstractmethod
    def add(self, n): ...

class Eval(Visitor):
    def num(self, n): return n.value
    def add(self, n): return n.left.accept(self) + n.right.accept(self)

class Print(Visitor):
    def num(self, n): return str(n.value)
    def add(self, n): return f"({n.left.accept(self)} + {n.right.accept(self)})"

tree = Add(Num(3), Add(Num(4), Num(5)))
print(tree.accept(Print()), "=", tree.accept(Eval()))  # (3 + (4 + 5)) = 12
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Element</b> <span class="bp-dim">Node</span></li><li><b>ConcreteElement</b> <span class="bp-dim">Num, Add</span></li><li><b>Visitor</b></li><li><b>ConcreteVisitor</b> <span class="bp-dim">Eval, Print</span></li><li><b>Client</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>accept(visitor) calls back the matching visit() — double dispatch, no isinstance ladders</li><li>New operation = new visitor; the element hierarchy never changes</li><li>Use when element types are stable but operations keep growing</li><li>Each operation lives in one testable visitor, not scattered</li></ul>

</div>
</div>

<!--
Key points: accept(visitor) calls back the matching visit() — double dispatch, no isinstance ladders | New operation = new visitor; the element hierarchy never changes | Use when element types are stable but operations keep growing | Each operation lives in one testable visitor, not scattered

Problem: When many unrelated operations pile onto a stable set of types, each class bloats and every new behavior forces edits across the whole hierarchy. Visitor pulls the operations out into separate classes so the types stay untouched.

Real-world: Python's ast.NodeVisitor / NodeTransformer, where visit_<NodeType> methods walk a parsed syntax tree. · Compilers and linters that run multiple passes (type checking, optimization, codegen) over a stable AST. · Document/serialization toolkits that export one object model to several formats (HTML, PDF, JSON) via separate exporter visitors.

Gotcha: Visitor optimizes for adding operations, not types: every new element class forces a new method on the visitor interface and edits to all existing visitors. Avoid it when the element hierarchy changes often but the operations are few.
-->

---

## Visitor

<div class="bp-dim bp-mono text-sm mb-3">The method that runs is chosen by two axes at once: the element's concrete type AND the selected visitor. Visitor makes that two-axis (double) dispatch the whole point.</div>

<VisitorDoubleDispatchTracer />

---

## Mediator

<div class="bp-dim bp-mono text-sm mb-3">Route peer-to-peer chatter through one hub so objects coordinate without knowing each other.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: "Device", event: str) -> None: ...


class Device:
    def __init__(self, name: str, hub: Mediator) -> None:
        self.name, self.hub = name, hub


class MotionSensor(Device):
    def detect(self) -> None:
        print(f"{self.name}: motion detected")
        self.hub.notify(self, "motion")


class Lamp(Device):
    def switch(self, on: bool) -> None:
        print(f"{self.name}: {'ON' if on else 'OFF'}")


class HomeHub(Mediator):
    def __init__(self) -> None:
        self.lamp = Lamp("Lamp", self)
        self.sensor = MotionSensor("Sensor", self)

    def notify(self, sender: Device, event: str) -> None:
        if event == "motion":
            self.lamp.switch(True)


hub = HomeHub()
hub.sensor.detect()  # Sensor: motion detected -> Lamp: ON
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Mediator</b> <span class="bp-dim">interface</span></li><li><b>ConcreteMediator</b> <span class="bp-dim">HomeHub</span></li><li><b>Colleague</b> <span class="bp-dim">Device base</span></li><li><b>ConcreteColleague</b> <span class="bp-dim">MotionSensor, Lamp</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Components report to one mediator instead of calling peers</li><li>Loosely coupled — each depends only on the mediator</li><li>Use for a tight cluster whose interactions keep sprawling</li><li>Unlike Observer: the mediator orchestrates, not just broadcasts</li></ul>

</div>
</div>

<!--
Key points: Components report to one mediator instead of calling peers | Loosely coupled — each depends only on the mediator | Use for a tight cluster whose interactions keep sprawling | Unlike Observer: the mediator orchestrates, not just broadcasts

Problem: When many objects must react to each other, they accumulate direct references and tangled callbacks, turning a small change into edits across the whole web. Mediator collapses that many-to-many mesh into a star with a single coordinator at the center.

Real-world: GUI dialog/form coordinators (a controller that enables a submit button only when fields validate) and frameworks like Qt's signal/slot wiring routed through a parent controller. · Chat servers and message brokers: a room or hub relays messages between participants who never reference each other directly. · Air traffic control and microservice orchestrators / API gateways that centralize routing instead of letting services call each other directly.

Gotcha: The mediator absorbs everyone's coupling, so it can swell into a God Object packed with conditional routing logic; if interactions are simple or stable, direct calls or an Observer are lighter than a central hub.
-->

---

## Mediator

<div class="bp-dim bp-mono text-sm mb-3">A mediator replaces a tangled mesh of direct object-to-object links with a clean star routed through one hub, and the edge count makes the savings undeniable.</div>

<MediatorStarTopology />

---

## Memento

<div class="bp-dim bp-mono text-sm mb-3">Snapshot and restore an object's private state via an opaque token, without leaking its internals.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
class Game:                                  # Originator
    def __init__(self):
        self.level, self.hp = 1, 100

    def save(self) -> "_GameState":
        return _GameState(self.level, self.hp)   # seal a snapshot

    def restore(self, s: "_GameState") -> None:
        self.level, self.hp = s.level, s.hp      # unpack my own state

    def __repr__(self):
        return f"level={self.level} hp={self.hp}"


class _GameState:                            # Memento, opaque to caretaker
    def __init__(self, level, hp):
        self.level, self.hp = level, hp


class Checkpoints:                           # Caretaker
    def __init__(self):
        self._stack: list[_GameState] = []

    def save(self, g: Game):
        self._stack.append(g.save())         # store, never inspect

    def undo(self, g: Game):
        if self._stack:
            g.restore(self._stack.pop())


g, cp = Game(), Checkpoints()
cp.save(g)
g.level, g.hp = 2, 60
print("now:", g)            # now: level=2 hp=60
cp.undo(g)
print("undone:", g)         # undone: level=1 hp=100
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Originator</b></li><li><b>Memento</b></li><li><b>Caretaker</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Originator packs its private fields into a Memento and unpacks them</li><li>Caretaker stacks Mementos and triggers save/restore, opaque to it</li><li>New state changes only Originator + Memento; caretaker untouched</li><li>Use for undo/redo, checkpoints, rollback with encapsulated snapshots</li></ul>

</div>
</div>

<!--
Key points: Originator packs its private fields into a Memento and unpacks them | Caretaker stacks Mementos and triggers save/restore, opaque to it | New state changes only Originator + Memento; caretaker untouched | Use for undo/redo, checkpoints, rollback with encapsulated snapshots

Problem: Features like undo, checkpoints, and versioning need to roll an object back to an earlier state. Exposing and copying its fields to do this breaks encapsulation and scatters fragile snapshot logic across callers.

Real-world: Python's pickle / copy.deepcopy used to snapshot and reload object state · Database transaction savepoints with ROLLBACK TO restoring an earlier state · Editor and IDE undo/redo histories (text editors, Photoshop history panel)

Gotcha: Deep snapshots of large or frequently-changing state can blow up memory; cap history depth or store diffs instead of full copies, and watch for shared mutable references that quietly alias the live object.
-->

---

## Memento

<div class="bp-dim bp-mono text-sm mb-3">State lives in the Originator; the Caretaker only holds opaque snapshots and pops them to rewind.</div>

<MementoUndoStack />

---
layout: default
class: section-slide
---

<div class="ghost-num">04</div>
<div class="section-body">
  <div class="accent-bar"></div>
  <div class="bp-eyebrow mb-3">MODULE 04</div>
  <h1>Additional Patterns</h1>
  <div class="flex gap-3 mt-6"><span class="bp-chip">beyond the GoF 23</span></div>
</div>

---

## Null Object Pattern

<div class="bp-dim bp-mono text-sm mb-3">Swap null for a do-nothing object that shares the interface, so callers never branch on absence.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, msg: str) -> None: ...


class ConsoleLogger(Logger):
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")


class NullLogger(Logger):
    def log(self, msg: str) -> None:
        pass  # absence of behavior is still a behavior


def make_logger(verbose: bool) -> Logger:
    return ConsoleLogger() if verbose else NullLogger()


def run_job(logger: Logger) -> int:
    logger.log("job started")          # no `if logger:` ever needed
    result = sum(range(5))
    logger.log(f"job done -> {result}")
    return result


print("verbose:", run_job(make_logger(True)))
print("quiet:  ", run_job(make_logger(False)))
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>AbstractOperation</b> <span class="bp-dim">interface, e.g. Logger</span></li><li><b>RealOperation</b> <span class="bp-dim">e.g. ConsoleLogger</span></li><li><b>NullObject</b> <span class="bp-dim">e.g. NullLogger</span></li><li><b>Client</b> <span class="bp-dim">calls through the interface, never checks for null</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>A Null variant implements the interface with no-op / safe-default methods</li><li>Callers skip null guards; the happy path stays readable</li><li>Stateless — share one immutable singleton</li><li>Use when absence is normal; avoid when missing means a bug</li></ul>

</div>
</div>

<!--
Key points: A Null variant implements the interface with no-op / safe-default methods | Callers skip null guards; the happy path stays readable | Stateless — share one immutable singleton | Use when absence is normal; avoid when missing means a bug

Problem: Optional collaborators force defensive null checks at every call site; miss one and you crash at runtime. The pattern removes that scatter by making "nothing to do" a real, callable object.

Real-world: Python's logging.NullHandler, attached to library loggers so emitting records is a safe no-op until an app configures handlers. · Slf4j's NOPLogger / Logback NOPAppender and similar no-op logger backends in the JVM ecosystem. · Domain defaults like a Guest/anonymous user object returned from a lookup so callers treat found and not-found uniformly.

Gotcha: A null object that silently swallows everything can mask real bugs; if a missing collaborator means something is genuinely broken, prefer failing fast (raise or return Optional) instead of quietly doing nothing.
-->

---

## Null Object Pattern

<div class="bp-dim bp-mono text-sm mb-3">A real object and a null object are interchangeable behind one interface; only the method body differs, never the call site.</div>

<NullObjectCallTracer />

---

## Repository

<div class="bp-dim bp-mono text-sm mb-3">Hide data access behind a collection-like interface so the domain never sees SQL or an ORM.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order): ...
    @abstractmethod
    def get(self, oid): ...


class InMemoryOrders(OrderRepository):
    def __init__(self):
        self._db = {}
    def add(self, order):
        self._db[order.id] = order
    def get(self, oid):
        return self._db.get(oid)


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo            # depends on the interface
    def place(self, order):
        self.repo.add(order)        # no SQL in the domain
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Repository</b> <span class="bp-dim">interface, e.g. OrderRepository</span></li><li><b>ConcreteRepository</b> <span class="bp-dim">InMemoryOrders / SqlOrders</span></li><li><b>Client</b> <span class="bp-dim">OrderService, talks to the interface</span></li><li><b>Entity</b> <span class="bp-dim">Order</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Domain depends on a repository interface, not on SQL</li><li>Swap the store (memory, SQL, Mongo) without touching callers</li><li>Tests run against an in-memory repo — no database</li><li>One place maps rows to objects</li></ul>

</div>
</div>

<!--
Key points: Domain depends on a repository interface, not on SQL | Swap the store (memory, SQL, Mongo) without touching callers | Tests run against an in-memory repo — no database | One place maps rows to objects

Problem: When services build queries inline, persistence details leak everywhere and the domain becomes impossible to test without a database. A Repository gives the domain one in-memory-looking API and keeps storage swappable.

Real-world: Spring Data / JPA repositories · Django's ORM manager and the repository layer on top of it · SQLAlchemy session wrapped in a domain repository

Gotcha: Don't let the repository balloon into a god-object with a method per query; keep it focused on one aggregate, and avoid leaking ORM query objects back through the interface.
-->

---

## Repository

<div class="bp-dim bp-mono text-sm mb-3">The domain calls the same repository interface; swapping the backing store changes where data lives, never the caller.</div>

<RepositorySwapStore />

---

## MVC

<div class="bp-dim bp-mono text-sm mb-3">Split a UI into Model (data), View (presentation), and Controller (input) so each owns exactly one job.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
class Model:
    def __init__(self):
        self.count = 0
        self._views = []
    def attach(self, view):
        self._views.append(view)
    def increment(self):
        self.count += 1
        for v in self._views:
            v.render(self.count)


class View:
    def render(self, count):
        print(f"[View] count = {count}")


class Controller:
    def __init__(self, model):
        self.model = model
    def on_click(self):
        self.model.increment()      # input -> model
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Model</b> <span class="bp-dim">state + notify</span></li><li><b>View</b> <span class="bp-dim">render only</span></li><li><b>Controller</b> <span class="bp-dim">input -> model</span></li><li><b>User</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Model holds state and rules; never draws</li><li>View renders the model; never mutates it</li><li>Controller turns input into model updates</li><li>Model notifies views on change (observer underneath)</li></ul>

</div>
</div>

<!--
Key points: Model holds state and rules; never draws | View renders the model; never mutates it | Controller turns input into model updates | Model notifies views on change (observer underneath)

Problem: When data, rendering, and input handling tangle together, every change risks the others and nothing is reusable. MVC routes input one way — Controller to Model to View — so concerns stay separate.

Real-world: Django and Rails (MVC / MVT web stacks) · iOS UIKit view controllers · classic Swing / desktop UIs

Gotcha: Beware the 'fat controller' or 'massive view controller' where logic creeps in; keep business rules in the model and presentation in the view.
-->

---

## MVC

<div class="bp-dim bp-mono text-sm mb-3">Input flows Controller to Model to View in a one-way loop; each part owns one job and never reaches into the others.</div>

<MvcRoundTrip />

---

## Dependency Injection

<div class="bp-dim bp-mono text-sm mb-3">Hand a class its dependencies from outside instead of constructing them inside, so they can be swapped.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Mailer(ABC):
    @abstractmethod
    def send(self, to, body): ...


class SmtpMailer(Mailer):
    def send(self, to, body):
        print(f"SMTP -> {to}")


class FakeMailer(Mailer):           # swap in for tests
    def __init__(self):
        self.sent = []
    def send(self, to, body):
        self.sent.append(to)


class Signup:
    def __init__(self, mailer: Mailer):   # injected, not constructed
        self.mailer = mailer
    def register(self, email):
        self.mailer.send(email, "welcome")
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Service</b> <span class="bp-dim">depends on an abstraction</span></li><li><b>Dependency interface</b> <span class="bp-dim">Mailer</span></li><li><b>Real / Fake implementations</b></li><li><b>Injector / composition root</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Pass collaborators in; don't build them inside</li><li>Depend on an abstraction, not a concrete class</li><li>Swap real for fake to test in isolation</li><li>A container wires the graph once</li></ul>

</div>
</div>

<!--
Key points: Pass collaborators in; don't build them inside | Depend on an abstraction, not a concrete class | Swap real for fake to test in isolation | A container wires the graph once

Problem: A class that news-up its own collaborators is welded to them — you can't substitute a fake in a test or a different implementation in production. Injecting dependencies makes the seam explicit and swappable.

Real-world: Spring's IoC container · Angular's injector · pytest fixtures / FastAPI Depends

Gotcha: DI is a technique, not a framework requirement; over-using a magic container can hide the object graph. For small programs, plain constructor injection is enough.
-->

---

## Dependency Injection

<div class="bp-dim bp-mono text-sm mb-3">A dependency built inside a class is welded in; injected from outside, the same slot accepts a real or a fake at will.</div>

<DependencyInjector />

---

## Specification

<div class="bp-dim bp-mono text-sm mb-3">Wrap a business rule in a small predicate object you can combine with and / or / not.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from abc import ABC, abstractmethod


class Spec(ABC):
    @abstractmethod
    def is_satisfied(self, item): ...
    def __and__(self, other):
        return AndSpec(self, other)


class AndSpec(Spec):
    def __init__(self, a, b):
        self.a, self.b = a, b
    def is_satisfied(self, item):
        return self.a.is_satisfied(item) and self.b.is_satisfied(item)


class IsActive(Spec):
    def is_satisfied(self, u):
        return u.active


class IsPremium(Spec):
    def is_satisfied(self, u):
        return u.tier == "premium"


rule = IsActive() & IsPremium()
# [u for u in users if rule.is_satisfied(u)]
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Specification</b> <span class="bp-dim">interface, is_satisfied</span></li><li><b>Leaf specs</b> <span class="bp-dim">IsActive, IsPremium</span></li><li><b>Composite specs</b> <span class="bp-dim">And / Or / Not</span></li><li><b>Candidate item</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>Each rule is an object with is_satisfied(item)</li><li>Compose with and / or / not into bigger rules</li><li>Reuse one spec for filtering, validation, and queries</li><li>Name the rule once; read it like a sentence</li></ul>

</div>
</div>

<!--
Key points: Each rule is an object with is_satisfied(item) | Compose with and / or / not into bigger rules | Reuse one spec for filtering, validation, and queries | Name the rule once; read it like a sentence

Problem: Validation and selection rules duplicated across queries, UI, and services drift out of sync. A Specification captures one rule as a reusable object, and composes with others instead of copy-pasting boolean logic.

Real-world: Domain-Driven Design specification objects · rule engines / eligibility checks · query builders that AND/OR criteria

Gotcha: For a single trivial check a plain function is simpler; reach for Specification when rules are reused, combined, or need to be named and tested on their own.
-->

---

## Specification

<div class="bp-dim bp-mono text-sm mb-3">Business rules are tiny predicate objects; compose them with AND / OR / NOT and the live filter updates instantly.</div>

<SpecificationComposer />

---

## Game Loop

<div class="bp-dim bp-mono text-sm mb-3">Run forever: process input, update the world by elapsed time, render — decoupled from wall-clock speed.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import time


class Game:
    def __init__(self):
        self.running = True
        self.x = 0
    def process_input(self): ...
    def update(self, dt):
        self.x = (self.x + 1) % 10
    def render(self):
        print(f"frame: x={self.x}")
    def run(self):
        last = time.time()
        while self.running:
            now = time.time()
            dt = now - last
            last = now
            self.process_input()
            self.update(dt)
            self.render()
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Game loop</b> <span class="bp-dim">the while</span></li><li><b>Input stage</b></li><li><b>Update stage</b> <span class="bp-dim">advances by dt</span></li><li><b>Render stage</b></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>One loop: input -> update(dt) -> render, repeating</li><li>Update by elapsed time, not frame count</li><li>Render rate can vary; simulation stays stable</li><li>A fixed timestep catches up with extra updates</li></ul>

</div>
</div>

<!--
Key points: One loop: input -> update(dt) -> render, repeating | Update by elapsed time, not frame count | Render rate can vary; simulation stays stable | A fixed timestep catches up with extra updates

Problem: If game logic is driven by the rendering rate, the world runs faster on fast machines and stutters on slow ones. A game loop separates 'how fast we draw' from 'how far time advanced', keeping play consistent.

Real-world: every game engine (Unity, Unreal, Godot main loop) · physics simulations · animation / render loops (requestAnimationFrame)

Gotcha: A naive loop that updates once per render couples simulation to frame rate; use a fixed timestep (or multiply by dt) so behavior is the same on fast and slow machines.
-->

---

## Game Loop

<div class="bp-dim bp-mono text-sm mb-3">One loop forever: process input, update the world by dt, render — decoupled from wall-clock so play stays smooth.</div>

<GameLoopTicker />

---

## Thread Pool

<div class="bp-dim bp-mono text-sm mb-3">Keep a fixed crew of worker threads pulling tasks from a shared queue instead of spawning one per task.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
from concurrent.futures import ThreadPoolExecutor
import time


def work(n):
    time.sleep(0.1)         # pretend it is slow
    return n * n


# a fixed crew of 3 threads, shared queue under the hood
with ThreadPoolExecutor(max_workers=3) as pool:
    futures = [pool.submit(work, i) for i in range(8)]
    for f in futures:
        print(f.result())
# 8 tasks submitted; only 3 run at once, the rest queue
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Thread pool / executor</b></li><li><b>Worker threads</b> <span class="bp-dim">fixed N</span></li><li><b>Task queue</b></li><li><b>Client</b> <span class="bp-dim">submits tasks</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>A fixed set of workers pulls from one queue</li><li>Bounded concurrency: at most N run at once</li><li>Reuse threads — no per-task create/destroy</li><li>Extra work waits in the queue (back-pressure)</li></ul>

</div>
</div>

<!--
Key points: A fixed set of workers pulls from one queue | Bounded concurrency: at most N run at once | Reuse threads — no per-task create/destroy | Extra work waits in the queue (back-pressure)

Problem: Spawning a thread per task is expensive and unbounded — thousands of tasks can exhaust the machine. A thread pool reuses a fixed number of workers and queues the overflow, capping concurrency.

Real-world: Java's ExecutorService · Python's ThreadPoolExecutor / Gunicorn workers · web-server request worker pools

Gotcha: Sizing matters: too few workers starves throughput, too many thrash the CPU or exhaust connections; and a slow task can block a worker, so keep tasks bounded or use a separate pool.
-->

---

## Thread Pool

<div class="bp-dim bp-mono text-sm mb-3">A fixed crew of workers pulls tasks from a shared queue; only N run at once while the rest wait in line.</div>

<ThreadPoolDispatcher />

---

## Producer-Consumer

<div class="bp-dim bp-mono text-sm mb-3">Decouple producers from consumers with a bounded buffer; each side blocks when it's full or empty.</div>

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start">
<div class="min-w-0 patcode">

```python
import queue, threading, time

buffer = queue.Queue(maxsize=5)   # bounded buffer


def producer():
    for i in range(10):
        buffer.put(i)             # blocks when full
        time.sleep(0.05)


def consumer():
    while True:
        item = buffer.get()       # blocks when empty
        print("consumed", item)
        buffer.task_done()


threading.Thread(target=producer).start()
threading.Thread(target=consumer, daemon=True).start()
```

</div>
<div class="min-w-0">

<div class="bp-eyebrow mb-2">ROLES</div>
<ul class="roles"><li><b>Producer</b> <span class="bp-dim">puts items</span></li><li><b>Bounded buffer / queue</b></li><li><b>Consumer</b> <span class="bp-dim">takes items</span></li><li><b>Blocking condition</b> <span class="bp-dim">full / empty</span></li></ul>

<div class="bp-eyebrow mb-2">KEY POINTS</div>
<ul class="kpts bp-dim text-sm"><li>A bounded buffer sits between producers and consumers</li><li>Producer blocks when full; consumer when empty</li><li>The buffer absorbs bursts and applies back-pressure</li><li>Sides scale independently — add more of either</li></ul>

</div>
</div>

<!--
Key points: A bounded buffer sits between producers and consumers | Producer blocks when full; consumer when empty | The buffer absorbs bursts and applies back-pressure | Sides scale independently — add more of either

Problem: When a fast producer feeds a slow consumer directly, one waits on the other and they're tightly coupled. A bounded buffer between them smooths bursts and lets each run at its own pace, blocking only at the limits.

Real-world: Kafka / RabbitMQ message queues · logging with an async buffered handler · OS pipes and bounded channels (Go channels)

Gotcha: An unbounded buffer just hides the imbalance until memory runs out; keep it bounded so back-pressure is real, and size it for expected burstiness.
-->

---

## Producer-Consumer

<div class="bp-dim bp-mono text-sm mb-3">A bounded buffer decouples a producer from a consumer; each blocks when the buffer is full or empty.</div>

<ProducerConsumerBuffer />

---
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

---
layout: end
---

<div class="text-center">
  <div class="bp-eyebrow mb-3">END OF DECK 3</div>
  <h1>Questions?</h1>
  <div class="bp-dim bp-mono mt-3">Foundations &rarr; Principles &rarr; Patterns &rarr; Interviews</div>
</div>
