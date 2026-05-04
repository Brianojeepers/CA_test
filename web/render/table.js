import { badge, escapeHtml, statusLabels } from "../format.js";

export function renderDecisionTable(rows, selectedDecisionId, onSelectDecision) {
  document.getElementById("decision-table").innerHTML = rows
    .map((row) => {
      const selected = row.decision_id === selectedDecisionId ? "selected" : "";
      const releases = row.release_refs.map((release) => `${release.release_id}:${release.status}`).join(", ");
      return `
        <tr class="${selected}" data-decision-id="${escapeHtml(row.decision_id)}">
          <td>
            <span class="decision-id">${escapeHtml(row.decision_id)}</span>
            <span class="decision-summary">${escapeHtml(row.summary)}</span>
          </td>
          <td>${badge(statusLabels[row.status], row.status)}</td>
          <td>${escapeHtml(row.owner)}</td>
          <td>${escapeHtml(releases || "none")}</td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll("[data-decision-id]").forEach((row) => {
    row.addEventListener("click", () => {
      onSelectDecision(row.dataset.decisionId);
    });
  });
}
