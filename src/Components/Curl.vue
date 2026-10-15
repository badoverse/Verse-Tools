<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateCurlCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");
const url = ref("");
const method = ref("GET");

// Flags
const followRedirects = ref(false);   // -L
const silent = ref(false);            // -s
const showErrors = ref(false);        // -S (only meaningful with silent)
const verbose = ref(false);           // -v
const includeHeaders = ref(false);    // -i
const insecure = ref(false);          // -k
const compressed = ref(false);        // --compressed

// Identity / networking
const userAgent = ref("");
const referer = ref("");
const proxy = ref("");
const maxTime = ref("");
const connectTimeout = ref("");

// Auth
const authMode = ref("none"); // none | basic | bearer
const basicUser = ref("");
const basicPass = ref("");
const bearerToken = ref("");

// Headers
const headers = ref([{ key: "", value: "" }]);

// Body
const data = ref("");
const dataIsJson = ref(false);

// Output
const outputMode = ref("none"); // none | file | remote
const outputFile = ref("");

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const methods = [
  { value: "GET", label: "GET" },
  { value: "POST", label: "POST" },
  { value: "PUT", label: "PUT" },
  { value: "DELETE", label: "DELETE" },
  { value: "PATCH", label: "PATCH" },
  { value: "HEAD", label: "HEAD" },
];

const installCommands = {
  linux: "sudo apt update && sudo apt install curl -y",
  windows: "choco install curl -y",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "curl ships built-in on modern Windows 10/11 — this is only needed on older systems."
    : "Works on Debian/Ubuntu-based distros. Use dnf/pacman/etc. if you're on something else."
);

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
      method: method.value,
      follow_redirects: followRedirects.value,
      silent: silent.value,
      show_errors: showErrors.value,
      verbose: verbose.value,
      include_headers: includeHeaders.value,
      insecure: insecure.value,
      compressed: compressed.value,
      user_agent: userAgent.value || null,
      referer: referer.value || null,
      proxy: proxy.value || null,
      max_time: maxTime.value ? Number(maxTime.value) : null,
      connect_timeout: connectTimeout.value ? Number(connectTimeout.value) : null,
      basic_auth:
        authMode.value === "basic" && basicUser.value
          ? `${basicUser.value}:${basicPass.value}`
          : null,
      bearer_token: authMode.value === "bearer" ? bearerToken.value || null : null,
      headers: headers.value
        .filter((h) => h.key.trim())
        .map((h) => `${h.key.trim()}: ${h.value.trim()}`),
      data: data.value || null,
      data_is_json: dataIsJson.value,
      output_file: outputMode.value === "file" ? outputFile.value : null,
      save_remote_name: outputMode.value === "remote",
    };

    const result = await generateCurlCommand(payload);
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
        <span class="hero-badge">🌐 Curl</span>
        <h1 class="hero-title">Curl Command Builder</h1>
        <p class="hero-subtitle">
          -X POST your feelings, I'll handle the syntax.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install curl</h2>

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
                <label for="url">URL</label>
                <input
                  id="url"
                  v-model="url"
                  type="text"
                  placeholder="https://api.example.com/users"
                  required
                />
              </div>

              <div class="field">
                <label>HTTP method</label>
                <div class="pill-group">
                  <button
                    v-for="m in methods"
                    :key="m.value"
                    type="button"
                    class="pill"
                    :class="{ active: method === m.value }"
                    @click="method = m.value"
                  >
                    {{ m.label }}
                  </button>
                </div>
              </div>

              <!-- Flags -->
              <div class="field">
                <label>Options</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="followRedirects" />
                    Follow redirects (-L)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="verbose" />
                    Verbose (-v)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="includeHeaders" />
                    Include response headers (-i)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="insecure" />
                    Ignore SSL errors (-k)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="compressed" />
                    Request compressed (--compressed)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="silent" />
                    Silent mode (-s)
                  </label>
                  <label class="checkbox" :class="{ disabled: !silent }">
                    <input type="checkbox" v-model="showErrors" :disabled="!silent" />
                    Show errors in silent mode (-sS)
                  </label>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="userAgent">User agent (-A)</label>
                  <input id="userAgent" v-model="userAgent" type="text" placeholder="Mozilla/5.0" />
                </div>
                <div class="field">
                  <label for="referer">Referer (-e)</label>
                  <input id="referer" v-model="referer" type="text" placeholder="https://google.com" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="proxy">Proxy (-x)</label>
                  <input id="proxy" v-model="proxy" type="text" placeholder="http://proxy:8080" />
                </div>
                <div class="field">
                  <label for="maxTime">Max time / connect timeout (s)</label>
                  <div class="field-row">
                    <input id="maxTime" v-model="maxTime" type="number" placeholder="--max-time" />
                    <input v-model="connectTimeout" type="number" placeholder="--connect-timeout" />
                  </div>
                </div>
              </div>

              <!-- Auth -->
              <div class="field">
                <label>Authentication</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: authMode === 'none' }" @click="authMode = 'none'">None</button>
                  <button type="button" class="pill" :class="{ active: authMode === 'basic' }" @click="authMode = 'basic'">Basic (-u)</button>
                  <button type="button" class="pill" :class="{ active: authMode === 'bearer' }" @click="authMode = 'bearer'">Bearer token</button>
                </div>

                <div v-if="authMode === 'basic'" class="field-row auth-row">
                  <input v-model="basicUser" type="text" placeholder="username" />
                  <input v-model="basicPass" type="password" placeholder="password" />
                </div>

                <input
                  v-if="authMode === 'bearer'"
                  v-model="bearerToken"
                  type="text"
                  placeholder="TOKEN"
                  class="auth-row"
                />
              </div>

              <!-- Headers -->
              <div class="field">
                <label>Custom headers (-H)</label>
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

              <!-- Body -->
              <div class="field">
                <label for="data">Body data (-d)</label>
                <textarea
                  id="data"
                  v-model="data"
                  rows="3"
                  placeholder='name=John&amp;age=20  or  {"name":"John"}'
                ></textarea>
                <label class="checkbox">
                  <input type="checkbox" v-model="dataIsJson" />
                  Send as JSON (adds Content-Type: application/json)
                </label>
              </div>

              <!-- Output -->
              <div class="field">
                <label>Output</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: outputMode === 'none' }" @click="outputMode = 'none'">Print to terminal</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'file' }" @click="outputMode = 'file'">Save as file (-o)</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'remote' }" @click="outputMode = 'remote'">Save with remote name (-O)</button>
                </div>

                <input
                  v-if="outputMode === 'file'"
                  v-model="outputFile"
                  type="text"
                  placeholder="output.html"
                  class="auth-row"
                />
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

