import {
  fetchDecisionDetail,
  fetchMonthlyPacket,
  fetchPilotIntakeReview,
  fetchPilotRequestPack,
  fetchSchemaGap,
  fetchV02Intelligence,
  updateSchemaAction,
} from "./api.js";
import { setStatus } from "./format.js";
import { renderActions } from "./render/actions.js";
import { renderChangelog } from "./render/changelog.js";
import { renderDecisionDetail } from "./render/detail.js";
import { renderDrilldowns, renderKnownLimits } from "./render/drilldowns.js";
import { renderFilters, renderMeetingControls, renderOwnerFilter } from "./render/filters.js";
import { renderImpactBars } from "./render/impact.js";
import { renderInsights } from "./render/insights.js";
import { buildMeetingNotes, renderMeetingNotes } from "./render/meetingNotes.js";
import { renderPilotIntake } from "./render/pilotIntake.js";
import { renderPilotRequests } from "./render/pilotRequests.js";
import { renderRecommendation } from "./render/recommendation.js";
import { renderReviewDiff } from "./render/reviewDiff.js";
import { renderSchemaGap } from "./render/schemaGap.js";
import { buildStakeholderBrief } from "./render/stakeholderBrief.js";
import { renderSummary } from "./render/summary.js";
import { renderDecisionTable } from "./render/table.js";
import { renderV02Intelligence } from "./render/v02Intelligence.js";
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
let schemaGap = null;
let v02Intelligence = null;
let pilotRequestPack = null;
let pilotIntakeReview = null;
let selectedDecisionId = null;
let activeView = defaultView();
let activeFilter = "all";
let activeOwner = "all";
let activeChangelogCategory = "all";
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
  renderRecommendation(packet, selectedDecisionId, activeView);
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
  activeChangelogCategory = "all";
  searchQuery = "";
  actionMode = false;
  document.getElementById("decision-search").value = "";
  render();
  if (selectedDecisionId) {
    loadDecisionDetail(selectedDecisionId);
  }
}

function handleChangelogCategoryChange(nextCategory) {
  activeChangelogCategory = nextCategory ?? "all";
  renderChangelog(
    packet.decision_changelog,
    activeChangelogCategory,
    handleChangelogCategoryChange,
    selectDecision,
    new Set(packet.decision_impact.rows.map((row) => row.decision_id)),
  );
}

function focusPanel(target) {
  const targetIds = {
    actions: "action-list",
    detail: "decision-detail",
    table: "decision-table",
    warnings: "warning-list",
  };
  const targetId = targetIds[target] ?? targetIds.table;
  const element = document.getElementById(targetId);
  const section = element?.closest("section") ?? element;
  if (!section) return;
  if (!section.hasAttribute("tabindex")) {
    section.setAttribute("tabindex", "-1");
  }
  section.focus({ preventScroll: true });
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

function handleInsightAction(action) {
  if (action.type === "filterStatus") {
    activeFilter = action.status ?? "all";
    actionMode = false;
    render();
    focusPanel(action.focus);
    return;
  }
  if (action.type === "actionMode") {
    activeFilter = "all";
    actionMode = true;
    render();
    focusPanel(action.focus ?? "actions");
    return;
  }
  if (action.type === "focusWarnings") {
    focusPanel("warnings");
    return;
  }
  if (action.type === "focusDetail") {
    focusPanel("detail");
    return;
  }
  if (action.type === "clearFilters") {
    activeFilter = "all";
    actionMode = false;
    render();
    focusPanel(action.focus ?? "table");
  }
}

function selectDecision(decisionId) {
  selectedDecisionId = decisionId;
  renderDecisionTableFromState();
  renderSelectedDecisionDetail();
  loadDecisionDetail(selectedDecisionId);
}

async function handleSchemaActionUpdate(action, status, notes) {
  try {
    schemaGap = await updateSchemaAction(action.capability, action.field, status, notes);
    v02Intelligence = await fetchV02Intelligence();
    pilotRequestPack = await fetchPilotRequestPack();
    pilotIntakeReview = await fetchPilotIntakeReview();
    render();
    setStatus(`Updated ${action.field.replaceAll("_", " ")} to ${status.replaceAll("_", " ")}.`, "ok");
  } catch (error) {
    setStatus(`Unable to update v0.2 field action: ${error.message}`, "error");
  }
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
  renderInsights(activeView, rows, actions, packet, handleInsightAction);
  renderSummary(packet, rows, actions);
  renderReviewDiff(
    packet.review_diff,
    selectDecision,
    new Set(packet.decision_impact.rows.map((row) => row.decision_id)),
  );
  renderSchemaGap(schemaGap, handleSchemaActionUpdate);
  renderV02Intelligence(v02Intelligence);
  renderPilotRequests(pilotRequestPack);
  renderPilotIntake(pilotIntakeReview);
  renderFilters(packet, activeFilter, handleFilterChange);
  renderOwnerFilter(rows, activeOwner);
  renderMeetingControls(actionMode);
  renderImpactBars(countsForRows(rows));
  renderDecisionTableFromState();
  renderActions(actions, selectDecision, `No ${activeView.label} actions for the current view.`);
  renderSelectedDecisionDetail();
  renderChangelog(
    packet.decision_changelog,
    activeChangelogCategory,
    handleChangelogCategoryChange,
    selectDecision,
    new Set(packet.decision_impact.rows.map((row) => row.decision_id)),
  );
  renderDrilldowns(packet.stakeholder_drilldowns);
  renderKnownLimits(packet.known_limits);
  renderWarnings(packet.data_trust.warnings);
  renderMeetingNotes(packet);
}

async function loadPacket() {
  setStatus("Refreshing monthly packet...");
  try {
    const [nextPacket, nextSchemaGap, nextV02Intelligence, nextPilotRequestPack, nextPilotIntakeReview] = await Promise.all([
      fetchMonthlyPacket(),
      fetchSchemaGap(),
      fetchV02Intelligence(),
      fetchPilotRequestPack(),
      fetchPilotIntakeReview(),
    ]);
    packet = nextPacket;
    schemaGap = nextSchemaGap;
    v02Intelligence = nextV02Intelligence;
    pilotRequestPack = nextPilotRequestPack;
    pilotIntakeReview = nextPilotIntakeReview;
    decisionDetails = {};
    selectedDecisionId = packet.decision_impact.rows[0]?.decision_id ?? null;
    render();
    if (selectedDecisionId) {
      loadDecisionDetail(selectedDecisionId);
    }
    setStatus("Connected to FastAPI monthly packet, schema-gap, pilot request, and intake endpoints.", "ok");
  } catch (error) {
    setStatus(`Unable to load dashboard data: ${error.message}`, "error");
  }
}

document.getElementById("refresh-button").addEventListener("click", loadPacket);
document.getElementById("copy-stakeholder-brief").addEventListener("click", async () => {
  if (!packet) {
    setStatus("Stakeholder brief is not ready until the monthly packet loads.", "error");
    return;
  }
  const rows = baseRows();
  const actions = viewActions(rows);
  const brief = buildStakeholderBrief(packet, activeView, rows, actions);
  try {
    await navigator.clipboard.writeText(brief);
    setStatus(`${activeView.label} brief copied.`, "ok");
  } catch {
    setStatus("Copy failed; use the stakeholder packet export script.", "error");
  }
});
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
