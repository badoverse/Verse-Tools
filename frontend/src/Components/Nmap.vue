<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { generateNmapCommand } from "@/api/commands-api";

const router = useRouter();

const os = ref("linux");

const target = ref("");
const ports = ref("");
const scanType = ref("-sV");

const osDetection = ref(false);
const versionDetection = ref(true);
const versionIntensity = ref("");
const aggressive = ref(false);
const noPing = ref(false);
const pingOnly = ref(false);

const defaultScripts = ref(false);
const script = ref("");
const scriptArgs = ref("");

const portMode = ref("custom"); // custom | all | top | fast
const topPorts = ref("");
const excludePorts = ref("");

const timing = ref("");
const minRate = ref("");
const maxRate = ref("");
const hostTimeout = ref("");

const fragmentPackets = ref(false);
const decoy = ref("");
const spoofSourceIp = ref("");
const spoofMac = ref("");
const sourcePort = ref("");

const ipv6 = ref(false);

const verbose = ref(0);
const outputMode = ref("none"); // none | normal | xml | grepable | all
const outputPath = ref("");
const reason = ref(false);
const openOnly = ref(false);

const excludeHosts = ref("");
const interfaceName = ref("");

const command = ref("");
const error = ref("");
const loading = ref(false);
const copied = ref(false);
const installCopied = ref(false);

const osOptions = [
  { value: "linux", label: "Linux" },
  { value: "windows", label: "Windows" },
];

const scanTypes = [
  { value: "-sS", label: "-sS  SYN scan (stealthy, needs root)" },
  { value: "-sT", label: "-sT  TCP connect scan" },
  { value: "-sU", label: "-sU  UDP scan" },
  { value: "-sV", label: "-sV  Version detection" },
  { value: "-sA", label: "-sA  ACK scan (firewall mapping)" },
  { value: "-sW", label: "-sW  Window scan" },
  { value: "-sM", label: "-sM  Maimon scan" },
];

const installCommands = {
  linux: "sudo apt update && sudo apt install nmap -y",
  windows: "choco install nmap -y",
};

const installNote = computed(() =>
  os.value === "windows"
    ? "The Chocolatey package includes Npcap, required for raw packet scans like -sS."
    : "SYN scans (-sS) and OS detection (-O) need root — run nmap with sudo."
);

