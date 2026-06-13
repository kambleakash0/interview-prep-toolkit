# Deck 1 — Foundations · Exercises

Practice tasks that accompany **Deck 1** (LLD Introduction · OOP Fundamentals · Class Relationships). Each maps to a slide in `deck1.md`. Do them in **Python**; aim for clean, well-named classes.

---

## Module 01 · LLD Introduction

- [ ] **Types of LLD interviews** — Identify which interview format (OOD, Machine Coding, Concurrency, API, or Schema Design) would best assess a developer's ability to design a **thread-safe caching layer**, and justify why.

---

## Module 02 · OOP Fundamentals

- [ ] **Classes & Objects** — Implement a `BankAccount` class with `deposit`, `withdraw`, and `get_balance` methods that validate amounts and maintain independent balances across multiple accounts.

- [ ] **Enums** — Create a `TrafficLight` enum with `RED`, `GREEN`, `YELLOW` constants, each carrying a duration property and a `next()` method that cycles through the states.

- [ ] **Interfaces** — Implement a `Formatter` interface with `PlainFormatter` and `JsonFormatter` subclasses, then use dependency injection in a `Logger` class to swap formatting implementations at runtime.

- [ ] **Encapsulation** — Implement a `TemperatureSensor` that stores readings privately, validates values between −50 and 150 degrees, and returns only copies of its internal data.

- [ ] **Abstraction** — Implement `Circle` and `Rectangle` classes extending an abstract `Shape`, where `describe()` in the base class calls the overridden `area()` method.

- [ ] **Inheritance** — Implement a `BankAccount` base class with `deposit`/`withdraw`, then create `SavingsAccount` (enforce a $100 minimum) and `CheckingAccount` (allow overdraft) subclasses.

- [ ] **Polymorphism** — Implement three `Discount` subclasses (`Percentage`, `Flat`, `BuyOneGetOneFree`) where each overrides `apply()` to calculate the price differently.

---

## Module 03 · Class Relationships

- [ ] **Association** — Implement a Course Platform where `Instructor` teaches `Course`s and `Student`s enroll in `Course`s, keeping both sides of the relationship synchronized.

- [ ] **Aggregation** — Implement a shopping-cart system where products live in a catalog and customers add them to carts; demonstrate that clearing a cart does **not** destroy the products.

- [ ] **Composition** — Build a `Computer` class that composes `CPU`, `RAM`, and `HardDrive` internally, then upgrade the `RAM` without breaking ownership.

- [ ] **Dependency** — Implement a `FileConverter` that accepts `FileReader`, `FormatParser`, and `FileWriter` as **method parameters** to orchestrate a CSV-to-JSON conversion without storing them as fields.

- [ ] **Realization** — Implement a `Drawable` interface with `Circle`, `Rectangle`, and `Triangle` classes that each compute their own area and draw representation.
