# Andela AI Academy Intelligence Engine Blueprint

## Objective
Transform the current static dashboard into a continuously updated **market intelligence + curriculum decision system** that:
1. Detects shifts in talent demand early.
2. Converts evidence into curriculum changes with clear governance.
3. Forecasts role demand by horizon (0–3, 3–9, 9–18 months).
4. Helps matching teams place graduates at the right time with the right evidence.

## Implementation Contract

This blueprint defines product direction and target architecture.

The executable local MVP contract lives in `SPEC.md`. Use `SPEC.md` as the
source of truth for current data contracts, command surface, acceptance criteria,
reasoning gates, generated outputs, tests, and known limitations.

## 1) Product evolution: from dashboard to decision engine

### Current state (snapshot dashboard)
- Great narrative synthesis and strategic framing.
- Manual updates and static data lock in assumptions.
- Weak traceability from source signals to curriculum decisions over time.

### Target state
A layered system:
- **Signal ingestion layer**: jobs, skills taxonomies, salary, hiring velocity, employer reports, OSS trends.
- **Normalization layer**: role/skill ontology, deduping, confidence scoring.
- **Intelligence layer**: trend scoring, role-anchor demand index, competency gap detection.
- **Decision layer**: recommended curriculum deltas with expected placement impact.
- **Activation layer**: updates to curriculum maps, assessment rubrics, matcher playbooks.

### Current MVP implementation
The first working version is intentionally smaller than the target architecture. It proves the operating loop before live ingestion or predictive modeling:

- Seed JSON data for `signals -> decisions -> releases -> cohort outcomes -> prediction learning`.
- `scripts/validate_data.py` for validation-first trust in joins, dates, statuses, and temporal cohort warnings.
- `scripts/report_kpis.py` for K1-K7 KPI status.
- `scripts/council_review.py` for action queues: decisions needed, release accountability, traceability, and prediction follow-ups.
- `scripts/signal_review.py` for signal-to-action review: act now, act tracked, monitor, do not act.
- `scripts/credential_requirements.py` for Assessment Ops credential and assessment actions.
- `docs/real_data_readiness.md` for the controlled path from synthetic seed data to real pilot extracts.
- `docs/source_data_contracts.md` and `scripts/source_contract_review.py` for source-owner, privacy, field, freshness, and pilot-readiness contracts before real data is imported.
- `scripts/v02_intelligence_preview.py` for directional role-demand, competency-gap, horizon, and curriculum-impact previews that keep hard recommendations disabled until fields and sources are ready.
- `scripts/export_pilot_request_pack.py` for turning v0.2 missing fields into owner-ready pilot data requests before database design.
- `scripts/pilot_intake_review.py` for checking whether owner responses are accepted, unclear, privacy blocked, or not ready before schema work begins.
- `scripts/architecture_readiness_review.py` and `docs/architecture_readiness_map.md` for checking horizontal coverage across the target architecture before database/schema work.
- `scripts/trust_registry_review.py` and `docs/trust_registry.md` for showing which stakeholder surfaces are privacy blocked, planning-ready, manual-sampling-only, or pilot candidates.
- `scripts/source_ingestion_review.py` and `docs/source_ingestion_contract.md` for defining the canonical ingestion envelope, freshness posture, allowed use, and standardization risk before live connectors or schemas.
- `scripts/normalization_crosswalk_review.py` and `docs/normalization_crosswalk.md` for aligning role, competency, pedagogy, decision, release, evidence, and outcome language before ontology/schema work.
- `scripts/governance_cadence_review.py` and `docs/governance_cadence.md` for defining weekly, monthly, and quarterly manual review cadence before scheduling or automation.
- `scripts/stakeholder_journey_review.py` and `docs/stakeholder_journey_map.md` for mapping what each stakeholder can do now, must defer, escalate, and evidence-gate.
- `scripts/decision_policy_review.py` and `docs/decision_policy.md` for turning current evidence posture into safe policy outcomes: act now, revise, monitor, wait, escalate, or archive.
- `scripts/reasoning_stress_review.py` and `docs/reasoning_stress_tests.md` for forcing unsafe claims to downgrade across signal, trust, ingestion, decision, activation, and stakeholder-experience layers.
- `SPEC.md` for the executable MVP specification and acceptance criteria.

This MVP is not the end state. It is the smallest trustworthy operating surface for the larger intelligence engine.

### Expanded MVP boundary (v0.2)
The next useful MVP is broader than the first dashboard but still short of a
production intelligence platform. It should prove that the system can support
role demand, competency gap, horizon, and impact reasoning from governed data
contracts before we invest in live ingestion or a database migration.

v0.2 should add:
- a schema gap review that compares seed data, pilot templates, source contracts, and target intelligence fields,
- a minimum viable pilot extract for role-anchor demand and competency-gap inputs,
- explicit field requirements for demand volume, demand growth, hiring velocity, compensation pressure, learner demonstrated proficiency, proficiency gap, maturity stage, and curriculum cost/impact assumptions,
- dashboard surfaces that expose source coverage and confidence before recommendations,
- a strict rule that expanded intelligence outputs remain directional until real pilot data passes privacy, ownership, and freshness gates.

