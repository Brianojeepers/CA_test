import { escapeHtml } from "../format.js";

const COUNT_LABELS = {
  new_decisions: "New decisions",
  removed_decisions: "Removed",
  status_changes: "Status changes",
  recommendation_changes: "Recommendation changes",
  new_actions: "New actions",
  removed_actions: "Cleared actions",
  new_changelog_items: "New changelog",
};

function countPill([key, value]) {
  return `
    <span class="review-diff-count">
      <strong>${value}</strong>
      <span>${escapeHtml(COUNT_LABELS[key] ?? key)}</span>
    </span>
  `;
}

function diffItem(item, selectableDecisionIds) {
  const selectable = item.decision_id && selectableDecisionIds.has(item.decision_id);
  const tag = selectable ? "button" : "article";
  const typeAttr = selectable ? ' type="button"' : "";
  const dataAttr = selectable ? ` data-review-diff-decision-id="${escapeHtml(item.decision_id)}"` : "";
  return `
    <${tag} class="review-diff-item ${escapeHtml(item.severity)} ${selectable ? "clickable" : ""}"${typeAttr}${dataAttr}>
      <span class="metric-label">${escapeHtml(item.kind.replaceAll("_", " "))}</span>
      <strong>${escapeHtml(item.text)}</strong>
    </${tag}>
  `;
}

export function renderReviewDiff(reviewDiff, onSelectDecision, selectableDecisionIds) {
  document.getElementById("review-diff-summary").textContent = reviewDiff.summary;
  document.getElementById("review-diff-counts").innerHTML = Object.entries(reviewDiff.counts)
    .map(countPill)
    .join("");
  const list = document.getElementById("review-diff-list");
  if (!reviewDiff.items.length) {
    list.innerHTML =
      reviewDiff.snapshot_status === "no_snapshot"
        ? '<p class="muted-copy">Run `python3 scripts/save_review_snapshot.py` after the review to start diffing.</p>'
        : '<p class="muted-copy">No material changes detected.</p>';
    return;
  }
  list.innerHTML = reviewDiff.items.slice(0, 8).map((item) => diffItem(item, selectableDecisionIds)).join("");
  document.querySelectorAll("[data-review-diff-decision-id]").forEach((item) => {
    item.addEventListener("click", () => {
      onSelectDecision(item.dataset.reviewDiffDecisionId);
    });
  });
}
