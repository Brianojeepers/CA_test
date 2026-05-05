# Normalization Crosswalk

This review maps role, competency, pedagogy, decision, release, learner evidence,
and outcome language before committing to an ontology schema, semantic model, or
warehouse table.

The crosswalk is a horizontal MVP slice. It is meant to expose alignment and
ambiguity across the operating model, not to define the final data model.

## Current State

| State | Count | Meaning |
| --- | ---: | --- |
| Aligned for planning | 1 | Role, competency, signal, decision, release, pedagogy, learner evidence, and outcome cohort links are present. |
| Evidence pending | 1 | The implementation exists, but learner evidence has not been scored yet. |
| Implementation pending | 1 | The competency maps to an in-progress release. |
| Suppressed evidence | 1 | Evidence exists, but suppression prevents standalone readiness claims. |
| Monitor only | 1 | The capability is being tracked but should not become a standalone credential or schema anchor yet. |
| Needs mapping | 0 | No current competency is completely unmapped. |

Ontology schema work remains deferred.

## Role Coverage

| Role archetype | Current normalization posture |
| --- | --- |
| Builder | One planning-aligned competency for evaluation and observability. |
| Scaler | One evidence-pending integration competency and one implementation-pending security/privacy competency. |
| Prototyper | One suppressed multimodal-prototyping competency and one monitor-only workflow-asset competency. |

## Guardrails

- This crosswalk clarifies language and joins; it is not a canonical ontology
  schema.
- Monitor-only competencies should stay out of standalone credentials until
  signal pull strengthens.
- Suppressed or pending evidence cannot support readiness claims.
- Implementation-pending releases cannot be treated as proof of activation.
- Use crosswalk gaps to shape pilot extracts before designing tables.

## Normalization Questions

- Are role archetype names consistent across signals, competencies, evidence,
  and outcomes?
- Does each active competency have a clear signal, decision, release, pedagogy,
  evidence, and cohort outcome path?
- Which competencies are safe for planning language but not stakeholder claims?
- Which capabilities should stay embedded in broader workflow language instead
  of becoming standalone credentials?
- Which joins should shape pilot extracts before schema design?

## Command

Run:

```bash
python3 scripts/normalization_crosswalk_review.py
```
