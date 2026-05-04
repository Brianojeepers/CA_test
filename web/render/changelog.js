import { badge, escapeHtml } from "../format.js";

function categoryButton(category, activeCategory) {
  const active = category.id === activeCategory ? "active" : "";
  return `
    <button class="${active}" type="button" data-changelog-category="${escapeHtml(category.id)}">
      ${escapeHtml(category.label)} ${category.count}
    </button>
  `;
}

function changelogItem(item, selectableDecisionIds) {
  const signalText = item.signal_themes.length ? item.signal_themes.join(", ") : "No signal theme linked";
  const selectable = selectableDecisionIds.has(item.decision_id);
  const tag = selectable ? "button" : "article";
  const typeAttr = selectable ? ' type="button"' : "";
  const dataAttr = selectable ? ` data-changelog-decision-id="${escapeHtml(item.decision_id)}"` : "";
  return `
    <${tag} class="changelog-item ${escapeHtml(item.severity)} ${selectable ? "clickable" : ""}"${typeAttr}${dataAttr}>
      <span class="changelog-item-top">
        ${badge(item.category_label, item.severity)}
        <span>${escapeHtml(item.date || "date pending")}</span>
      </span>
      <strong>${escapeHtml(item.title)}</strong>
      <span class="muted-copy">${escapeHtml(item.item_id)} · owner=${escapeHtml(item.owner)}</span>
      <span>${escapeHtml(item.summary)}</span>
      <span><strong>Why:</strong> ${escapeHtml(item.why_it_matters)}</span>
      <span><strong>Signals:</strong> ${escapeHtml(signalText)}</span>
      <span><strong>Next:</strong> ${escapeHtml(item.next_step)}</span>
    </${tag}>
  `;
}

export function renderChangelog(changelog, activeCategory, onCategoryChange, onSelectDecision, selectableDecisionIds) {
  document.getElementById("changelog-title").textContent = changelog.title;
  document.getElementById("changelog-basis").textContent = changelog.basis;
  document.getElementById("changelog-filter").innerHTML = changelog.categories
    .map((category) => categoryButton(category, activeCategory))
    .join("");

  const items =
    activeCategory === "all"
      ? changelog.items
      : changelog.items.filter((item) => item.category === activeCategory);
  document.getElementById("changelog-list").innerHTML = items.length
    ? items.map((item) => changelogItem(item, selectableDecisionIds)).join("")
    : '<p class="muted-copy">No changelog items match this filter.</p>';

  document.querySelectorAll("[data-changelog-category]").forEach((button) => {
    button.addEventListener("click", () => {
      onCategoryChange(button.dataset.changelogCategory);
    });
  });
  document.querySelectorAll("[data-changelog-decision-id]").forEach((item) => {
    item.addEventListener("click", () => {
      onSelectDecision(item.dataset.changelogDecisionId);
    });
  });
}
