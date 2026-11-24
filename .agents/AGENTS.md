# EstateFlow agent guidance

## Engineering and architecture standard

- Work as an experienced senior software engineer and architect. Deliver professional, industry-standard work that a teammate can understand, test, operate, and extend.
- Before changing a service boundary, public interface, or data model, check who owns it, which callers depend on it, and how the change affects testing, deployment, and recovery. Record consequential trade-offs and decisions in the active phase plan.
- Use the simplest design that fully meets the requirement and fits the existing architecture. Keep the implementation proportional to the MVP while preserving correctness, security, and maintainability.

## Before making changes

- Start with the [roadmap](../Documentation/implementation/roadmap.md). Read the active phase plan, its subphase when applicable, and the design references it links. Use the [repository layout](../Documentation/implementation/repository-layout.md) to find the owner of each change.
- Use `Documentation/` for current project design and update it when the work calls for design changes. Edit the organizer’s `docs/` only if explicitly requested. Ignore the outdated proposal at `docs/Proposal.docx` and proposal-era material when determining current requirements. Base the build on the [MVP design](../Documentation/mvp/agent-details/agent-details.md) and use the [complete scope](../Documentation/complete%20scope/complete-scope.md) for background.
- When the plan and design disagree, record the conflict and its effect in the active plan. Use confirmed MVP decisions for the affected work. Bring material product decisions to the user if the available sources do not resolve them.

## Find the design for a phase

Before drafting or revising a phase plan, use the roadmap to identify the phase’s scope, then open the applicable specs below and follow their links to detailed contracts. Use those sources to define tasks, service boundaries, and acceptance checks. Link each phase or subphase to the specific sections it relies on. Record any unresolved requirement in the plan.

| Area | Design references |
| --- | --- |
| Frontend behavior | Screens, user actions, and application states. [Frontend spec](../Documentation/mvp/containers/frontend/frontend.md) |
| UI and visual design | Theme, layouts, accessibility, and the public listing example. [UI spec](../Documentation/mvp/containers/frontend/ui.md) · [Courtyard House showcase](../Documentation/mvp/showcase/index.html) |
| Backend services and jobs | Runtime roles, ownership, and links to Property, Engagement, Agent API, dispatcher, workers, and RabbitMQ specs. [Container index](../Documentation/mvp/containers/containers.md) |
| AI workflows | Agent behavior, handoffs, and acceptance scenarios. Follow the container index for agent-specific implementation specs. [MVP agent design](../Documentation/mvp/agent-details/agent-details.md) |
| Data and transactions | PostgreSQL tables and views, plus rules for writes, reads, permissions, and retries. [Schema](../Documentation/mvp/database/schema.md) · [Database contracts](../Documentation/mvp/database/contracts.md) |
| Stack, AWS, and CI | Technology choices, shared development dependencies, hosted deployment, and checks. [Technology stack](../Documentation/mvp/teach-stack/tech-stack.md) · [CI and release design](../Documentation/mvp/ci/cd/ci.md) |

## Organize implementation plans

- Keep the [roadmap](../Documentation/implementation/roadmap.md) brief. Give each phase one coherent outcome, explicit dependencies, and an acceptance check. Split work where a phase can own and verify a deliverable independently. Keep tightly coupled work in the same phase.
- When a future phase is ready to plan, create its numbered folder under `Documentation/implementation/` and link to its main plan from the roadmap. Follow the Phase 1 pattern. For example, Phase 2 goes in `Documentation/implementation/phase-02/phase2.md`. Include scope, dependencies, references to current design docs, a progress checklist, acceptance checks, and a decision log. Base the plan on the files and interfaces that exist at that point.
- When a phase contains work that can be handed off and tested separately, add one numbered Markdown file per subphase inside the phase folder, such as `phase2.1.md`. Link to those files from `phase2.md`. Keep short or tightly related steps in the main phase plan.
- State which services, data, or interfaces a phase owns. Use fixtures or mocks at dependency boundaries when they let a phase run and be tested independently. Record contract changes and their effect on dependent phases.

## Keep code encapsulated and maintainable

- Keep real code inside the service or feature that owns it. Group related files in clearly named folders and keep service-specific tests near their code. Use the [repository layout](../Documentation/implementation/repository-layout.md) for top-level placement and add folders as the code gains distinct responsibilities.
- Keep files short enough to understand in isolation. Give each file one clear responsibility. When a file grows long or handles several jobs, split it into focused modules and group them in a feature folder when useful. Keep tightly related behavior together and let responsibility guide the split.
- Keep service interfaces explicit. Share code when multiple services need the same behavior and keep domain decisions with their owner. Follow the [container boundaries](../Documentation/mvp/containers/containers.md) and the [database contracts](../Documentation/mvp/database/contracts.md) for cross-service work.
- Trace defects to the layer that owns the behavior and fix the underlying cause there. Exercise the normal user or service path to prove the fix. Avoid bypasses and one-off workarounds that leave the defect in place. Keep error handling, data integrity, permissions, and retry behavior consistent with the affected contracts.

## Test and verify changes

- Give each phase and subphase an acceptance check with a setup, steps or commands, and an expected result. Use the smallest check that proves the outcome. Use integration checks when a database or service boundary is part of the behavior.
- Run the relevant tests and acceptance checks before marking work complete. For a bug fix, use an existing check or add focused regression coverage when the existing checks would miss the defect. Record what ran and whether it passed. Leave blocked or unverified checks open and state what is needed to run them.
- Use fictional fixtures, a disposable database, and mocked model calls for routine tests. Run shared AWS and live model checks deliberately when the phase calls for them, and apply shared database migrations explicitly. Follow the [CI design](../Documentation/mvp/ci/cd/ci.md) and use the verified commands in the active plan.

## Keep the plan current

- Update the active Markdown plan as you work. Tick a task after its check passes and record the command or action and result. Tick the roadmap phase after the phase acceptance check passes.
- When a decision changes the plan, update the remaining steps and record what changed, why, and which phase or interface is affected. If a task moves, link or name its destination and track completion there.
- Keep the active plan detailed enough for a fresh agent to resume. Record outstanding work and its owner before handing off.
