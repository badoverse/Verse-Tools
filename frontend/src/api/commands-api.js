
const ALLOWED_BASE_URLS = [
  import.meta.env.VITE_API_URL,
  "http://localhost:8000/api",
  "https://verse-tools-backend.onrender.com/api",
];

async function postCommand(path, payload) {
  for (const baseUrl of ALLOWED_BASE_URLS) {
    if (!baseUrl) continue;

    try {
      const res = await fetch(`${baseUrl}${path}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        return res.json();
      }
    } catch (error) {
      //try the next URL
    }
  }

  throw new Error("Failed to generate command");
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