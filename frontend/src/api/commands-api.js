const BASE_URL = "http://localhost:8000/api";

export async function generateNmapCommand(payload) {
  const res = await fetch(`${BASE_URL}/commands/nmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to generate command");
  }

  return res.json();
}