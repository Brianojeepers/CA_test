import { escapeHtml, statusLabels } from "../format.js";

export function renderFilters(packet, activeFilter, onFilterChange) {
  const filters = ["all", ...Object.keys(packet.decision_impact.counts)];
  document.getElementById("impact-filter").innerHTML = filters
    .map((filter) => {
      const label = filter === "all" ? "All" : statusLabels[filter];
      const active = filter === activeFilter ? "active" : "";
      return `<button class="${active}" type="button" data-filter="${filter}">${escapeHtml(label)}</button>`;
    })
    .join("");

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      onFilterChange(button.dataset.filter);
    });
  });
}

export function renderOwnerFilter(rows, activeOwner) {
  const owners = [...new Set(rows.map((row) => row.owner))].sort();
  const select = document.getElementById("owner-filter");
  select.innerHTML = [
    '<option value="all">All owners</option>',
    ...owners.map((owner) => {
      const selected = owner === activeOwner ? "selected" : "";
      return `<option value="${escapeHtml(owner)}" ${selected}>${escapeHtml(owner)}</option>`;
    }),
  ].join("");
}

export function renderMeetingControls(actionMode) {
  const button = document.getElementById("action-mode-button");
  button.classList.toggle("active", actionMode);
  button.textContent = actionMode ? "Exit action mode" : "Action mode";
}
