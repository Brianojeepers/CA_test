import { escapeHtml, statusLabels } from "../format.js";

function viewGateFor(stakeholderGates, activeView) {
  return stakeholderGates?.stakeholder_views?.find((view) => view.view_id === activeView.id) ?? null;
}

function actionTone(action) {
  if (!action) return "neutral";
  return action.severity === "red" ? "red" : action.severity === "green" ? "green" : "amber";
}

function priorityAction(actions) {
  return (
    actions.find((action) => action.severity === "red") ??
    actions.find((action) => action.severity === "amber") ??
    actions[0] ??
    null
  );
}

function decisionSummary(rows, selectedDecisionId) {
  return rows.find((row) => row.decision_id === selectedDecisionId) ?? rows[0] ?? null;
}

function renderGateCard(gate) {
  if (!gate) {
    return `
      <article class="focus-card neutral">
        <span class="metric-label">Share state</span>
        <strong>Loading</strong>
        <p>Review-gate data is loading.</p>
      </article>
    `;
  }
  const tone = gate.suppressed_count ? "red" : gate.needs_follow_up_count ? "amber" : gate.share_ready_count ? "green" : "neutral";
  return `
    <article class="focus-card ${tone}">
      <span class="metric-label">Share state</span>
      <strong>${escapeHtml(gate.mode_label)}</strong>
      <p>${gate.share_ready_count} share-ready; ${gate.needs_follow_up_count + gate.suppressed_count} blocked/follow-up.</p>
    </article>
  `;
}

function renderActionCard(action) {
  if (!action) {
    return `
      <article class="focus-card neutral">
        <span class="metric-label">Next action</span>
        <strong>None</strong>
        <p>No action items for this stakeholder lens.</p>
      </article>
    `;
  }
  return `
    <article class="focus-card ${actionTone(action)}">
      <span class="metric-label">Next action</span>
      <strong>${escapeHtml(action.kind.replaceAll("_", " "))}</strong>
      <p>${escapeHtml(action.text)}</p>
    </article>
  `;
}

function renderDecisionCard(row) {
  if (!row) {
    return `
      <article class="focus-card neutral">
        <span class="metric-label">Selected decision</span>
        <strong>None</strong>
        <p>No decisions in this stakeholder lens.</p>
      </article>
    `;
  }
  const tone = row.status === "needs_attention" ? "red" : row.status === "positive_signal" ? "green" : "amber";
  return `
    <article class="focus-card ${tone}">
      <span class="metric-label">Selected decision</span>
      <strong>${escapeHtml(row.decision_id)}</strong>
      <p>${escapeHtml(statusLabels[row.status] ?? row.status)}: ${escapeHtml(row.recommendation.recommended_action)}</p>
    </article>
  `;
}

export function renderFocusStrip(stakeholderGates, activeView, rows, actions, selectedDecisionId) {
  const gate = viewGateFor(stakeholderGates, activeView);
  const action = priorityAction(actions);
  const row = decisionSummary(rows, selectedDecisionId);
  document.getElementById("focus-strip").innerHTML = `
    ${renderGateCard(gate)}
    ${renderActionCard(action)}
    ${renderDecisionCard(row)}
  `;
}
