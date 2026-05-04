# Competency Ontology

## Purpose

The competency ontology is the bridge between market evidence and academy action.
It translates signals into durable capabilities that can be taught, practiced,
assessed, credentialed, and explained to clients.

It should answer:

- Which role archetype does the signal affect?
- What competency cluster is changing?
- What capability must talent demonstrate?
- What proficiency level is required?
- Which decision, release, and pedagogy records already act on it?
- Which market signals are still only being monitored?

## Current MVP Register

The working register lives in `data/role_competencies.json`.

Each record represents one competency target for one role archetype. It is not a
module catalog and not a skill keyword list. A useful competency is framed as a
capability that can be evidenced in realistic work.

## Required Fields

| Field | Meaning |
| --- | --- |
| `competency_id` | Stable local identifier. |
| `role_archetype` | Builder, Scaler, Prototyper, or another role archetype used by the signal model. |
| `competency_cluster` | Durable capability family, such as evaluation, integration, governance, or prototyping. |
| `capability` | The observable ability talent should demonstrate. |
| `target_proficiency` | Dreyfus-style autonomy/proficiency target. |
| `market_priority` | `core`, `emerging`, or `monitor`. |
| `horizon_window` | Timing pressure inherited from linked market evidence. |
| `linked_signal_ids` | Signals that justify the competency. |
| `linked_decision_ids` | Decisions that act on or monitor the competency. |
| `linked_release_ids` | Released or pending artifacts, if any. |
| `pedagogy_ids` | Pedagogical framing entries, if any. |
| `assessment_signal` | What evidence would prove the capability. |
| `gap_hypothesis` | Why the competency gap matters for placement, retention, or client trust. |
| `owner` | Function accountable for the competency target. |
| `status` | `active`, `monitor`, or `deprecated`. |

## Operating Rules

- Do not create competencies for every tool mention.
- Core competencies should link to green market signals and an approved decision.
- Emerging competencies can be active when market pull is clear but the outcome
  evidence is still maturing.
- Monitor competencies should not become standalone requirements until the
  council sees enough commercial pull or outcome impact.
- Every active competency should eventually have assessment evidence and a
  pedagogy map entry.
- Red or weak signals can remain unmatched when the right action is to avoid
  credential inflation.

## Review Command

Run:

```bash
python3 scripts/competency_gap_review.py
```

The review groups competencies by role archetype, shows traceability to signals
and releases, flags monitor items, and identifies market signals that do not yet
map to a competency.
