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
import { renderStakeholderContext, renderStakeholderTabs } from "./render/views.js";
import { renderWarnings } from "./render/warnings.js";
import {
  actionsForView,
  countsForRows,
  defaultView,
  rowsForView,
  stakeholderViews,
  viewById,
} from "./stakeholders.js";

let packet = null;
let selectedDecisionId = null;
let activeView = defaultView();
let activeFilter = "all";
let activeOwner = "all";
let searchQuery = "";
let actionMode = false;
let decisionDetails = {};

function baseRows() {
  return rowsForView(packet, activeView);
}

function viewActions(rows = baseRows()) {
  return actionsForView(packet, rows, activeView);
}

function actionDecisionIds() {
  return new Set(viewActions().map((action) => action.decision_id).filter(Boolean));
}

function filteredRows() {
  const actionIds = actionDecisionIds();
  const rows = baseRows().filter((row) => {
    if (actionMode && !actionIds.has(row.decision_id) && row.status !== "needs_attention") return false;
    if (activeFilter !== "all" && row.status !== activeFilter) return false;
    if (activeOwner !== "all" && row.owner !== activeOwner) return false;
    if (!searchQuery) return true;
    const detail = decisionDetails[row.decision_id];
    const haystack = [
      row.decision_id,
      row.status,
      row.owner,
      ...(row.partner_functions ?? []),
      activeView.id,
      activeView.label,
      activeView.title,
      activeView.description,
      ...activeView.focus,
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
  const rows = filteredRows();
  if (!rows.some((row) => row.decision_id === selectedDecisionId)) {
    selectedDecisionId = rows[0]?.decision_id ?? null;
  }
  renderDecisionTable(rows, selectedDecisionId, selectDecision, activeView.emptyLabel);
}

function renderSelectedDecisionDetail() {
  renderDecisionDetail(packet, selectedDecisionId, decisionDetails[selectedDecisionId], activeView);
}

function handleFilterChange(nextFilter) {
  activeFilter = nextFilter;
  renderFilters(packet, activeFilter, handleFilterChange);
  renderDecisionTableFromState();
  renderSelectedDecisionDetail();
}

function handleViewChange(nextViewId) {
  activeView = viewById(nextViewId);
  activeFilter = "all";
  activeOwner = "all";
  searchQuery = "";
  actionMode = false;
  document.getElementById("decision-search").value = "";
  render();
  if (selectedDecisionId) {
    loadDecisionDetail(selectedDecisionId);
  }
}

function selectDecision(decisionId) {
  selectedDecisionId = decisionId;
  renderDecisionTableFromState();
  renderSelectedDecisionDetail();
  loadDecisionDetail(selectedDecisionId);
}

async function loadDecisionDetail(decisionId) {
  if (decisionDetails[decisionId]) {
    renderSelectedDecisionDetail();
    return;
  }
  try {
    decisionDetails[decisionId] = await fetchDecisionDetail(decisionId);
    renderSelectedDecisionDetail();
    renderDecisionTableFromState();
  } catch (error) {
    setStatus(`Unable to load decision detail: ${error.message}`, "error");
  }
}

function render() {
  const rows = baseRows();
  const actions = viewActions(rows);
  if (!rows.some((row) => row.decision_id === selectedDecisionId)) {
    selectedDecisionId = rows[0]?.decision_id ?? null;
  }
  renderStakeholderTabs(stakeholderViews, activeView, handleViewChange);
  renderStakeholderContext(activeView, rows, actions);
  renderSummary(packet, rows, actions);
  renderFilters(packet, activeFilter, handleFilterChange);
  renderOwnerFilter(rows, activeOwner);
  renderMeetingControls(actionMode);
  renderImpactBars(countsForRows(rows));
  renderDecisionTableFromState();
  renderActions(actions, selectDecision, `No ${activeView.label} actions for the current view.`);
  renderSelectedDecisionDetail();
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
  renderSelectedDecisionDetail();
});
document.getElementById("owner-filter").addEventListener("change", (event) => {
  activeOwner = event.target.value;
  renderDecisionTableFromState();
  renderSelectedDecisionDetail();
});
document.getElementById("action-mode-button").addEventListener("click", () => {
  actionMode = !actionMode;
  renderMeetingControls(actionMode);
  renderDecisionTableFromState();
  renderSelectedDecisionDetail();
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