.glow-one {
  top: -12rem;
  left: -8rem;
  background: radial-gradient(circle, #6366f1, transparent 65%);
}

.glow-two {
  bottom: -14rem;
  right: -10rem;
  background: radial-gradient(circle, #22d3ee, transparent 65%);
}

.content {
  position: relative;
  z-index: 1;
  max-width: 700px;
  margin: 0 auto;
}

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

.back-link:hover {
  color: #22d3ee;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
  animation: fade-down 0.5s ease both;
}

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

.hero-subtitle {
  margin: 0.7rem auto 0;
  max-width: 30rem;
  color: #8b93a3;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* ---------- Step layout ---------- */

.steps {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.step-rail {
  position: absolute;
  left: 17px;
  top: 34px;
  bottom: 34px;
  width: 2px;
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.4), rgba(34, 211, 238, 0.15));
  z-index: 0;
}

.step {
  position: relative;
  display: flex;
  gap: 1.25rem;
  animation: fade-up 0.5s ease both;
}

.step:nth-child(2) {
  animation-delay: 0.08s;
}

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

.step-title {
  margin: 0 0 1.1rem;
  font-size: 1rem;
  font-weight: 700;
  color: #f3f4f6;
  letter-spacing: -0.01em;
}

/* ---------- Install card ---------- */

.install-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.1rem;
}

.install-card-head .step-title {
  margin: 0;
}

.os-toggle {
  display: inline-flex;
  padding: 3px;
  border-radius: 999px;
  background: #0a0b0e;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

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

.os-toggle-btn.active {
  color: #0a0b0e;
  background: linear-gradient(100deg, #6366f1, #22d3ee);
}

.terminal {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: #0a0b0e;
}

.terminal-bar {
  display: flex;
  gap: 6px;
  padding: 0.6rem 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.dot-red { background: #f87171; }
.dot-yellow { background: #fbbf24; }
.dot-green { background: #4ade80; }

.terminal-body {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.9rem 1rem;
}

.prompt {
  color: #22d3ee;
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-weight: 700;
}

.install-code {
  flex: 1;
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 0.85rem;
  color: #a5b4fc;
  word-break: break-all;
}

.install-note {
  margin: 0.85rem 0 0;
  font-size: 0.78rem;
  color: #6b7280;
  line-height: 1.5;
}

/* ---------- Form ---------- */

.form {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  flex: 1;
}

.field-row {
  display: flex;
  gap: 1rem;
}

.field-row .field,
.field-row input {
  min-width: 0;
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
}

input,
select,
textarea {
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

textarea {
  resize: vertical;
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 0.85rem;
}

input::placeholder,
textarea::placeholder {
  color: #4b5563;
}

input:focus,
select:focus,
textarea:focus {
  border-color: rgba(34, 211, 238, 0.5);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.1);
}

.pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

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

.pill.active {
  color: #0a0b0e;
  background: linear-gradient(100deg, #6366f1, #22d3ee);
  border-color: transparent;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.6rem 1rem;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: #d1d5db;
  cursor: pointer;
}

.checkbox.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.checkbox input {
  width: auto;
  accent-color: #22d3ee;
}

.auth-row {
  display: flex;
  gap: 0.75rem;
}

.header-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  margin-bottom: 0.5rem;
}

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

.remove-btn:hover:not(:disabled) {
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.remove-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

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

.add-btn:hover {
  border-color: rgba(34, 211, 238, 0.4);
  color: #67e8f9;
}

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

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px -8px rgba(99, 102, 241, 0.5);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

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

.output-box {
  margin-top: 1.25rem;
  border-radius: 14px;
  border: 1px solid rgba(34, 211, 238, 0.25);
  background: #0a0b0e;
  overflow: hidden;
}

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

.copy-btn:hover {
  border-color: rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.08);
}

.output-code {
  display: block;
  padding: 1.1rem;
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 0.88rem;
  color: #67e8f9;
  word-break: break-all;
  line-height: 1.6;
}

.pop-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.pop-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes fade-down {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>