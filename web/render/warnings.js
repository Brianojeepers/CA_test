import { escapeHtml } from "../format.js";

export function renderWarnings(warnings) {
  const list = document.getElementById("warning-list");
  if (!warnings.length) {
    list.innerHTML = "<p>No validation warnings.</p>";
    return;
  }
  list.innerHTML = warnings
    .map((warning) => `<div class="warning-item">${escapeHtml(warning)}</div>`)
    .join("");
}
