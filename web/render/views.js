import { escapeHtml } from "../format.js";

export function renderStakeholderTabs(views, activeView, onViewChange) {
  document.getElementById("stakeholder-views").innerHTML = views
    .map((view) => {
      const active = view.id === activeView.id ? "active" : "";
      return `<button class="${active}" type="button" data-view-id="${escapeHtml(view.id)}">${escapeHtml(view.label)}</button>`;
    })
    .join("");

  document.querySelectorAll("[data-view-id]").forEach((button) => {
    button.addEventListener("click", () => {
      onViewChange(button.dataset.viewId);
    });
  });
}

export function renderStakeholderContext(view, rows, actions) {
  document.getElementById("view-title").textContent = view.title;
  document.getElementById("view-description").textContent = view.description;
  document.getElementById("view-primary-question").textContent = view.primaryQuestion;
  document.getElementById("view-focus-list").innerHTML = view.focus
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  document.getElementById("view-scope-count").textContent = `${rows.length} decision(s) in scope`;
  document.getElementById("view-action-count").textContent = `${actions.length} action(s)`;
  document.getElementById("decision-heading").textContent = `${view.label} decision impact`;
  document.getElementById("decision-question").textContent = view.primaryQuestion;
  document.getElementById("action-heading").textContent = `${view.label} actions`;
}
