<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateNiktoCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

const target = ref("");
const port = ref("");
const ssl = ref(false);

const outputMode = ref("none"); // none | file
const outputFile = ref("");
const outputFormat = ref("");

const tuning = ref([]);
const evasion = ref("");

const basicAuthUser = ref("");
const basicAuthPass = ref("");
const rootPath = ref("");
const cgiDirs = ref("");
const vhost = ref("");
const userAgent = ref("");
const proxy = ref("");

const timeout = ref("");
const maxTime = ref("");

const askMode = ref("");
const noInteractive = ref(true);
const no404 = ref(false);
const singleScan = ref(false);

const plugins = ref("");
const mutate = ref([]);
const mutateOptions = ref("");

const displayOptions = ref([]);

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const formatOptions = ["", "htm", "csv", "json", "nbe", "sql", "txt", "xml"];

const tuningOptions = [
  { key: "1", label: "1 — File upload" },
  { key: "2", label: "2 — Misconfig / default files" },
  { key: "3", label: "3 — Information disclosure" },
  { key: "4", label: "4 — Injection (XSS/script/HTML)" },
  { key: "5", label: "5 — Remote file retrieval" },
  { key: "6", label: "6 — Denial of service" },
  { key: "7", label: "7 — Remote file retrieval (server-wide)" },
  { key: "8", label: "8 — Command execution" },
  { key: "9", label: "9 — SQL injection" },
  { key: "0", label: "0 — File retrieval (server-wide)" },
  { key: "a", label: "a — Authentication bypass" },
  { key: "b", label: "b — Software identification" },
  { key: "c", label: "c — Remote source inclusion" },
];

const mutateOptionsList = [
  { key: "1", label: "1 — Test all cgi dirs with common file names" },
  { key: "2", label: "2 — Guess password file names" },
  { key: "3", label: "3 — Enumerate user names (Apache)" },
  { key: "4", label: "4 — Enumerate user names (cgiwrap)" },
  { key: "5", label: "5 — Attempt to brute force sub-domains" },
  { key: "6", label: "6 — Attempt to guess directory names" },
];

const displayOptionsList = [
  { key: "1", label: "1 — Redirects" },
  { key: "2", label: "2 — Cookies received" },
  { key: "3", label: "3 — All 200/OK responses" },
  { key: "4", label: "4 — URLs requested (with GET params)" },
  { key: "D", label: "D — Debug output" },
  { key: "V", label: "V — Verbose output" },
];

const installCommands = {
  linux: "sudo apt update && sudo apt install nikto -y",
  windows: "choco install nikto -y",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "Nikto is a Perl script — install Strawberry Perl first if the Chocolatey package doesn't pull it in automatically."
    : "Available in the default Debian/Ubuntu repos. Run `nikto -update` afterwards to refresh plugin/vulnerability databases."
);

function toggleInArray(arr, key) {
  const i = arr.value.indexOf(key);
  if (i === -1) arr.value.push(key);
  else arr.value.splice(i, 1);
}

