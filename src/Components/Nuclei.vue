<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateNucleiCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

// Target
const targets = ref("");
const targetList = ref("");
const excludeHosts = ref("");

// Templates
const templates = ref("");
const workflows = ref("");
const newTemplates = ref(false);
const automaticScan = ref(false);
const dast = ref(false);

// Filtering
const tags = ref("");
const excludeTags = ref("");
const templateIds = ref("");
const excludeIds = ref("");
const excludeTemplates = ref("");
const author = ref("");
const severity = ref([]);
const excludeSeverity = ref([]);
const protocolTypes = ref([]);

// Network
const headers = ref("");
const variables = ref("");
const redirects = ref(""); // "" = default, "fr" = follow, "fhr" = same host only, "dr" = disable
const maxRedirects = ref("");
const proxy = ref("");
const resolvers = ref("");
const systemResolvers = ref(false);
const iface = ref("");
const sourceIp = ref("");

// Interactsh
const interactshServer = ref("");
const noInteractsh = ref(false);

// Rate limits
const rateLimit = ref("");
const bulkSize = ref("");
const concurrency = ref("");
const timeout = ref("");
const retries = ref("");
const maxHostError = ref("");
const scanStrategy = ref("");
const stopAtFirstMatch = ref(false);
const noHttpx = ref(false);

// Headless
const headless = ref(false);
const pageTimeout = ref("");
const systemChrome = ref(false);

// Output
const output = ref("");
const jsonl = ref(false);
const jsonExport = ref("");
const markdownExport = ref("");
const sarifExport = ref("");
const storeResp = ref(false);
const silent = ref(false);
const noColor = ref(false);
const noMeta = ref(false);
const timestamp = ref(false);
const matcherStatus = ref(false);

// Debug / update
const verbose = ref(false);
const debug = ref(false);
const stats = ref(false);
const updateTemplates = ref(false);
const disableUpdateCheck = ref(false);

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const severityOptions = ["info", "low", "medium", "high", "critical", "unknown"];
const typeOptions = ["http", "dns", "tcp", "ssl", "file", "headless", "websocket", "whois", "code", "javascript", "workflow"];
const scanStrategyOptions = ["", "auto", "host-spray", "template-spray"];

const installCommands = {
  linux: "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
  windows: "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "Nuclei is a Go binary. Install Go first, then run the command above, or download a release zip from the projectdiscovery/nuclei GitHub page. Templates download on first run."
    : "Nuclei is a Go binary. Install Go first and make sure ~/go/bin is on your PATH. On Kali, `sudo apt install nuclei` also works. Templates download on first run."
);

function toLines(v) {
  return v
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
}

function toggle(list, value) {
  const i = list.value.indexOf(value);
  if (i === -1) list.value.push(value);
  else list.value.splice(i, 1);
}

