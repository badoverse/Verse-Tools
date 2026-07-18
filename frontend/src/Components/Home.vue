<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import CommandCard from "./CommandCard.vue";

const router = useRouter();


const phrases = [
  "Pick a tool n get to work.",
  "No cheat sheets. No guesswork. Just the right commands.",
  "Install the tools locally on your PC before executing any command.",
  "Also try Minecraft!",
];

const phraseIndex = ref(0);
let phraseTimer = null;

onMounted(() => {
  phraseTimer = setInterval(() => {
    phraseIndex.value = (phraseIndex.value + 1) % phrases.length;
  }, 3000);
});

onUnmounted(() => {
  clearInterval(phraseTimer);
});

const commands = ref([
  {
    id: "nmap",
    title: "Nmap",
    description: "Scan hosts and discover open ports & services.",
    icon: "📡",
    route: "/commands/nmap",
  },
  {
    id: "nikto",
    title: "Nikto",
    description: "Scan web servers for known vulnerabilities.",
    icon: "🛡️",
    route: "/commands/nikto",
  },
  {
    id: "gobuster",
    title: "Gobuster",
    description: "Brute-force directories, files & DNS subdomains.",
    icon: "🗂️",
    route: "/commands/gobuster",
  },
  {
    id: "curl",
    title: "Curl",
    description: "Craft custom HTTP requests for quick testing.",
    icon: "🌐",
    route: "/commands/curl",
  },
  {
    id: "sqlmap",
    title: "SQLmap",
    description: "Build commands to test for SQL injection points.",
    icon: "🧬",
    route: "/commands/sqlmap",
  },
  {
    id: "hydra",
    title: "Hydra",
    description: "Generate brute-force login attack commands.",
    icon: "🔑",
    route: "/commands/hydra",
  },
]);

function goToCommand(cmd) {
  //vue Router will be wired up later — this is ready to go
  if (cmd.route) {
    router.push(cmd.route);
  }
}
</script>

<template>
  <div class="page">
    <div class="ambient-glow glow-one"></div>
    <div class="ambient-glow glow-two"></div>

    <header class="hero">
      <span class="hero-badge">Command Generator</span>
      <h1 class="hero-title">Verse Tools</h1>

      <div class="hero-subtitle">
        <Transition name="phrase" mode="out-in">
          <p :key="phraseIndex">{{ phrases[phraseIndex] }}</p>
        </Transition>
      </div>
    </header>

    <main class="grid">
      <CommandCard
        v-for="(cmd, index) in commands"
        :key="cmd.id"
        :title="cmd.title"
        :description="cmd.description"
        :icon="cmd.icon"
        :style="{ '--delay': `${index * 60}ms` }"
        @click="goToCommand(cmd)"
      />
    </main>

    <footer class="footer">
      <div class="footer-divider"></div>
      <p class="footer-text">
        Built by <span class="footer-author">badoVerse</span>
      </p>
      <div class="footer-links">
        <a
          href="https://github.com/badoverse"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="GitHub"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55v-1.94c-3.2.7-3.87-1.36-3.87-1.36-.53-1.33-1.29-1.68-1.29-1.68-1.05-.72.08-.7.08-.7 1.17.08 1.78 1.2 1.78 1.2 1.03 1.77 2.72 1.26 3.38.96.1-.75.4-1.26.73-1.55-2.55-.29-5.23-1.28-5.23-5.68 0-1.25.45-2.28 1.18-3.08-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.74 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.58.23 2.75.11 3.04.74.8 1.18 1.83 1.18 3.08 0 4.41-2.69 5.38-5.25 5.67.41.36.78 1.06.78 2.14v3.17c0 .31.21.66.79.55A11.5 11.5 0 0 0 23.5 12c0-6.35-5.15-11.5-11.5-11.5Z"/>
          </svg>
          <span>GitHub</span>
        </a>
      </div>
    </footer>
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
  padding: 5rem 2rem 3rem;
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

.hero {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-bottom: 4rem;
  animation: fade-down 0.6s ease both;
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
  font-size: clamp(2.5rem, 5vw, 3.4rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  background: linear-gradient(100deg, #f9fafb 10%, #a5b4fc 50%, #22d3ee 90%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  position: relative;
  margin: 0.85rem auto 0;
  max-width: 32rem;
  min-height: 3.2rem;
  color: #8b93a3;
  font-size: 1.02rem;
  line-height: 1.6;
}

.hero-subtitle p {
  margin: 0;
}

.phrase-enter-active,
.phrase-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.phrase-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.phrase-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.5rem;
  max-width: 1120px;
  margin: 0 auto;
}

.footer {
  position: relative;
  z-index: 1;
  margin-top: 5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.1rem;
  max-width: 1120px;
  margin-left: auto;
  margin-right: auto;
}

.footer-divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.1) 50%,
    transparent
  );
}

.footer-text {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
}

.footer-author {
  color: #cbd5e1;
  font-weight: 600;
}

.footer-links {
  display: flex;
  gap: 0.75rem;
}

.footer-links a {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #9ca3af;
  font-size: 0.82rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease, border-color 0.2s ease, background 0.2s ease,
    transform 0.2s ease;
}

.footer-links a:hover {
  color: #e5e7eb;
  border-color: rgba(34, 211, 238, 0.4);
  background: rgba(34, 211, 238, 0.06);
  transform: translateY(-2px);
}

@keyframes fade-down {
  from {
    opacity: 0;
    transform: translateY(-12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>