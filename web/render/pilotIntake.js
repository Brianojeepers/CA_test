function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[character];
  });
}

function fieldLabel(value) {
  return String(value ?? "").replaceAll("_", " ");
}

function renderCapability(group) {
  return `
    <article class="pilot-intake-card ${escapeHtml(group.tone)}">
      <div class="pilot-intake-top">
        <strong>${escapeHtml(group.capability_label)}</strong>
        <span class="badge ${escapeHtml(group.tone)}">${escapeHtml(group.readiness_label)}</span>
      </div>
      <p>${group.accepted_count}/${group.field_count} field(s) accepted for schema design.</p>
      <div class="pilot-intake-meta">
        <span>${group.needs_clarification_count} clarify</span>
        <span>${group.privacy_blocked_count} privacy</span>
        <span>${group.not_ready_count} not ready</span>
      </div>
    </article>
  `;
}

function renderItem(item) {
  const response = item.response ?? {};
  const intakeStatus = item.intake_status;
  return `
    <article class="pilot-intake-item ${escapeHtml(item.tone)}" data-intake-status="${escapeHtml(intakeStatus)}">
      <div class="pilot-intake-top">
        <div>
          <strong>${escapeHtml(fieldLabel(item.field))}</strong>
          <span>${escapeHtml(item.owner)} · ${escapeHtml(item.capability_label)}</span>
        </div>
        <span class="badge ${escapeHtml(item.tone)}">${escapeHtml(item.intake_label)}</span>
      </div>
      <p>${escapeHtml(item.rationale)}</p>
      <p>${escapeHtml(item.next_step)}</p>
      <div class="pilot-intake-meta">
        <span>${escapeHtml(response.source_contract_id ?? "no contract")}</span>
        <span>${escapeHtml(response.privacy_decision ?? "no privacy decision")}</span>
        <span>${escapeHtml(response.freshness_sla ?? "no freshness")}</span>
      </div>
    </article>
  `;
}

export function renderPilotIntake(review) {
  const summaryElement = document.getElementById("pilot-intake-summary");
  const capabilitiesElement = document.getElementById("pilot-intake-capabilities");
  const listElement = document.getElementById("pilot-intake-list");
  if (!summaryElement || !capabilitiesElement || !listElement) return;

  if (!review) {
    summaryElement.textContent = "Loading pilot intake readiness...";
    capabilitiesElement.innerHTML = "";
    listElement.innerHTML = "";
    return;
  }

  const summary = review.summary;
  summaryElement.textContent = `${summary.accepted_count} accepted, ${summary.needs_clarification_count} need clarification, ${summary.privacy_blocked_count} privacy blocked, ${summary.not_ready_count} not ready.`;
  capabilitiesElement.innerHTML = (review.capability_groups ?? []).map(renderCapability).join("");
  listElement.innerHTML = (review.items ?? []).map(renderItem).join("");
}
