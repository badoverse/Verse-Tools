const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function postCommand(path, payload) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to generate command");
  }

  return res.json();
}

export const generateNmapCommand = (payload) =>
  postCommand("/commands/nmap", payload);

export const generateCurlCommand = (payload) =>
  postCommand("/commands/curl", payload);

export const generateGobusterCommand = (payload) =>
  postCommand("/commands/gobuster", payload);

export const generateHydraCommand = (payload) =>
  postCommand("/commands/hydra", payload);

export const generateSqlmapCommand = (payload) =>
  postCommand("/commands/sqlmap", payload);

export const generateNiktoCommand = (payload) =>
  postCommand("/commands/nikto", payload);