<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateHydraCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

const target = ref("");
const service = ref("ssh");
const port = ref("");
const ssl = ref(false);

const credMode = ref("single"); // single | list | combo
const login = ref("");
const loginList = ref("");
const password = ref("");
const passwordList = ref("");
const comboFile = ref("");

const tryEmptyPassword = ref(false);
const tryLoginAsPassword = ref(false);
const tryReversedLogin = ref(false);
const loopAroundUsers = ref(false);

const tasks = ref("");
const waitTime = ref("");
const waitTimePerThread = ref("");

const exitOnFirstFound = ref(false);
const exitOnFirstFoundPerHost = ref(false);
const verbose = ref(false);
const debug = ref(false);
const quiet = ref(false);
const restoreSession = ref(false);
const ignoreRestoreFile = ref(false);

const outputFile = ref("");
const outputFormat = ref("");

// Structured http-post-form / https-post-form builder
const formPath = ref("");
const loginField = ref("username");
const passwordField = ref("password");
const extraFields = ref([]); // [{ name, value }]
const conditionType = ref("F"); // "F" | "S"
const conditionString = ref("");

// Advanced escape hatch — used verbatim by the backend if present
const showRawOverride = ref(false);
const moduleOptions = ref("");

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const services = [
  "ssh", "ftp", "telnet", "smb", "rdp",
  "http-get", "http-post-form", "https-get", "https-post-form",
  "mysql", "postgres", "smtp", "vnc",
];

const outputFormats = [
  { value: "", label: "None" },
  { value: "text", label: "text" },
  { value: "json", label: "json" },
  { value: "jsonv1", label: "jsonv1" },
];

const installCommands = {
  linux: "sudo apt update && sudo apt install hydra -y",
  windows: "choco install hydra -y",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "Windows support is limited — running Hydra inside WSL is usually more reliable than a native build."
    : "Available in the default Debian/Ubuntu repos. Build from source (github.com/vanhauser-thc/thc-hydra) for the latest modules."
);

const showModuleOptions = computed(() =>
  service.value.endsWith("-form")
);

// Live preview of the assembled module string, mirrors build_http_form_module_options
const modulePreview = computed(() => {
  if (moduleOptions.value.trim()) return moduleOptions.value.trim();
  if (!formPath.value.trim()) return "";

  const lf = loginField.value.trim() || "username";
  const pf = passwordField.value.trim() || "password";

  const bodyParts = [`${lf}=^USER^`, `${pf}=^PASS^`];
  for (const f of extraFields.value) {
    if (f.name.trim()) bodyParts.push(`${f.name.trim()}=${f.value.trim()}`);
  }
  const body = bodyParts.join("&");
  const condition = `${conditionType.value}=${conditionString.value || ""}`;

  const esc = (v) => v.replace(/:/g, "\\:");
  return `${esc(formPath.value.trim())}:${esc(body)}:${esc(condition)}`;
});

function addExtraField() {
  extraFields.value.push({ name: "", value: "" });
}

function removeExtraField(index) {
  extraFields.value.splice(index, 1);
}

