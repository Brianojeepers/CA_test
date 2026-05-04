import { escapeHtml } from "../format.js";

function uniqueCount(rows, key) {
  return new Set(rows.flatMap((row) => row[key] ?? [])).size;
}

function insightValue(metric, rows, actions, packet) {
  const statusCount = (status) => rows.filter((row) => row.status === status).length;
  const highPriorityDecisionIds = new Set(
    actions.map((action) => action.decision_id).filter(Boolean),
  );
  rows
    .filter((row) => row.recommendation.priority === "high" || row.status === "needs_attention")
    .forEach((row) => highPriorityDecisionIds.add(row.decision_id));

  const values = {
    actions: actions.length,
    assessment: rows.filter((row) => ["assessment", "credential"].includes(row.decision_type)).length,
    blocked: statusCount("too_early"),
    claimReady: rows.filter((row) => ["positive_signal", "evidence_emerging"].includes(row.status)).length,
    clientCaution: rows.filter((row) => ["too_early", "needs_attention", "no_outcome_data"].includes(row.status))
      .length,
    competencies: uniqueCount(rows, "competency_ids"),
    curriculum: rows.filter((row) => row.decision_type === "curriculum").length,
    emerging: statusCount("evidence_emerging"),
    evidence: uniqueCount(rows, "evidence_ids"),
    evidenceNeeds: rows.filter((row) => ["evidence_emerging", "too_early", "needs_attention"].includes(row.status))
      .length,
    highPriority: highPriorityDecisionIds.size,
    needsAttention: statusCount("needs_attention"),
    outcomeGaps: rows.filter((row) => ["too_early", "no_outcome_data", "needs_attention"].includes(row.status)).length,
    rows: rows.length,
    signals: uniqueCount(rows, "signal_ids"),
    warnings: packet.data_trust.warning_count,
  };

  return values[metric] ?? 0;
}

function insightTone(metric, value) {
  if (["needsAttention", "highPriority", "warnings"].includes(metric) && value > 0) return "red";
  if (["blocked", "clientCaution", "evidenceNeeds", "outcomeGaps"].includes(metric) && value > 0) return "amber";
  if (["claimReady", "emerging"].includes(metric) && value > 0) return "green";
  return "neutral";
}

export function renderInsights(view, rows, actions, packet) {
  document.getElementById("stakeholder-insights").innerHTML = view.insightCards
    .map((card) => {
      const value = insightValue(card.metric, rows, actions, packet);
      const tone = insightTone(card.metric, value);
      return `
        <article class="insight-card ${tone}">
          <span class="metric-label">${escapeHtml(card.label)}</span>
          <strong>${value}</strong>
          <small>${escapeHtml(card.description)}</small>
        </article>
      `;
    })
    .join("");
}