async function handleGenerate() {
  error.value = "";
  command.value = "";
  loading.value = true;

  try {
    const payload = {
      target: target.value,
      port: port.value ? Number(port.value) : null,
      ssl: ssl.value,

      output_file: outputMode.value === "file" ? outputFile.value || null : null,
      output_format: outputMode.value === "file" ? outputFormat.value || null : null,

      tuning: tuning.value.length ? tuning.value.join(",") : null,
      evasion: evasion.value || null,

      basic_auth: basicAuthUser.value ? `${basicAuthUser.value}:${basicAuthPass.value}` : null,
      root_path: rootPath.value || null,
      cgi_dirs: cgiDirs.value || null,
      vhost: vhost.value || null,
      user_agent: userAgent.value || null,
      proxy: proxy.value || null,

      timeout: timeout.value ? Number(timeout.value) : null,
      max_time: maxTime.value || null,

      ask_mode: askMode.value || null,
      no_interactive: noInteractive.value,
      no_404: no404.value,
      single_scan: singleScan.value,

      plugins: plugins.value || null,
      mutate: mutate.value.length ? mutate.value.join(",") : null,
      mutate_options: mutateOptions.value || null,

      display_options: displayOptions.value.length ? displayOptions.value.join(",") : null,
    };

    const result = await generateNiktoCommand(payload);
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
        <span class="hero-badge">🛡️ Nikto</span>
        <h1 class="hero-title">Nikto Command Builder</h1>
        <p class="hero-subtitle">
          Scan web servers for known vulnerabilities and misconfigurations.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install nikto</h2>

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
              <div class="field-row">
                <div class="field">
                  <label for="target">Target (-h)</label>
                  <input
                    id="target"
                    v-model="target"
                    type="text"
                    placeholder="scanme.nmap.org or https://target.com"
                    required
                  />
                </div>
                <div class="field">
                  <label for="port">Port (-p)</label>
                  <input id="port" v-model="port" type="number" placeholder="80 / 443" />
                </div>
              </div>

              <div class="field checkbox-field">
                <label class="checkbox">
                  <input type="checkbox" v-model="ssl" />
                  Force SSL (-ssl)
                </label>
              </div>

              <!-- Output -->
              <div class="field">
                <label>Output</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: outputMode === 'none' }" @click="outputMode = 'none'">Terminal only</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'file' }" @click="outputMode = 'file'">Save to file (-o)</button>
                </div>

                <div v-if="outputMode === 'file'" class="field-row auth-row">
                  <input v-model="outputFile" type="text" placeholder="results.txt" />
                  <select v-model="outputFormat">
                    <option v-for="f in formatOptions" :key="f" :value="f">{{ f || "Format from extension" }}</option>
                  </select>
                </div>
              </div>

              <!-- Tuning -->
              <div class="field">
                <label>Tuning (-Tuning) — limit which vulnerability categories are tested</label>
                <div class="checkbox-grid">
                  <label v-for="t in tuningOptions" :key="t.key" class="checkbox">
                    <input
                      type="checkbox"
                      :checked="tuning.includes(t.key)"
                      @change="toggleInArray(tuning, t.key)"
                    />
                    {{ t.label }}
                  </label>
                </div>
                <p class="hint">Leave all unselected to test every category (default).</p>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="evasion">Evasion technique (-evasion)</label>
                  <input id="evasion" v-model="evasion" type="text" placeholder="1 (random URI encoding)" />
                </div>
                <div class="field">
                  <label for="vhost">Virtual host (-vhost)</label>
                  <input id="vhost" v-model="vhost" type="text" placeholder="internal.target.com" />
                </div>
              </div>

              <!-- Auth / access -->
              <div class="field">
                <label>Basic auth (-id)</label>
                <div class="field-row auth-row">
                  <input v-model="basicAuthUser" type="text" placeholder="username" />
                  <input v-model="basicAuthPass" type="password" placeholder="password" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="rootPath">Root path (-root)</label>
                  <input id="rootPath" v-model="rootPath" type="text" placeholder="/app" />
                </div>
                <div class="field">
                  <label for="cgiDirs">CGI dirs (-Cgidirs)</label>
                  <input id="cgiDirs" v-model="cgiDirs" type="text" placeholder="/cgi-bin/,/cgi/" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="userAgent">User agent</label>
                  <input id="userAgent" v-model="userAgent" type="text" placeholder="Mozilla/5.0" />
                </div>
                <div class="field">
                  <label for="proxy">Proxy (-useproxy)</label>
                  <input id="proxy" v-model="proxy" type="text" placeholder="http://127.0.0.1:8080" />
                </div>
              </div>

              <!-- Timing -->
              <div class="field-row">
                <div class="field">
                  <label for="timeout">Request timeout (-timeout, sec)</label>
                  <input id="timeout" v-model="timeout" type="number" placeholder="10" />
                </div>
                <div class="field">
                  <label for="maxTime">Max scan time (-maxtime)</label>
                  <input id="maxTime" v-model="maxTime" type="text" placeholder="1h / 30m" />
                </div>
              </div>

              <!-- Behaviour -->
              <div class="field">
                <label>Behaviour</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="noInteractive" />
                    Non-interactive (-nointeractive)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="no404" />
                    Skip 404 baseline check (-no404)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="singleScan" />
                    Single request per test (-Single)
                  </label>
                </div>
              </div>

              <div class="field">
                <label for="askMode">Prompt on SSL cert issues (-ask)</label>
                <select id="askMode" v-model="askMode">
                  <option value="">Default</option>
                  <option value="yes">yes</option>
                  <option value="no">no</option>
                  <option value="auto">auto</option>
                </select>
              </div>

              <!-- Plugins / mutate -->
              <div class="field">
                <label for="plugins">Plugins (-Plugins)</label>
                <input id="plugins" v-model="plugins" type="text" placeholder="@@ALL or headers;cookies" />
              </div>

              <div class="field">
                <label>Mutation techniques (-mutate)</label>
                <div class="checkbox-grid">
                  <label v-for="m in mutateOptionsList" :key="m.key" class="checkbox">
                    <input
                      type="checkbox"
                      :checked="mutate.includes(m.key)"
                      @change="toggleInArray(mutate, m.key)"
                    />
                    {{ m.label }}
                  </label>
                </div>
              </div>

              <div v-if="mutate.includes('1') || mutate.includes('6')" class="field">
                <label for="mutateOptions">Mutate wordlist (-mutate-options)</label>
                <input id="mutateOptions" v-model="mutateOptions" type="text" placeholder="/path/to/wordlist.txt" />
              </div>

              <!-- Display -->
              <div class="field">
                <label>Display options (-Display)</label>
                <div class="checkbox-grid">
                  <label v-for="d in displayOptionsList" :key="d.key" class="checkbox">
                    <input
                      type="checkbox"
                      :checked="displayOptions.includes(d.key)"
                      @change="toggleInArray(displayOptions, d.key)"
                    />
                    {{ d.label }}
                  </label>
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
.checkbox-field { justify-content: center; }

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
input::placeholder, textarea::placeholder { color: #4b5563; }
input:focus, select:focus, textarea:focus { border-color: rgba(34, 211, 238, 0.5); box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.1); }

.hint { margin: 0; font-size: 0.75rem; color: #6b7280; }

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

.auth-row { display: flex; gap: 0.75rem; }

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