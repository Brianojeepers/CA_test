const API_BASE_URL = "http://127.0.0.1:8000/api";
const API_URL = `${API_BASE_URL}/monthly-packet`;

const statusLabels = {
  positive_signal: "Positive signal",
  evidence_emerging: "Evidence emerging",
  too_early: "Too early",
  needs_attention: "Needs attention",
  no_outcome_data: "No outcome data",
};

const statusExplanations = {
  positive_signal:
    "Evidence and outcomes are directionally positive enough to consider amplification while monitoring retention.",
  evidence_emerging:
    "Learner evidence is promising, but placement, retention, or confidence is not mature enough for a stronger claim.",
  too_early:
    "Implementation, learner evidence, or outcome windows have not matured enough to judge impact.",
  needs_attention:
    "Evidence, sample size, suppression, release quality, or outcomes indicate a risk that needs review.",
  no_outcome_data:
    "Traceability exists, but learner evidence or cohort outcomes are not yet linked.",
};

let packet = null;
let selectedDecisionId = null;
let activeFilter = "all";
let activeOwner = "all";
let searchQuery = "";
let decisionDetails = {};

function formatPercent(value) {
  if (value === null || value === undefined) return "n/a";
  return `${(value * 100).toFixed(1)}%`;
}

function cssStatus(status) {
  return String(status || "").replaceAll("_", "-");
}

function badge(label, status) {
  return `<span class="badge ${status} ${cssStatus(status)}">${label}</span>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function listItems(items, renderItem) {
  if (!items.length) return "<p class=\"muted-copy\">None linked.</p>";
  return `<ul class="trace-list">${items.map((item) => `<li>${renderItem(item)}</li>`).join("")}</ul>`;
}

function setStatus(message, kind = "") {
  const banner = document.getElementById("status-banner");
  banner.textContent = message;
  banner.className = `status-banner ${kind}`.trim();
}

async function loadPacket() {
  setStatus("Refreshing monthly packet...");
  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    packet = await response.json();
    selectedDecisionId = packet.decision_impact.rows[0]?.decision_id ?? null;
    render();
    if (selectedDecisionId) {
      loadDecisionDetail(selectedDecisionId);
    }
    setStatus("Connected to FastAPI monthly packet endpoint.", "ok");
  } catch (error) {
    setStatus(`Unable to load monthly packet: ${error.message}`, "error");
  }
}

function renderSummary() {
  const trust = packet.data_trust;
  const signal = packet.kpi_posture.signal_strength;
  const prediction = packet.kpi_posture.prediction_accuracy;

  document.getElementById("generated-date").textContent = `Generated ${packet.generated_date}`;
  document.getElementById("data-trust").textContent = trust.validation_status;
  document.getElementById("data-warning").textContent = `${trust.warning_count} validation warning(s)`;
  document.getElementById("signal-average").textContent = signal.average.toFixed(1);
  document.getElementById("signal-mix").textContent =
    `Green ${signal.green} / Amber ${signal.amber} / Red ${signal.red}`;
  document.getElementById("prediction-accuracy").textContent = formatPercent(prediction.value);
  document.getElementById("prediction-scored").textContent = `${prediction.scored_count} scored predictions`;
  document.getElementById("action-count").textContent = packet.actions.length;
}

function renderFilters() {
  const filters = ["all", ...Object.keys(packet.decision_impact.counts)];
  document.getElementById("impact-filter").innerHTML = filters
    .map((filter) => {
      const label = filter === "all" ? "All" : statusLabels[filter];
      const active = filter === activeFilter ? "active" : "";
      return `<button class="${active}" type="button" data-filter="${filter}">${label}</button>`;
    })
    .join("");

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.filter;
      renderFilters();
      renderDecisionTable();
    });
  });
}

function renderOwnerFilter() {
  const owners = [...new Set(packet.decision_impact.rows.map((row) => row.owner))].sort();
  const select = document.getElementById("owner-filter");
  select.innerHTML = [
    '<option value="all">All owners</option>',
    ...owners.map((owner) => {
      const selected = owner === activeOwner ? "selected" : "";
      return `<option value="${escapeHtml(owner)}" ${selected}>${escapeHtml(owner)}</option>`;
    }),
  ].join("");
}

function renderImpactBars() {
  const counts = packet.decision_impact.counts;
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

function filteredRows() {
  return packet.decision_impact.rows.filter((row) => {
    if (activeFilter !== "all" && row.status !== activeFilter) return false;
    if (activeOwner !== "all" && row.owner !== activeOwner) return false;
    if (!searchQuery) return true;
    const detail = decisionDetails[row.decision_id];
    const haystack = [
      row.decision_id,
      row.status,
      row.owner,
      row.summary,
      row.decision_type,
      ...row.release_refs.flatMap((release) => [release.release_id, release.status]),
      ...(detail?.signals ?? []).flatMap((signal) => [signal.signal_id, signal.signal_theme]),
      ...(detail?.competencies ?? []).flatMap((competency) => [
        competency.competency_id,
        competency.competency_cluster,
        competency.capability,
      ]),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(searchQuery);
  });
}

function renderDecisionTable() {
  const rows = filteredRows();
  document.getElementById("decision-table").innerHTML = rows
    .map((row) => {
      const selected = row.decision_id === selectedDecisionId ? "selected" : "";
      const releases = row.release_refs.map((release) => `${release.release_id}:${release.status}`).join(", ");
      return `
        <tr class="${selected}" data-decision-id="${row.decision_id}">
          <td>
            <span class="decision-id">${row.decision_id}</span>
            <span class="decision-summary">${row.summary}</span>
          </td>
          <td>${badge(statusLabels[row.status], row.status)}</td>
          <td>${row.owner}</td>
          <td>${releases || "none"}</td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll("[data-decision-id]").forEach((row) => {
    row.addEventListener("click", () => {
      selectDecision(row.dataset.decisionId);
    });
  });
}

