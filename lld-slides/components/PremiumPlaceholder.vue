<script setup lang="ts">
defineProps<{ note?: string }>()
</script>

<template>
  <div class="locked">
    <svg class="lockicon" viewBox="0 0 24 24" width="56" height="56" fill="none"
         stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="11" width="16" height="10" rx="2.2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
      <circle cx="12" cy="16" r="1.3" fill="currentColor" stroke="none" />
    </svg>

    <div class="ltitle">PREMIUM LESSON</div>
    <div class="lnote">{{ note || 'The full lesson is paywalled on the source course — content to be added.' }}</div>
    <div class="lbadge">content pending</div>
  </div>
</template>

<style scoped>
.locked {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: .9rem; text-align: center; min-height: 320px;
  border: 1px dashed rgba(167,139,250,.4); border-radius: 16px;
  background: linear-gradient(180deg, rgba(167,139,250,.06), rgba(167,139,250,.02));
  padding: 2rem; position: relative; overflow: hidden;
}
.locked::before {       /* faint corner glow */
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(60% 50% at 50% 0%, rgba(167,139,250,.12), transparent 70%);
}
.lockicon { color: var(--bp-violet); filter: drop-shadow(0 0 16px rgba(167,139,250,.4)); }
.ltitle {
  font-family: "Fira Code", monospace; font-size: .8rem; letter-spacing: .28em;
  color: var(--bp-violet); text-transform: uppercase;
}
.lnote { color: var(--bp-dim); max-width: 30rem; font-size: .95rem; line-height: 1.5; }
.lbadge {
  font-family: "Fira Code", monospace; font-size: .68rem; letter-spacing: .12em;
  color: var(--bp-warn); border: 1px solid rgba(251,191,36,.35); border-radius: 999px;
  padding: .25em .9em; background: rgba(251,191,36,.06); margin-top: .3rem;
}
</style>
