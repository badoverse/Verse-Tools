const BASE_URL = "http://localhost:8000/api";

async function postCommand(path, payload) {
  const res = await fetch(`${BASE_URL}${path}`, {
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

export function generateNmapCommand(payload) {
  return postCommand("/commands/nmap", payload);
}

export function generateCurlCommand(payload) {
  return postCommand("/commands/curl", payload);
}

export function generateGobusterCommand(payload) {
  return postCommand("/commands/gobuster", payload);
}

export function generateHydraCommand(payload) {
  return postCommand("/commands/hydra", payload);
}

export function generateSqlmapCommand(payload) {
  return postCommand("/commands/sqlmap", payload);
}