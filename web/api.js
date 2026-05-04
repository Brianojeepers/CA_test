const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function fetchMonthlyPacket() {
  const response = await fetch(`${API_BASE_URL}/monthly-packet`);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

export async function fetchSchemaGap() {
  const response = await fetch(`${API_BASE_URL}/schema-gap`);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

export async function fetchV02Intelligence() {
  const response = await fetch(`${API_BASE_URL}/v02-intelligence`);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}

export async function fetchPilotRequestPack() {
  const response = await fetch(`${API_BASE_URL}/pilot-request-pack`);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
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

export async function fetchDecisionDetail(decisionId) {
  const response = await fetch(`${API_BASE_URL}/decisions/${encodeURIComponent(decisionId)}`);
  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }
  return response.json();
}
