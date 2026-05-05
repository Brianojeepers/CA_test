import { badge, escapeHtml } from "../format.js";

const ARCHITECTURE_VIEWS = [
  { id: "layers", label: "Layers" },
  { id: "sources", label: "Sources" },
  { id: "normalization", label: "Normalization" },
  { id: "governance", label: "Governance" },
  { id: "policy", label: "Policy" },
];

function list(values, limit = 4) {
  const items = (values ?? []).slice(0, limit);
  if (!items.length) return '<p class="muted-copy">None listed.</p>';
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function chips(values, limit = 6) {
  const items = (values ?? []).slice(0, limit);
  if (!items.length) return '<span class="meta-pill">None linked</span>';
  const overflow = (values ?? []).length - items.length;
  return [
    ...items.map((item) => `<span class="meta-pill">${escapeHtml(item)}</span>`),
    overflow > 0 ? `<span class="meta-pill">+${overflow}</span>` : "",
  ].join("");
}

function toneForReadiness(readiness) {
  return {
    covered: "green",
    partial: "amber",
    thin: "amber",
    missing: "red",
  }[readiness] ?? "neutral";
}

function toneForTrust(status) {
  return {
    privacy_blocked: "red",
    manual_sampling_only: "amber",
    unmapped: "amber",
    planning_ready: "neutral",
    pilot_candidate: "green",
  }[status] ?? "neutral";
}

function toneForIngestion(status) {
  return {
    blocked: "red",
    manual_contracting: "amber",
    pilot_candidate: "green",
  }[status] ?? "neutral";
}

function toneForPolicy(policy) {
  return {
    act_now: "green",
    revise: "amber",
    monitor: "neutral",
    wait: "amber",
    escalate: "red",
    archive: "neutral",
  }[policy] ?? "neutral";
}

function toneForStress(result) {
  return result === "pass" ? "green" : "red";
}

function renderTabs(activeView) {
  return ARCHITECTURE_VIEWS.map((view) => {
    const active = view.id === activeView ? "active" : "";
    return `<button class="${active}" type="button" data-architecture-view="${escapeHtml(view.id)}">${escapeHtml(view.label)}</button>`;
  }).join("");
}

function renderLayer(layer) {
  return `
    <article class="architecture-card ${toneForReadiness(layer.readiness)}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(layer.label)}</h3>
          <p>${escapeHtml(layer.current_coverage)}</p>
        </div>
        ${badge(layer.readiness.replaceAll("_", " "), toneForReadiness(layer.readiness))}
      </div>
      <dl class="architecture-detail-list">
        <div>
          <dt>Target</dt>
          <dd>${escapeHtml(layer.target_state)}</dd>
        </div>
        <div>
          <dt>Value</dt>
          <dd>${escapeHtml(layer.stakeholder_value)}</dd>
        </div>
        <div>
          <dt>Next</dt>
          <dd>${escapeHtml(layer.horizontal_next_step)}</dd>
        </div>
        <div>
          <dt>Deferred</dt>
          <dd>${escapeHtml(layer.defer_vertical_work)}</dd>
        </div>
      </dl>
      <div class="architecture-chip-list">${chips(layer.current_assets, 5)}</div>
    </article>
  `;
}

function renderLayers(data) {
  const layers = data.architectureReadiness?.layers ?? [];
  return `
    <div class="architecture-list">
      ${layers.map(renderLayer).join("")}
    </div>
  `;
}

function renderSurface(surface) {
  const counts = surface.source_readiness_counts ?? {};
  return `
    <article class="architecture-card ${toneForTrust(surface.trust_status)}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(surface.label)}</h3>
          <p>${escapeHtml(surface.decision_use)}</p>
        </div>
        ${badge(surface.trust_label ?? surface.trust_status, toneForTrust(surface.trust_status))}
      </div>
      <div class="architecture-metrics">
        <span>Green ${counts.green ?? 0}</span>
        <span>Amber ${counts.amber ?? 0}</span>
        <span>Red ${counts.red ?? 0}</span>
        <span>${escapeHtml(surface.stakeholder_confidence)} confidence</span>
      </div>
      <p class="architecture-limit">${escapeHtml(surface.known_limit)}</p>
      <p>${escapeHtml(surface.next_trust_action)}</p>
    </article>
  `;
}

function renderSource(source) {
  return `
    <article class="architecture-card ${toneForIngestion(source.ingestion_status)}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(source.contract_id)} - ${escapeHtml(source.data_domain)}</h3>
          <p>${escapeHtml(source.candidate_source)}</p>
        </div>
        ${badge(source.ingestion_status.replaceAll("_", " "), toneForIngestion(source.ingestion_status))}
      </div>
      <div class="architecture-metrics">
        <span>${escapeHtml(source.allowed_use)}</span>
        <span>${escapeHtml(source.standardization_risk)} risk</span>
        <span>${escapeHtml(source.freshness_sla)}</span>
      </div>
      <p>${escapeHtml(source.confidence_basis)}</p>
      <p>${escapeHtml(source.next_ingestion_action)}</p>
    </article>
  `;
}

function renderSources(data) {
  const trustSurfaces = data.trustRegistry?.surfaces ?? [];
  const sources = data.sourceIngestion?.sources ?? [];
  return `
    <div class="architecture-two-column">
      <section>
        <h3>Surface trust</h3>
        <div class="architecture-list compact-list">${trustSurfaces.map(renderSurface).join("")}</div>
      </section>
      <section>
        <h3>Source posture</h3>
        <div class="architecture-list compact-list">${sources.map(renderSource).join("")}</div>
      </section>
    </div>
  `;
}

function stateSummary(states) {
  return Object.entries(states ?? {})
    .map(([state, count]) => `<span class="meta-pill">${escapeHtml(state.replaceAll("_", " "))}: ${escapeHtml(count)}</span>`)
    .join("");
}

function renderRole(role) {
  return `
    <article class="architecture-card neutral">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(role.role_archetype)}</h3>
          <p>${escapeHtml(role.competency_count)} competencies across ${escapeHtml((role.clusters ?? []).join(", "))}</p>
        </div>
      </div>
      <div class="architecture-chip-list">${stateSummary(role.states)}</div>
      <p>${escapeHtml((role.owners ?? []).join(", "))}</p>
    </article>
  `;
}

function renderCrosswalkRow(row) {
  const tone = {
    aligned_for_planning: "green",
    monitor_only: "neutral",
    evidence_pending: "amber",
    implementation_pending: "amber",
    suppressed_evidence: "red",
    needs_mapping: "red",
  }[row.crosswalk_state] ?? "neutral";
  return `
    <article class="architecture-card ${tone}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(row.competency_id)} - ${escapeHtml(row.competency_cluster)}</h3>
          <p>${escapeHtml(row.capability)}</p>
        </div>
        ${badge(row.state_label, tone)}
      </div>
      <div class="architecture-metrics">
        <span>${escapeHtml(row.role_archetype)}</span>
        <span>${escapeHtml(row.target_proficiency)}</span>
        <span>${escapeHtml(row.market_priority)}</span>
      </div>
      <p>${escapeHtml(row.normalization_focus)}</p>
      <div class="architecture-chip-list">${chips(row.ambiguity_flags, 5)}</div>
    </article>
  `;
}

function renderNormalization(data) {
  const roles = data.normalizationCrosswalk?.role_summaries ?? [];
  const rows = data.normalizationCrosswalk?.rows ?? [];
  return `
    <div class="architecture-two-column">
      <section>
        <h3>Role anchors</h3>
        <div class="architecture-list compact-list">${roles.map(renderRole).join("")}</div>
      </section>
      <section>
        <h3>Competency crosswalk</h3>
        <div class="architecture-list compact-list">${rows.map(renderCrosswalkRow).join("")}</div>
      </section>
    </div>
  `;
}

function renderCadence(cadence) {
  const tone = cadence.manual_readiness === "ready_for_manual_trial" ? "green" : "amber";
  return `
    <article class="architecture-card ${tone}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(cadence.label)}</h3>
          <p>${escapeHtml(cadence.purpose)}</p>
        </div>
        ${badge(cadence.manual_readiness.replaceAll("_", " "), tone)}
      </div>
      <div class="architecture-metrics">
        <span>${escapeHtml(cadence.cadence)}</span>
        <span>${escapeHtml(cadence.owner)}</span>
      </div>
      <dl class="architecture-detail-list">
        <div>
          <dt>Entry</dt>
          <dd>${list(cadence.entry_criteria, 3)}</dd>
        </div>
        <div>
          <dt>Exit</dt>
          <dd>${list(cadence.exit_criteria, 3)}</dd>
        </div>
        <div>
          <dt>Rights</dt>
          <dd>${list(cadence.decision_rights, 3)}</dd>
        </div>
      </dl>
    </article>
  `;
}

function renderGovernance(data) {
  const cadences = data.governanceCadence?.cadences ?? [];
  return `<div class="architecture-list">${cadences.map(renderCadence).join("")}</div>`;
}

function renderPolicyRow(row) {
  const tone = toneForPolicy(row.policy_outcome);
  return `
    <article class="architecture-card ${tone}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(row.decision_id)} - ${escapeHtml(row.policy_label)}</h3>
          <p>${escapeHtml(row.rationale)}</p>
        </div>
        ${badge(row.policy_outcome.replaceAll("_", " "), tone)}
      </div>
      <div class="architecture-metrics">
        <span>${escapeHtml(row.owner)}</span>
        <span>${escapeHtml(row.impact_status)}</span>
        <span>${escapeHtml(row.journey_mode)}</span>
      </div>
      <p>${escapeHtml(row.allowed_action)}</p>
      <p class="architecture-limit">${escapeHtml(row.must_defer)}</p>
    </article>
  `;
}

function renderStressScenario(scenario) {
  const tone = toneForStress(scenario.result);
  return `
    <article class="architecture-card ${tone}">
      <div class="architecture-card-top">
        <div>
          <h3>${escapeHtml(scenario.scenario_id)} - ${escapeHtml(scenario.title)}</h3>
          <p>${escapeHtml(scenario.claim_pressure)}</p>
        </div>
        ${badge(scenario.result, tone)}
      </div>
      <p>${escapeHtml(scenario.safe_response)}</p>
      <div class="architecture-chip-list">${chips(scenario.evidence, 4)}</div>
    </article>
  `;
}

function renderPolicy(data) {
  const rows = data.decisionPolicy?.policy_rows ?? [];
  const scenarios = data.reasoningStress?.scenarios ?? [];
  return `
    <div class="architecture-two-column">
      <section>
        <h3>Decision policy</h3>
        <div class="architecture-list compact-list">${rows.map(renderPolicyRow).join("")}</div>
      </section>
      <section>
        <h3>Reasoning stress</h3>
        <div class="architecture-list compact-list">${scenarios.map(renderStressScenario).join("")}</div>
      </section>
    </div>
  `;
}

function renderNextSlices(data) {
  const slices = data.reasoningStress?.next_horizontal_slices ?? data.architectureReadiness?.next_horizontal_slices ?? [];
  return slices.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderBody(data, activeView) {
  if (activeView === "sources") return renderSources(data);
  if (activeView === "normalization") return renderNormalization(data);
  if (activeView === "governance") return renderGovernance(data);
  if (activeView === "policy") return renderPolicy(data);
  return renderLayers(data);
}

export function renderArchitectureSurface(data, activeView, onViewChange) {
  const summaryElement = document.getElementById("architecture-summary");
  const tabsElement = document.getElementById("architecture-tabs");
  const bodyElement = document.getElementById("architecture-body");
  const nextElement = document.getElementById("architecture-next-list");
  if (!summaryElement || !tabsElement || !bodyElement || !nextElement) return;

  const architectureSummary = data.architectureReadiness?.summary;
  const rating = data.architectureReadiness?.rating;
  const sourceSummary = data.sourceIngestion?.summary;
  const policySummary = data.decisionPolicy?.summary;
  const stressSummary = data.reasoningStress?.summary;

  if (!architectureSummary || !rating) {
    summaryElement.textContent = "Loading architecture navigation...";
    return;
  }

  summaryElement.textContent = `${rating.score}/${rating.out_of} horizontal rating; ${architectureSummary.layer_count} architecture layers, ${sourceSummary?.source_count ?? 0} source contracts, ${policySummary?.decision_count ?? 0} policy outcomes, ${stressSummary?.pass_count ?? 0}/${stressSummary?.scenario_count ?? 0} stress tests passing.`;
  tabsElement.innerHTML = renderTabs(activeView);
  bodyElement.innerHTML = renderBody(data, activeView);
  nextElement.innerHTML = renderNextSlices(data);

  tabsElement.querySelectorAll("[data-architecture-view]").forEach((button) => {
    button.addEventListener("click", () => onViewChange(button.dataset.architectureView));
  });
}