The first implementation of this boundary is `scripts/schema_gap_review.py`. It
does not claim the new intelligence features are solved; it tells us which fields
and source agreements are missing before those features can be trustworthy.
The next implementation layer is `scripts/v02_intelligence_preview.py`: it shows
what the current MVP can say directionally about role demand, competency gaps,
horizon signals, and curriculum impact while preserving explicit "do not claim
yet" guardrails.
The current bridge from preview to implementation is the pilot request pack: it
groups missing v0.2 fields by source owner, separates privacy-review requests
from simple field-definition requests, and gives us a concrete data collection
brief before committing to database schemas.
The next gate is pilot intake review: it distinguishes fields that can enter
schema design from fields that still need clarification, privacy approval, or
sample evidence.

Before the MVP goes deeper into database schemas, it should expand horizontally
across the target architecture: signal ingestion, normalization, intelligence,
decision, activation, governance cadence, observability/trust, and stakeholder
experience. The architecture readiness map makes this explicit so the product
does not over-optimize one narrow module while the broader intelligence engine
is still underrepresented.
The first implementation of that horizontal expansion is the trust registry: it
connects stakeholder-facing surfaces back to source contracts, labels confidence
and privacy blockers, and keeps decision-grade claims disabled while source
trust is still immature.
The next implementation is the stakeholder journey map: it turns the trust
posture into operating behavior by naming the question, safe action, deferred
claim, escalation path, and evidence needed for each stakeholder group.
Decision policy checks then convert that operating behavior into explicit
policy outcomes so incomplete evidence leads to a safe decision posture rather
than a vague "interesting signal" state.
Source ingestion contract checks then make the future ingestion problem explicit
without building it too early: every candidate source gets an envelope, allowed
use, freshness obligation, standardization risk, canonical target, and blocker
before any connector, schedule, landing table, or database schema is considered.
Normalization crosswalk checks then show whether role archetypes, competency
clusters, pedagogy, releases, learner evidence, and outcome cohorts line up
well enough for pilot planning without pretending that a final ontology exists.
Governance cadence checks then define how weekly signal refresh, monthly council
review, and quarterly recalibration should work manually before the system adds
scheduled jobs, production automation, or downstream writes.
Reasoning stress tests then check whether the horizontal architecture holds
together under pressure: strong signals cannot bypass red evidence sources,
approvals cannot masquerade as implementation proof, and dashboard actions
cannot override policy outcomes.

## 2) Data domains to add (richness expansion)
1. **Live job demand signals**
   - Job posts by role, region, seniority, industry.
   - Required skills extracted from descriptions.
   - Time-to-fill proxies and hiring velocity.
2. **Compensation and budget proxies**
   - Salary bands and posted compensation trends.
   - Helps prioritize skills where willingness-to-pay is highest.
3. **Tooling adoption indicators**
   - SDK/package download trends, OSS repo growth, stars/forks velocity.
   - Mentions in engineering blogs and architecture docs.
4. **Enterprise adoption + governance signals**
   - Compliance requirements (e.g., privacy, security, model governance).
   - Demand for evals, observability, and risk controls.
5. **Placement outcomes feedback loop**
   - Interview pass rates, placement conversion, extension rates, time-to-placement.
   - Post-placement performance signals from clients.
6. **Learner performance telemetry**
   - Module-level completion, rubric outcomes, simulation results.
   - Correlate learning artifacts to placement outcomes.

## 3) Core data model (source-of-truth schema)
Create a canonical ontology and version it.

- `role_anchor` (backend, fullstack, solutions architect, data, frontend, product)
- `competency_cluster` (agentic engineering, evaluation, systems thinking, integration, communication)
- `skill` (atomic capability + proficiency levels)
- `pedagogical_frame` (Bloom target, Dreyfus target, performance context, assessment evidence)
- `market_signal` (source, timestamp, region, confidence)
- `curriculum_module` (outcomes, prerequisites, assessments)
- `placement_event` (candidate, role, client, conversion stage)
- `forecast` (role/skill, horizon, confidence interval)

Key rule: every curriculum change must link to specific market signals and outcome hypotheses.

Pedagogical translation is defined in `docs/pedagogical_framing.md`. Bloom's taxonomy should describe cognitive complexity, Dreyfus should describe proficiency and autonomy, and assessment evidence should prove realistic performance rather than content exposure.
The local MVP now tests this as optional structured data in `data/pedagogy_map.json`, reviewed through `scripts/pedagogy_review.py`, before making pedagogical labels mandatory across every curriculum or credential record.
The first competency ontology lives in `data/role_competencies.json` and is reviewed through `scripts/competency_gap_review.py`; it links role archetypes to competency clusters, market signals, decisions, releases, and gap hypotheses.
Aggregated proficiency evidence lives in `data/learner_evidence_summary.json` and is reviewed through `scripts/proficiency_readiness_review.py`; it checks whether cohorts can demonstrate the competencies without storing learner-level records.
Decision impact synthesis is reviewed through `scripts/decision_impact_review.py`; it combines implementation, readiness, outcomes, and prediction context to decide whether a council decision is too early, promising, positive, or needs attention.

