const STATUS_ORDER = [
  "positive_signal",
  "evidence_emerging",
  "too_early",
  "needs_attention",
  "no_outcome_data",
];

export const stakeholderViews = [
  {
    id: "council",
    label: "Council",
    title: "Council Review",
    description: "Decision owners, evidence maturity, and unblockers for the monthly review.",
    primaryQuestion: "Which decisions need action, patience, or amplification this month?",
    focus: ["Action queue", "Decision impact", "Traceability"],
    emptyLabel: "No council decisions match the current filters.",
  },
  {
    id: "learning",
    label: "Learning",
    title: "Learning View",
    description: "Curriculum changes, learner-readiness evidence, and pedagogy-linked delivery risk.",
    primaryQuestion: "Which learning changes need evidence, iteration, or stronger implementation quality?",
    focus: ["Curriculum releases", "Readiness evidence", "Pedagogy links"],
    decisionTypes: ["curriculum"],
    owners: ["Learning"],
    emptyLabel: "No learning-owned or curriculum decisions match the current filters.",
    detailLens:
      "Review learner evidence, competency targets, and whether the release should be iterated before being amplified.",
  },
  {
    id: "assessment",
    label: "Assessment Ops",
    title: "Assessment Ops View",
    description: "Credential and assessment changes that need rubric, simulation, or evidence review.",
    primaryQuestion: "Which assessment decisions need implementation or readiness evidence before confidence increases?",
    focus: ["Credential thresholds", "Assessment releases", "Readiness risk"],
    decisionTypes: ["credential", "assessment"],
    owners: ["Assessment Ops"],
    emptyLabel: "No assessment decisions match the current filters.",
    detailLens:
      "Review release status, evidence thresholds, sample size, and whether assessment signals are sufficient.",
  },
  {
    id: "matching",
    label: "Matching / CSM",
    title: "Matching and CSM View",
    description: "Placement-facing signals, outcome maturity, and client-success risks tied to active decisions.",
    primaryQuestion: "Which decisions are ready to influence matching narratives, and which need more outcome evidence?",
    focus: ["Placement evidence", "Client-facing risk", "Outcome maturity"],
    partnerFunctions: ["Matching", "CSM"],
    emptyLabel: "No Matching or CSM-linked decisions match the current filters.",
    detailLens:
      "Review placement, retention, and client-facing confidence before using the decision in matching narratives.",
  },
  {
    id: "solutions",
    label: "Solutions / Sales",
    title: "Solutions and Sales View",
    description: "Market-backed claims, positioning readiness, and decisions connected to commercial pull.",
    primaryQuestion: "Which signals can support client conversations without overstating evidence?",
    focus: ["Market signal", "Positioning readiness", "Commercial risk"],
    partnerFunctions: ["Solutions"],
    emptyLabel: "No Solutions-linked decisions match the current filters.",
    detailLens:
      "Review signal strength, evidence maturity, and the limits that should shape external positioning.",
  },
  {
    id: "data",
    label: "Data / Analytics",
    title: "Data and Analytics View",
    description: "Evidence gaps, validation warnings, source limitations, and measurement readiness.",
    primaryQuestion: "Where is the evidence strong enough to trust, and where is the data still limiting judgment?",
    focus: ["Data trust", "Evidence maturity", "Measurement gaps"],
    statuses: ["evidence_emerging", "too_early", "needs_attention", "no_outcome_data"],
    emptyLabel: "No evidence-risk decisions match the current filters.",
    detailLens:
      "Review validation warnings, traceability completeness, and whether evidence windows are mature enough for claims.",
  },
];

export function defaultView() {
  return stakeholderViews[0];
}

export function viewById(viewId) {
  return stakeholderViews.find((view) => view.id === viewId) ?? defaultView();
}

function intersects(values = [], candidates = []) {
  return values.some((value) => candidates.includes(value));
}

export function rowMatchesView(row, view) {
  if (view.id === "council") return true;
  return (
    intersects([row.owner], view.owners) ||
    intersects([row.decision_type], view.decisionTypes) ||
    intersects(row.partner_functions ?? [], view.partnerFunctions) ||
    intersects([row.status], view.statuses)
  );
}

export function rowsForView(packet, view) {
  return packet.decision_impact.rows.filter((row) => rowMatchesView(row, view));
}

export function countsForRows(rows) {
  return Object.fromEntries(
    STATUS_ORDER.map((status) => [status, rows.filter((row) => row.status === status).length]),
  );
}

export function actionsForView(packet, rows, view) {
  const visibleDecisionIds = new Set(rows.map((row) => row.decision_id));
  const apiActions =
    view.id === "council" || view.id === "data"
      ? packet.actions
      : packet.actions.filter((action) => !action.decision_id || visibleDecisionIds.has(action.decision_id));
  const actionDecisionIds = new Set(apiActions.map((action) => action.decision_id).filter(Boolean));
  const recommendationActions = rows
    .filter((row) => !actionDecisionIds.has(row.decision_id))
    .filter((row) => row.status === "needs_attention" || row.recommendation.priority === "high")
    .map((row) => ({
      kind: "recommendation",
      severity: row.status === "needs_attention" ? "red" : "amber",
      text: `${view.label}: ${row.decision_id} - ${row.recommendation.recommended_action}`,
      decision_id: row.decision_id,
    }));

  return [...apiActions, ...recommendationActions];
}