async function handleGenerate() {
  error.value = "";
  command.value = "";
  loading.value = true;

  try {
    const payload = {
      target: target.value,
      service: service.value,
      port: port.value ? Number(port.value) : null,
      ssl: ssl.value,

      login: credMode.value === "single" ? login.value || null : null,
      login_list: credMode.value === "list" ? loginList.value || null : null,
      password: credMode.value === "single" ? password.value || null : null,
      password_list: credMode.value === "list" ? passwordList.value || null : null,
      combo_file: credMode.value === "combo" ? comboFile.value || null : null,

      try_empty_password: tryEmptyPassword.value,
      try_login_as_password: tryLoginAsPassword.value,
      try_reversed_login: tryReversedLogin.value,
      loop_around_users: loopAroundUsers.value,

      tasks: tasks.value ? Number(tasks.value) : null,
      wait_time: waitTime.value ? Number(waitTime.value) : null,
      wait_time_per_thread: waitTimePerThread.value ? Number(waitTimePerThread.value) : null,

      exit_on_first_found: exitOnFirstFound.value,
      exit_on_first_found_per_host: exitOnFirstFoundPerHost.value,
      verbose: verbose.value,
      debug: debug.value,
      quiet: quiet.value,
      restore_session: restoreSession.value,
      ignore_restore_file: ignoreRestoreFile.value,

      output_file: outputFile.value || null,
      output_format: outputFormat.value || null,

      form_path: showModuleOptions.value ? formPath.value || null : null,
      login_field: loginField.value || "username",
      password_field: passwordField.value || "password",
      extra_fields: extraFields.value.some((f) => f.name.trim())
        ? extraFields.value
            .filter((f) => f.name.trim())
            .map((f) => ({ name: f.name.trim(), value: f.value.trim() }))
        : null,
      condition_type: conditionType.value || "F",
      condition_string: showModuleOptions.value ? conditionString.value || null : null,

      module_options: moduleOptions.value || null,
    };

    const result = await generateHydraCommand(payload);
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
        <span class="hero-badge">🔑 Hydra</span>
        <h1 class="hero-title">Hydra Command Builder</h1>
        <p class="hero-subtitle">
          password123 isn't going to crack itself.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install hydra</h2>

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
                  <label for="target">Target</label>
                  <input id="target" v-model="target" type="text" placeholder="192.168.1.10" required />
                </div>
                <div class="field">
                  <label for="service">Service</label>
                  <select id="service" v-model="service">
                    <option v-for="s in services" :key="s" :value="s">{{ s }}</option>
                  </select>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="port">Port (-s)</label>
                  <input id="port" v-model="port" type="number" placeholder="default for service" />
                </div>
                <div class="field checkbox-field">
                  <label class="checkbox">
                    <input type="checkbox" v-model="ssl" />
                    SSL/TLS (-S)
                  </label>
                </div>
              </div>

              <!-- Credentials -->
              <div class="field">
                <label>Credentials</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: credMode === 'single' }" @click="credMode = 'single'">Single (-l / -p)</button>
                  <button type="button" class="pill" :class="{ active: credMode === 'list' }" @click="credMode = 'list'">Wordlists (-L / -P)</button>
                  <button type="button" class="pill" :class="{ active: credMode === 'combo' }" @click="credMode = 'combo'">Combo file (-C)</button>
                </div>

                <div v-if="credMode === 'single'" class="field-row auth-row">
                  <input v-model="login" type="text" placeholder="username" />
                  <input v-model="password" type="text" placeholder="password" />
                </div>

                <div v-if="credMode === 'list'" class="field-row auth-row">
                  <input v-model="loginList" type="text" placeholder="users.txt" />
                  <input v-model="passwordList" type="text" placeholder="passwords.txt" />
                </div>

                <input
                  v-if="credMode === 'combo'"
                  v-model="comboFile"
                  type="text"
                  placeholder="combos.txt (login:pass per line)"
                  class="auth-row"
                />
              </div>

              <div v-if="credMode !== 'combo'" class="field">
                <label>Credential extras</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="tryEmptyPassword" />
                    Try empty password (-e n)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="tryLoginAsPassword" />
                    Try login as password (-e s)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="tryReversedLogin" />
                    Try reversed login (-e r)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="loopAroundUsers" />
                    Loop around users (-u)
                  </label>
                </div>
              </div>

              <!-- Structured form-module builder for http-post-form / https-post-form -->
              <div v-if="showModuleOptions" class="field form-module">
                <label>Form module ({{ service }})</label>
                <p class="hint">
                  The username/password above still supply <code>^USER^</code> / <code>^PASS^</code>, this section
                  just describes the login form itself.
                </p>

                <div class="field-row">
                  <div class="field">
                    <label for="formPath">Form path</label>
                    <input id="formPath" v-model="formPath" type="text" placeholder="/login.php" />
                  </div>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label for="loginField">Login field name</label>
                    <input id="loginField" v-model="loginField" type="text" placeholder="username" />
                  </div>
                  <div class="field">
                    <label for="passwordField">Password field name</label>
                    <input id="passwordField" v-model="passwordField" type="text" placeholder="password" />
                  </div>
                </div>

                <div class="field">
                  <label>Extra form fields</label>
                  <div class="extra-fields">
                    <div v-for="(f, i) in extraFields" :key="i" class="extra-field-row">
                      <input v-model="f.name" type="text" placeholder="field name" />
                      <input v-model="f.value" type="text" placeholder="static value" />
                      <button type="button" class="remove-btn" @click="removeExtraField(i)" aria-label="Remove field">
                        ✕
                      </button>
                    </div>
                  </div>
                  <button type="button" class="add-field-btn" @click="addExtraField">+ Add field</button>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label>Condition</label>
                    <div class="pill-group">
                      <button type="button" class="pill" :class="{ active: conditionType === 'F' }" @click="conditionType = 'F'">Failure (F=)</button>
                      <button type="button" class="pill" :class="{ active: conditionType === 'S' }" @click="conditionType = 'S'">Success (S=)</button>
                    </div>
                  </div>
                </div>

                <div class="field">
                  <label for="conditionString">
                    {{ conditionType === "F" ? "Text present on a failed login" : "Text present on a successful login" }}
                  </label>
                  <input
                    id="conditionString"
                    v-model="conditionString"
                    type="text"
                    :placeholder="conditionType === 'F' ? 'incorrect' : 'Welcome back'"
                  />
                </div>

                <div v-if="modulePreview" class="module-preview">
                  <span class="module-preview-label">Preview</span>
                  <code>{{ modulePreview }}</code>
                </div>

                <button type="button" class="advanced-toggle" @click="showRawOverride = !showRawOverride">
                  {{ showRawOverride ? "Hide" : "Show" }} raw override
                </button>

                <div v-if="showRawOverride" class="field">
                  <label for="moduleOptions">Raw module string (overrides everything above)</label>
                  <input
                    id="moduleOptions"
                    v-model="moduleOptions"
                    type="text"
                    placeholder="/login:user=^USER^&pass=^PASS^:F=incorrect"
                  />
                </div>
              </div>

              <!-- Performance -->
              <div class="field-row">
                <div class="field">
                  <label for="tasks">Tasks (-t)</label>
                  <input id="tasks" v-model="tasks" type="number" placeholder="16" />
                </div>
                <div class="field">
                  <label for="waitTime">Wait time (-w)</label>
                  <input id="waitTime" v-model="waitTime" type="number" placeholder="32" />
                </div>
                <div class="field">
                  <label for="waitTimePerThread">Wait/thread (-W)</label>
                  <input id="waitTimePerThread" v-model="waitTimePerThread" type="number" />
                </div>
              </div>

              <!-- Behaviour -->
              <div class="field">
                <label>Options</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="exitOnFirstFound" />
                    Exit on first found (-f)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="exitOnFirstFoundPerHost" />
                    Exit on first per host (-F)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="verbose" />
                    Verbose (-v)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="debug" />
                    Debug (-d)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="quiet" />
                    Quiet (-q)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="restoreSession" />
                    Restore session (-R)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="ignoreRestoreFile" />
                    Ignore restore file (-I)
                  </label>
                </div>
              </div>

              <!-- Output -->
              <div class="field-row">
                <div class="field">
                  <label for="outputFile">Output file (-o)</label>
                  <input id="outputFile" v-model="outputFile" type="text" placeholder="results.txt" />
                </div>
                <div class="field">
                  <label for="outputFormat">Format (-b)</label>
                  <select id="outputFormat" v-model="outputFormat">
                    <option v-for="f in outputFormats" :key="f.value" :value="f.value">{{ f.label }}</option>
                  </select>
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

/* Form-module builder */
.form-module {
  padding: 1.1rem 1.1rem 1.2rem;
  border-radius: 14px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: rgba(99, 102, 241, 0.04);
  gap: 1rem;
}
.form-module > label:first-child { font-size: 0.85rem; }
.hint {
  margin: -0.4rem 0 0.2rem;
  font-size: 0.78rem;
  color: #8b93a3;
  line-height: 1.5;
}
.hint code {
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  color: #a5b4fc;
  background: rgba(165, 180, 252, 0.1);
  padding: 0.05rem 0.3rem;
  border-radius: 4px;
}

.extra-fields { display: flex; flex-direction: column; gap: 0.5rem; }
.extra-field-row { display: flex; gap: 0.5rem; align-items: center; }
.extra-field-row input { flex: 1; }
.remove-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  background: #0a0b0e;
  color: #9ca3af;
  font-size: 0.8rem;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}
