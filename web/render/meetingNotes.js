export function actionRowsForMeeting(packet) {
  const actionIds = new Set(packet.actions.map((action) => action.decision_id).filter(Boolean));
  return packet.decision_impact.rows
    .filter((row) => actionIds.has(row.decision_id) || row.status === "needs_attention")
    .sort((a, b) => {
      const aAction = actionIds.has(a.decision_id) ? -1 : 0;
      const bAction = actionIds.has(b.decision_id) ? -1 : 0;
      return aAction - bAction || a.decision_id.localeCompare(b.decision_id);
    });
}

export function buildMeetingNotes(packet) {
  if (!packet) return "## Council Actions This Month\n\n- Monthly packet data has not loaded yet.";
  const rows = actionRowsForMeeting(packet);
  const lines = ["## Council Actions This Month", ""];
  if (!rows.length) {
    lines.push("- No decision actions currently require council review.");
    return lines.join("\n");
  }
  rows.forEach((row) => {
    const relatedActions = packet.actions.filter((action) => action.decision_id === row.decision_id);
    lines.push(`- ${row.decision_id} (${row.status}, owner: ${row.owner})`);
    lines.push(`  - Decision: ${row.summary}`);
    lines.push(`  - Recommended action: ${row.recommendation.recommended_action}`);
    lines.push(`  - Evidence basis: ${row.recommendation.evidence_basis}`);
    lines.push(`  - Risk/blocker: ${row.recommendation.blocker_or_risk}`);
    lines.push(`  - Review trigger: ${row.recommendation.next_review_trigger}`);
    relatedActions.forEach((action) => {
      lines.push(`  - Current action item: ${action.text}`);
    });
  });
  return lines.join("\n");
}

export function renderMeetingNotes(packet) {
  document.getElementById("meeting-notes").textContent = buildMeetingNotes(packet);
}
