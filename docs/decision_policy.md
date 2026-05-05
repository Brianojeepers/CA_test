# Decision Policy Checks

Decision policy checks turn the current evidence, trust, impact, and stakeholder
journey posture into safe operating decisions.

This remains a read-only horizontal MVP slice. It does not automate approvals,
write to downstream systems, introduce database schemas, or claim causal impact.

## Policy Outcomes

| Outcome | When to use | Safe action | Deferred action |
| --- | --- | --- | --- |
| `act_now` | Evidence is positive and source posture is strong enough for controlled amplification. | Amplify, scale, or convert the change into the next operating plan. | Automated downstream writes or causal claims. |
| `revise` | Implementation is blocked, release quality is unclear, or evidence requirements need correction. | Revise scope, release plan, rubric, sample strategy, or evidence requirement. | Presenting the decision as working. |
| `monitor` | Directional evidence exists but is not mature enough for action. | Keep on review calendar and gather stronger evidence. | Scaling, archiving, or stakeholder claims. |
| `wait` | Evidence windows, release windows, or source intake are not mature. | Hold claims and define the next review trigger. | Threshold changes, public claims, or schema deepening. |
| `escalate` | Risk is visible and passive monitoring would hide ownership. | Assign a named blocker and require follow-up. | Recycling the decision without owner-level intervention. |
| `archive` | Evidence remains weak, rejected, stale, or superseded. | Retire the claim with rationale and audit trail. | Silent deletion or loss of traceability. |

## Current Seed Policy Posture

Current decisions are not decision-grade. The policy review should currently
show:

- `act_now`: 0
- `revise`: 1
- `monitor`: 2
- `wait`: 1
- `escalate`: 1
- `archive`: 0

Interpretation:

- `DEC-2026-001` is monitored because evidence is emerging, not mature.
- `DEC-2026-002` waits because evidence and outcome windows are immature.
- `DEC-2026-003` remains a monitor/watch decision.
- `DEC-2026-004` needs revision because implementation is still incomplete.
- `DEC-2026-005` escalates because evidence is suppressed, sample size is
  insufficient, and outcomes are pending.

## Guardrails

- Policy outcomes are operating guidance, not automated approvals.
- Workflow-design-only journeys can monitor, wait, revise, or escalate, but
  cannot support performance claims.
- `act_now` requires positive evidence plus source posture strong enough for
  controlled amplification.
- Escalate when risk is visible and passive monitoring would hide ownership.
- Archive must preserve rationale and audit trail.

## Command

```bash
python3 scripts/decision_policy_review.py
```
