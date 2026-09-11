# VDP Orchestration to GraphQL Subgraph — A Critical Analysis

A working note capturing (1) what the ADR proposed and where it overreaches, (2) the gaps I identified that hold up under scrutiny, and (3) what to actually do now that it is approved and executing.

## Part 1 — What Was Proposed and Approved (and where it is not a great idea)

### The proposal in one line
Treat GraphQL Federation as the single source of truth for read-mostly business logic, migrate VDP Orchestration's logic into the graph, and expose it as a subgraph (vdp-context / "Listing View Context"), so any consumer queries the router directly instead of hopping through orchestration.

### The strong, genuinely correct core
One part of the ADR is right and stands on its own:

* Shared *domain facts* should be owned by the domain that owns their data, not re-implemented in every consumer.
* The flagship case studies prove exactly this: `isTSRP = (make == Toyota) && isNew` belongs in LDS; computed dealer fees belong in fee-tax.
* The real pain was legitimate: the same logic was copy-pasted into Remix (TypeScript), srp-orchestration (Java), and clients, then drifted — an `isNew` check existed in one path and not another, causing tracking-vs-UI mismatches.
* Centralizing a domain fact in its domain subgraph genuinely fixes that. This argument needs nothing about hops, payload size, or caching.

### Where the ADR overreaches
The overreach is that it spends the credibility of the correct core to carry conclusions the core does not support:

1. It conflates "single source of truth" with "GraphQL." Single-source-of-truth is a code-organization problem with at least three solutions — a shared library, an owning service everyone calls, or a subgraph. The ADR presents only the subgraph option, so reviewers never actually chose; they ratified the only path on the page.

2. The "eliminate the extra hop" argument inverts for vdp-context. It is valid only for passthrough fields that merely forward a value originating in a domain subgraph (Client -> orchestration -> Router -> subgraph becomes Client -> Router -> subgraph). But for logic that genuinely originates in VDP Orchestration, going through the router is Client -> Router -> vdp-context (2 hops) versus Client -> VDP-Orchestration (1 hop). The migration adds a hop, it does not remove one.

3. Payload / declarative field selection is real but secondary. LDS has ~230 fields and VDP needs ~110, so field selection is a convenience — not the justification.

4. Performance / caching is not a driver at all. The router adds only ~4ms and is non-caching by design, so this was never a latency or caching play.

