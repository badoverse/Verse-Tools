<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateWapitiCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

// Target
const url = ref("");
const scope = ref("");
const modules = ref("");
const data = ref("");
const swagger = ref("");

// Crawl limits
const depth = ref("");
const maxLinks = ref("");
const maxFiles = ref("");
const maxParams = ref("");
const tasks = ref("");
const scanForce = ref("");

// Attack
const level = ref("");
const maxScanTime = ref("");
const maxAttackTime = ref("");

// Scope lists
const startUrls = ref("");
const excludeUrls = ref("");
const removeParams = ref("");
const skipParams = ref("");

// Network
const proxy = ref("");
const tor = ref(false);
const timeout = ref("");
const userAgent = ref("");
const headers = ref("");
const verifySsl = ref(false);
const headless = ref("");

// Auth
const authUser = ref("");
const authPassword = ref("");
const authMethod = ref("");
const formUser = ref("");
const formPassword = ref("");
const formUrl = ref("");

// Session / cookies
const cookieFile = ref("");
const cookieValue = ref("");
const jwt = ref("");
const dropSetCookie = ref(false);
const skipCrawl = ref(false);
const resumeCrawl = ref(false);
const flushAttacks = ref(false);
const flushSession = ref(false);

// Output
const outputFormat = ref("");
const output = ref("");
const detailedReport = ref("");
const verbose = ref("");
const color = ref(false);
const noBugreport = ref(false);
const cms = ref("");

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const scopeOptions = ["", "url", "page", "folder", "subdomain", "domain", "punk"];
const scanForceOptions = ["", "paranoid", "sneaky", "polite", "normal", "aggressive", "insane"];
const authMethodOptions = ["", "basic", "digest", "ntlm"];
const headlessOptions = ["", "no", "hidden", "visible", "both"];
const formatOptions = ["", "csv", "html", "json", "md", "txt", "xml"];
const cmsOptions = ["", "drupal", "joomla", "magento", "prestashop", "spip", "typo3", "wp"];

const installCommands = {
  linux: "pipx install wapiti3",
  windows: "pip install wapiti3",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "Wapiti is a Python package. Install Python 3.10+ first, then run the command above (use pipx instead of pip to keep it isolated)."
    : "Wapiti is a Python package needing Python 3.10+. pipx keeps it isolated; `pip install wapiti3` also works. Run `wapiti --update` afterwards to refresh attack modules."
);

function toLines(v) {
  return v
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
}

