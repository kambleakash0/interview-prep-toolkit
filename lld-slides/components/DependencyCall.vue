<script setup lang="ts">
import { ref } from 'vue'

// phases: idle -> incoming -> using -> gone
const phase = ref<'idle' | 'incoming' | 'using' | 'gone'>('idle')
let running = false

function call() {
  if (running) return
  running = true
  phase.value = 'incoming'
  setTimeout(() => (phase.value = 'using'), 600)
  setTimeout(() => (phase.value = 'gone'), 1300)
  setTimeout(() => { phase.value = 'idle'; running = false }, 2100)
}
</script>

<template>
  <div class="dc">
    <div class="stage">
      <!-- transient Document token -->
      <div class="doc" :class="phase">Document("Hello")</div>

      <!-- the Printer keeps no reference -->
      <div class="printer" :class="{ active: phase === 'using' }">
        <span class="lbl">Printer</span>
        <span class="sig">print(doc)</span>
        <span class="store bp-dim">no stored field</span>
      </div>
    </div>

    <div class="ctl">
      <button class="b" @click="call">Printer().print(doc)</button>
    </div>
    <div class="trace">
      <span :class="{ lit: phase === 'incoming' }">passed in</span>
      <span class="sep">▸</span>
      <span :class="{ lit: phase === 'using' }">used</span>
      <span class="sep">▸</span>
      <span :class="{ lit: phase === 'gone' }">gone</span>
    </div>
    <div class="cap bp-dim bp-mono">dashed arrow — the link lives only during the call</div>
  </div>
</template>

<style scoped>
.dc { font-family: "Fira Code", monospace; display: flex; flex-direction: column; gap: 1rem; }
.stage { position: relative; height: 130px; display: flex; align-items: center; justify-content: flex-end; }
.doc { position: absolute; left: 0; top: 50%; transform: translateY(-50%); padding: .4rem .7rem; border: 1px dashed var(--bp-violet); border-radius: 8px; color: var(--bp-violet); background: rgba(167,139,250,.08); font-size: .72rem; opacity: 0; transition: all .55s ease; }
.doc.incoming { opacity: 1; left: 0; }
.doc.using { opacity: 1; left: 42%; }
.doc.gone { opacity: 0; left: 42%; transform: translateY(-50%) scale(.6); }
.printer { display: flex; flex-direction: column; gap: .25rem; padding: .8rem 1rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.03); transition: all .3s; }
.printer.active { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.printer .lbl { color: #fff; font-size: .9rem; }
.printer .sig { color: var(--bp-cyan); font-size: .72rem; }
.printer .store { font-size: .62rem; }
.ctl { margin-top: -.2rem; }
.b { font-family: inherit; font-size: .8rem; padding: .45rem .9rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.trace { display: flex; align-items: center; gap: .6rem; font-size: .74rem; color: var(--bp-dim); }
.trace .lit { color: var(--bp-cyan); text-shadow: 0 0 8px rgba(34,211,238,.5); }
.trace .sep { color: var(--bp-line); }
.cap { font-size: .7rem; }
</style>
