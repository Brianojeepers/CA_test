import { cssStatus, statusLabels } from "../format.js";

export function renderImpactBars(counts) {
  const max = Math.max(...Object.values(counts), 1);
  document.getElementById("impact-bars").innerHTML = Object.entries(counts)
    .map(([status, count]) => {
      const width = `${Math.max((count / max) * 100, count > 0 ? 8 : 0)}%`;
      return `
        <div class="impact-row">
          <span>${statusLabels[status]}</span>
          <div class="bar-track">
            <div class="bar-fill ${cssStatus(status)}" style="width:${width}"></div>
          </div>
          <strong>${count}</strong>
        </div>
      `;
    })
    .join("");
}
