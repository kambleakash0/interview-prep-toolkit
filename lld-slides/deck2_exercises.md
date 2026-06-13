# Deck 2 — Principles & UML · Exercises

Practice tasks for **Deck 2** (Design Principles · SOLID). Do them in **Python**; aim for clean, well-named classes. (UML lessons have no exercises.)

---

## Module 01 · Design Principles

- [ ] **DRY** — Extract duplicated tax-calculation logic from three region-specific order processors into a single `TaxCalculator` interface with per-region implementations.

- [ ] **KISS** — Refactor an over-engineered `StringFormatter` system into a single method that trims and capitalizes a name.

- [ ] **YAGNI** — Simplify an over-engineered password validator (multiple rule interfaces and classes) into a single class with one method.

- [ ] **Law of Demeter** — Refactor an `OrderSummaryPrinter` that reaches through `customer.get_address().get_city()` so it instead calls a single delegation method on `Order`.

- [ ] **Separation of Concerns** — Split a monolithic `ReportGenerator` (fetches data, formats it, and emails it) into separate data-source, formatter, and delivery components.

- [ ] **Coupling & Cohesion** — Refactor a `NotificationManager` that instantiates SMTP/SMS clients directly so it depends on a `Notifier` interface and contains only notification logic.

- [ ] **Composing Objects** — Replace a deep `Vehicle → Car → SportsCar` inheritance chain with a `Car` that composes swappable `Engine` and `Transmission` parts.

---

## Module 02 · SOLID Principles

- [ ] **Single Responsibility (SRP)** — Refactor a god-class `OrderService` into three focused classes: `OrderProcessor`, `InventoryManager`, and `NotificationService`.

- [ ] **Open/Closed (OCP)** — Refactor a `ShippingCostCalculator` to use the strategy pattern, replacing if-else chains with concrete shipping classes implementing a shared interface.

- [ ] **Liskov Substitution (LSP)** — Refactor `ReadOnlyDocument` and `EditableDocument` to honor substitutability by splitting capabilities into `Document` and `Editable` interfaces.

- [ ] **Interface Segregation (ISP)** — Split a fat `MultiFunctionDevice` into `Printable`, `Scannable`, `Faxable`, and `Stapleable` so that `BasicPrinter` implements only `Printable`.

- [ ] **Dependency Inversion (DIP)** — Refactor `OrderService` to depend on a `Database` abstraction instead of a concrete `MySQLDatabase`.
