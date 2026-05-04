export const statusLabels = {
  positive_signal: "Positive signal",
  evidence_emerging: "Evidence emerging",
  too_early: "Too early",
  needs_attention: "Needs attention",
  no_outcome_data: "No outcome data",
};

export const statusExplanations = {
  positive_signal:
    "Evidence and outcomes are directionally positive enough to consider amplification while monitoring retention.",
  evidence_emerging:
    "Learner evidence is promising, but placement, retention, or confidence is not mature enough for a stronger claim.",
  too_early:
    "Implementation, learner evidence, or outcome windows have not matured enough to judge impact.",
  needs_attention:
    "Evidence, sample size, suppression, release quality, or outcomes indicate a risk that needs review.",
  no_outcome_data:
    "Traceability exists, but learner evidence or cohort outcomes are not yet linked.",
};

export function formatPercent(value) {
  if (value === null || value === undefined) return "n/a";
  return `${(value * 100).toFixed(1)}%`;
}

export function cssStatus(status) {
  return String(status || "").replaceAll("_", "-");
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function badge(label, status) {
  return `<span class="badge ${status} ${cssStatus(status)}">${escapeHtml(label)}</span>`;
}

export function listItems(items, renderItem) {
  if (!items.length) return '<p class="muted-copy">None linked.</p>';
  return `<ul class="trace-list">${items.map((item) => `<li>${renderItem(item)}</li>`).join("")}</ul>`;
}

export function setStatus(message, kind = "") {
  const banner = document.getElementById("status-banner");
  banner.textContent = message;
  banner.className = `status-banner ${kind}`.trim();
}
