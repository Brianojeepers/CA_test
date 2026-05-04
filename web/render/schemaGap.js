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
  return field.replaceAll("_", " ");
}

function renderAction(action) {
  const blockedText = action.blocked ? "Blocked" : "Needs definition";
  return `
    <div class="schema-action ${escapeHtml(action.severity)}">
      <div>
        <strong>${escapeHtml(action.source_owner)}</strong>
        <span>${escapeHtml(fieldLabel(action.field))} · ${escapeHtml(action.capability_label)}</span>
      </div>
      <span class="badge ${escapeHtml(action.severity)}">${blockedText}</span>
      <p>${escapeHtml(action.action_text)}</p>
    </div>
  `;
}

function statusForRequirement(requirement) {
  const missingCount = requirement.missing_fields?.length ?? 0;
  if (missingCount === 0) {
    return { tone: "green", label: "Ready" };
  }
  if ((requirement.privacy_sensitivity ?? "").includes("learner")) {
    return { tone: "red", label: "Privacy review" };
  }
  if (requirement.coverage < 0.7) {
    return { tone: "amber", label: "Source gaps" };
  }
  return { tone: "amber", label: "Needs fields" };
}

function missingFieldDetails(requirement) {
  const missing = new Set(requirement.missing_fields ?? []);
  const detailsByField = new Map((requirement.field_details ?? []).map((field) => [field.field, field]));
  return [...missing].map(
    (field) =>
      detailsByField.get(field) ?? {
        field,
        purpose: "Field required by the v0.2 contract.",
        source_owner: requirement.owner,
      },
  );
}

function renderCapabilityCard(requirement) {
  const status = statusForRequirement(requirement);
  const missingDetails = missingFieldDetails(requirement);
  const missingCount = missingDetails.length;
  const missingFields = missingDetails
    .map(
      (field) =>
        `<span class="schema-field" title="${escapeHtml(field.purpose)}">${escapeHtml(fieldLabel(field.field))}</span>`,
    )
    .join("");
  const nextOwner = escapeHtml(missingDetails[0]?.source_owner ?? requirement.owner ?? "Unassigned");
  const nextAction =
    missingCount === 0
      ? "Ready for pilot review once source freshness is agreed."
      : `Next owner: ${nextOwner}. Confirm ${escapeHtml(fieldLabel(missingDetails[0].field))} and related field definitions.`;

  return `
    <article class="schema-card ${status.tone}">
      <div class="schema-card-top">
        <div>
          <h3>${escapeHtml(requirement.label)}</h3>
          <p>${escapeHtml(requirement.decision_unlocked)}</p>
        </div>
        <span class="badge ${status.tone}">${escapeHtml(status.label)}</span>
      </div>
      <div class="schema-meter" aria-label="${escapeHtml(requirement.label)} coverage">
        <span style="width: ${Math.round(requirement.coverage * 100)}%"></span>
      </div>
      <div class="schema-meta">
        <span>${Math.round(requirement.coverage * 100)}% coverage</span>
        <span>${missingCount} missing</span>
        <span>${escapeHtml(requirement.owner)}</span>
        <span>${escapeHtml(fieldLabel(requirement.privacy_sensitivity))}</span>
      </div>
      <div class="schema-fields">${missingFields || '<span class="schema-field">No missing fields</span>'}</div>
      <p class="schema-next">${nextAction}</p>
    </article>
  `;
}

export function renderSchemaGap(report) {
  const summaryElement = document.getElementById("schema-gap-summary");
  const listElement = document.getElementById("schema-gap-list");
  const actionsElement = document.getElementById("schema-gap-actions");
  const blockerElement = document.getElementById("schema-gap-blockers");
  if (!summaryElement || !listElement || !actionsElement || !blockerElement) return;

  if (!report) {
    summaryElement.textContent = "Loading v0.2 readiness...";
    listElement.innerHTML = "";
    actionsElement.innerHTML = "";
    blockerElement.innerHTML = "";
    return;
  }

  const requirements = report.v02_requirements ?? [];
  const fieldActions = report.field_actions ?? [];
  const missingCount = report.summary?.v02_gap_count ?? 0;
  const blockedSources = (report.source_readiness ?? []).filter((source) => source.blocked);
  summaryElement.textContent = `${missingCount} missing v0.2 field(s) across ${requirements.length} capability contracts. ${fieldActions.length} field action(s) queued. ${blockedSources.length} source(s) remain blocked.`;

  listElement.innerHTML = requirements.map(renderCapabilityCard).join("");
  actionsElement.innerHTML = fieldActions.length
    ? fieldActions.slice(0, 8).map(renderAction).join("")
    : '<div class="schema-action green"><strong>No field actions</strong><p>All v0.2 fields are covered by the pilot shape.</p></div>';
  blockerElement.innerHTML = blockedSources.length
    ? blockedSources
        .map(
          (source) => `
            <div class="schema-blocker">
              <strong>${source.contract_id} ${source.data_domain}</strong>
              <span>${escapeHtml(source.next_action)}</span>
            </div>
          `,
        )
        .join("")
    : '<div class="schema-blocker"><strong>No blocked sources</strong><span>All source contracts are at least pilot-reviewable.</span></div>';
}
