# Governance Cadence

This document defines the manual operating cadence for the Decision Spine MVP
before scheduled jobs, production automation, or downstream writes are
introduced.

The cadence is deliberately human-first. The system should prove which reviews,
decisions, escalations, and artifacts matter before any workflow is automated.

## Cadence Summary

| Cadence | Review | Current readiness |
| --- | --- | --- |
| Weekly | Signal and source-quality refresh | Ready for manual trial |
| Monthly | Council decision review | Ready for manual trial |
| Quarterly | Role, competency, and horizon recalibration | Defined but not trialed |

Automation remains deferred.

## Weekly Signal And Source-Quality Refresh

Purpose: review new or changed signals, source blockers, freshness posture, and
urgent evidence-quality risks.

Entry criteria:

- Seed data validation has no errors.
- Source ingestion and trust registry reviews are current.
- New or changed signals have source, confidence, and horizon context.
- Open source-owner and privacy blockers are visible.

Exit criteria:

- Signals are classified as act, track, monitor, or exclude.
- Freshness or ownership blockers have named owners.
- Urgent source-quality issues are escalated to the council chair or privacy
  owner.
- No scheduled ingestion or database work is started from this review alone.

## Monthly Council Decision Review

Purpose: convert evidence, policy, stakeholder journeys, and reasoning stress
tests into safe operating decisions.

Entry criteria:

- Monthly packet is generated from current seed data.
- Decision policy and reasoning stress reviews pass.
- Normalization crosswalk exposes pending, suppressed, and monitor-only
  competencies.
- Trust and source blockers are visible before any stakeholder claim.

Exit criteria:

- Each active decision has an operating policy outcome.
- Approved actions identify owner, next trigger, and known limits.
- Review snapshot is saved after council decisions are recorded.
- Stakeholder-facing claims remain bounded by trust posture.

## Quarterly Role, Competency, And Horizon Recalibration

Purpose: review role anchors, competency clusters, horizon predictions, outcome
evidence, and structural programme changes.

Entry criteria:

- At least one monthly council cycle has completed with saved snapshots.
- Prediction scoring and horizon review notes are available.
- Normalization crosswalk identifies stable and unstable role/competency links.
- Outcome and learner evidence limitations are explicitly named.

Exit criteria:

- Role or competency changes are classified as keep, revise, monitor, or
  deprecate.
- Prediction learning is recorded for horizon claims that matured.
- Pilot extract priorities are updated without committing to production schemas.
- Quarterly structural changes have named owners and evidence requirements.

## Guardrails

- Human review cadence must prove which decisions matter before scheduling jobs.
- Weekly review can classify and escalate signals, but cannot approve curriculum
  or credential changes.
- Monthly council review can decide operating posture, but cannot automate
  downstream writes.
- Quarterly recalibration can recommend structural changes, but final
  ontology/schema work stays deferred.
- Every cadence needs entry criteria, exit criteria, artifacts, decision rights,
  and escalation triggers.

## Command

Run:

```bash
python3 scripts/governance_cadence_review.py
```
