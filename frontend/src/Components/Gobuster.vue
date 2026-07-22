<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateGobusterCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

const mode = ref("dir");
const url = ref("");
const domain = ref("");
const wordlist = ref("/usr/share/wordlists/dirb/common.txt");


const threads = ref("");
const timeout = ref("");
const delay = ref("");
const outputFile = ref("");
const verbose = ref(false);
const quiet = ref(false);
const noProgress = ref(false);
const noError = ref(false);

// Network / auth
const proxy = ref("");
const insecure = ref(false);
const userAgent = ref("");
const cookies = ref("");
const headers = ref([{ key: "", value: "" }]);
const basicAuthUser = ref("");
const basicAuthPass = ref("");

// dir
const extensions = ref("");
const followRedirect = ref(false);
const expanded = ref(false);
const addSlash = ref(false);
const includeLength = ref(false);
const discoverBackup = ref(false);
const statusCodes = ref("");
const statusCodesBlacklist = ref("");
const excludeLength = ref("");

// dns
const showIps = ref(false);
const showCname = ref(false);
const wildcard = ref(false);
const resolver = ref("");

// vhost
const appendDomain = ref(false);

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const modes = [
  { value: "dir", label: "dir" },
  { value: "dns", label: "dns" },
  { value: "vhost", label: "vhost" },
  { value: "fuzz", label: "fuzz" },
];

const installCommands = {
  linux: "sudo apt update && sudo apt install gobuster -y",
  windows: "choco install gobuster -y",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "Requires Chocolatey. Alternatively grab a prebuilt binary from the OJ/gobuster GitHub releases."
    : "Available in the default Debian/Ubuntu repos. Use go install github.com/OJ/gobuster/v3@latest for the latest version."
);

