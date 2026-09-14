# AI Report

## AI tools used


| Tool             | Role                                                                                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ChatGPT - GPT5.6 Sol (High Thinking)**      | Pre-coding: broke the assignment spec into an implementation order, discussed architecture tradeoffs (atomic ingestion, validation boundaries), and drafted prompts for Cursor. |
| **Cursor Agent - Composer model** | Primary implementation: backend (FastAPI), tests, frontend scaffold, and initial UI.                                                                                            |
| **Cursor Chat**  | Targeted iteration: UI refinements, bug fixes, and clarifying requirements (e.g. keyboard Tab vs navigation tabs).                                                              |


Total build time: ~90 minutes (excluding this report).

## How I worked with AI

This was collaborative, not autopilot. I owned **spec interpretation**, **layer boundaries** (routes → services → validators → repositories), and **UI/UX direction**. AI drafted code quickly; I reviewed every layer, corrected misunderstandings, and ran the full test suite before considering a workflow done.

ChatGPT was used *before* heavy coding to sanity-check design choices. Cursor Agent executed against a structured plan. I treated AI output as a first draft — especially for validation logic and error semantics — and verified behavior with tests and manual demo flows.

## Example prompts

### **ChatGPT (planning) - GPT5.6 Sol (High Thinking)**

- **Role-based task prompt** 
  > "You are a senior AI Engineer with 10 years of SWE/ML experience. Your task is to evaluate and give the most practical recommendations on the following assignment, potential approaches/tradeoffs. And briefly suggest solutions for discussion later."
  -- Followed by the full assignment upload, user prompt on thought process and reasoning behind solutions. 
- **High-level understanding and overview** 
  > "Draft a high-level solution architecture before implementation, covering the main components, data flow, responsibilities, and key design decisions.Identify any ambiguous requirements, assumptions, edge cases, or behavioral decisions that could materially affect the implementation. Ask targeted clarifying questions, provide a recommended default and tradeoff for each where useful, and continue until the core architecture, API behavior, validation rules, and scope are sufficiently defined to implement without major assumptions."
- **High-level understanding and overview** 
  > "Convert the agreed architecture and requirements into a comprehensive Cursor build prompt.The prompt should be implementation-ready and include the project objective, architecture, component responsibilities, API contracts, validation rules, edge cases, error handling, testing strategy, acceptance criteria, implementation order, explicit non-goals, and the key design decisions we already agreed on. Preserve the principle of building the simplest correct solution without unnecessary abstraction or scope expansion."


### **Cursor (implementation) - Composer model (switch between modes)**

- **Backend [Build Mode]** 
  > "Built a lightweight FastAPI backend that supports schema registration, validated atomic data ingestion, dashboard configuration, and dashboard data generation using simple in-memory storage. The design prioritizes correctness, simplicity, clear separation of concerns, explicit validation, testability, and minimal extensibility without unnecessary infrastructure or overengineering..." 
  -- Actual prompt is structured and 5800 words long.
- **Frontend [Agent Mode]** 
  > "Built a lightweight React + TypeScript single-page UI for schema registration, data ingestion, dashboard configuration, and dashboard viewing against the existing backend. The frontend stays intentionally thin, using local state, native API calls, minimal styling, and clear error handling without duplicating backend business logic or adding unnecessary frontend frameworks..." 
  -- Actual prompt is structured and 1450 words long.
- **Finetuning [Agent Mode]** 
> "Refine the existing UI to improve usability and visual hierarchy by keeping navigation visible, adding contextual instructions, separating dashboard view configurations, and applying consistent styling to Add/Remove actions. Preserve existing backend behavior and lightweight architecture while improving keyboard-assisted input, accessibility, and clarity across the workflow..."
-- Actual prompt is structured and 375 words long.




## One AI suggestion accepted

> Centralize row validation in `app/validation/row_validator.py` instead of validating inside the ingestion route.

**Why:** Validation is a core domain concern with non-obvious edge cases (bool/int, optional null, batch error collection). A dedicated module keeps routes thin, makes unit testing straightforward, and gives one place to extend type rules later.

## One AI suggestion rejected

> Introduce a generic plugin/strategy registry for dashboard view handlers.

**Why:** Only two view types exist (`summary`, `table`). Typed dispatch in `DashboardService` is readable in one sitting. A registry adds indirection without benefit at this scale; it can be introduced when view types genuinely multiply.

**Also rejected (my call):** third-party DI framework, generic `Repository[T]`, and showing all four UI workflows stacked on one page — each added ceremony without meeting assignment goals.

## Where AI got it wrong (and how I caught it)


| Issue/Bug                                                                           | Manual Fix                                                                                        |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| "Tab autofill" interpreted as **navigation tab clicks** prefilling forms            | Clarified: **keyboard Tab** on empty fields should accept placeholder suggestions only.           |
| Renamed Pydantic `schema` field to `schema_name`; missed references in `generate()` | Found via failing dashboard tests; fixed before shipping.                                         |
| Register Dashboard panel looked unfilled                                            | White semi-transparent fieldsets washed out purple theme; tinted inner sections to match sidebar. |
| Forms prefilled on page load                                                        | Removed load-time defaults; fields start empty with placeholders until user presses Tab.          |


These are typical AI failure modes: plausible but wrong requirement interpretation, incomplete refactors, and UI that looks correct in code but not in the browser. Tests and a quick manual walkthrough caught all of them.

## Validation approach

- **Automated:** `pytest` — 33 backend tests (happy paths, 409/404/422, atomic batch, no-data dashboard).
- **Manual:** Full UI demo flow (register schema → ingest → register dashboard → view results) against a running backend.
- **Contract check:** FastAPI `/docs` OpenAPI review for error shapes and status codes.
- **Principle:** Backend remains source of truth for validation; frontend displays errors, does not reimplement business rules.



## Reflections

AI made this project **fast to scaffold and slow to trust**. The payoff came from using ChatGPT for architecture *before* coding, using Cursor for boilerplate and breadth, and applying judgment on scope: reject abstractions early, test invariants explicitly, and treat every AI misunderstanding as a spec-clarification opportunity — not a reason to add complexity.