async function handleGenerate() {
  error.value = "";
  command.value = "";
  loading.value = true;

  try {
    const payload = {
      target: target.value,
      ports: portMode.value === "custom" ? ports.value || null : null,
      scan_type: scanType.value,

      os_detection: osDetection.value,
      version_detection: versionDetection.value,
      version_intensity: versionIntensity.value !== "" ? Number(versionIntensity.value) : null,
      aggressive: aggressive.value,
      no_ping: noPing.value,
      ping_only: pingOnly.value,

      default_scripts: defaultScripts.value,
      script: script.value || null,
      script_args: scriptArgs.value || null,

      all_ports: portMode.value === "all",
      top_ports: portMode.value === "top" && topPorts.value ? Number(topPorts.value) : null,
      fast_scan: portMode.value === "fast",
      exclude_ports: excludePorts.value || null,

      timing: timing.value !== "" ? Number(timing.value) : null,
      min_rate: minRate.value ? Number(minRate.value) : null,
      max_rate: maxRate.value ? Number(maxRate.value) : null,
      host_timeout: hostTimeout.value || null,

      fragment_packets: fragmentPackets.value,
      decoy: decoy.value || null,
      spoof_source_ip: spoofSourceIp.value || null,
      spoof_mac: spoofMac.value || null,
      source_port: sourcePort.value ? Number(sourcePort.value) : null,

      ipv6: ipv6.value,

      verbose: verbose.value,
      reason: reason.value,
      open_only: openOnly.value,

      output_normal: outputMode.value === "normal" ? outputPath.value || null : null,
      output_xml: outputMode.value === "xml" ? outputPath.value || null : null,
      output_grepable: outputMode.value === "grepable" ? outputPath.value || null : null,
      output_all: outputMode.value === "all" ? outputPath.value || null : null,

      exclude_hosts: excludeHosts.value || null,
      interface: interfaceName.value || null,
    };

    const result = await generateNmapCommand(payload);
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
        <span class="hero-badge">📡 Nmap</span>
        <h1 class="hero-title">Nmap Command Builder</h1>
        <p class="hero-subtitle">
          Scan responsibly — only hosts you own or are authorized to test.
        </p>
      </header>

      <div class="steps">
        <div class="step-rail"></div>

        <section class="step">
          <div class="step-marker">1</div>

          <div class="step-card install-card">
            <div class="install-card-head">
              <h2 class="step-title">Install nmap</h2>

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
                <label for="target">Target</label>
                <input
                  id="target"
                  v-model="target"
                  type="text"
                  placeholder="192.168.1.1 or scanme.nmap.org"
                  required
                />
              </div>

              <div class="field">
                <label>Scan type</label>
                <select v-model="scanType" :disabled="pingOnly || aggressive">
                  <option v-for="s in scanTypes" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>

              <div class="field">
                <label>Quick modes</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="aggressive" />
                    Aggressive (-A: OS + version + scripts + traceroute)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="pingOnly" />
                    Host discovery only (-sn, no port scan)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="noPing" />
                    Skip host discovery (-Pn)
                  </label>
                </div>
              </div>

              <div v-if="!pingOnly && !aggressive" class="field">
                <label>Detection</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="osDetection" />
                    OS detection (-O)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="versionDetection" />
                    Version detection (-sV)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="defaultScripts" />
                    Default scripts (-sC)
                  </label>
                </div>
              </div>

              <div v-if="versionDetection" class="field">
                <label for="versionIntensity">Version intensity (0-9)</label>
                <input id="versionIntensity" v-model="versionIntensity" type="number" min="0" max="9" placeholder="7 (default)" />
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="script">NSE scripts (--script)</label>
                  <input id="script" v-model="script" type="text" placeholder="vuln,http-title" />
                </div>
                <div class="field">
                  <label for="scriptArgs">Script args</label>
                  <input id="scriptArgs" v-model="scriptArgs" type="text" placeholder="user=admin,pass=admin" />
                </div>
              </div>

              <!-- Ports -->
              <div v-if="!pingOnly" class="field">
                <label>Ports</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: portMode === 'custom' }" @click="portMode = 'custom'">Custom</button>
                  <button type="button" class="pill" :class="{ active: portMode === 'all' }" @click="portMode = 'all'">All 65535 (-p-)</button>
                  <button type="button" class="pill" :class="{ active: portMode === 'top' }" @click="portMode = 'top'">Top N</button>
                  <button type="button" class="pill" :class="{ active: portMode === 'fast' }" @click="portMode = 'fast'">Fast (-F)</button>
                </div>

                <input
                  v-if="portMode === 'custom'"
                  v-model="ports"
                  type="text"
                  placeholder="22,80,443 or 1-1000"
                  class="auth-row"
                />
                <input
                  v-if="portMode === 'top'"
                  v-model="topPorts"
                  type="number"
                  placeholder="100"
                  class="auth-row"
                />
              </div>

              <div v-if="!pingOnly" class="field">
                <label for="excludePorts">Exclude ports</label>
                <input id="excludePorts" v-model="excludePorts" type="text" placeholder="21,23" />
              </div>

              <!-- Timing -->
              <div class="field">
                <label>
                  Timing template {{ timing !== "" ? `(-T${timing})` : "(default)" }}
                </label>
                <input type="range" min="0" max="5" step="1" v-model="timing" />
                <p class="hint">0 = paranoid/slowest &nbsp;·&nbsp; 5 = insane/fastest</p>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="minRate">Min rate (pkt/s)</label>
                  <input id="minRate" v-model="minRate" type="number" placeholder="300" />
                </div>
                <div class="field">
                  <label for="maxRate">Max rate (pkt/s)</label>
                  <input id="maxRate" v-model="maxRate" type="number" />
                </div>
                <div class="field">
                  <label for="hostTimeout">Host timeout</label>
                  <input id="hostTimeout" v-model="hostTimeout" type="text" placeholder="30m" />
                </div>
              </div>

              <!-- Evasion -->
              <div class="field">
                <label>Evasion / spoofing</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="fragmentPackets" />
                    Fragment packets (-f)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="ipv6" />
                    IPv6 (-6)
                  </label>
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="decoy">Decoys (-D)</label>
                  <input id="decoy" v-model="decoy" type="text" placeholder="10.0.0.1,10.0.0.2,ME" />
                </div>
                <div class="field">
                  <label for="spoofSourceIp">Spoof source IP (-S)</label>
                  <input id="spoofSourceIp" v-model="spoofSourceIp" type="text" placeholder="1.2.3.4" />
                </div>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="spoofMac">Spoof MAC</label>
                  <input id="spoofMac" v-model="spoofMac" type="text" placeholder="00:11:22:33:44:55" />
                </div>
                <div class="field">
                  <label for="sourcePort">Source port (-g)</label>
                  <input id="sourcePort" v-model="sourcePort" type="number" placeholder="53" />
                </div>
              </div>

              <!-- Output -->
              <div class="field">
                <label>Verbosity</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: verbose === 0 }" @click="verbose = 0">None</button>
                  <button type="button" class="pill" :class="{ active: verbose === 1 }" @click="verbose = 1">-v</button>
                  <button type="button" class="pill" :class="{ active: verbose === 2 }" @click="verbose = 2">-vv</button>
                  <button type="button" class="pill" :class="{ active: verbose === 3 }" @click="verbose = 3">-vvv</button>
                </div>
              </div>

              <div class="field">
                <label>Result filtering</label>
                <div class="checkbox-grid">
                  <label class="checkbox">
                    <input type="checkbox" v-model="reason" />
                    Show reason (--reason)
                  </label>
                  <label class="checkbox">
                    <input type="checkbox" v-model="openOnly" />
                    Open ports only (--open)
                  </label>
                </div>
              </div>

              <div class="field">
                <label>Save output</label>
                <div class="pill-group">
                  <button type="button" class="pill" :class="{ active: outputMode === 'none' }" @click="outputMode = 'none'">Terminal only</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'normal' }" @click="outputMode = 'normal'">Normal (-oN)</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'xml' }" @click="outputMode = 'xml'">XML (-oX)</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'grepable' }" @click="outputMode = 'grepable'">Grepable (-oG)</button>
                  <button type="button" class="pill" :class="{ active: outputMode === 'all' }" @click="outputMode = 'all'">All formats (-oA)</button>
                </div>

                <input
                  v-if="outputMode !== 'none'"
                  v-model="outputPath"
                  type="text"
                  :placeholder="outputMode === 'all' ? 'scan-results (no extension)' : 'scan-results.txt'"
                  class="auth-row"
                />
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="excludeHosts">Exclude hosts</label>
                  <input id="excludeHosts" v-model="excludeHosts" type="text" placeholder="192.168.1.5,192.168.1.6" />
                </div>
                <div class="field">
                  <label for="interfaceName">Interface (-e)</label>
                  <input id="interfaceName" v-model="interfaceName" type="text" placeholder="eth0" />
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
input:disabled, select:disabled { opacity: 0.4; cursor: not-allowed; }
input::placeholder, textarea::placeholder { color: #4b5563; }
input:focus, select:focus, textarea:focus { border-color: rgba(34, 211, 238, 0.5); box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.1); }

input[type="range"] { padding: 0; accent-color: #22d3ee; }

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