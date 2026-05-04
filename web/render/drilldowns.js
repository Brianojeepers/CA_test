import { escapeHtml } from "../format.js";

export function renderDrilldowns(drilldowns) {
  document.getElementById("drilldowns").innerHTML = drilldowns
    .map(
      (item) => `
        <div class="drilldown">
          <strong>${escapeHtml(item.label)}</strong>
          <code>${escapeHtml(item.command)}</code>
        </div>
      `,
    )
    .join("");
}

export function renderKnownLimits(knownLimits) {
  document.getElementById("known-limits").innerHTML = knownLimits
    .map((limit) => `<li>${escapeHtml(limit)}</li>`)
    .join("");
}
