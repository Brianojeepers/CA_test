const API_BASE_URL = "http://127.0.0.1:8000/api";
const API_URL = `${API_BASE_URL}/monthly-packet`;

const statusLabels = {
  positive_signal: "Positive signal",
  evidence_emerging: "Evidence emerging",
  too_early: "Too early",
  needs_attention: "Needs attention",
  no_outcome_data: "No outcome data",
};

let packet = null;
let selectedDecisionId = null;
let activeFilter = "all";
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
  if (activeFilter === "all") return packet.decision_impact.rows;
  return packet.decision_impact.rows.filter((row) => row.status === activeFilter);
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
      selectedDecisionId = row.dataset.decisionId;
      renderDecisionTable();
      renderDecisionDetail();
      loadDecisionDetail(selectedDecisionId);
    });
  });
}

function renderActions() {
  const list = document.getElementById("action-list");
  if (!packet.actions.length) {
    list.innerHTML = "<p>No current action items.</p>";
    return;
  }
  list.innerHTML = packet.actions
    .map((action) => `<div class="action-item ${action.severity}">${action.text}</div>`)
    .join("");
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
  renderImpactBars();
  renderDecisionTable();
  renderActions();
  renderDecisionDetail();
  renderDrilldowns();
  renderKnownLimits();
}

document.getElementById("refresh-button").addEventListener("click", loadPacket);
loadPacket();
