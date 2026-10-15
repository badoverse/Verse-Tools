<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  icon: { type: String, default: "⚙️" },
});

defineEmits(["click"]);
</script>

<template>
  <button class="card" type="button" @click="$emit('click')">
    <div class="card-top">
      <div class="card-icon">{{ icon }}</div>
      <svg class="card-arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M7 17 17 7M9 7h8v8" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </div>

    <h3 class="card-title">{{ title }}</h3>
    <p class="card-description">{{ description }}</p>

    <span class="card-glow"></span>
    <span class="card-border"></span>
  </button>
</template>

<style scoped>
.card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.9rem;
  aspect-ratio: 1 / 1;
  padding: 1.4rem;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: linear-gradient(155deg, #15171d 0%, #0d0e12 100%);
  color: inherit;
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  isolation: isolate;
  opacity: 0;
  transform: translateY(14px);
  animation: rise 0.5s ease forwards;
  animation-delay: var(--delay, 0ms);
  transition: transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1),
    box-shadow 0.28s ease, border-color 0.28s ease;
}

.card:hover {
  transform: translateY(-6px) scale(1.025);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(99, 102, 241, 0.25) inset;
}

.card:active {
  transform: translateY(-2px) scale(1.01);
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 12px;
  font-size: 1.3rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform 0.28s ease, background 0.28s ease, border-color 0.28s ease;
}

.card:hover .card-icon {
  transform: scale(1.08);
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.3);
}

.card-arrow {
  color: #4b5563;
  opacity: 0;
  transform: translate(-4px, 4px);
  transition: opacity 0.25s ease, transform 0.25s ease, color 0.25s ease;
}

.card:hover .card-arrow {
  opacity: 1;
  transform: translate(0, 0);
  color: #22d3ee;
}

.card-title {
  margin: 0;
  font-size: 1.08rem;
  font-weight: 650;
  color: #f3f4f6;
  letter-spacing: -0.01em;
}

.card-description {
  margin: 0;
  font-size: 0.83rem;
  color: #8b93a3;
  line-height: 1.45;
}

.card-glow {
  position: absolute;
  inset: -40%;
  background: radial-gradient(
    circle at 30% 0%,
    rgba(99, 102, 241, 0.18),
    transparent 60%
  );
  opacity: 0;
  transition: opacity 0.35s ease;
  pointer-events: none;
  z-index: -1;
}

.card:hover .card-glow {
  opacity: 1;
}

.card-border {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.5), transparent 45%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.28s ease;
  pointer-events: none;
}

.card:hover .card-border {
  opacity: 1;
}

@keyframes rise {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>