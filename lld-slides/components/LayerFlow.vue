<script setup lang="ts">
import { ref } from 'vue'
const LAYERS = [
  { name: 'Presentation', job: 'render & collect input' },
  { name: 'Business logic', job: 'rules & decisions' },
  { name: 'Data access', job: 'queries & mapping' },
  { name: 'Database', job: 'storage' },
]
const active = ref(-1)
const dir = ref<'down' | 'up'>('down')
let running = false

function send() {
  if (running) return
  running = true
  let i = 0; dir.value = 'down'
  const step = () => {
    active.value = i
    if (dir.value === 'down') {
      if (i < LAYERS.length - 1) { i++; setTimeout(step, 380) }
      else { dir.value = 'up'; setTimeout(step, 480) }
    } else {
      if (i > 0) { i--; setTimeout(step, 320) }
      else { setTimeout(() => { active.value = -1; running = false }, 400) }
    }
  }
  step()
}
</script>

<template>
  <div class="lf">
    <div class="stack">
      <template v-for="(l, i) in LAYERS" :key="l.name">
        <div class="layer" :class="{ on: active === i }">
          <span class="nm">{{ l.name }}</span><span class="job">{{ l.job }}</span>
        </div>
        <div v-if="i < LAYERS.length - 1" class="seam" :class="{ lit: active === i || active === i + 1 }">|</div>
      </template>
    </div>

    <div class="panel">
      <button class="send" @click="send">▸ send a request</button>
      <div class="hint bp-dim">Each layer owns one concern. A request flows through clear seams — and back — without any layer reaching into another.</div>
    </div>
  </div>
</template>

<style scoped>
.lf { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.8rem; align-items: center; font-family: "Fira Code", monospace; }
.stack { display: flex; flex-direction: column; align-items: stretch; }
.layer { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: .75rem 1.1rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.02); transition: all .3s ease; }
.layer .nm { color: var(--bp-ink); font-size: .95rem; } .layer .job { color: var(--bp-dim); font-size: .72rem; }
.layer.on { border-color: var(--bp-cyan); background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); transform: scale(1.03); }
.layer.on .nm { color: #fff; }
.seam { text-align: center; color: var(--bp-line); font-size: 1rem; line-height: 1.1; transition: color .3s; }
.seam.lit { color: var(--bp-cyan); }
.panel { display: flex; flex-direction: column; gap: 1rem; }
.send { font-family: inherit; font-size: .95rem; padding: .6rem 1.1rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 9px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); width: fit-content; }
.hint { font-size: .82rem; line-height: 1.5; }
</style>
