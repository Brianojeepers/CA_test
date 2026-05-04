import { badge, escapeHtml } from "../format.js";

const ACTIONS_BY_STATUS = {
  positive_signal: {
    label: "Keep / Amplify",
    tone: "green",
    summary: "Continue the change and consider careful amplification while monitoring retention.",
  },
  evidence_emerging: {
    label: "Update / Monitor",
    tone: "amber",
    summary: "Keep the change active, tighten evidence quality, and review before stronger claims.",
  },
  too_early: {
    label: "Wait",
    tone: "amber",
    summary: "Do not judge impact yet; implementation or outcome windows still need to mature.",
  },
  needs_attention: {
    label: "Update",
    tone: "red",
    summary: "Review quality, sample size, rubric thresholds, or outcome signals before continuing as-is.",
  },
  no_outcome_data: {
    label: "Wait",
    tone: "neutral",
    summary: "Add learner or cohort evidence before making a confident impact claim.",
  },
};

function actionForRow(row) {
  const action = ACTIONS_BY_STATUS[row.status] ?? ACTIONS_BY_STATUS.no_outcome_data;
  const risk = row.recommendation.blocker_or_risk.toLowerCase();
  if (row.status === "needs_attention" && risk.includes("suppressed evidence")) {
    return {
      label: "Update / Consider Deprecation",
      tone: "red",
      summary: "Treat this as a corrective review; deprecate only if the next evidence cycle remains weak.",
    };
  }
  return action;
}

function priorityTone(priority) {
  if (priority === "high") return "red";
  if (priority === "low") return "green";
  return "amber";
}

export function renderRecommendation(packet, selectedDecisionId, view) {
  const panel = document.getElementById("recommendation-panel");
  const row = packet.decision_impact.rows.find((item) => item.decision_id === selectedDecisionId);
  if (!row) {
    panel.textContent = "Select a decision row to see the recommended action.";
    return;
  }

  const action = actionForRow(row);
  panel.innerHTML = `
    <div class="recommendation-verdict ${action.tone}">
      <span class="metric-label">Decision</span>
      <strong>${escapeHtml(action.label)}</strong>
      <p>${escapeHtml(action.summary)}</p>
    </div>
    <div class="recommendation-meta">
      ${badge(row.recommendation.priority, priorityTone(row.recommendation.priority))}
      <span class="meta-pill">${escapeHtml(row.owner)}</span>
      <span class="meta-pill">${escapeHtml(view.label)}</span>
    </div>
    <dl class="recommendation-reasons">
      <div>
        <dt>Rationale</dt>
        <dd>${escapeHtml(row.recommendation.evidence_basis)}</dd>
      </div>
      <div>
        <dt>Risk</dt>
        <dd>${escapeHtml(row.recommendation.blocker_or_risk)}</dd>
      </div>
      <div>
        <dt>Next trigger</dt>
        <dd>${escapeHtml(row.recommendation.next_review_trigger)}</dd>
      </div>
    </dl>
  `;
}
