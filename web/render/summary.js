import { formatPercent } from "../format.js";

export function renderSummary(packet) {
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