function selectDecision(decisionId) {
  selectedDecisionId = decisionId;
  renderDecisionTable();
  renderDecisionDetail();
  loadDecisionDetail(selectedDecisionId);
}

function renderActions() {
  const list = document.getElementById("action-list");
  if (!packet.actions.length) {
    list.innerHTML = "<p>No current action items.</p>";
    return;
  }
  list.innerHTML = packet.actions
    .map((action) => {
      const decisionId = action.decision_id || "";
      const clickable = decisionId ? "clickable" : "";
      const dataAttr = decisionId ? `data-action-decision-id="${escapeHtml(decisionId)}"` : "";
      return `<button class="action-item ${action.severity} ${clickable}" type="button" ${dataAttr}>${escapeHtml(action.text)}</button>`;
    })
    .join("");
  document.querySelectorAll("[data-action-decision-id]").forEach((item) => {
    item.addEventListener("click", () => {
      selectDecision(item.dataset.actionDecisionId);
    });
  });
}

async function loadDecisionDetail(decisionId) {
  const detail = document.getElementById("decision-detail");
  if (decisionDetails[decisionId]) {
    renderDecisionDetail();
    return;
  }
  detail.innerHTML = `<p class="muted-copy">Loading traceability for ${escapeHtml(decisionId)}...</p>`;
  try {
    const response = await fetch(`${API_BASE_URL}/decisions/${encodeURIComponent(decisionId)}`);
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    decisionDetails[decisionId] = await response.json();
    renderDecisionDetail();
  } catch (error) {
    detail.innerHTML = `<p class="muted-copy">Unable to load decision detail: ${escapeHtml(error.message)}</p>`;
  }
}

