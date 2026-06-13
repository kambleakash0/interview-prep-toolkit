<script setup lang="ts">
import { useNav } from '@slidev/client'
const { currentPage, total } = useNav()
</script>

<template>
  <!-- subtle drifting glow: blends over content, never blocks clicks -->
  <div class="bp-aura" />
  <!-- persistent footer -->
  <div class="bp-footer">
    <span>LLD · DECK 1 — FOUNDATIONS</span>
    <span>{{ String(currentPage).padStart(2, '0') }} / {{ String(total).padStart(2, '0') }}</span>
  </div>
</template>

<style>
.bp-aura {
  position: absolute; inset: -10%;
  pointer-events: none; z-index: 1;
  mix-blend-mode: screen; opacity: .5;
  background:
    radial-gradient(38% 32% at 18% 22%, rgba(34,211,238,.16), transparent 70%),
    radial-gradient(34% 30% at 84% 78%, rgba(167,139,250,.14), transparent 70%);
  animation: bp-drift 18s ease-in-out infinite alternate;
}
@keyframes bp-drift {
  0%   { transform: translate3d(0,0,0) scale(1); }
  100% { transform: translate3d(2%, -2%, 0) scale(1.08); }
}
@media (prefers-reduced-motion: reduce) { .bp-aura { animation: none; } }
</style>