function toCsv(v) {
  return v
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

async function handleGenerate() {
  error.value = "";
  command.value = "";
  loading.value = true;

  try {
    const payload = {
      url: url.value,
      scope: scope.value || null,
      modules: modules.value || null,
      level: level.value ? Number(level.value) : null,
      data: data.value || null,
      swagger: swagger.value || null,

      depth: depth.value ? Number(depth.value) : null,
      max_links_per_page: maxLinks.value ? Number(maxLinks.value) : null,
      max_files_per_dir: maxFiles.value ? Number(maxFiles.value) : null,
      max_scan_time: maxScanTime.value ? Number(maxScanTime.value) : null,
      max_attack_time: maxAttackTime.value ? Number(maxAttackTime.value) : null,
      max_parameters: maxParams.value ? Number(maxParams.value) : null,
      scan_force: scanForce.value || null,
      tasks: tasks.value ? Number(tasks.value) : null,

      start_urls: toLines(startUrls.value),
      exclude_urls: toLines(excludeUrls.value),
      remove_params: toCsv(removeParams.value),
      skip_params: toCsv(skipParams.value),

      proxy: proxy.value || null,
      tor: tor.value,

      auth_user: authUser.value || null,
      auth_password: authPassword.value || null,
      auth_method: authMethod.value || null,

      form_user: formUser.value || null,
      form_password: formPassword.value || null,
      form_url: formUrl.value || null,

      cookie_file: cookieFile.value || null,
      cookie_value: cookieValue.value || null,
      jwt: jwt.value || null,
      drop_set_cookie: dropSetCookie.value,

      skip_crawl: skipCrawl.value,
      resume_crawl: resumeCrawl.value,
      flush_attacks: flushAttacks.value,
      flush_session: flushSession.value,

      headers: toLines(headers.value),
      user_agent: userAgent.value || null,
      verify_ssl: verifySsl.value ? true : null,
      headless: headless.value || null,
      timeout: timeout.value ? Number(timeout.value) : null,

      color: color.value,
      verbose: verbose.value !== "" ? Number(verbose.value) : null,
      output_format: outputFormat.value || null,
      output: output.value || null,
      detailed_report: detailedReport.value ? Number(detailedReport.value) : null,
      no_bugreport: noBugreport.value,
      cms: cms.value || null,
    };

    const result = await generateWapitiCommand(payload);
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
        <span class="hero-badge">🕷️ Wapiti</span>
        <h1 class="hero-title">Wapiti Command Builder</h1>
        <p class="hero-subtitle">
          Black-box web app vulnerability scanner — crawl, then fuzz.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install wapiti</h2>

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
              <!-- Target -->
              <div class="field">
                <label for="url">Target URL (-u)</label>
                <input
                  id="url"
                  v-model="url"
                  type="text"
                  placeholder="https://target.com/"
                  required
                />
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="scope">Scan scope (--scope)</label>
                  <select id="scope" v-model="scope">
                    <option v-for="s in scopeOptions" :key="s" :value="s">{{ s || "Default (folder)" }}</option>
                  </select>
                </div>
                <div class="field">
                  <label for="modules">Modules (-m)</label>
                  <input id="modules" v-model="modules" type="text" placeholder="sql,xss,exec or all" />
                </div>
              </div>

              <div class="field">
                <label for="data">POST data (--data)</label>
                <input id="data" v-model="data" type="text" placeholder="login=admin&password=test" />
              </div>

              <div class="field">
                <label for="swagger">Swagger file URI (--swagger)</label>
                <input id="swagger" v-model="swagger" type="text" placeholder="https://target.com/openapi.json" />
              </div>

              <!-- Crawl limits -->
              <div class="field-row">
                <div class="field">
                  <label for="depth">Crawl depth (-d)</label>
                  <input id="depth" v-model="depth" type="number" placeholder="40" />
                </div>
                <div class="field">
                  <label for="scanForce">Scan force (-S)</label>
                  <select id="scanForce" v-model="scanForce">
                    <option v-for="s in scanForceOptions" :key="s" :value="s">{{ s || "Default (normal)" }}</option>
                  </select>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="maxLinks">Max links / page (--max-links-per-page)</label>
                  <input id="maxLinks" v-model="maxLinks" type="number" placeholder="100" />
                </div>
                <div class="field">
                  <label for="maxFiles">Max files / dir (--max-files-per-dir)</label>
                  <input id="maxFiles" v-model="maxFiles" type="number" placeholder="0 (no limit)" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="maxParams">Max parameters (--max-parameters)</label>
                  <input id="maxParams" v-model="maxParams" type="number" placeholder="0" />
                </div>
                <div class="field">
                  <label for="tasks">Concurrent tasks (--tasks)</label>
                  <input id="tasks" v-model="tasks" type="number" placeholder="2" />
                </div>
              </div>

              <!-- Attack -->
              <div class="field-row">
                <div class="field">
                  <label for="level">Attack level (-l)</label>
                  <select id="level" v-model="level">
                    <option value="">Default (1)</option>
                    <option value="1">1 — cautious</option>
                    <option value="2">2 — thorough</option>
                  </select>
                </div>
                <div class="field">
                  <label for="maxScanTime">Max scan time (--max-scan-time, sec)</label>
                  <input id="maxScanTime" v-model="maxScanTime" type="number" placeholder="0 (unlimited)" />
                </div>
              </div>

              <div class="field">
                <label for="maxAttackTime">Max attack time per module (--max-attack-time, sec)</label>
                <input id="maxAttackTime" v-model="maxAttackTime" type="number" placeholder="0 (unlimited)" />
              </div>

              <!-- Scope lists -->
              <div class="field">
                <label for="startUrls">Extra start URLs (-s) — one per line</label>
                <textarea id="startUrls" v-model="startUrls" rows="2" placeholder="https://target.com/admin/"></textarea>
              </div>

              <div class="field">
                <label for="excludeUrls">Exclude URLs (-x) — one per line</label>
                <textarea id="excludeUrls" v-model="excludeUrls" rows="2" placeholder="https://target.com/logout"></textarea>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="removeParams">Remove params (-r) — comma separated</label>
                  <input id="removeParams" v-model="removeParams" type="text" placeholder="sessionid,tracking" />
                </div>
                <div class="field">
                  <label for="skipParams">Skip attacking params (--skip) — comma separated</label>
                  <input id="skipParams" v-model="skipParams" type="text" placeholder="csrf_token" />
                </div>
              </div>

              <!-- Network -->
              <div class="field-row">
                <div class="field">
                  <label for="proxy">Proxy (-p)</label>
                  <input id="proxy" v-model="proxy" type="text" placeholder="http://127.0.0.1:8080" />
                </div>
                <div class="field">
                  <label for="timeout">Request timeout (-t, sec)</label>
                  <input id="timeout" v-model="timeout" type="number" placeholder="6" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="userAgent">User agent (-A)</label>
                  <input id="userAgent" v-model="userAgent" type="text" placeholder="Mozilla/5.0" />
                </div>
                <div class="field">
                  <label for="headless">Headless crawler (--headless)</label>
                  <select id="headless" v-model="headless">
                    <option v-for="h in headlessOptions" :key="h" :value="h">{{ h || "Default (no)" }}</option>
                  </select>
                </div>
              </div>

              <div class="field">
                <label for="headers">Custom headers (-H) — one per line</label>
                <textarea id="headers" v-model="headers" rows="2" placeholder="X-Forwarded-For: 127.0.0.1"></textarea>
              </div>

              <div class="field checkbox-field">
                <label class="checkbox">
                  <input type="checkbox" v-model="verifySsl" />
                  Verify SSL certificates (--verify-ssl 1)
                </label>
                <label class="checkbox">
                  <input type="checkbox" v-model="tor" />
                  Route through Tor (--tor)
                </label>
              </div>

              <!-- Auth -->
              <div class="field">
                <label>HTTP auth (--auth-user / --auth-password)</label>
                <div class="field-row auth-row">
                  <input v-model="authUser" type="text" placeholder="username" />
                  <input v-model="authPassword" type="password" placeholder="password" />
                  <select v-model="authMethod">
                    <option v-for="m in authMethodOptions" :key="m" :value="m">{{ m || "method" }}</option>
                  </select>
                </div>
              </div>

              <div class="field">
                <label>Login form (--form-user / --form-password / --form-url)</label>
                <div class="field-row auth-row">
                  <input v-model="formUser" type="text" placeholder="form username" />
                  <input v-model="formPassword" type="password" placeholder="form password" />
                </div>
                <input v-model="formUrl" type="text" placeholder="https://target.com/login" />
              </div>

              <!-- Session / cookies -->
              <div class="field-row">
                <div class="field">
                  <label for="cookieFile">Cookie file (-c)</label>
                  <input id="cookieFile" v-model="cookieFile" type="text" placeholder="cookies.json / firefox / chrome" />
                </div>
                <div class="field">
                  <label for="cookieValue">Cookie value (-C)</label>
                  <input id="cookieValue" v-model="cookieValue" type="text" placeholder="SESSIONID=abc; role=admin" />
                </div>
              </div>

              <div class="field">
                <label for="jwt">JWT token (--jwt)</label>
                <input id="jwt" v-model="jwt" type="text" placeholder="eyJhbGciOi..." />
              </div>

              <div class="field">
                <label>Session behaviour</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="dropSetCookie" />
                    Ignore Set-Cookie (--drop-set-cookie)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="skipCrawl" />
                    Skip crawl, attack known URLs (--skip-crawl)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="resumeCrawl" />
                    Resume crawl (--resume-crawl)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="flushAttacks" />
                    Flush attack history (--flush-attacks)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="flushSession" />
                    Flush session (--flush-session)
                  </label>
                </div>
              </div>

              <!-- Output -->
              <div class="field-row">
                <div class="field">
                  <label for="outputFormat">Report format (-f)</label>
                  <select id="outputFormat" v-model="outputFormat">
                    <option v-for="f in formatOptions" :key="f" :value="f">{{ f || "Default (html)" }}</option>
                  </select>
                </div>
                <div class="field">
                  <label for="output">Report output path (-o)</label>
                  <input id="output" v-model="output" type="text" placeholder="report/ or report.json" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="detailedReport">Detailed report (-dr)</label>
                  <select id="detailedReport" v-model="detailedReport">
                    <option value="">Default</option>
                    <option value="1">1 — include HTTP requests</option>
                    <option value="2">2 — requests + responses</option>
                  </select>
                </div>
                <div class="field">
                  <label for="verbose">Verbosity (-v)</label>
                  <select id="verbose" v-model="verbose">
                    <option value="">Default</option>
                    <option value="0">0 — quiet</option>
                    <option value="1">1 — normal</option>
                    <option value="2">2 — verbose</option>
                  </select>
                </div>
              </div>

              <div class="field">
                <label for="cms">CMS to scan (--cms)</label>
                <select id="cms" v-model="cms">
                  <option v-for="c in cmsOptions" :key="c" :value="c">{{ c || "None" }}</option>
                </select>
              </div>

              <div class="field checkbox-field">
                <label class="checkbox">
                  <input type="checkbox" v-model="color" />
                  Colorize output (--color)
                </label>
                <label class="checkbox">
                  <input type="checkbox" v-model="noBugreport" />
                  Disable auto bug report (--no-bugreport)
                </label>
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
  resize: vertical;
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