## 4) Intelligence features to implement

### A. Role Anchor Demand Index (RDI)
Composite score per anchor role:
- demand volume
- demand growth rate
- salary/budget pressure
- strategic durability (not hype-only)
- placement conversion alignment

Output: priority ranking and confidence per region.

### B. Competency Gap Index (CGI)
For each role anchor, measure:
- market-required proficiency vs learner demonstrated proficiency.
- include decay curves for fast-changing tools.
- distinguish cognitive complexity from autonomy level so a skill is not over- or under-taught.

Output: “teach now / monitor / deprecate” recommendation.

### C. Horizon radar (0–3 / 3–9 / 9–18 months)
- Detect weak signals early (e.g., new protocols, eval standards).
- Assign maturity stage: emerging, accelerating, baseline, commoditizing.

### D. Curriculum Impact Simulator
“What if we add a 2-week evaluation engineering block?”
- estimated effect on placement conversion and extension likelihood.
- cost in learner time and instructional capacity.

## 5) Automation workflow (operating cadence)

### Weekly (light refresh)
- Pull incremental market signals.
- Recompute demand and competency indices.
- Flag anomalies and rising topics.

### Monthly (decision review)
- Intelligence review with academy + matching + delivery leads.
- Approve curriculum micro-adjustments.
- Publish “What changed and why” changelog.

### Quarterly (structural recalibration)
- Re-score role anchors.
- Add/deprecate modules.
- Re-baseline assessment framework.

## 6) Governance model
- **Signal Intelligence Council** (Academy, Matching, Data, Delivery, Client Success) as the operating owner for signal quality, horizon judgment, credential integrity inputs, and placement outcome learning.
- Decision log with:
  - evidence used,
  - confidence,
  - expected impact,
  - owner,
  - review date.
- “No source, no change” rule for curriculum updates.

The council charter for this operating owner is defined in `docs/signal_intelligence_council.md`.

## 7) Technical architecture (pragmatic)

### Stack suggestion
- Ingestion: scheduled pipelines (e.g., Airflow/Prefect).
- Storage: warehouse + lakehouse pattern.
- Transformation: dbt models.
- Semantic layer: metrics contracts for demand/gap KPIs.
- App/API: internal insights service for dashboard + downstream tools.
- Observability: data quality checks + freshness SLAs.

### Decision API examples
- `GET /anchors/demand?region=...`
- `GET /competencies/gaps?anchor=backend`
- `GET /horizon/signals?window=9m`
- `POST /curriculum/simulate`

## 8) Metrics that prove this is working

### Outcome metrics
- time-to-placement
- placement conversion rate
- extension rate
- client satisfaction signal

### Leading indicators
- % curriculum outcomes directly linked to current evidence
- signal-to-decision cycle time
- skill freshness index (median age of taught tooling)
- forecast accuracy by horizon

## 9) 90-day rollout plan

### Days 0–30: foundation
- Stabilize the local Decision Spine MVP.
- Validate seed data and document contribution rules.
- Run signal review, council review, KPI report, and credential requirements views.
- Define the real-data readiness gate and minimum viable pilot extract.
- Confirm source-system owners for signals, decisions, releases, outcomes, and predictions.

### Days 31–60: activation
- Pilot monthly council review using the action queues.
- Introduce a small anonymized real-data extract if approved.
- Connect validated signals to Assessment Ops and Developer Learning workflows.
- Add decision changelog output for stakeholder communication.
- Use `scripts/schema_gap_review.py` to identify gaps between seed schema, pilot templates, real source contracts, and v0.2 intelligence requirements.

### Days 61–90: optimization
- Mature the placement and retention feedback loop.
- Add matcher-facing and Sales-facing evidence summaries.
- Begin role-anchor demand and competency-gap prototypes only after the schema gap review has a named source owner and privacy posture for every required field.
- Add horizon radar and prediction scoring improvements.
- Decide whether to move from local scripts to an internal service, dashboard, or scheduled workflow.

## 10) Practical next steps for your existing dashboard
1. Keep current narrative UX, but back every panel with live metric queries.
2. Add “last updated,” confidence, and source coverage badges to each insight.
3. Add a “recommended action” panel: update module, keep, or deprecate.
4. Add a “matcher view” that translates curriculum outcomes into client-ready talent profiles.
5. Add changelog diffing so stakeholders see what changed since last review.
6. Add architecture-wide navigation so stakeholders can move across signals, trust, decisions, activation, and learning without needing technical packet output.

---

This approach preserves your strategy-led framing and upgrades it into an operational intelligence engine that can continuously answer:
- what to teach now,
- what to prepare next,
- and who is ready for which opportunity.