function renderDecisionDetail() {
  const row = packet.decision_impact.rows.find((item) => item.decision_id === selectedDecisionId);
  const detail = document.getElementById("decision-detail");
  if (!row) {
    detail.textContent = "Select a decision row to inspect the traceability summary.";
    return;
  }
  const fullDetail = decisionDetails[selectedDecisionId];
  if (!fullDetail) {
    const releases = row.release_refs.map((release) => `${release.release_id} ${release.status}`);
    detail.innerHTML = `
      <p class="detail-title">${escapeHtml(row.decision_id)}</p>
      <p>${escapeHtml(row.summary)}</p>
      <div class="detail-row">${badge(statusLabels[row.status], row.status)}</div>
      <div class="detail-row">
        <span class="meta-pill">${escapeHtml(row.owner)}</span>
        <span class="meta-pill">${escapeHtml(row.decision_type)}</span>
      </div>
      <div class="detail-row">
        <strong>Releases</strong>
        <span>${escapeHtml(releases.join(", ") || "none")}</span>
      </div>
      <p class="muted-copy">Traceability detail is loading...</p>
    `;
    return;
  }
  const releases = row.release_refs.map((release) => `${release.release_id} ${release.status}`);
  const decision = fullDetail.decision;
  const trace = fullDetail.traceability;
  detail.innerHTML = `
    <p class="detail-title">${escapeHtml(row.decision_id)}</p>
    <p>${escapeHtml(decision.decision_summary)}</p>
    <div class="detail-row">${badge(statusLabels[row.status], row.status)}</div>
    <div class="detail-row">
      <span class="meta-pill">${escapeHtml(row.owner)}</span>
      <span class="meta-pill">${escapeHtml(row.decision_type)}</span>
      <span class="meta-pill">${escapeHtml(decision.complexity_tier)}</span>
    </div>
    <div class="trace-counts">
      <span>${trace.signal_count} signals</span>
      <span>${trace.release_count} releases</span>
      <span>${trace.competency_count} competencies</span>
      <span>${trace.evidence_count} evidence rows</span>
    </div>
    <section class="trace-section">
      <h3>Why this status?</h3>
      <p>${escapeHtml(statusExplanations[row.status])}</p>
    </section>
    <section class="trace-section">
      <h3>Rationale</h3>
      <p>${escapeHtml(decision.rationale)}</p>
    </section>
    <section class="trace-section">
      <h3>Signals</h3>
      ${listItems(fullDetail.signals, (signal) =>
        `<strong>${escapeHtml(signal.signal_id)}</strong> ${escapeHtml(signal.signal_theme)}
         <span class="muted-copy">${escapeHtml(signal.status)} / ${escapeHtml(signal.confidence)}</span>`,
      )}
    </section>
    <section class="trace-section">
      <h3>Releases</h3>
      ${listItems(fullDetail.releases, (release) =>
        `<strong>${escapeHtml(release.release_id)}</strong> ${escapeHtml(release.artifact)}
         <span class="muted-copy">${escapeHtml(release.release_status)}</span>`,
      )}
    </section>
    <section class="trace-section">
      <h3>Competencies And Evidence</h3>
      ${listItems(fullDetail.competencies, (competency) =>
        `<strong>${escapeHtml(competency.competency_id)}</strong> ${escapeHtml(competency.capability)}
         <span class="muted-copy">${escapeHtml(competency.target_proficiency)}</span>`,
      )}
      ${listItems(fullDetail.learner_evidence, (evidence) =>
        `<strong>${escapeHtml(evidence.evidence_id)}</strong> ${escapeHtml(evidence.readiness_level)}
         <span class="muted-copy">${escapeHtml(evidence.evidence_summary)}</span>`,
      )}
    </section>
    <section class="trace-section">
      <h3>Outcomes And Predictions</h3>
      ${listItems(fullDetail.cohort_outcomes, (cohort) =>
        `<strong>${escapeHtml(cohort.cohort_id)}</strong> placement ${formatPercent(cohort.placement_rate)}
         <span class="muted-copy">retention ${formatPercent(cohort.retention_90d_rate)}</span>`,
      )}
      ${listItems(fullDetail.predictions, (prediction) =>
        `<strong>${escapeHtml(prediction.prediction_id)}</strong> ${escapeHtml(prediction.outcome)}
         <span class="muted-copy">${escapeHtml(prediction.prediction_statement)}</span>`,
      )}
    </section>
  `;
}

function renderWarnings() {
  const warnings = packet.data_trust.warnings;
  const list = document.getElementById("warning-list");
  if (!warnings.length) {
    list.innerHTML = "<p>No validation warnings.</p>";
    return;
  }
  list.innerHTML = warnings
    .map((warning) => `<div class="warning-item">${escapeHtml(warning)}</div>`)
    .join("");
}

function renderDrilldowns() {
  document.getElementById("drilldowns").innerHTML = packet.stakeholder_drilldowns
    .map(
      (item) => `
        <div class="drilldown">
          <strong>${item.label}</strong>
          <code>${item.command}</code>
        </div>
      `,
    )
    .join("");
}

function renderKnownLimits() {
  document.getElementById("known-limits").innerHTML = packet.known_limits
    .map((limit) => `<li>${limit}</li>`)
    .join("");
}

function render() {
  renderSummary();
  renderFilters();
  renderOwnerFilter();
  renderImpactBars();
  renderDecisionTable();
  renderActions();
  renderDecisionDetail();
  renderDrilldowns();
  renderKnownLimits();
  renderWarnings();
}

document.getElementById("refresh-button").addEventListener("click", loadPacket);
document.getElementById("decision-search").addEventListener("input", (event) => {
  searchQuery = event.target.value.trim().toLowerCase();
  renderDecisionTable();
});
document.getElementById("owner-filter").addEventListener("change", (event) => {
  activeOwner = event.target.value;
  renderDecisionTable();
});
loadPacket();
