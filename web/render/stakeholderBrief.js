function recommendationLabel(row) {
  if (row.status === "needs_attention" && row.recommendation.blocker_or_risk.includes("suppressed evidence")) {
    return "Update / consider deprecation";
  }
  const labels = {
    positive_signal: "Keep / amplify",
    evidence_emerging: "Update / monitor",
    too_early: "Wait",
    needs_attention: "Update",
    no_outcome_data: "Wait",
  };
  return labels[row.status] ?? "Review";
}

function sortRowsForBrief(rows) {
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  const statusOrder = {
    needs_attention: 0,
    too_early: 1,
    evidence_emerging: 2,
    no_outcome_data: 3,
    positive_signal: 4,
  };
  return [...rows].sort(
    (a, b) =>
      (priorityOrder[a.recommendation.priority] ?? 9) - (priorityOrder[b.recommendation.priority] ?? 9) ||
      (statusOrder[a.status] ?? 9) - (statusOrder[b.status] ?? 9) ||
      a.decision_id.localeCompare(b.decision_id),
  );
}

function changelogForView(packet, rows, view) {
  if (view.id === "council" || view.id === "data") return packet.decision_changelog.items;
  const visibleDecisionIds = new Set(rows.map((row) => row.decision_id));
  return packet.decision_changelog.items.filter((item) => visibleDecisionIds.has(item.decision_id));
}

export function buildStakeholderBrief(packet, view, rows, actions) {
  if (!packet) return "## Stakeholder Brief\n\n- Monthly packet data has not loaded yet.";
  const lines = [
    `# ${view.title} Brief`,
    "",
    `Generated: ${packet.generated_date}`,
    "",
    `Primary question: ${view.primaryQuestion}`,
    "",
    "## At A Glance",
    "",
    `- Scope: ${rows.length} decision(s).`,
    `- Actions: ${actions.length} item(s).`,
    `- Data trust: passed with ${packet.data_trust.warning_count} warning(s).`,
    `- Focus: ${view.focus.join(", ")}.`,
    "",
    "## Key Decisions",
    "",
  ];

  const keyRows = sortRowsForBrief(rows).slice(0, 5);
  if (keyRows.length) {
    keyRows.forEach((row) => {
      lines.push(`- ${row.decision_id} ${recommendationLabel(row)} (${row.status}, owner: ${row.owner})`);
      lines.push(`  - Decision: ${row.summary}`);
      lines.push(`  - Evidence: ${row.recommendation.evidence_basis}`);
      lines.push(`  - Risk: ${row.recommendation.blocker_or_risk}`);
      lines.push(`  - Next trigger: ${row.recommendation.next_review_trigger}`);
    });
  } else {
    lines.push("- No decisions in scope.");
  }

  lines.push("", "## Action Items", "");
  if (actions.length) {
    actions.slice(0, 6).forEach((action) => lines.push(`- ${action.text}`));
  } else {
    lines.push("- No action items for this stakeholder lens.");
  }

  lines.push("", "## What Changed", "");
  const changelogItems = changelogForView(packet, rows, view).slice(0, 6);
  if (changelogItems.length) {
    changelogItems.forEach((item) => {
      lines.push(`- ${item.category} ${item.title} (${item.status}, owner: ${item.owner})`);
      lines.push(`  - Why: ${item.why_it_matters}`);
      lines.push(`  - Next: ${item.next_step}`);
    });
  } else {
    lines.push("- No changelog items for this stakeholder lens.");
  }

  lines.push("", "## Limits", "");
  packet.known_limits.slice(0, 2).forEach((limit) => lines.push(`- ${limit}`));
  return lines.join("\n");
}
