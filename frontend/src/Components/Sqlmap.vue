<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateSqlmapCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

const url = ref("");
const data = ref("");
const cookie = ref("");
const headers = ref([{ key: "", value: "" }]);
const userAgent = ref("");
const referer = ref("");
const randomAgent = ref(false);
const proxy = ref("");
const tor = ref(false);

const method = ref("");
const paramDelimiter = ref("");

const level = ref(1);
const risk = ref(1);
const technique = ref("");
const dbms = ref("");
const targetOs = ref("");

const threads = ref("");
const delay = ref("");
const timeout = ref("");
const retries = ref("");
const tamper = ref("");
const batch = ref(true);

const dbs = ref(false);
const currentDb = ref(false);
const currentUser = ref(false);
const isDba = ref(false);
const tables = ref(false);
const columns = ref(false);
const dump = ref(false);
const dumpAll = ref(false);
const db = ref("");
const table = ref("");
const columnsTarget = ref("");

const osShell = ref(false);
const sqlShell = ref(false);
const fileRead = ref("");
const fileWrite = ref("");
const fileDest = ref("");

const outputDir = ref("");
const verboseLevel = ref("");

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const techniqueOptions = [
  { key: "B", label: "Boolean-based blind" },
  { key: "E", label: "Error-based" },
  { key: "U", label: "UNION query-based" },
  { key: "S", label: "Stacked queries" },
  { key: "T", label: "Time-based blind" },
  { key: "Q", label: "Inline queries" },
];

const dbmsOptions = ["", "mysql", "postgresql", "mssql", "oracle", "sqlite", "mariadb"];

const installCommands = {
  linux: "sudo apt update && sudo apt install sqlmap -y",
  windows: "choco install sqlmap -y",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "Requires Python installed and on PATH. Chocolatey wraps the same script sqlmap.org distributes."
    : "Available in the default Debian/Ubuntu repos. Run `sqlmap --update` afterwards to pull the latest checks."
);

const riskWarning = computed(() => risk.value >= 2);

function toggleTechnique(key) {
  const current = technique.value.toUpperCase();
  technique.value = current.includes(key)
    ? current.replace(key, "")
    : current + key;
}

function addHeaderRow() {
  headers.value.push({ key: "", value: "" });
}

function removeHeaderRow(index) {
  headers.value.splice(index, 1);
}

async function handleGenerate() {
  error.value = "";
  command.value = "";
  loading.value = true;

  try {
    const payload = {
      url: url.value,
      data: data.value || null,
      cookie: cookie.value || null,
      headers: headers.value
        .filter((h) => h.key.trim())
        .map((h) => `${h.key.trim()}: ${h.value.trim()}`),
      user_agent: userAgent.value || null,
      referer: referer.value || null,
      random_agent: randomAgent.value,
      proxy: proxy.value || null,
      tor: tor.value,

      method: method.value || null,
      param_delimiter: paramDelimiter.value || null,

      level: Number(level.value) || 1,
      risk: Number(risk.value) || 1,
      technique: technique.value || null,
      dbms: dbms.value || null,
      os: targetOs.value || null,

      threads: threads.value ? Number(threads.value) : null,
      delay: delay.value ? Number(delay.value) : null,
      timeout: timeout.value ? Number(timeout.value) : null,
      retries: retries.value ? Number(retries.value) : null,
      tamper: tamper.value || null,
      batch: batch.value,

      dbs: dbs.value,
      current_db: currentDb.value,
      current_user: currentUser.value,
      is_dba: isDba.value,
      tables: tables.value,
      columns: columns.value,
      dump: dump.value,
      dump_all: dumpAll.value,
      db: db.value || null,
      table: table.value || null,
      columns_target: columnsTarget.value || null,

      os_shell: osShell.value,
      sql_shell: sqlShell.value,
      file_read: fileRead.value || null,
      file_write: fileWrite.value || null,
      file_dest: fileDest.value || null,

      output_dir: outputDir.value || null,
      verbose_level: verboseLevel.value !== "" ? Number(verboseLevel.value) : null,
    };

    const result = await generateSqlmapCommand(payload);
    command.value = result.command;
  } catch (e) {
    error.value = e.message || "Something went wrong.";
  } finally {
    loading.value = false;
  }
}

async function copyCommand() {
  if (!command.value) return;
  await navigator.clipboard.writeText(command.value);
  copied.value = true;
  setTimeout(() => (copied.value = false), 1500);
}

