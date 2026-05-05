const API_BASE_URL = "http://127.0.0.1:8000/api";

async function fetchJson(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

export async function fetchMonthlyPacket() {
  return fetchJson("/monthly-packet");
}

export async function fetchSchemaGap() {
  return fetchJson("/schema-gap");
}

export async function fetchV02Intelligence() {
  return fetchJson("/v02-intelligence");
}

export async function fetchPilotRequestPack() {
  return fetchJson("/pilot-request-pack");
}

export async function fetchPilotIntakeReview() {
  return fetchJson("/pilot-intake-review");
}

export async function fetchArchitectureReadiness() {
  return fetchJson("/architecture-readiness");
}

export async function fetchTrustRegistry() {
  return fetchJson("/trust-registry");
}

export async function fetchSourceIngestion() {
  return fetchJson("/source-ingestion");
}

export async function fetchNormalizationCrosswalk() {
  return fetchJson("/normalization-crosswalk");
}

export async function fetchGovernanceCadence() {
  return fetchJson("/governance-cadence");
}

export async function fetchDecisionPolicy() {
  return fetchJson("/decision-policy");
}

export async function fetchReasoningStress() {
  return fetchJson("/reasoning-stress");
}

export async function fetchReviewWorkflow() {
  return fetchJson("/review-workflow");
}

export async function updateSchemaAction(capability, field, status, notes) {
  const response = await fetch(
    `${API_BASE_URL}/schema-gap/actions/${encodeURIComponent(capability)}/${encodeURIComponent(field)}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, notes }),
    },
  );
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

export async function updateReviewWorkflowOutcome(stepId, itemId, outcome, notes) {
  const response = await fetch(
    `${API_BASE_URL}/review-workflow/items/${encodeURIComponent(stepId)}/${encodeURIComponent(itemId)}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ outcome, notes }),
    },
  );
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

export async function fetchDecisionDetail(decisionId) {
  return fetchJson(`/decisions/${encodeURIComponent(decisionId)}`);
}
