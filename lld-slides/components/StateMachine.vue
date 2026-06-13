<script setup lang="ts">
import { ref, computed } from 'vue'

const STATES = ['Idle', 'Playing', 'Paused', 'Stopped'] as const
type S = typeof STATES[number]
const TRANSITIONS: Record<S, { event: string; to: S }[]> = {
  Idle:    [{ event: 'play()', to: 'Playing' }],
  Playing: [{ event: 'pause()', to: 'Paused' }, { event: 'stop()', to: 'Stopped' }],
  Paused:  [{ event: 'resume()', to: 'Playing' }, { event: 'stop()', to: 'Stopped' }],
  Stopped: [{ event: 'reset()', to: 'Idle' }],
}
const POS: Record<S, { x: number; y: number }> = {
  Idle: { x: 50, y: 12 }, Playing: { x: 50, y: 40 }, Paused: { x: 14, y: 74 }, Stopped: { x: 78, y: 74 },
}

const current = ref<S>('Idle')
const log = ref<string[]>([])
const pulse = ref(false)

function fire(t: { event: string; to: S }) {
  log.value.unshift(`${current.value} --${t.event}--> ${t.to}`)
  if (log.value.length > 3) log.value.pop()
  current.value = t.to
  pulse.value = false; requestAnimationFrame(() => (pulse.value = true))
}
function reset() { current.value = 'Idle'; log.value = [] }
const options = computed(() => TRANSITIONS[current.value])
</script>

<template>
  <div class="sm">
    <div class="board">
      <svg class="wires" viewBox="0 0 100 90" preserveAspectRatio="none">
        <line x1="50" y1="20" x2="50" y2="38" /><line x1="46" y1="46" x2="18" y2="72" />
        <line x1="54" y1="46" x2="78" y2="72" /><line x1="20" y1="74" x2="74" y2="74" />
        <line x1="78" y1="68" x2="54" y2="20" />
      </svg>
      <div v-for="s in STATES" :key="s" class="node" :class="{ on: current === s, pulse: current === s && pulse }"
           :style="{ left: POS[s].x + '%', top: POS[s].y + '%' }">{{ s }}</div>
    </div>

    <div class="panel">
      <div class="now">state = <b>{{ current }}</b></div>
      <div class="events">
        <button v-for="t in options" :key="t.event" class="ev" @click="fire(t)">{{ t.event }}</button>
        <button class="ev ghost" @click="reset">reset()</button>
      </div>
      <div class="log">
        <div v-for="(l, i) in log" :key="i" class="ln">{{ l }}</div>
        <div v-if="!log.length" class="ln dim">click an event to transition…</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sm { display: grid; grid-template-columns: 1.3fr 1fr; gap: 1.5rem; align-items: center; font-family: "Fira Code", monospace; }
.board { position: relative; height: 330px; }
.wires { position: absolute; inset: 0; width: 100%; height: 100%; }
.wires line { stroke: var(--bp-line); stroke-width: .4; }
.node {
  position: absolute; transform: translate(-50%, -50%); padding: .5rem 1rem; border-radius: 9px;
  border: 1px solid var(--bp-line); background: rgba(255,255,255,.03); color: var(--bp-dim);
  font-size: .9rem; transition: all .4s ease; white-space: nowrap;
}
.node.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); transform: translate(-50%,-50%) scale(1.08); }
.node.pulse { animation: ring .6s ease; }
@keyframes ring { 0% { box-shadow: 0 0 0 0 rgba(34,211,238,.5); } 100% { box-shadow: 0 0 0 18px rgba(34,211,238,0); } }
.panel { display: flex; flex-direction: column; gap: .8rem; }
.now { font-size: 1rem; color: var(--bp-dim); } .now b { color: var(--bp-cyan); }
.events { display: flex; flex-wrap: wrap; gap: .5rem; }
.ev { font-family: inherit; font-size: .82rem; padding: .5rem .8rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); cursor: pointer; transition: .15s; }
.ev:hover { background: rgba(34,211,238,.18); }
.ev.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
.log { margin-top: .4rem; border-top: 1px dashed var(--bp-line); padding-top: .5rem; min-height: 4.6rem; display: flex; flex-direction: column; gap: 4px; }
.ln { font-size: .76rem; color: var(--bp-good); } .ln.dim { color: var(--bp-dim); }
</style>