async function copyInstallCommand() {
  await navigator.clipboard.writeText(installCommands[os.value]);
  installCopied.value = true;
  setTimeout(() => (installCopied.value = false), 1500);
}
</script>

<template>
  <div class="page">
    <div class="ambient-glow glow-one"></div>
    <div class="ambient-glow glow-two"></div>

    <div class="content">
      <button class="back-link" type="button" @click="router.push('/')">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 6l-6 6 6 6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        Back to tools
      </button>

      <header class="hero">
        <span class="hero-badge">🧬 SQLmap</span>
        <h1 class="hero-title">SQLmap Command Builder</h1>
        <p class="hero-subtitle">
         "UNION SELECT * FROM beautiful_people WHERE target = 'you'"
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install sqlmap</h2>

              <div class="os-toggle">
                <button
                  v-for="opt in osOptions"
                  :key="opt.value"
                  type="button"
                  class="os-toggle-btn"
                  :class="{ active: os === opt.value }"
                  @click="os = opt.value"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <div class="terminal">
              <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
              </div>
              <div class="terminal-body">
                <span class="prompt">$</span>
                <code class="install-code">{{ installCommands[os] }}</code>
                <button class="copy-btn" type="button" @click="copyInstallCommand">
                  {{ installCopied ? "Copied!" : "Copy" }}
                </button>
              </div>
            </div>

            <p class="install-note">{{ installNote }}</p>
          </div>
        </section>

        <section class="step">
          <div class="step-marker">2</div>

          <div class="step-card">
            <h2 class="step-title">Request</h2>

            <form class="form" @submit.prevent="handleGenerate">
              <div class="field">
                <label for="url">Target URL</label>
                <input
                  id="url"
                  v-model="url"
                  type="text"
                  placeholder="https://target.com/page.php?id=1"
                  required
                />
              </div>

              <div class="field">
                <label for="data">POST data (--data)</label>
                <textarea
                  id="data"
                  v-model="data"
                  rows="2"
                  placeholder="id=1&action=view"
                ></textarea>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="method">HTTP method (--method)</label>
                  <input id="method" v-model="method" type="text" placeholder="POST" />
                </div>
                <div class="field">
                  <label for="paramDelimiter">Param delimiter</label>
                  <input id="paramDelimiter" v-model="paramDelimiter" type="text" placeholder="&amp;" />
                </div>
              </div>

              <div class="field">
                <label for="cookie">Cookie</label>
                <input id="cookie" v-model="cookie" type="text" placeholder="PHPSESSID=abc123" />
              </div>

              <div class="field">
                <label>Custom headers</label>
                <div
                  v-for="(header, index) in headers"
                  :key="index"
                  class="header-row"
                >
                  <input v-model="header.key" type="text" placeholder="Header name" />
                  <input v-model="header.value" type="text" placeholder="Value" />
                  <button
                    type="button"
                    class="remove-btn"
                    @click="removeHeaderRow(index)"
                    :disabled="headers.length === 1"
                  >
                    ✕
                  </button>
                </div>
                <button type="button" class="add-btn" @click="addHeaderRow">
                  + Add header
                </button>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="userAgent">User agent</label>
                  <input id="userAgent" v-model="userAgent" type="text" placeholder="Mozilla/5.0" />
                </div>
                <div class="field">
                  <label for="referer">Referer</label>
                  <input id="referer" v-model="referer" type="text" placeholder="https://target.com" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="proxy">Proxy</label>
                  <input id="proxy" v-model="proxy" type="text" placeholder="http://127.0.0.1:8080" />
                </div>
                <div class="field checkbox-field">
                  <label class="checkbox">
                    <input type="checkbox" v-model="randomAgent" />
                    Random user agent
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="tor" />
                    Route through Tor
                  </label>
                </div>
              </div>

              <!-- Detection tuning -->
              <div class="field">
                <label>
                  Level ({{ level }}) — how many request parts sqlmap probes
                </label>
                <input type="range" min="1" max="5" v-model="level" />
              </div>

              <div class="field">
                <label>
                  Risk ({{ risk }}) — how aggressive the payloads are
                </label>
                <input type="range" min="1" max="3" v-model="risk" />
                <p v-if="riskWarning" class="risk-warning">
                  Risk 2+ includes payloads that can modify data (e.g. time-based
                  heavy queries, OR-based statements). Only use against targets
                  you're explicitly authorized to test.
                </p>
              </div>

              <div class="field">
                <label>Techniques (--technique)</label>
                <div class="pill-group">
                  <button
                    v-for="t in techniqueOptions"
                    :key="t.key"
                    type="button"
                    class="pill"
                    :class="{ active: technique.toUpperCase().includes(t.key) }"
                    @click="toggleTechnique(t.key)"
                  >
                    {{ t.key }} — {{ t.label }}
                  </button>
                </div>
                <p class="hint">Leave all unselected to let sqlmap try everything.</p>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="dbms">Target DBMS (--dbms)</label>
                  <select id="dbms" v-model="dbms">
                    <option v-for="d in dbmsOptions" :key="d" :value="d">
                      {{ d || "Auto-detect" }}
                    </option>
                  </select>
                </div>
                <div class="field">
                  <label for="targetOs">Target OS (--os)</label>
                  <input id="targetOs" v-model="targetOs" type="text" placeholder="Linux" />
                </div>
              </div>

              <!-- Performance -->
              <div class="field-row">
                <div class="field">
                  <label for="threads">Threads</label>
                  <input id="threads" v-model="threads" type="number" placeholder="1" />
                </div>
                <div class="field">
                  <label for="delay">Delay (s)</label>
                  <input id="delay" v-model="delay" type="number" step="0.1" />
                </div>
                <div class="field">
                  <label for="timeout">Timeout (s)</label>
                  <input id="timeout" v-model="timeout" type="number" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="retries">Retries</label>
                  <input id="retries" v-model="retries" type="number" />
                </div>
                <div class="field">
                  <label for="tamper">Tamper scripts</label>
                  <input id="tamper" v-model="tamper" type="text" placeholder="space2comment,charencode" />
                </div>
              </div>

              <div class="field checkbox-field">
                <label class="checkbox">
                  <input type="checkbox" v-model="batch" />
                  Non-interactive mode (--batch, accepts sqlmap defaults automatically)
                </label>
              </div>

              <!-- Enumeration -->
              <div class="field">
                <label>Enumeration</label>
                <div class="checkbox-grid">
                  <label class="checkbox"><input type="checkbox" v-model="dbs" /> List databases (--dbs)</label>
                  <label class="checkbox"><input type="checkbox" v-model="currentDb" /> Current DB</label>
                  <label class="checkbox"><input type="checkbox" v-model="currentUser" /> Current user</label>
                  <label class="checkbox"><input type="checkbox" v-model="isDba" /> Check DBA privileges</label>
                  <label class="checkbox"><input type="checkbox" v-model="tables" /> List tables</label>
                  <label class="checkbox"><input type="checkbox" v-model="columns" /> List columns</label>
                  <label class="checkbox"><input type="checkbox" v-model="dump" /> Dump table data</label>
                  <label class="checkbox"><input type="checkbox" v-model="dumpAll" /> Dump everything</label>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="db">Database (-D)</label>
                  <input id="db" v-model="db" type="text" placeholder="app_db" />
                </div>
                <div class="field">
                  <label for="table">Table (-T)</label>
                  <input id="table" v-model="table" type="text" placeholder="users" />
                </div>
                <div class="field">
                  <label for="columnsTarget">Columns (-C)</label>
                  <input id="columnsTarget" v-model="columnsTarget" type="text" placeholder="username,password" />
                </div>
              </div>

              <!-- Access -->
              <div class="field">
                <label>Access</label>
                <div class="checkbox-grid">
                  <label class="checkbox"><input type="checkbox" v-model="osShell" /> OS shell (--os-shell)</label>
                  <label class="checkbox"><input type="checkbox" v-model="sqlShell" /> SQL shell (--sql-shell)</label>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="fileRead">Read remote file</label>
                  <input id="fileRead" v-model="fileRead" type="text" placeholder="/etc/passwd" />
                </div>
                <div class="field">
                  <label for="fileWrite">Write local file</label>
                  <input id="fileWrite" v-model="fileWrite" type="text" placeholder="shell.php" />
                </div>
                <div class="field">
                  <label for="fileDest">Remote destination</label>
                  <input id="fileDest" v-model="fileDest" type="text" placeholder="/var/www/html/shell.php" />
                </div>
              </div>

              <!-- Output -->
              <div class="field-row">
                <div class="field">
                  <label for="outputDir">Output directory</label>
                  <input id="outputDir" v-model="outputDir" type="text" placeholder="./sqlmap-output" />
                </div>
                <div class="field">
                  <label for="verboseLevel">Verbosity (-v)</label>
                  <input id="verboseLevel" v-model="verboseLevel" type="number" min="0" max="6" placeholder="1" />
                </div>
              </div>

              <button class="generate-btn" type="submit" :disabled="loading">
                <span v-if="loading" class="spinner"></span>
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M5 12h14M13 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                {{ loading ? "Generating…" : "Generate command" }}
              </button>
            </form>

            <Transition name="pop">
              <p v-if="error" class="error-box">{{ error }}</p>
            </Transition>

            <Transition name="pop">
              <div v-if="command" class="output-box">
                <div class="output-header">
                  <span>Command</span>
                  <button class="copy-btn" type="button" @click="copyCommand">
                    {{ copied ? "Copied!" : "Copy" }}
                  </button>
                </div>
                <code class="output-code">{{ command }}</code>
              </div>
            </Transition>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  margin: 0;
  padding: 0;
  min-height: 100%;
  background: #08090c;
}

