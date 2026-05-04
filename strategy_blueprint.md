# Andela AI Academy Intelligence Engine Blueprint

## Objective
Transform the current static dashboard into a continuously updated **market intelligence + curriculum decision system** that:
1. Detects shifts in talent demand early.
2. Converts evidence into curriculum changes with clear governance.
3. Forecasts role demand by horizon (0–3, 3–9, 9–18 months).
4. Helps matching teams place graduates at the right time with the right evidence.

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
- `market_signal` (source, timestamp, region, confidence)
- `curriculum_module` (outcomes, prerequisites, assessments)
- `placement_event` (candidate, role, client, conversion stage)
- `forecast` (role/skill, horizon, confidence interval)

Key rule: every curriculum change must link to specific market signals and outcome hypotheses.

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
- **Intelligence Council** (Academy, Matching, Data, Delivery, Client Success).
- Decision log with:
  - evidence used,
  - confidence,
  - expected impact,
  - owner,
  - review date.
- “No source, no change” rule for curriculum updates.

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
- Define ontology + metric definitions.
- Stand up ingestion for top-priority data sources.
- Build initial RDI and CGI.

### Days 31–60: activation
- Connect intelligence outputs to curriculum map.
- Ship decision changelog.
- Pilot monthly council review.

### Days 61–90: optimization
- Add horizon radar and basic forecast models.
- Integrate placement outcomes loop.
- Launch matcher-facing views and recommendation summaries.

## 10) Practical next steps for your existing dashboard
1. Keep current narrative UX, but back every panel with live metric queries.
2. Add “last updated,” confidence, and source coverage badges to each insight.
3. Add a “recommended action” panel: update module, keep, or deprecate.
4. Add a “matcher view” that translates curriculum outcomes into client-ready talent profiles.
5. Add changelog diffing so stakeholders see what changed since last review.

---

This approach preserves your strategy-led framing and upgrades it into an operational intelligence engine that can continuously answer:
- what to teach now,
- what to prepare next,
- and who is ready for which opportunity.
