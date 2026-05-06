import { escapeHtml } from "../format.js";

const COVERAGE_FIELDS = ["signal_ids", "release_refs", "competency_ids", "evidence_ids"];

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

function rowsForInsight(card, rows) {
  const byStatus = (statuses) => rows.filter((row) => statuses.includes(row.status));
  const values = {
    blocked: byStatus(["too_early"]),
    claimReady: byStatus(["positive_signal", "evidence_emerging"]),
    clientCaution: byStatus(["too_early", "needs_attention", "no_outcome_data"]),
    emerging: byStatus(["evidence_emerging"]),
    evidenceNeeds: byStatus(["evidence_emerging", "too_early", "needs_attention"]),
    needsAttention: byStatus(["needs_attention"]),
    outcomeGaps: byStatus(["too_early", "no_outcome_data", "needs_attention"]),
  };
  return values[card.metric] ?? rows;
}

function sourceCoverageForRows(rows) {
  if (!rows.length) return { label: "Sources n/a", tone: "neutral", title: "No rows in this lens." };
  const covered = rows.reduce((total, row) => {
    const fieldCount = COVERAGE_FIELDS.filter((field) => (row[field] ?? []).length > 0).length;
    return total + fieldCount;
  }, 0);
  const ratio = covered / (rows.length * COVERAGE_FIELDS.length);
  const percent = Math.round(ratio * 100);
  const tone = ratio >= 0.75 ? "green" : ratio >= 0.5 ? "amber" : "red";
  return {
    label: `Sources ${percent}%`,
    tone,
    title: "Share of visible rows with linked signals, releases, competencies, and evidence.",
  };
}

function maturityForRows(rows) {
  if (!rows.length) return { label: "Maturity n/a", tone: "neutral" };
  const statuses = new Set(rows.map((row) => row.status));
  if (statuses.has("needs_attention")) return { label: "Maturity contested", tone: "red" };
  if (statuses.has("too_early") || statuses.has("no_outcome_data")) return { label: "Maturity immature", tone: "amber" };
  if (statuses.has("evidence_emerging")) return { label: "Maturity emerging", tone: "amber" };
  return { label: "Maturity validated", tone: "green" };
}

function confidenceForRows(rows, coverage) {
  if (!rows.length) return { label: "Confidence n/a", tone: "neutral" };
  const statuses = new Set(rows.map((row) => row.status));
  if (statuses.has("needs_attention")) return { label: "Confidence review", tone: "red" };
  if (coverage.tone === "red" || statuses.has("too_early") || statuses.has("no_outcome_data")) {
    return { label: "Confidence guarded", tone: "amber" };
  }
  if (statuses.has("evidence_emerging") || coverage.tone === "amber") {
    return { label: "Confidence moderate", tone: "amber" };
  }
  return { label: "Confidence high", tone: "green" };
}

function limitationForRows(rows, packet) {
  if (rows.some((row) => row.status === "needs_attention")) {
    return { label: "Limit: evidence risk", tone: "red" };
  }
  if (rows.some((row) => ["too_early", "no_outcome_data"].includes(row.status))) {
    return { label: "Limit: outcome window", tone: "amber" };
  }
  if (packet.data_trust.warning_count > 0) {
    return { label: "Limit: validation warning", tone: "amber" };
  }
  return { label: "Limit: synthetic data", tone: "neutral", title: packet.known_limits[0] };
}

function trustBadges(card, rows, packet) {
  const insightRows = rowsForInsight(card, rows);
  const coverage = sourceCoverageForRows(insightRows);
  const badges = [
    coverage,
    confidenceForRows(insightRows, coverage),
    maturityForRows(insightRows),
    limitationForRows(insightRows, packet),
  ];
  const visibleBadges = badges.slice(0, 2);
  const hiddenBadges = badges.slice(2);
  if (hiddenBadges.length) {
    visibleBadges.push({
      label: `+${hiddenBadges.length} trust detail(s)`,
      tone: "neutral",
      title: hiddenBadges.map((badge) => badge.label).join("; "),
    });
  }
  return visibleBadges
    .map(
      (badge) =>
        `<span class="trust-badge ${badge.tone}" title="${escapeHtml(badge.title ?? badge.label)}">${escapeHtml(
          badge.label,
        )}</span>`,
    )
    .join("");
}

function actionAttributes(action) {
  if (!action) return "";
  const attributes = [`data-insight-action="${escapeHtml(action.type)}"`];
  if (action.status) attributes.push(`data-insight-status="${escapeHtml(action.status)}"`);
  if (action.focus) attributes.push(`data-insight-focus="${escapeHtml(action.focus)}"`);
  return attributes.join(" ");
}

export function renderInsights(view, rows, actions, packet, onInsightAction) {
  document.getElementById("stakeholder-insights").innerHTML = view.insightCards.slice(0, 3)
    .map((card) => {
      const value = insightValue(card.metric, rows, actions, packet);
      const tone = insightTone(card.metric, value);
      return `
        <button class="insight-card ${tone}" type="button" ${actionAttributes(card.action)}>
          <span class="metric-label">${escapeHtml(card.label)}</span>
          <strong>${value}</strong>
          <small>${escapeHtml(card.description)}</small>
          <span class="trust-badges" aria-label="Trust context">${trustBadges(card, rows, packet)}</span>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll("[data-insight-action]").forEach((card) => {
    card.addEventListener("click", () => {
      onInsightAction({
        type: card.dataset.insightAction,
        status: card.dataset.insightStatus,
        focus: card.dataset.insightFocus,
      });
    });
  });
}