:global(*) {
  box-sizing: border-box;
}

.page {
  position: relative;
  min-height: 100vh;
  padding: 4rem 2rem 5rem;
  overflow: hidden;
  background:
    radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.035) 1px, transparent 0),
    linear-gradient(180deg, #0b0c10 0%, #08090c 55%, #08090c 100%);
  background-size: 28px 28px, 100% 100%;
  color: #e5e7eb;
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}

.ambient-glow {
  position: absolute;
  width: 40rem;
  height: 40rem;
  border-radius: 50%;
  filter: blur(110px);
  opacity: 0.16;
  pointer-events: none;
  z-index: 0;
}

.glow-one { top: -12rem; left: -8rem; background: radial-gradient(circle, #6366f1, transparent 65%); }
.glow-two { bottom: -14rem; right: -10rem; background: radial-gradient(circle, #22d3ee, transparent 65%); }

.content { position: relative; z-index: 1; max-width: 700px; margin: 0 auto; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 2.5rem;
  padding: 0;
  border: none;
  background: none;
  color: #8b93a3;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s ease;
}
.back-link:hover { color: #22d3ee; }

.hero { text-align: center; margin-bottom: 3rem; animation: fade-down 0.5s ease both; }
.hero-badge {
  display: inline-block;
  padding: 0.3rem 0.85rem;
  margin-bottom: 1.1rem;
  border-radius: 999px;
  border: 1px solid rgba(99, 102, 241, 0.35);
  background: rgba(99, 102, 241, 0.08);
  color: #a5b4fc;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.hero-title {
  font-size: clamp(1.9rem, 4vw, 2.4rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
  background: linear-gradient(100deg, #f9fafb 10%, #a5b4fc 50%, #22d3ee 90%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero-subtitle { margin: 0.7rem auto 0; max-width: 30rem; color: #8b93a3; font-size: 0.95rem; line-height: 1.6; }

.steps { position: relative; display: flex; flex-direction: column; gap: 2rem; }
.step-rail {
  position: absolute;
  left: 17px;
  top: 34px;
  bottom: 34px;
  width: 2px;
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.4), rgba(34, 211, 238, 0.15));
  z-index: 0;
}
.step { position: relative; display: flex; gap: 1.25rem; animation: fade-up 0.5s ease both; }
.step:nth-child(2) { animation-delay: 0.08s; }

.step-marker {
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(145deg, #1c1f27, #101216);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #a5b4fc;
  font-size: 0.85rem;
  font-weight: 700;
  box-shadow: 0 0 0 4px #08090c;
}

.step-card {
  flex: 1;
  min-width: 0;
  padding: 1.5rem 1.6rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: linear-gradient(155deg, #15171d 0%, #0d0e12 100%);
  box-shadow: 0 20px 40px -20px rgba(0, 0, 0, 0.6);
}
.step-title { margin: 0 0 1.1rem; font-size: 1rem; font-weight: 700; color: #f3f4f6; letter-spacing: -0.01em; }

.install-card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.1rem; }
.install-card-head .step-title { margin: 0; }

.os-toggle { display: inline-flex; padding: 3px; border-radius: 999px; background: #0a0b0e; border: 1px solid rgba(255, 255, 255, 0.08); }
.os-toggle-btn {
  padding: 0.35rem 0.9rem;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #8b93a3;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease;
}
.os-toggle-btn.active { color: #0a0b0e; background: linear-gradient(100deg, #6366f1, #22d3ee); }

.terminal { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.07); background: #0a0b0e; }
.terminal-bar { display: flex; gap: 6px; padding: 0.6rem 0.75rem; background: rgba(255, 255, 255, 0.03); border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
.dot { width: 9px; height: 9px; border-radius: 50%; }
.dot-red { background: #f87171; }
.dot-yellow { background: #fbbf24; }
.dot-green { background: #4ade80; }

.terminal-body { display: flex; align-items: center; gap: 0.6rem; padding: 0.9rem 1rem; }
.prompt { color: #22d3ee; font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace; font-weight: 700; }
.install-code { flex: 1; font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace; font-size: 0.85rem; color: #a5b4fc; word-break: break-all; }
.install-note { margin: 0.85rem 0 0; font-size: 0.78rem; color: #6b7280; line-height: 1.5; }

.form { display: flex; flex-direction: column; gap: 1.4rem; }
.field { display: flex; flex-direction: column; gap: 0.55rem; flex: 1; }
.field-row { display: flex; gap: 1rem; }
.field-row .field, .field-row input { min-width: 0; }
.checkbox-field { justify-content: center; gap: 0.6rem; }

label { font-size: 0.8rem; font-weight: 600; color: #cbd5e1; }

input, select, textarea {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: #0a0b0e;
  color: #e5e7eb;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
textarea { resize: vertical; font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace; font-size: 0.85rem; }
input::placeholder, textarea::placeholder { color: #4b5563; }
input:focus, select:focus, textarea:focus { border-color: rgba(34, 211, 238, 0.5); box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.1); }

input[type="range"] {
  padding: 0;
  accent-color: #22d3ee;
}

.risk-warning {
  margin: 0.2rem 0 0;
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(251, 191, 36, 0.3);
  background: rgba(251, 191, 36, 0.08);
  color: #fcd34d;
  font-size: 0.78rem;
  line-height: 1.5;
}

.hint {
  margin: 0;
  font-size: 0.75rem;
  color: #6b7280;
}

.pill-group { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.pill {
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: #0a0b0e;
  color: #9ca3af;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}
.pill.active { color: #0a0b0e; background: linear-gradient(100deg, #6366f1, #22d3ee); border-color: transparent; }

.checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.6rem 1rem; }
.checkbox { display: flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; font-weight: 500; color: #d1d5db; cursor: pointer; }
.checkbox input { width: auto; accent-color: #22d3ee; }

.header-row { display: flex; gap: 0.6rem; align-items: center; margin-bottom: 0.5rem; }

.remove-btn {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0a0b0e;
  color: #9ca3af;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;
}
.remove-btn:hover:not(:disabled) { border-color: rgba(239, 68, 68, 0.4); color: #fca5a5; }
.remove-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.add-btn {
  align-self: flex-start;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.15);
  background: transparent;
  color: #8b93a3;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;
}
.add-btn:hover { border-color: rgba(34, 211, 238, 0.4); color: #67e8f9; }

.generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  border: none;
  background: linear-gradient(100deg, #6366f1, #22d3ee);
  color: #0a0b0e;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}
.generate-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 24px -8px rgba(99, 102, 241, 0.5); }
.generate-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(10, 11, 14, 0.3);
  border-top-color: #0a0b0e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.error-box {
  margin-top: 1.25rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.08);
  color: #fca5a5;
  font-size: 0.85rem;
}

.output-box { margin-top: 1.25rem; border-radius: 14px; border: 1px solid rgba(34, 211, 238, 0.25); background: #0a0b0e; overflow: hidden; }
.output-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1rem;
  background: rgba(34, 211, 238, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #67e8f9;
}
.copy-btn {
  flex-shrink: 0;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: #e5e7eb;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: none;
  letter-spacing: normal;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}
.copy-btn:hover { border-color: rgba(34, 211, 238, 0.4); background: rgba(34, 211, 238, 0.08); }

.output-code {
  display: block;
  padding: 1.1rem;
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 0.88rem;
  color: #67e8f9;
  word-break: break-all;
  line-height: 1.6;
}

.pop-enter-active { transition: opacity 0.35s ease, transform 0.35s ease; }
.pop-enter-from { opacity: 0; transform: translateY(8px); }

@keyframes fade-down { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fade-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>