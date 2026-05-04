import { fetchDecisionDetail, fetchMonthlyPacket } from "./api.js";
import { setStatus } from "./format.js";
import { renderActions } from "./render/actions.js";
import { renderDecisionDetail } from "./render/detail.js";
import { renderDrilldowns, renderKnownLimits } from "./render/drilldowns.js";
import { renderFilters, renderMeetingControls, renderOwnerFilter } from "./render/filters.js";
import { renderImpactBars } from "./render/impact.js";
import { buildMeetingNotes, renderMeetingNotes } from "./render/meetingNotes.js";
import { renderSummary } from "./render/summary.js";
import { renderDecisionTable } from "./render/table.js";
import { renderWarnings } from "./render/warnings.js";

let packet = null;
let selectedDecisionId = null;
let activeFilter = "all";
let activeOwner = "all";
let searchQuery = "";
let actionMode = false;
let decisionDetails = {};

function actionDecisionIds() {
  return new Set(packet.actions.map((action) => action.decision_id).filter(Boolean));
}

function filteredRows() {
  const actionIds = actionDecisionIds();
  const rows = packet.decision_impact.rows.filter((row) => {
    if (actionMode && !actionIds.has(row.decision_id) && row.status !== "needs_attention") return false;
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
      ...row.signal_ids,
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
  if (!actionMode) return rows;
  const order = {
    needs_attention: 0,
    too_early: 1,
    evidence_emerging: 2,
    no_outcome_data: 3,
    positive_signal: 4,
  };
  return rows.sort((a, b) => {
    const aAction = actionIds.has(a.decision_id) ? -1 : 0;
    const bAction = actionIds.has(b.decision_id) ? -1 : 0;
    return aAction - bAction || order[a.status] - order[b.status] || a.decision_id.localeCompare(b.decision_id);
  });
}

function renderDecisionTableFromState() {
  renderDecisionTable(filteredRows(), selectedDecisionId, selectDecision);
}

function handleFilterChange(nextFilter) {
  activeFilter = nextFilter;
  renderFilters(packet, activeFilter, handleFilterChange);
  renderDecisionTableFromState();
}

function selectDecision(decisionId) {
  selectedDecisionId = decisionId;
  renderDecisionTableFromState();
  renderDecisionDetail(packet, selectedDecisionId, decisionDetails[selectedDecisionId]);
  loadDecisionDetail(selectedDecisionId);
}

async function loadDecisionDetail(decisionId) {
  if (decisionDetails[decisionId]) {
    renderDecisionDetail(packet, selectedDecisionId, decisionDetails[selectedDecisionId]);
    return;
  }
  try {
    decisionDetails[decisionId] = await fetchDecisionDetail(decisionId);
    renderDecisionDetail(packet, selectedDecisionId, decisionDetails[selectedDecisionId]);
    renderDecisionTableFromState();
  } catch (error) {
    setStatus(`Unable to load decision detail: ${error.message}`, "error");
  }
}

function render() {
  renderSummary(packet);
  renderFilters(packet, activeFilter, handleFilterChange);
  renderOwnerFilter(packet, activeOwner);
  renderMeetingControls(actionMode);
  renderImpactBars(packet.decision_impact.counts);
  renderDecisionTableFromState();
  renderActions(packet.actions, selectDecision);
  renderDecisionDetail(packet, selectedDecisionId, decisionDetails[selectedDecisionId]);
  renderDrilldowns(packet.stakeholder_drilldowns);
  renderKnownLimits(packet.known_limits);
  renderWarnings(packet.data_trust.warnings);
  renderMeetingNotes(packet);
}

async function loadPacket() {
  setStatus("Refreshing monthly packet...");
  try {
    packet = await fetchMonthlyPacket();
    decisionDetails = {};
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

document.getElementById("refresh-button").addEventListener("click", loadPacket);
document.getElementById("decision-search").addEventListener("input", (event) => {
  searchQuery = event.target.value.trim().toLowerCase();
  renderDecisionTableFromState();
});
document.getElementById("owner-filter").addEventListener("change", (event) => {
  activeOwner = event.target.value;
  renderDecisionTableFromState();
});
document.getElementById("action-mode-button").addEventListener("click", () => {
  actionMode = !actionMode;
  renderMeetingControls(actionMode);
  renderDecisionTableFromState();
});
document.getElementById("copy-meeting-notes").addEventListener("click", async () => {
  const notes = buildMeetingNotes(packet);
  try {
    await navigator.clipboard.writeText(notes);
    setStatus("Council meeting notes copied.", "ok");
  } catch {
    setStatus("Copy failed; select text from the Council notes panel.", "error");
  }
});
loadPacket();
