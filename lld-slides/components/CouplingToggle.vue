<script setup lang="ts">
import { ref } from 'vue'
const loose = ref(false)
// node centers in % of the board
const A = { x: 18, y: 22 }, B = { x: 82, y: 22 }, C = { x: 50, y: 86 }, I = { x: 50, y: 52 }
</script>

<template>
  <div class="cp">
    <div class="board">
      <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
        <!-- tight: everything wired to everything -->
        <g :class="{ hide: loose }" class="bad">
          <line :x1="A.x" :y1="A.y" :x2="B.x" :y2="B.y" />
          <line :x1="B.x" :y1="B.y" :x2="C.x" :y2="C.y" />
          <line :x1="A.x" :y1="A.y" :x2="C.x" :y2="C.y" />
        </g>
        <!-- loose: each module wired only to the seam -->
        <g :class="{ hide: !loose }" class="ok">
          <line :x1="A.x" :y1="A.y" :x2="I.x" :y2="I.y" />
          <line :x1="B.x" :y1="B.y" :x2="I.x" :y2="I.y" />
          <line :x1="C.x" :y1="C.y" :x2="I.x" :y2="I.y" />
        </g>
      </svg>
      <div class="mod" :style="{ left: A.x + '%', top: A.y + '%' }">Orders</div>
      <div class="mod" :style="{ left: B.x + '%', top: B.y + '%' }">Billing</div>
      <div class="mod" :style="{ left: C.x + '%', top: C.y + '%' }">Shipping</div>
      <div class="seam" :class="{ show: loose }" :style="{ left: I.x + '%', top: I.y + '%' }">«interface»</div>
    </div>

    <div class="panel">
      <div class="ctl">
        <button :class="{ on: !loose }" @click="loose = false">Tight</button>
        <button :class="{ on: loose }"  @click="loose = true">Loose</button>
      </div>
      <div class="note" :class="loose ? 'ok' : 'bad'">
        <b v-if="!loose">High coupling.</b><b v-else>Low coupling.</b>
        {{ loose
          ? 'Each module knows only the shared contract — change one without breaking the others.'
          : 'Every module wired directly to every other — one change ripples everywhere.' }}
      </div>
      <div class="cohesion bp-dim">Pair it with <b style="color:var(--bp-ink)">high cohesion</b>: each module keeps one job inside.</div>
    </div>
  </div>
</template>

<style scoped>
.cp { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.8rem; align-items: center; font-family: "Fira Code", monospace; }
.board { position: relative; height: 320px; }
.wires { position: absolute; inset: 0; width: 100%; height: 100%; }
.wires line { stroke-width: .6; transition: opacity .4s; }
.wires .bad line { stroke: var(--bp-bad); }
.wires .ok line { stroke: var(--bp-cyan); }
.wires .hide { opacity: 0; }
.mod { position: absolute; transform: translate(-50%, -50%); padding: .5rem .9rem; border-radius: 9px; border: 1px solid var(--bp-line); background: rgba(255,255,255,.03); color: var(--bp-ink); font-size: .85rem; white-space: nowrap; }
.seam { position: absolute; transform: translate(-50%, -50%); padding: .45rem .8rem; border-radius: 999px; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.1); font-size: .78rem; opacity: 0; transition: opacity .4s; box-shadow: var(--bp-glow); }
.seam.show { opacity: 1; }
.panel { display: flex; flex-direction: column; gap: 1rem; }
.ctl { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; width: fit-content; }
.ctl button { font-family: inherit; font-size: .82rem; padding: .45rem 1.1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.ctl button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.note { font-size: .88rem; line-height: 1.5; padding: .7rem .9rem; border-radius: 9px; border: 1px solid var(--bp-line); color: var(--bp-dim); }
.note b { color: #fff; }
.note.ok { border-color: rgba(34,211,238,.3); } .note.bad { border-color: rgba(251,113,133,.3); }
.cohesion { font-size: .8rem; }
</style>
