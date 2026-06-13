<script setup lang="ts">
import { ref } from 'vue'

const BIRDS = [
  { name: 'Sparrow', ok: true,  out: 'flaps and flies away' },
  { name: 'Eagle',   ok: true,  out: 'soars on a thermal' },
  { name: 'Penguin', ok: false, out: 'raises CantFlyError' },
]
const pick = ref(0)
</script>

<template>
  <div class="lsp">
    <div class="caller">
      <div class="bp-chip">caller expects a Bird</div>
      <pre class="code">def release(bird: Bird):
    bird.<span class="hl">fly()</span>      <span class="dim"># must work for ANY Bird</span></pre>
    </div>

    <div class="run">
      <div class="lbl">substitute a subtype</div>
      <div class="opts">
        <button v-for="(b, i) in BIRDS" :key="b.name" class="opt" :class="{ on: pick === i }" @click="pick = i">
          {{ b.name }}
        </button>
      </div>

      <div class="result" :class="BIRDS[pick].ok ? 'ok' : 'bad'">
        <div class="rl">release({{ BIRDS[pick].name }}())</div>
        <div class="ro">&rarr; {{ BIRDS[pick].out }}</div>
        <div class="rv">{{ BIRDS[pick].ok ? 'substitutable — contract honored' : 'LSP VIOLATED — not safely substitutable' }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lsp { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; align-items: start; font-family: "Fira Code", monospace; }
.caller { display: flex; flex-direction: column; gap: .7rem; }
.code { font-size: .85rem; color: var(--bp-ink); margin: 0; line-height: 1.5; }
.code .hl { color: var(--bp-cyan); } .code .dim, .dim { color: var(--bp-dim); }
.run { display: flex; flex-direction: column; gap: .7rem; }
.lbl { font-size: .64rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bp-dim); }
.opts { display: flex; gap: .5rem; }
.opt { font-family: inherit; font-size: .84rem; padding: .5rem .9rem; border: 1px solid var(--bp-line); border-radius: 8px; background: rgba(255,255,255,.02); color: var(--bp-ink); cursor: pointer; transition: .15s; }
.opt:hover { border-color: var(--bp-cyan); }
.opt.on { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.1); }
.result { border-radius: 11px; padding: 1rem; border: 1px solid var(--bp-line); transition: all .3s; margin-top: .4rem; }
.result.ok { border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.06); }
.result.bad { border-color: rgba(251,113,133,.45); background: rgba(251,113,133,.07); animation: shake .4s; }
.rl { color: #fff; font-size: .9rem; } .ro { margin: .4rem 0; font-size: .95rem; }
.result.ok .ro { color: var(--bp-good); } .result.bad .ro { color: var(--bp-bad); }
.rv { font-size: .72rem; letter-spacing: .04em; }
.result.ok .rv { color: var(--bp-good); } .result.bad .rv { color: var(--bp-bad); }
@keyframes shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
</style>
