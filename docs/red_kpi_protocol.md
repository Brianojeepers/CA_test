# Red KPI Action Protocol v1.0

## Purpose

This protocol defines what happens when a Decision Spine KPI turns red.

The intent is to make red metrics operational. A red KPI should produce diagnosis, ownership, and action, not passive reporting.

## Trigger

Open a red case whenever any KPI crosses its red threshold during a weekly, monthly, or quarterly readout.

## Required Within 48 Hours

The KPI owner opens a red case with:

- KPI ID and name.
- Date red status was observed.
- Impacted segments.
- Suspected root cause.
- Data confidence: high, medium, or low.
- Immediate containment action.
- Named owner for diagnosis.

## Required Within 7 Days

The KPI owner completes diagnosis and logs:

- Root cause category: data issue, operational issue, market issue, governance issue, or metric design issue.
- Evidence reviewed.
- Action plan.
- One directly accountable owner.
- One due date.
- One measurable recovery indicator.
- Escalation decision: stay with owner, escalate to function lead, or escalate to Signal Intelligence Council.

If no action is logged by day 7, escalation to the Signal Intelligence Council chair is automatic.

## Required Within 30 Days

The KPI owner re-reads the KPI and updates the red case:

- Current status.
- Progress against action plan.
- Whether the recovery indicator moved.
- Whether intervention should continue, change, or stop.

If the KPI remains red after 30 days, choose one of the following:

- Revise the intervention.
- Declare a structural issue and open a metric design review.
- Escalate to Signal Intelligence Council for cross-functional decision.

## Red Case Template

```text
Red Case ID:
KPI:
Observed date:
Owner:
Impacted segments:
Data confidence:

Suspected root cause:
Root cause category:
Evidence reviewed:

Immediate containment action:
Seven-day action:
Due date:
Recovery indicator:

Escalation path:
Thirty-day review date:
Status at thirty days:
Decision:
```

## Non-Compliance Rule

If a red KPI has no logged action within seven days, escalation is automatic.

If the same KPI is red for two consecutive cycles without a completed diagnosis, the Signal Intelligence Council must decide whether the issue is operational or whether the metric definition itself needs redesign.

## Severity Guidance

| Severity | Description | Default Escalation |
| --- | --- | --- |
| S1 | Red KPI affects credential integrity, premium authorization, or client trust. | Signal Intelligence Council immediately. |
| S2 | Red KPI affects placement, retention, or release commitments. | Function lead within seven days. |
| S3 | Red KPI appears to be a data quality or process issue. | KPI owner manages for one cycle. |
