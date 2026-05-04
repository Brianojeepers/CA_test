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

let activeSchemaOwner = "all";

function statusTone(status) {
  const tones = {
    open: "neutral",
    in_review: "amber",
    approved: "green",
    blocked: "red",
    deferred: "neutral",
  };
  return tones[status] ?? "neutral";
}

function statusLabel(status) {
  return fieldLabel(status ?? "open");
}

function statusOptions(selectedStatus) {
  return ["open", "in_review", "approved", "blocked", "deferred"]
    .map((status) => `<option value="${status}" ${status === selectedStatus ? "selected" : ""}>${escapeHtml(statusLabel(status))}</option>`)
    .join("");
}

function renderAction(action) {
  const actionStatus = action.action_status ?? "open";
  return `
    <div class="schema-action ${escapeHtml(action.severity)}">
      <div>
        <strong>${escapeHtml(action.source_owner)}</strong>
        <span>${escapeHtml(fieldLabel(action.field))} · ${escapeHtml(action.capability_label)}</span>
      </div>
      <span class="badge ${statusTone(actionStatus)}">${escapeHtml(statusLabel(actionStatus))}</span>
      <p>${escapeHtml(action.action_text)}</p>
      ${action.status_notes ? `<p class="schema-status-note">${escapeHtml(action.status_notes)}</p>` : ""}
      <form class="schema-status-form" data-schema-action-capability="${escapeHtml(action.capability)}" data-schema-action-field="${escapeHtml(action.field)}">
        <label>
          <span>Status</span>
          <select name="status" aria-label="Status for ${escapeHtml(fieldLabel(action.field))}">
            ${statusOptions(actionStatus)}
          </select>
        </label>
        <label class="schema-status-notes">
          <span>Notes</span>
          <textarea name="notes" rows="2" aria-label="Notes for ${escapeHtml(fieldLabel(action.field))}">${escapeHtml(action.status_notes ?? "")}</textarea>
        </label>
        <button type="submit" class="secondary-button">Save</button>
      </form>
    </div>
  `;
}

function ownerGroups(report) {
  return report.field_actions_by_owner ?? [];
}

function ownerActions(report) {
  if (activeSchemaOwner === "all") {
    return report.field_actions ?? [];
  }
  return ownerGroups(report).find((group) => group.owner === activeSchemaOwner)?.actions ?? [];
}

function allOwnerCounts(report) {
  const actions = report.field_actions ?? [];
  return {
    action_count: actions.length,
    red: actions.filter((action) => action.severity === "red").length,
    amber: actions.filter((action) => action.severity === "amber").length,
    blocked: actions.filter((action) => action.blocked).length,
  };
}

function selectedOwnerSummary(report) {
  const selected =
    activeSchemaOwner === "all"
      ? { owner: "All owners", ...allOwnerCounts(report), top_action: ownerActions(report)[0] }
      : ownerGroups(report).find((group) => group.owner === activeSchemaOwner);
  if (!selected) {
    return "No owner actions for the selected view.";
  }
  const top = selected.top_action ? ` Top action: ${fieldLabel(selected.top_action.field)}.` : "";
  const openCount = selected.status_counts?.open ?? ownerActions(report).filter((action) => action.action_status === "open").length;
  return `${selected.owner}: ${selected.action_count} action(s), ${openCount} open, ${selected.red} red, ${selected.amber} amber, ${selected.blocked} blocked.${top}`;
}

function renderOwnerTabs(report) {
  const groups = ownerGroups(report);
  if (activeSchemaOwner !== "all" && !groups.some((group) => group.owner === activeSchemaOwner)) {
    activeSchemaOwner = "all";
  }
  const tabs = [
    { owner: "all", label: "All owners", count: report.field_actions?.length ?? 0 },
    ...groups.map((group) => ({ owner: group.owner, label: group.owner, count: group.action_count })),
  ];
  return tabs
    .map(
      (tab) => `
        <button type="button" class="${tab.owner === activeSchemaOwner ? "active" : ""}" data-schema-owner="${escapeHtml(tab.owner)}">
          ${escapeHtml(tab.label)} (${tab.count})
        </button>
      `,
    )
    .join("");
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

export function renderSchemaGap(report, onActionUpdate) {
  const summaryElement = document.getElementById("schema-gap-summary");
  const listElement = document.getElementById("schema-gap-list");
  const ownerTabsElement = document.getElementById("schema-owner-tabs");
  const ownerSummaryElement = document.getElementById("schema-owner-summary");
  const actionsElement = document.getElementById("schema-gap-actions");
  const blockerElement = document.getElementById("schema-gap-blockers");
  if (!summaryElement || !listElement || !ownerTabsElement || !ownerSummaryElement || !actionsElement || !blockerElement) return;

  if (!report) {
    summaryElement.textContent = "Loading v0.2 readiness...";
    listElement.innerHTML = "";
    ownerTabsElement.innerHTML = "";
    ownerSummaryElement.textContent = "Loading owner actions...";
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
  ownerTabsElement.innerHTML = renderOwnerTabs(report);
  ownerSummaryElement.textContent = selectedOwnerSummary(report);

  const scopedActions = ownerActions(report);
  actionsElement.innerHTML = scopedActions.length
    ? scopedActions.slice(0, activeSchemaOwner === "all" ? 8 : scopedActions.length).map(renderAction).join("")
    : '<div class="schema-action green"><strong>No field actions</strong><p>All v0.2 fields are covered by the pilot shape.</p></div>';

  ownerTabsElement.querySelectorAll("[data-schema-owner]").forEach((button) => {
    button.addEventListener("click", () => {
      activeSchemaOwner = button.dataset.schemaOwner ?? "all";
      renderSchemaGap(report, onActionUpdate);
    });
  });

  actionsElement.querySelectorAll("[data-schema-action-capability]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!onActionUpdate) return;
      const action = scopedActions.find(
        (candidate) =>
          candidate.capability === form.dataset.schemaActionCapability &&
          candidate.field === form.dataset.schemaActionField,
      );
      const statusInput = form.querySelector("[name='status']");
      const notesInput = form.querySelector("[name='notes']");
      const button = form.querySelector("button[type='submit']");
      if (!action || !statusInput || !notesInput) return;
      if (button) {
        button.disabled = true;
        button.textContent = "Saving";
      }
      try {
        await onActionUpdate(action, statusInput.value, notesInput.value.trim());
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = "Save";
        }
      }
    });
  });

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
