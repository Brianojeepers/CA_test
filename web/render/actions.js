import { escapeHtml } from "../format.js";

export function renderActions(actions, onSelectDecision, emptyLabel = "No current action items.") {
  const list = document.getElementById("action-list");
  if (!actions.length) {
    list.innerHTML = `<p>${escapeHtml(emptyLabel)}</p>`;
    return;
  }
  list.innerHTML = actions
    .map((action) => {
      const decisionId = action.decision_id || "";
      const clickable = decisionId ? "clickable" : "";
      const dataAttr = decisionId ? `data-action-decision-id="${escapeHtml(decisionId)}"` : "";
      return `<button class="action-item ${action.severity} ${clickable}" type="button" ${dataAttr}>${escapeHtml(action.text)}</button>`;
    })
    .join("");
  document.querySelectorAll("[data-action-decision-id]").forEach((item) => {
    item.addEventListener("click", () => {
      onSelectDecision(item.dataset.actionDecisionId);
    });
  });
}
