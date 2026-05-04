# Pedagogical Framing For Decision Spine

## Purpose

Pedagogical framing should help the council translate market evidence into teachable, assessable capability. It should not become decorative taxonomy.

Use this document when deciding whether a signal should change:

- a learning outcome,
- a practice task,
- an assessment criterion,
- a credential requirement,
- or talent-facing evidence guidance.

## Core Rule

Every market-backed learning or credential change should answer four questions:

| Question | Useful Frame |
| --- | --- |
| What kind of thinking is required? | Bloom's taxonomy. |
| How independently must the person perform? | Dreyfus proficiency model. |
| What real-world performance proves it? | Authentic assessment. |
| How does practice build toward that proof? | Deliberate practice and feedback. |

## Bloom's Taxonomy: Cognitive Complexity

Use Bloom's taxonomy to describe the cognitive demand of a learning outcome or assessment task.

| Level | Use In This System | Example For AI Engineering |
| --- | --- | --- |
| Remember | Recall concepts, terms, or syntax. | Define eval dataset, trace, guardrail, or embedding. |
| Understand | Explain concepts and tradeoffs. | Explain why an agent needs observability and failure analysis. |
| Apply | Use a known method in a familiar situation. | Add a standard eval harness to a simple workflow. |
| Analyze | Diagnose structure, causes, or failure modes. | Compare failure traces and identify brittle tool-use behavior. |
| Evaluate | Judge quality against criteria. | Decide whether model output meets reliability, safety, and client acceptance thresholds. |
| Create | Produce an original working artifact. | Build and defend an eval plan for a production AI workflow. |

Operating guidance:

- Do not use Bloom levels as seniority labels.
- Credential requirements should rarely stop at Remember or Understand.
- Premium AI talent signals usually require Analyze, Evaluate, or Create.
- Curriculum can start lower, but assessment should test the level the market requires.

## Dreyfus Model: Proficiency And Autonomy

Use Dreyfus levels to describe how much context, judgment, and independence the learner or talent must demonstrate.

| Level | Meaning In This System | Evidence Standard |
| --- | --- | --- |
| Novice | Can follow explicit instructions in a stable context. | Completes guided task with strong scaffolding. |
| Advanced beginner | Can handle simple variation with some prompts. | Adapts an example to a nearby use case. |
| Competent | Can plan, execute, and troubleshoot in a realistic context. | Produces a defensible artifact with tradeoff reasoning. |
| Proficient | Can see patterns, prioritize risks, and adapt under ambiguity. | Diagnoses ambiguous failure and chooses a fit-for-purpose approach. |
| Expert | Can shape strategy, invent patterns, and coach others. | Establishes standards or novel approach others can reuse. |

Operating guidance:

- Use Dreyfus for autonomy and reliability, not trivia difficulty.
- AI-certified credential thresholds should generally require at least Competent performance.
- Scaler or regulated-client requirements may require Proficient evidence for risk, governance, and integration work.
- Expert should be used sparingly; it is not the default target for academy completion.

## Practical Design Frames

### Constructive Alignment

Learning outcomes, practice tasks, assessment criteria, and credential evidence must point at the same capability.

Bad pattern:

```text
Market signal: clients need eval and observability.
Learning task: read about evals.
Assessment: multiple-choice quiz.
Credential claim: can monitor agentic workflows.
```

Better pattern:

```text
Market signal: clients need eval and observability.
Learning task: instrument a workflow, inspect traces, and improve failure handling.
Assessment: diagnose failures and justify reliability thresholds.
Credential claim: can evaluate and monitor agentic workflows in a realistic client scenario.
```

### Authentic Assessment

Use tasks that resemble the work clients actually need performed.

Useful evidence includes:

- working prototype or system artifact,
- evaluation plan,
- failure analysis,
- architecture decision record,
- risk register,
- client-style explanation,
- before/after improvement evidence.

Weak evidence includes:

- completion alone,
- attendance,
- unaudited self-report,
- generic quiz score disconnected from performance.

### Deliberate Practice

Practice should isolate the hard part before asking for full performance.

For example, evaluation engineering practice can progress through:

1. Identify expected behavior.
2. Build a small eval dataset.
3. Instrument traces.
4. Diagnose failures.
5. Set quality thresholds.
6. Improve the workflow.
7. Explain residual risks.

### Cognitive Apprenticeship

Make expert judgment visible before expecting independent performance.

Useful instructional moves:

- show worked examples,
- narrate tradeoffs,
- compare strong and weak artifacts,
- scaffold the first attempt,
- fade support,
- require reflection on decisions.

## Decision Spine Translation Template

Use this template when converting a signal into a learning or credential change:

| Field | Prompt |
| --- | --- |
| Market signal | What demand evidence triggered this? |
| Role archetype | Prototyper, Builder, Scaler, or other. |
| Capability | What must the person be able to do? |
| Bloom target | What thinking level is required? |
| Dreyfus target | How independently must they perform? |
| Performance context | What realistic situation proves the capability? |
| Practice path | What smaller tasks build toward performance? |
| Assessment evidence | What artifact or behavior will be judged? |
| Credential threshold | What minimum evidence earns the claim? |
| Outcome hypothesis | How should this improve placement, retention, or client trust? |

## Examples

| Signal | Capability | Bloom Target | Dreyfus Target | Useful Evidence |
| --- | --- | --- | --- | --- |
| Agent evaluation and observability | Evaluate and improve agentic workflow reliability. | Evaluate/Create | Competent to Proficient | Eval plan, traces, failure analysis, reliability threshold rationale. |
| AI integration architecture | Connect models, APIs, data stores, and governance constraints. | Analyze/Create | Competent | Architecture decision record, integration prototype, tradeoff explanation. |
| AI security and privacy controls | Reason about data flow, privacy risk, and control points. | Analyze/Evaluate | Competent to Proficient | Threat/risk notes, simulation decisions, mitigations, client-safe explanation. |
| Multimodal product prototyping | Build prototypes using multiple modalities in a workflow. | Apply/Create | Advanced beginner to Competent | Prototype artifact, modality choice rationale, user workflow demo. |
| Prompt library maintenance | Maintain prompt assets as part of broader workflow quality. | Apply/Analyze | Advanced beginner | Monitor as embedded workflow practice, not standalone credential yet. |

## Anti-Patterns

- Mapping every outcome to Create because it sounds ambitious.
- Treating Dreyfus levels as job titles.
- Adding credential tags without performance evidence.
- Counting content coverage as capability.
- Using Bloom verbs without changing the assessment.
- Teaching a tool without defining the durable capability behind it.

## MVP Use

In the current local MVP, this framing is a design guide rather than a validated data field. The next schema maturity step is to add optional fields such as:

- `bloom_target`
- `dreyfus_target`
- `performance_context`
- `assessment_evidence`
- `credential_threshold`

These should be added only after the council agrees the labels are being used consistently.
