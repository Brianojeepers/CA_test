const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function fetchMonthlyPacket() {
  const response = await fetch(`${API_BASE_URL}/monthly-packet`);
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
