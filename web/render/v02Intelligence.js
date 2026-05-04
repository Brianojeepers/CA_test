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

function fieldLabel(field) {
  return String(field ?? "").replaceAll("_", " ");
}

function renderEvidence(items) {
  return (items ?? [])
    .map((item) => `<span class="meta-pill">${escapeHtml(item.label)}: ${escapeHtml(item.value)}</span>`)
    .join("");
}

function renderMissingFields(fields) {
  if (!fields?.length) return '<span class="schema-field">No missing fields</span>';
  return fields
    .slice(0, 6)
    .map(
      (field) =>
        `<span class="schema-field" title="${escapeHtml(field.purpose)}">${escapeHtml(fieldLabel(field.field))} · ${escapeHtml(field.source_owner)}</span>`,
    )
    .join("");
}

function renderFindings(findings) {
  return (findings ?? [])
    .slice(0, 4)
    .map(
      (finding) => `
        <li class="${escapeHtml(finding.tone)}">
          <strong>${escapeHtml(finding.title)}</strong>
          <span>${escapeHtml(finding.metric)}</span>
          <p>${escapeHtml(finding.detail)}</p>
        </li>
      `,
    )
    .join("");
}

function renderNextActions(actions) {
  if (!actions?.length) return "<li>No field actions queued.</li>";
  return actions
    .map(
      (action) => `
        <li>
          <strong>${escapeHtml(action.owner)}</strong>
          <span>${escapeHtml(fieldLabel(action.field))} · ${escapeHtml(fieldLabel(action.status))}</span>
        </li>
      `,
    )
    .join("");
}

function renderSection(section) {
  return `
    <article class="v02-card ${escapeHtml(section.readiness.tone)}">
      <div class="v02-card-top">
        <div>
          <h3>${escapeHtml(section.label)}</h3>
          <p>${escapeHtml(section.question)}</p>
        </div>
        <span class="badge ${escapeHtml(section.readiness.tone)}">${escapeHtml(section.readiness.label)}</span>
      </div>
      <div class="v02-evidence">${renderEvidence(section.evidence)}</div>
      <p class="v02-guardrail">${escapeHtml(section.do_not_claim)}</p>
      <div class="schema-fields">${renderMissingFields(section.missing_fields)}</div>
      <div class="v02-grid">
        <div>
          <h4>Directional signals</h4>
          <ul class="v02-finding-list">${renderFindings(section.directional_findings)}</ul>
        </div>
        <div>
          <h4>Next owner actions</h4>
          <ul class="v02-action-list">${renderNextActions(section.next_actions)}</ul>
        </div>
      </div>
    </article>
  `;
}

export function renderV02Intelligence(preview) {
  const summaryElement = document.getElementById("v02-intelligence-summary");
  const guardrailsElement = document.getElementById("v02-intelligence-guardrails");
  const listElement = document.getElementById("v02-intelligence-list");
  if (!summaryElement || !guardrailsElement || !listElement) return;

  if (!preview) {
    summaryElement.textContent = "Loading v0.2 intelligence preview...";
    guardrailsElement.innerHTML = "";
    listElement.innerHTML = "";
    return;
  }

  const summary = preview.summary;
  summaryElement.textContent = `${summary.section_count} directional preview(s), ${summary.missing_field_count} missing field(s), ${summary.blocked_section_count} blocked section(s). Hard recommendations are disabled.`;
  guardrailsElement.innerHTML = (preview.guardrails ?? [])
    .map((guardrail) => `<li>${escapeHtml(guardrail)}</li>`)
    .join("");
  listElement.innerHTML = (preview.sections ?? []).map(renderSection).join("");
}