5. vdp-context has no legitimate landing zone. It is defined as the residue that is not a clean domain fact. Sort its contents and it evaporates: domain-semantic derivations drain to their domains (LDS/SP), presentation/page logic drains to the app, and the only genuine residual is request-context-by-domain joins (e.g., the user's zip feeding a delivery-fee calc) — a thin sliver that is itself personalized and uncacheable, an awkward fit for a caching-oriented federation router. There is no end-state where vdp-context is a substantial, legitimate subgraph. If it stays fat, it becomes the distributed monolith the ADR itself lists as a negative consequence — now sitting on a single-point-of-failure router at ~350M req/day.

### Why it still got approved
Not carelessness — five predictable dynamics:

* The strong core (domain-fact relocation) carried the weak periphery; reviewers pattern-matched on the compelling examples and approved the direction.
* The framing ("kill duplication") is unopposable, and the alternatives (library, keep-as-service) were never shown, so no real choice was made.
* It pointed the same way as the existing federation strategy, so it read as "consistent" rather than "a new claim needing proof."
* The hard question — the boundary between domain logic and page logic — was explicitly parked as an Open Question, letting people approve a direction while deferring the crux.
* Approval means "proceed," not "proven." It is revisable at the execution layer.

## Part 2 — The Gaps I Identified That Hold Up

### 2.1 "Orchestrator" is a mechanism, not an identity
Fanning out to multiple services is something a service *does*, not what it *is*. VDP Orchestration's real identity is "the service that owns VDP page composition/context logic." Naming it after the mechanism (orchestration) is what led people to treat it as a dumb passthrough that could dissolve into the router. In fact it owns a real domain — the VDP view — which is a presentation/composition domain rather than a data domain, but a legitimate ownership boundary nonetheless.

### 2.2 The correct placement axis is "whose logic," not "logic vs data"
"Logic is logic, data is data" is too clean — taken literally it would exile `isTSRP` from LDS too, leaving domain derivations homeless. The correct axis is ownership:

* Domain-semantic derivation over one domain's own data (isTSRP, CPO tier, computed fee) -> that domain's subgraph. A domain owns its facts and the derivations of its facts, computed or not.
* Cross-domain composition (join listing + provider + fee into a page shape) -> an orchestration/domain service that owns that composition. Never a domain subgraph.
* Presentation / page logic (which banner, which layout, A/B wiring) -> the app.

### 2.3 The polyglot objection does not justify the subgraph
The one thing a shared library cannot do is span TypeScript + Java + native. My fix dissolves it: the Java backend owns the computed field, and Remix/mobile *call it* rather than recompute it. The sharing mechanism for cross-language consumers is the owning service, not the library. So:

* Same-language pure logic shared between VDP-Orch and SRP-Orch -> a shared library is ~10x cheaper than a subgraph.
* Cross-language consumers -> call the owning service.
* Either way, polyglot argues for "a runtime-neutral owning service," not "GraphQL," and certainly not "vdp-context."

### 2.4 "Everyone already calls it" is monolith gravity, not architecture
Marginal cost is a legitimate tiebreaker *between* correct homes. It cannot *make* a home correct. Using "the graph is already wired up" to place logic that does not belong in a domain promotes convenience from tiebreaker to justification — which is exactly how the router becomes the accretion point for all cross-domain and presentation logic. That is a distributed monolith with a single critical-path chokepoint.

### 2.5 The end-state argument is protocol-agnostic, so it justifies nothing about the migration
Draining fields to their correct owners (domain facts -> LDS/SP, page logic -> app) is completely independent of whether the residual orchestration is a REST API or a subgraph. You could keep VDP Orchestration a plain REST service and still drain isTSRP to LDS. Therefore migrating VDP Orchestration -> vdp-context accomplishes nothing on the very axis the ADR claims as its main value. The single-source-of-truth win comes entirely from relocating domain facts to domain owners — work that neither requires nor benefits from vdp-context existing.

### 2.6 The conclusion
Migrating VDP Orchestration into a GraphQL subgraph confuses mechanism for identity, relocates nothing to a better owner, and loads personalized/uncacheable page logic onto the critical-path router. The correct end-state:

* isTSRP-type domain facts -> drain to their domain (LDS/SP). Real, correct, protocol-agnostic.
* Cross-page pure logic shared between orchestrators -> shared library (same language) or a call to the owning domain service (cross-language).
* VDP page composition/context logic -> stays in VDP Orchestration, because that service already is its owner. Keep it a service; do not migrate it into the graph.

Guardrail against turning this into a grudge: VDP Orchestration is the correct owner *of its domain*, and the discipline is to keep it to its domain — not to defend it as a dumping ground. The enemy was never "subgraph vs API." It is logic living somewhere other than its owner, in either costume.

## Part 3 — What To Do Now (harm reduction, not reversal)

The ADR is approved, communicated, and executing. Trying to un-approve it would frame me as anti-progress, burn capital, and fail. The move is to shape execution — and the ADR itself hands me the mandate by leaving the boundary question open. Contributing the answer is completing the ADR, not fighting it.

### Step 1 — Concede the correct core loudly and first
Open with: "Domain facts, including derived ones, belong in their domain subgraph — isTSRP -> LDS is right, let's do it." True, cheap, and it establishes me as executing the ADR, not obstructing. Everything after lands differently once this is on record.

### Step 2 — Convert the critique into a placement rule, not an objection
Offer the "whose logic" axis as the answer to the ADR's own open question:

* Domain-semantic derivation over one domain's own data -> that domain's subgraph.
* Cross-domain composition -> an orchestration/domain service (stays a service).
* Presentation / page logic -> the app.

A testable, field-by-field rule is something the team can apply during migration, and it prevents the bloat without anyone having to "admit the ADR was wrong."

### Step 3 — Spend capital only on the reversible-now, expensive-later item: vdp-context bloat
Draining isTSRP to LDS is both hard to undo and correct — let it run. The one real battle is preventing vdp-context from becoming the accretion point for page/composition logic on the critical-path router. Fight it precisely:

* Get it named and scoped in writing as transitional debt with a drain plan and exit criteria — not a permanent, growing subgraph. Align explicitly with Debbie's "oversized catch-all / rename to Listing View Context" comment.
* Get a cap in writing: vdp-context may hold only request-context-by-domain joins with no domain home; everything else drains out. Write down what is not allowed in it.

### Step 4 — Use the org's own words as backing
Cite the PDP/Router team's own guidance ("domain subgraphs expose raw data, keep business logic out") and the ADR's own negative-consequence list (distributed monolith risk, router SPOF at ~350M req/day). This is enforcing constraints the org already endorsed, not introducing dissent.

### Step 5 — Add the operational guardrail (home turf)
Given the router is a single point of failure at that volume and non-caching, push the resilience discipline I know best:

* Do not route personalized/uncacheable page logic through the critical path.
* Keep fail-open timeouts and per-subgraph circuit breakers on any new subgraph.
* Instrument the new fields (error rates, latency) so blast radius is visible.

### Step 6 — Write it down where it outlives the conversation
Produce a one-page "field placement guide" attached to the DEC open-questions. Arguments evaporate; a checklist others reach for during PRs becomes the de-facto standard. That is how the model becomes the guardrail without needing to win a meeting.

### The reframe for myself
Shift the goal from "win the argument" to "shape the outcome." Two things are true: the migration's defensible core will proceed and that is fine (domain facts to domain owners is correct); and the specific damage I can prevent is narrow and real (page logic accreting on the router). Aim all energy at that narrow band and let the rest go. Relitigating the whole thing loses me the standing to win the part that actually matters — and I now understand the system's seams better than the document that governs it, which is exactly the position from which to shape execution rather than reopen the vote.

## Sources
* DEC-1618 / GraphQL as source of truth ADR: https://cargurus.atlassian.net/wiki/spaces/TL/pages/5653233750
