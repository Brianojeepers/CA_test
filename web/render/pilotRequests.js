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

function priorityTone(priority) {
  const tones = {
    privacy_review: "red",
    request_definition: "amber",
    already_moving: "green",
  };
  return tones[priority] ?? "neutral";
}

function renderRequest(request) {
  return `
    <article class="pilot-request ${priorityTone(request.request_priority)}">
      <div class="pilot-request-top">
        <div>
          <strong>${escapeHtml(fieldLabel(request.field))}</strong>
          <span>${escapeHtml(request.capability_label)}</span>
        </div>
        <span class="badge ${priorityTone(request.request_priority)}">${escapeHtml(request.request_label)}</span>
      </div>
      <p>${escapeHtml(request.purpose)}</p>
      <div class="pilot-request-meta">
        <span>${escapeHtml(fieldLabel(request.status))}</span>
        <span>${escapeHtml(fieldLabel(request.privacy_sensitivity))}</span>
      </div>
    </article>
  `;
}

function renderOwnerGroup(group) {
  return `
    <section class="pilot-owner-group">
      <div>
        <h3>${escapeHtml(group.owner)}</h3>
        <p>${group.request_count} request(s), ${group.privacy_review_count} privacy-review item(s)</p>
      </div>
      <div class="pilot-request-list">${group.requests.map(renderRequest).join("")}</div>
    </section>
  `;
}

export function renderPilotRequests(pack) {
  const summaryElement = document.getElementById("pilot-request-summary");
  const guardrailsElement = document.getElementById("pilot-request-guardrails");
  const listElement = document.getElementById("pilot-request-list");
  if (!summaryElement || !guardrailsElement || !listElement) return;

  if (!pack) {
    summaryElement.textContent = "Loading pilot data requests...";
    guardrailsElement.innerHTML = "";
    listElement.innerHTML = "";
    return;
  }

  const summary = pack.summary;
  summaryElement.textContent = `${summary.request_count} field request(s) across ${summary.owner_count} owner(s). ${summary.privacy_review_count} require privacy review.`;
  guardrailsElement.innerHTML = (pack.guardrails ?? [])
    .map((guardrail) => `<li>${escapeHtml(guardrail)}</li>`)
    .join("");
  listElement.innerHTML = (pack.owner_groups ?? []).map(renderOwnerGroup).join("");
}