const needsUrl = computed(() => ["dir", "vhost", "fuzz"].includes(mode.value));
const needsDomain = computed(() => mode.value === "dns");

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
      mode: mode.value,
      url: url.value || null,
      domain: domain.value || null,
      wordlist: wordlist.value,
      threads: threads.value ? Number(threads.value) : null,
      timeout: timeout.value || null,
      delay: delay.value || null,
      output_file: outputFile.value || null,
      verbose: verbose.value,
      quiet: quiet.value,
      no_progress: noProgress.value,
      no_error: noError.value,
      proxy: proxy.value || null,
      insecure: insecure.value,
      follow_redirect: followRedirect.value,
      user_agent: userAgent.value || null,
      cookies: cookies.value || null,
      headers: headers.value
        .filter((h) => h.key.trim())
        .map((h) => `${h.key.trim()}: ${h.value.trim()}`),
      basic_auth_user: basicAuthUser.value || null,
      basic_auth_pass: basicAuthPass.value || null,
      extensions: extensions.value || null,
      expanded: expanded.value,
      add_slash: addSlash.value,
      include_length: includeLength.value,
      discover_backup: discoverBackup.value,
      status_codes: statusCodes.value || null,
      status_codes_blacklist: statusCodesBlacklist.value || null,
      exclude_length: excludeLength.value || null,
      show_ips: showIps.value,
      show_cname: showCname.value,
      wildcard: wildcard.value,
      resolver: resolver.value || null,
      append_domain: appendDomain.value,
    };

    const result = await generateGobusterCommand(payload);
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
        <span class="hero-badge">🗂️ Gobuster</span>
        <h1 class="hero-title">Gobuster Command Builder</h1>
        <p class="hero-subtitle">
          Brute-force directories, DNS, vhosts and more.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install gobuster</h2>

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
                <label>Mode</label>
                <div class="pill-group">
                  <button
                    v-for="m in modes"
                    :key="m.value"
                    type="button"
                    class="pill"
                    :class="{ active: mode === m.value }"
                    @click="mode = m.value"
                  >
                    {{ m.label }}
                  </button>
                </div>
              </div>

              <div v-if="needsUrl" class="field">
                <label for="url">URL{{ mode === "fuzz" ? " (include FUZZ keyword)" : "" }}</label>
                <input
                  id="url"
                  v-model="url"
                  type="text"
                  :placeholder="mode === 'fuzz' ? 'http://target.com/FUZZ' : 'http://target.com'"
                  required
                />
              </div>

              <div v-if="needsDomain" class="field">
                <label for="domain">Domain</label>
                <input id="domain" v-model="domain" type="text" placeholder="example.com" required />
              </div>

              <div class="field">
                <label for="wordlist">Wordlist</label>
                <input
                  id="wordlist"
                  v-model="wordlist"
                  type="text"
                  placeholder="/usr/share/wordlists/dirb/common.txt"
                />
              </div>

              <!-- General -->
              <div class="field-row">
                <div class="field">
                  <label for="threads">Threads (-t)</label>
                  <input id="threads" v-model="threads" type="number" placeholder="10" />
                </div>
                <div class="field">
                  <label for="timeout">Timeout</label>
                  <input id="timeout" v-model="timeout" type="text" placeholder="10s" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="delay">Delay</label>
                  <input id="delay" v-model="delay" type="text" placeholder="100ms" />
                </div>
                <div class="field">
                  <label for="outputFile">Output file (-o)</label>
                  <input id="outputFile" v-model="outputFile" type="text" placeholder="results.txt" />
                </div>
              </div>

              <div class="field">
                <label>Options</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="verbose" />
                    Verbose (-v)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="quiet" />
                    Quiet (-q)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noProgress" />
                    No progress (-z)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noError" />
                    No error
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="insecure" />
                    Ignore SSL errors (-k)
                  </label>
                </div>
              </div>

              <!-- Network / auth -->
              <div class="field-row">
                <div class="field">
                  <label for="proxy">Proxy</label>
                  <input id="proxy" v-model="proxy" type="text" placeholder="http://127.0.0.1:8080" />
                </div>
                <div class="field">
                  <label for="userAgent">User agent (-a)</label>
                  <input id="userAgent" v-model="userAgent" type="text" placeholder="Mozilla/5.0" />
                </div>
              </div>

              <div class="field">
                <label for="cookies">Cookies (-c)</label>
                <input id="cookies" v-model="cookies" type="text" placeholder="session=abc123" />
              </div>

              <div class="field">
                <label>Basic auth</label>
                <div class="field-row auth-row">
                  <input v-model="basicAuthUser" type="text" placeholder="username (-U)" />
                  <input v-model="basicAuthPass" type="password" placeholder="password (-P)" />
                </div>
              </div>

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

              <!-- dir mode -->
              <template v-if="mode === 'dir'">
                <div class="field">
                  <label for="extensions">Extensions (-x)</label>
                  <input id="extensions" v-model="extensions" type="text" placeholder="php,html,txt" />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label for="statusCodes">Status codes (-s)</label>
                    <input id="statusCodes" v-model="statusCodes" type="text" placeholder="200,204,301,302" />
                  </div>
                  <div class="field">
                    <label for="statusCodesBlacklist">Status codes blacklist (-b)</label>
                    <input id="statusCodesBlacklist" v-model="statusCodesBlacklist" type="text" placeholder="404" />
                  </div>
                </div>

                <div class="field">
                  <label for="excludeLength">Exclude length</label>
                  <input id="excludeLength" v-model="excludeLength" type="text" placeholder="0,1234" />
                </div>

                <div class="field">
                  <label>Dir options</label>
                  <div class="checkbox-grid">
                    <label class="checkbox">
                      <input type="checkbox" v-model="followRedirect" />
                      Follow redirects (-r)
                    </label>
                    <label class="checkbox">
                      <input type="checkbox" v-model="expanded" />
                      Expanded (-e)
                    </label>
                    <label class="checkbox">
                      <input type="checkbox" v-model="addSlash" />
                      Add slash (-f)
                    </label>
                    <label class="checkbox">
                      <input type="checkbox" v-model="includeLength" />
                      Include length (-l)
                    </label>
                    <label class="checkbox">
                      <input type="checkbox" v-model="discoverBackup" />
                      Discover backups
                    </label>
                  </div>
                </div>
              </template>

              <!-- dns mode -->
              <template v-if="mode === 'dns'">
                <div class="field">
                  <label for="resolver">Resolver (-r)</label>
                  <input id="resolver" v-model="resolver" type="text" placeholder="8.8.8.8" />
                </div>
                <div class="field">
                  <label>DNS options</label>
                  <div class="checkbox-grid">
                    <label class="checkbox">
                      <input type="checkbox" v-model="showIps" />
                      Show IPs (-i)
                    </label>
                    <label class="checkbox">
                      <input type="checkbox" v-model="showCname" />
                      Show CNAME (-c)
                    </label>
                    <label class="checkbox">
                      <input type="checkbox" v-model="wildcard" />
                      Wildcard
                    </label>
                  </div>
                </div>
              </template>

              <!-- vhost mode -->
              <template v-if="mode === 'vhost'">
                <div class="field">
                  <label>Vhost options</label>
                  <div class="checkbox-grid">
                    <label class="checkbox">
                      <input type="checkbox" v-model="appendDomain" />
                      Append domain
                    </label>
                  </div>
                </div>
              </template>

              <!-- fuzz mode -->
              <template v-if="mode === 'fuzz'">
                <div class="field">
                  <label>Fuzz options</label>
                  <div class="checkbox-grid">
                    <label class="checkbox">
                      <input type="checkbox" v-model="followRedirect" />
                      Follow redirects (-r)
                    </label>
                  </div>
                </div>
              </template>

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