.remove-btn:hover { color: #fca5a5; border-color: rgba(239, 68, 68, 0.3); background: rgba(239, 68, 68, 0.06); }

.add-field-btn {
  align-self: flex-start;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px dashed rgba(165, 180, 252, 0.35);
  background: transparent;
  color: #a5b4fc;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}
.add-field-btn:hover { border-color: rgba(165, 180, 252, 0.6); background: rgba(165, 180, 252, 0.06); }

.module-preview {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.7rem 0.85rem;
  border-radius: 10px;
  background: #0a0b0e;
  border: 1px solid rgba(255, 255, 255, 0.07);
}
.module-preview-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #6b7280;
}
.module-preview code {
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 0.82rem;
  color: #67e8f9;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.advanced-toggle {
  align-self: flex-start;
  padding: 0;
  border: none;
  background: none;
  color: #8b93a3;
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 3px;
  cursor: pointer;
  transition: color 0.2s ease;
}
.advanced-toggle:hover { color: #22d3ee; }

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
  white-space: pre-wrap;
  overflow-wrap: break-word;
  line-height: 1.6;
}

.pop-enter-active { transition: opacity 0.35s ease, transform 0.35s ease; }
.pop-enter-from { opacity: 0; transform: translateY(8px); }

@keyframes fade-down { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fade-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>