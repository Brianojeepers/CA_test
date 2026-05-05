import { badge, escapeHtml } from "../format.js";

let activeReviewStep = "trust_posture";

function outcomeOptions(workflow, currentOutcome, recommendedOutcome) {
  return (workflow.allowed_outcomes ?? [])
    .map((item) => {
      const selected = item.outcome === currentOutcome ? "selected" : "";
      const recommended = item.outcome === recommendedOutcome ? " *" : "";
      return `<option value="${escapeHtml(item.outcome)}" ${selected}>${escapeHtml(item.label + recommended)}</option>`;
    })
    .join("");
}

function outcomeTone(outcome) {
  return {
    accepted: "green",
    needs_follow_up: "amber",
    blocked: "red",
    deferred: "neutral",
    unreviewed: "neutral",
  }[outcome] ?? "neutral";
}

function severityTone(severity) {
  return {
    red: "red",
    amber: "amber",
    green: "green",
    neutral: "neutral",
    pending: "amber",
  }[severity] ?? "neutral";
}

function renderStepTabs(workflow) {
  return (workflow.steps ?? [])
    .map((step) => {
      const active = step.step_id === activeReviewStep ? "active" : "";
      return `<button class="${active}" type="button" data-review-step="${escapeHtml(step.step_id)}">${escapeHtml(step.label)}</button>`;
    })
    .join("");
}

function renderCounts(step) {
  return `
    <div class="review-workflow-counts">
      <span>${escapeHtml(step.item_count)} item(s)</span>
      <span>${escapeHtml(step.unreviewed_count)} unreviewed</span>
      <span>${escapeHtml(step.blocked_count)} blocked</span>
      <span>${escapeHtml(step.needs_follow_up_count)} follow-up</span>
    </div>
  `;
}

function renderRecentEvents(workflow) {
  const events = workflow.recent_events ?? [];
  if (!events.length) return '<p class="muted-copy">No recorded review events yet.</p>';
  return `
    <ul class="review-event-list">
      ${events
        .map(
          (event) => `
            <li>
              <strong>${escapeHtml(event.event_date)} ${escapeHtml(event.title)}</strong>
              <span>${escapeHtml(event.previous_outcome)} -> ${escapeHtml(event.next_outcome)}</span>
            </li>
          `,
        )
        .join("")}
    </ul>
  `;
}

function renderItem(item, workflow) {
  const outcome = item.review_outcome ?? "unreviewed";
  return `
    <article class="review-workflow-item ${severityTone(item.severity)}" data-review-workflow-item>
      <div class="review-workflow-item-top">
        <div>
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.summary)}</p>
        </div>
        <div class="review-workflow-badges">
          ${badge(item.severity, severityTone(item.severity))}
          ${badge(item.review_outcome_label ?? outcome, outcomeTone(outcome))}
        </div>
      </div>
      <div class="review-workflow-meta">
        <span>${escapeHtml(item.owner)}</span>
        <span>${escapeHtml(item.source_ref)}</span>
        <span>Recommended: ${escapeHtml(item.recommended_outcome.replaceAll("_", " "))}</span>
      </div>
      <p class="review-workflow-prompt">${escapeHtml(item.review_prompt)}</p>
      <form class="review-workflow-form" data-review-step-id="${escapeHtml(item.step_id)}" data-review-item-id="${escapeHtml(item.item_id)}">
        <label>
          Outcome
          <select name="outcome">
            ${outcomeOptions(workflow, item.review_outcome === "unreviewed" ? item.recommended_outcome : item.review_outcome, item.recommended_outcome)}
          </select>
        </label>
        <label>
          Notes
          <textarea name="notes" rows="2" placeholder="Owner, blocker, trigger, or rationale">${escapeHtml(item.review_notes)}</textarea>
        </label>
        <button class="secondary-button" type="submit">Save</button>
      </form>
    </article>
  `;
}

export function renderReviewWorkflow(workflow, onStepChange, onOutcomeUpdate) {
  const summaryElement = document.getElementById("review-workflow-summary");
  const tabsElement = document.getElementById("review-workflow-tabs");
  const bodyElement = document.getElementById("review-workflow-body");
  const eventsElement = document.getElementById("review-workflow-events");
  if (!summaryElement || !tabsElement || !bodyElement || !eventsElement) return;

  if (!workflow?.summary) {
    summaryElement.textContent = "Loading review workflow...";
    return;
  }

  const summary = workflow.summary;
  summaryElement.textContent = `${summary.item_count} review item(s), ${summary.unreviewed_count} unreviewed, ${summary.blocked_count} blocked, ${summary.needs_follow_up_count} needing follow-up.`;
  if (!(workflow.steps ?? []).some((step) => step.step_id === activeReviewStep)) {
    activeReviewStep = workflow.steps?.[0]?.step_id ?? "trust_posture";
  }

  tabsElement.innerHTML = renderStepTabs(workflow);
  const step = (workflow.steps ?? []).find((item) => item.step_id === activeReviewStep);
  if (!step) {
    bodyElement.innerHTML = '<p class="muted-copy">No review step available.</p>';
  } else {
    bodyElement.innerHTML = `
      <div class="review-workflow-step-heading">
        <div>
          <h3>${escapeHtml(step.label)}</h3>
          <p>${escapeHtml(step.purpose)}</p>
        </div>
        ${renderCounts(step)}
      </div>
      <div class="review-workflow-list">${(step.items ?? []).map((item) => renderItem(item, workflow)).join("")}</div>
    `;
  }
  eventsElement.innerHTML = renderRecentEvents(workflow);

  tabsElement.querySelectorAll("[data-review-step]").forEach((button) => {
    button.addEventListener("click", () => {
      activeReviewStep = button.dataset.reviewStep;
      onStepChange(activeReviewStep);
    });
  });

  bodyElement.querySelectorAll(".review-workflow-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(form);
      onOutcomeUpdate(
        form.dataset.reviewStepId,
        form.dataset.reviewItemId,
        String(data.get("outcome") ?? ""),
        String(data.get("notes") ?? ""),
      );
    });
  });
}