async function handleGenerate() {
  error.value = "";
  command.value = "";
  loading.value = true;

  try {
    const payload = {
      targets: toLines(targets.value),
      target_list: targetList.value || null,
      exclude_hosts: excludeHosts.value || null,

      templates: templates.value || null,
      workflows: workflows.value || null,
      new_templates: newTemplates.value,
      automatic_scan: automaticScan.value,
      dast: dast.value,

      tags: tags.value || null,
      exclude_tags: excludeTags.value || null,
      template_ids: templateIds.value || null,
      exclude_ids: excludeIds.value || null,
      exclude_templates: excludeTemplates.value || null,
      author: author.value || null,
      severity: severity.value,
      exclude_severity: excludeSeverity.value,
      protocol_types: protocolTypes.value,

      headers: toLines(headers.value),
      variables: toLines(variables.value),
      follow_redirects: redirects.value === "fr",
      follow_host_redirects: redirects.value === "fhr",
      disable_redirects: redirects.value === "dr",
      max_redirects: maxRedirects.value !== "" ? Number(maxRedirects.value) : null,
      proxy: proxy.value || null,
      resolvers: resolvers.value || null,
      system_resolvers: systemResolvers.value,
      interface: iface.value || null,
      source_ip: sourceIp.value || null,

      interactsh_server: interactshServer.value || null,
      no_interactsh: noInteractsh.value,

      rate_limit: rateLimit.value !== "" ? Number(rateLimit.value) : null,
      bulk_size: bulkSize.value !== "" ? Number(bulkSize.value) : null,
      concurrency: concurrency.value !== "" ? Number(concurrency.value) : null,
      timeout: timeout.value !== "" ? Number(timeout.value) : null,
      retries: retries.value !== "" ? Number(retries.value) : null,
      max_host_error: maxHostError.value !== "" ? Number(maxHostError.value) : null,
      scan_strategy: scanStrategy.value || null,
      stop_at_first_match: stopAtFirstMatch.value,
      no_httpx: noHttpx.value,

      headless: headless.value,
      page_timeout: pageTimeout.value !== "" ? Number(pageTimeout.value) : null,
      system_chrome: systemChrome.value,

      output: output.value || null,
      jsonl: jsonl.value,
      json_export: jsonExport.value || null,
      markdown_export: markdownExport.value || null,
      sarif_export: sarifExport.value || null,
      store_resp: storeResp.value,
      silent: silent.value,
      no_color: noColor.value,
      no_meta: noMeta.value,
      timestamp: timestamp.value,
      matcher_status: matcherStatus.value,

      verbose: verbose.value,
      debug: debug.value,
      stats: stats.value,
      update_templates: updateTemplates.value,
      disable_update_check: disableUpdateCheck.value,
    };

    const result = await generateNucleiCommand(payload);
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
        <span class="hero-badge">☢️ Nuclei</span>
        <h1 class="hero-title">Nuclei Command Builder</h1>
        <p class="hero-subtitle">
          Template-based vulnerability scanner — fast, YAML-driven checks.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install nuclei</h2>

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
                <label for="targets">Targets (-u) — one per line</label>
                <textarea id="targets" v-model="targets" rows="2" placeholder="https://target.com"></textarea>
                <p class="hint">Give at least one target here or a target list file below.</p>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="targetList">Target list file (-l)</label>
                  <input id="targetList" v-model="targetList" type="text" placeholder="hosts.txt" />
                </div>
                <div class="field">
                  <label for="excludeHosts">Exclude hosts (-eh)</label>
                  <input id="excludeHosts" v-model="excludeHosts" type="text" placeholder="admin.target.com,10.0.0.0/24" />
                </div>
              </div>

              <!-- Templates -->
              <div class="field-row">
                <div class="field">
                  <label for="templates">Templates (-t) — comma separated</label>
                  <input id="templates" v-model="templates" type="text" placeholder="http/cves/,ssl/" />
                </div>
                <div class="field">
                  <label for="workflows">Workflows (-w) — comma separated</label>
                  <input id="workflows" v-model="workflows" type="text" placeholder="workflows/wordpress-workflow.yaml" />
                </div>
              </div>

              <div class="field">
                <label>Template selection</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="newTemplates" />
                    Only newest templates (-nt)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="automaticScan" />
                    Automatic scan by tech detection (-as)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="dast" />
                    Run DAST / fuzzing templates (-dast)
                  </label>
                </div>
              </div>

              <!-- Filtering -->
              <div class="field">
                <label>Severity (-s)</label>
                <div class="pill-group">
                  <button
                    v-for="s in severityOptions"
                    :key="s"
                    type="button"
                    class="pill"
                    :class="{ active: severity.includes(s) }"
                    @click="toggle(severity, s)"
                  >
                    {{ s }}
                  </button>
                </div>
              </div>

              <div class="field">
                <label>Exclude severity (-es)</label>
                <div class="pill-group">
                  <button
                    v-for="s in severityOptions"
                    :key="s"
                    type="button"
                    class="pill"
                    :class="{ active: excludeSeverity.includes(s) }"
                    @click="toggle(excludeSeverity, s)"
                  >
                    {{ s }}
                  </button>
                </div>
              </div>

              <div class="field">
                <label>Protocol types (-pt)</label>
                <div class="pill-group">
                  <button
                    v-for="t in typeOptions"
                    :key="t"
                    type="button"
                    class="pill"
                    :class="{ active: protocolTypes.includes(t) }"
                    @click="toggle(protocolTypes, t)"
                  >
                    {{ t }}
                  </button>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="tags">Tags (-tags)</label>
                  <input id="tags" v-model="tags" type="text" placeholder="cve,rce,lfi" />
                </div>
                <div class="field">
                  <label for="excludeTags">Exclude tags (-etags)</label>
                  <input id="excludeTags" v-model="excludeTags" type="text" placeholder="dos,intrusive" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="templateIds">Template IDs (-id)</label>
                  <input id="templateIds" v-model="templateIds" type="text" placeholder="CVE-2021-44228" />
                </div>
                <div class="field">
                  <label for="excludeIds">Exclude IDs (-eid)</label>
                  <input id="excludeIds" v-model="excludeIds" type="text" placeholder="tech-detect" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="excludeTemplates">Exclude templates (-et)</label>
                  <input id="excludeTemplates" v-model="excludeTemplates" type="text" placeholder="http/fuzzing/" />
                </div>
                <div class="field">
                  <label for="author">Author (-a)</label>
                  <input id="author" v-model="author" type="text" placeholder="pdteam" />
                </div>
              </div>

              <!-- Network -->
              <div class="field">
                <label for="headers">Custom headers (-H) — one per line</label>
                <textarea id="headers" v-model="headers" rows="2" placeholder="Authorization: Bearer token"></textarea>
              </div>

              <div class="field">
                <label for="variables">Template variables (-V) — key=value, one per line</label>
                <textarea id="variables" v-model="variables" rows="2" placeholder="username=admin"></textarea>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="redirects">Redirects</label>
                  <select id="redirects" v-model="redirects">
                    <option value="">Default</option>
                    <option value="fr">Follow (-fr)</option>
                    <option value="fhr">Follow on same host (-fhr)</option>
                    <option value="dr">Disable (-dr)</option>
                  </select>
                </div>
                <div class="field">
                  <label for="maxRedirects">Max redirects (-mr)</label>
                  <input id="maxRedirects" v-model="maxRedirects" type="number" min="0" placeholder="10" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="proxy">Proxy (-p)</label>
                  <input id="proxy" v-model="proxy" type="text" placeholder="http://127.0.0.1:8080" />
                </div>
                <div class="field">
                  <label for="resolvers">Resolvers file (-r)</label>
                  <input id="resolvers" v-model="resolvers" type="text" placeholder="resolvers.txt" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="iface">Network interface (-i)</label>
                  <input id="iface" v-model="iface" type="text" placeholder="eth0" />
                </div>
                <div class="field">
                  <label for="sourceIp">Source IP (-sip)</label>
                  <input id="sourceIp" v-model="sourceIp" type="text" placeholder="10.0.0.5" />
                </div>
              </div>

              <div class="field">
                <label for="interactshServer">Interactsh server (-iserver)</label>
                <input id="interactshServer" v-model="interactshServer" type="text" placeholder="oast.pro" />
              </div>

              <div class="field">
                <label>Network behaviour</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="systemResolvers" />
                    System DNS as fallback (-sr)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noInteractsh" />
                    Disable interactsh / OAST (-ni)
                  </label>
                </div>
              </div>

              <!-- Rate limits -->
              <div class="field-row">
                <div class="field">
                  <label for="rateLimit">Rate limit (-rl, req/sec)</label>
                  <input id="rateLimit" v-model="rateLimit" type="number" min="1" placeholder="150" />
                </div>
                <div class="field">
                  <label for="concurrency">Template concurrency (-c)</label>
                  <input id="concurrency" v-model="concurrency" type="number" min="1" placeholder="25" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="bulkSize">Hosts in parallel (-bs)</label>
                  <input id="bulkSize" v-model="bulkSize" type="number" min="1" placeholder="25" />
                </div>
                <div class="field">
                  <label for="timeout">Timeout (-timeout, sec)</label>
                  <input id="timeout" v-model="timeout" type="number" min="1" placeholder="10" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="retries">Retries (-retries)</label>
                  <input id="retries" v-model="retries" type="number" min="0" placeholder="1" />
                </div>
                <div class="field">
                  <label for="maxHostError">Max errors per host (-mhe)</label>
                  <input id="maxHostError" v-model="maxHostError" type="number" min="0" placeholder="30" />
                </div>
              </div>

              <div class="field">
                <label for="scanStrategy">Scan strategy (-ss)</label>
                <select id="scanStrategy" v-model="scanStrategy">
                  <option v-for="s in scanStrategyOptions" :key="s" :value="s">{{ s || "Default (auto)" }}</option>
                </select>
              </div>

              <div class="field">
                <label>Scan behaviour</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="stopAtFirstMatch" />
                    Stop at first match (-spm)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noHttpx" />
                    Skip httpx probing (-nh)
                  </label>
                </div>
              </div>

              <!-- Headless -->
              <div class="field-row">
                <div class="field checkbox-field">
                  <label class="checkbox">
                    <input type="checkbox" v-model="headless" />
                    Enable headless templates (-headless)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="systemChrome" />
                    Use system Chrome (-sc)
                  </label>
                </div>
                <div class="field">
                  <label for="pageTimeout">Page timeout (-page-timeout, sec)</label>
                  <input id="pageTimeout" v-model="pageTimeout" type="number" min="1" placeholder="20" />
                </div>
              </div>

              <!-- Output -->
              <div class="field-row">
                <div class="field">
                  <label for="output">Output file (-o)</label>
                  <input id="output" v-model="output" type="text" placeholder="results.txt" />
                </div>
                <div class="field">
                  <label for="jsonExport">JSON export file (-je)</label>
                  <input id="jsonExport" v-model="jsonExport" type="text" placeholder="results.json" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="markdownExport">Markdown export dir (-me)</label>
                  <input id="markdownExport" v-model="markdownExport" type="text" placeholder="reports/" />
                </div>
                <div class="field">
                  <label for="sarifExport">SARIF export file (-se)</label>
                  <input id="sarifExport" v-model="sarifExport" type="text" placeholder="results.sarif" />
                </div>
              </div>

              <div class="field">
                <label>Output options</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="jsonl" />
                    JSONL output (-j)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="storeResp" />
                    Store requests / responses (-sresp)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="silent" />
                    Findings only (-silent)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noColor" />
                    No color (-nc)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noMeta" />
                    Hide result metadata (-nm)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="timestamp" />
                    Timestamps (-ts)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="matcherStatus" />
                    Show match failures (-ms)
                  </label>
                </div>
              </div>

              <!-- Debug / update -->
              <div class="field">
                <label>Debug &amp; updates</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="verbose" />
                    Verbose (-v)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="debug" />
                    Show requests and responses (-debug)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="stats" />
                    Show scan statistics (-stats)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="updateTemplates" />
                    Update templates first (-ut)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="disableUpdateCheck" />
                    Disable update check (-duc)
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
