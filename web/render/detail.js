import { badge, escapeHtml, formatPercent, listItems, statusExplanations, statusLabels } from "../format.js";

export function renderDecisionDetail(packet, selectedDecisionId, fullDetail, view) {
  const row = packet.decision_impact.rows.find((item) => item.decision_id === selectedDecisionId);
  const detail = document.getElementById("decision-detail");
  if (!row) {
    detail.textContent = "Select a decision row to inspect the traceability summary.";
    return;
  }
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
    ${
      view?.detailLens
        ? `<section class="trace-section view-lens">
            <h3>${escapeHtml(view.label)} lens</h3>
            <p>${escapeHtml(view.detailLens)}</p>
          </section>`
        : ""
    }
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
