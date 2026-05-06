import { badge, escapeHtml } from "../format.js";

const MODE_CLASS = {
  share_ready: "green",
  needs_follow_up: "amber",
  suppressed: "red",
  internal_only: "neutral",
  unreviewed: "neutral",
};

function viewGateFor(stakeholderGates, activeView) {
  return stakeholderGates.stakeholder_views.find((view) => view.view_id === activeView.id);
}

function renderGateItems(items, emptyLabel) {
  if (!items.length) return `<p class="muted-copy">${escapeHtml(emptyLabel)}</p>`;
  return items
    .map(
      (item) => `
        <article class="stakeholder-gate-item ${escapeHtml(MODE_CLASS[item.gate_state] ?? "neutral")}">
          <div>
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml(item.communication_instruction)}</p>
          </div>
          <div class="stakeholder-gate-meta">
            ${badge(item.gate_label, MODE_CLASS[item.gate_state] ?? "neutral")}
            <span>${escapeHtml(item.owner)}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

export function renderStakeholderGates(stakeholderGates, activeView) {
  if (!stakeholderGates) {
    document.getElementById("stakeholder-gate-summary").textContent = "Loading stakeholder communication gates...";
    document.getElementById("stakeholder-gate-view").innerHTML = "";
    document.getElementById("stakeholder-gate-share-list").innerHTML = "";
    document.getElementById("stakeholder-gate-internal-list").innerHTML = "";
    return;
  }
  const summary = stakeholderGates.summary;
  const viewGate = viewGateFor(stakeholderGates, activeView);
  document.getElementById("stakeholder-gate-summary").textContent =
    `${summary.share_ready_count} share-ready, ${summary.needs_follow_up_count} follow-up, ` +
    `${summary.suppressed_count} suppressed, ${summary.unreviewed_count} unreviewed.`;

  if (!viewGate) {
    document.getElementById("stakeholder-gate-view").innerHTML = "<p>No gate data for this stakeholder lens.</p>";
    return;
  }

  document.getElementById("stakeholder-gate-view").innerHTML = `
    <div>
      <span class="metric-label">Current stakeholder mode</span>
      <strong>${escapeHtml(viewGate.mode_label)}</strong>
    </div>
    <div class="stakeholder-gate-counts">
      <span>${viewGate.share_ready_count} share-ready</span>
      <span>${viewGate.needs_follow_up_count} follow-up</span>
      <span>${viewGate.suppressed_count} suppressed</span>
      <span>${viewGate.internal_only_count + viewGate.unreviewed_count} internal/unreviewed</span>
    </div>
  `;

  document.getElementById("stakeholder-gate-share-list").innerHTML = renderGateItems(
    viewGate.share_ready_items,
    "No share-ready language has been accepted for this stakeholder lens yet.",
  );
  document.getElementById("stakeholder-gate-internal-list").innerHTML = renderGateItems(
    [...viewGate.follow_up_items, ...viewGate.internal_items].slice(0, 6),
    "No follow-up, suppressed, or internal-only items for this lens.",
  );
}
