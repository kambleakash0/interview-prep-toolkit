<script setup lang="ts">
import { ref, computed } from 'vue'

type DState = 'idle' | 'sending' | 'lit' | 'received' | 'delivered'

const CX = 175
const CY = 150
const R = 120

const count = ref(5)
const mode = ref<'mesh' | 'mediator'>('mesh')
const states = ref<DState[]>(Array(8).fill('idle'))
const hubState = ref<'idle' | 'routing'>('idle')
const hubIn = ref(false)        // hub faded in (mediator mode)
const chordsHidden = ref(false) // chords shrunk during transition
let busy = false

// active pulse list: each pulse renders a travelling dot
type Pulse = { id: number; x1: number; y1: number; x2: number; y2: number; cls: string }
const pulses = ref<Pulse[]>([])
let pid = 0

const nodes = computed(() => {
  const arr: { x: number; y: number; i: number }[] = []
  const n = count.value
  for (let i = 0; i < n; i++) {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n
    arr.push({ x: CX + R * Math.cos(a), y: CY + R * Math.sin(a), i })
  }
  return arr
})

// all C(n,2) chords
const chords = computed(() => {
  const out: { a: number; b: number; x1: number; y1: number; x2: number; y2: number }[] = []
  const ns = nodes.value
  for (let i = 0; i < ns.length; i++)
    for (let j = i + 1; j < ns.length; j++)
      out.push({ a: i, b: j, x1: ns[i].x, y1: ns[i].y, x2: ns[j].x, y2: ns[j].y })
  return out
})

const meshEdges = computed(() => (count.value * (count.value - 1)) / 2)
const starEdges = computed(() => count.value)
const saved = computed(() => meshEdges.value - starEdges.value)

function setState(i: number, s: DState, ms: number) {
  states.value[i] = s
  window.setTimeout(() => { if (states.value[i] === s) states.value[i] = 'idle' }, ms)
}

function spawnPulse(x1: number, y1: number, x2: number, y2: number, cls: string, ms: number) {
  const id = ++pid
  pulses.value.push({ id, x1, y1, x2, y2, cls })
  window.setTimeout(() => { pulses.value = pulses.value.filter(p => p.id !== id) }, ms)
}

// ---- MESH: clicking a node broadcasts along all direct chords ----
function clickNode(i: number) {
  if (busy) return
  if (mode.value === 'mesh') meshSend(i)
  else mediatorSend(i)
}

function meshSend(i: number) {
  busy = true
  states.value[i] = 'sending'
  const src = nodes.value[i]
  nodes.value.forEach((tgt) => {
    if (tgt.i === i) return
    spawnPulse(src.x, src.y, tgt.x, tgt.y, 'mesh', 520)
  })
  window.setTimeout(() => {
    nodes.value.forEach((tgt) => { if (tgt.i !== i) setState(tgt.i, 'lit', 400) })
    states.value[i] = 'idle'
    busy = false
  }, 520)
}

// ---- MEDIATOR: explicit 3-step route to chosen neighbours ----
function mediatorSend(i: number) {
  busy = true
  const n = count.value
  const src = nodes.value[i]
  // step 1: RECEIVED — pulse inward to hub
  states.value[i] = 'received'
  spawnPulse(src.x, src.y, CX, CY, 'in', 460)
  window.setTimeout(() => {
    // step 2: ROUTING — hub highlights
    hubState.value = 'routing'
    window.setTimeout(() => {
      // step 3: DELIVERED — hub emits to selected targets (two neighbours)
      hubState.value = 'idle'
      const targets = [(i + 1) % n, (i - 1 + n) % n]
      states.value[i] = 'idle'
      targets.forEach((t) => {
        const tgt = nodes.value[t]
        spawnPulse(CX, CY, tgt.x, tgt.y, 'out', 460)
      })
      window.setTimeout(() => {
        targets.forEach((t) => setState(t, 'delivered', 400))
        busy = false
      }, 460)
    }, 300)
  }, 460)
}

// ---- toggle MESH <-> MEDIATOR with chord shrink then hub fade-in ----
function setMode(m: 'mesh' | 'mediator') {
  if (busy || m === mode.value) return
  if (m === 'mediator') {
    busy = true
    chordsHidden.value = true        // shrink all chords to zero
    window.setTimeout(() => {
      mode.value = 'mediator'
      hubIn.value = true             // hub fades + scales in, spokes draw
      window.setTimeout(() => { busy = false }, 320)
    }, 320)
  } else {
    busy = true
    hubIn.value = false
    window.setTimeout(() => {
      mode.value = 'mesh'
      chordsHidden.value = false
      window.setTimeout(() => { busy = false }, 320)
    }, 200)
  }
}

function addDevice() {
  if (busy || count.value >= 8) return
  count.value++
}

function reset() {
  if (busy) return
  count.value = 5
  states.value = Array(8).fill('idle')
  hubState.value = 'idle'
  mode.value = 'mesh'
  hubIn.value = false
  chordsHidden.value = false
  pulses.value = []
}
</script>

<template>
  <div class="md">
    <!-- ===== STAGE ===== -->
    <div class="stage">
      <div class="topbar">
        <div class="seg">
          <button :class="{ on: mode === 'mesh' }" @click="setMode('mesh')">MESH</button>
          <button :class="{ on: mode === 'mediator' }" @click="setMode('mediator')">MEDIATOR</button>
        </div>
        <span class="hint">click a node to send</span>
      </div>

      <svg class="net" viewBox="0 0 350 300" preserveAspectRatio="xMidYMid meet">
        <!-- mesh chords -->
        <g class="chords" :class="{ gone: chordsHidden || mode === 'mediator' }">
          <line
            v-for="c in chords" :key="'c' + c.a + '-' + c.b"
            :x1="c.x1" :y1="c.y1" :x2="c.x2" :y2="c.y2"
            class="chord"
          />
        </g>

        <!-- mediator spokes -->
        <g class="spokes" :class="{ show: mode === 'mediator' && hubIn }">
          <line
            v-for="nd in nodes" :key="'s' + nd.i"
            :x1="CX" :y1="CY" :x2="nd.x" :y2="nd.y"
            class="spoke"
          />
        </g>

        <!-- travelling pulses -->
        <circle
          v-for="p in pulses" :key="p.id"
          class="pulse" :class="p.cls" r="4"
        >
          <animate attributeName="cx" :from="p.x1" :to="p.x2" dur="0.45s" fill="freeze" />
          <animate attributeName="cy" :from="p.y1" :to="p.y2" dur="0.45s" fill="freeze" />
        </circle>

        <!-- hub -->
        <g v-if="mode === 'mediator'" class="hub" :class="{ in: hubIn, routing: hubState === 'routing' }">
          <circle :cx="CX" :cy="CY" r="22" class="hub-ring" />
          <circle :cx="CX" :cy="CY" r="14" class="hub-core" />
          <text :x="CX" :y="CY + 3.5" class="hub-tx">HUB</text>
        </g>

        <!-- device nodes -->
        <g
          v-for="nd in nodes" :key="'n' + nd.i"
          class="node" :class="states[nd.i]"
          @click="clickNode(nd.i)"
        >
          <circle :cx="nd.x" :cy="nd.y" r="15" class="ndot" />
          <text :x="nd.x" :y="nd.y + 3" class="ntx">D{{ nd.i + 1 }}</text>
        </g>
      </svg>
    </div>

    <!-- ===== CONTROLS ===== -->
    <div class="panel">
      <div class="metric main">
        <span class="mlabel">{{ mode === 'mesh' ? 'mesh edges' : 'star spokes' }}</span>
        <b class="mval">{{ mode === 'mesh' ? meshEdges : starEdges }}</b>
      </div>

      <div class="grid">
        <div class="cell mesh">
          <span>mesh n(n-1)/2</span><b>{{ meshEdges }}</b>
        </div>
        <div class="cell star">
          <span>star n</span><b>{{ starEdges }}</b>
        </div>
        <div class="cell save">
          <span>saved = mesh - star</span><b>{{ saved }}</b>
        </div>
      </div>

      <div class="btns">
        <button class="b" :disabled="count >= 8 || busy" @click="addDevice">+ add device</button>
        <button class="b ghost" :disabled="busy" @click="reset">◀ reset</button>
      </div>

      <div class="state-readout">
        nodes <b>{{ count }}</b>
        <span class="sep">·</span>
        mode <b>{{ mode }}</b>
      </div>

      <ul class="kpts bp-dim">
        <li>Mesh links every pair: edges explode as n grows</li>
        <li>Mediator routes through one hub: just n spokes</li>
        <li>Add a device — mesh leaps, the star adds one line</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.md {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.4rem;
  font-family: "Fira Code", monospace;
  height: 340px;
}

/* ---- stage ---- */
.stage { display: flex; flex-direction: column; gap: .4rem; min-width: 0; }
.topbar { display: flex; align-items: center; gap: .8rem; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg button {
  font-family: inherit; font-size: .72rem; padding: .35rem .9rem;
  background: transparent; color: var(--bp-dim); cursor: pointer; transition: all .25s;
  border: none;
}
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.hint { font-size: .62rem; color: var(--bp-dim); letter-spacing: .04em; }

.net { width: 100%; flex: 1; min-height: 0; }

/* ---- chords (mesh) ---- */
.chords { transition: opacity .3s ease; }
.chords.gone { opacity: 0; }
.chord {
  stroke: var(--bp-line); stroke-width: 1.1;
  stroke-dasharray: 3 3;
  transition: stroke .3s;
}

/* ---- spokes (mediator) ---- */
.spokes { opacity: 0; transition: opacity .35s ease .05s; }
.spokes.show { opacity: 1; }
.spoke {
  stroke: rgba(34,211,238,.45); stroke-width: 1.4;
  stroke-dasharray: 200; stroke-dashoffset: 200;
}
.spokes.show .spoke { animation: draw .4s ease forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }

/* ---- pulses ---- */
.pulse { filter: drop-shadow(0 0 4px var(--bp-cyan)); }
.pulse.mesh { fill: var(--bp-blue); }
.pulse.in { fill: var(--bp-violet); }
.pulse.out { fill: var(--bp-cyan); }

/* ---- hub ---- */
.hub { transform-box: fill-box; transform-origin: center; }
.hub-ring {
  fill: none; stroke: var(--bp-line); stroke-width: 1.2;
  opacity: 0; transition: opacity .35s ease .1s;
}
.hub-core {
  fill: rgba(34,211,238,.12); stroke: var(--bp-cyan); stroke-width: 1.6;
  transform-box: fill-box; transform-origin: center;
  transform: scale(0); opacity: 0; transition: all .35s ease;
}
.hub-tx {
  fill: var(--bp-cyan); font-size: 8px; font-family: "Fira Code", monospace;
  text-anchor: middle; letter-spacing: .06em; opacity: 0; transition: opacity .3s ease .15s;
}
.hub.in .hub-core { transform: scale(1); opacity: 1; }
.hub.in .hub-ring { opacity: 1; }
.hub.in .hub-tx { opacity: 1; }
.hub.routing .hub-core {
  fill: rgba(34,211,238,.35);
  filter: drop-shadow(0 0 10px var(--bp-cyan));
  animation: hubpulse .3s ease;
}
.hub.routing .hub-ring { stroke: var(--bp-cyan); }
@keyframes hubpulse {
  0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); }
}

/* ---- device nodes ---- */
.node { cursor: pointer; }
.ndot {
  fill: var(--bp-bg-2); stroke: var(--bp-blue); stroke-width: 1.6;
  transform-box: fill-box; transform-origin: center; transition: all .3s;
}
.ntx {
  fill: var(--bp-ink); font-size: 8px; font-family: "Fira Code", monospace;
  text-anchor: middle; pointer-events: none; transition: fill .3s;
}
.node:hover .ndot { stroke: var(--bp-cyan); filter: drop-shadow(0 0 5px rgba(34,211,238,.5)); }

.node.sending .ndot {
  transform: scale(1.35); stroke: var(--bp-cyan); fill: rgba(34,211,238,.2);
  filter: drop-shadow(0 0 10px var(--bp-cyan));
}
.node.sending .ntx { fill: var(--bp-cyan); }

.node.lit .ndot {
  stroke: var(--bp-warn); fill: rgba(251,191,36,.18);
  filter: drop-shadow(0 0 8px var(--bp-warn));
}
.node.lit .ntx { fill: var(--bp-warn); }

.node.received .ndot {
  transform: scale(1.25); stroke: var(--bp-violet); fill: rgba(167,139,250,.2);
  filter: drop-shadow(0 0 9px var(--bp-violet));
}
.node.received .ntx { fill: var(--bp-violet); }

.node.delivered .ndot {
  stroke: var(--bp-good); fill: rgba(74,222,128,.18);
  filter: drop-shadow(0 0 8px var(--bp-good));
}
.node.delivered .ntx { fill: var(--bp-good); }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .55rem; align-items: stretch; min-width: 0; }
.metric.main {
  display: flex; align-items: baseline; justify-content: space-between;
  border: 1px solid var(--bp-cyan); border-radius: 10px; padding: .45rem .75rem;
  background: rgba(34,211,238,.08); box-shadow: var(--bp-glow);
}
.mlabel { font-size: .66rem; color: var(--bp-dim); text-transform: uppercase; letter-spacing: .06em; }
.mval { font-size: 1.5rem; color: var(--bp-cyan); line-height: 1; }

.grid { display: flex; flex-direction: column; gap: .35rem; }
.cell {
  display: flex; align-items: center; justify-content: space-between;
  font-size: .68rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 7px; padding: .3rem .6rem;
  transition: all .3s;
}
.cell b { font-size: .9rem; }
.cell.mesh b { color: var(--bp-bad); }
.cell.star b { color: var(--bp-good); }
.cell.save { border-color: rgba(167,139,250,.3); background: rgba(167,139,250,.06); }
.cell.save b { color: var(--bp-violet); }

.btns { display: flex; gap: .45rem; }
.b {
  flex: 1; font-family: inherit; font-size: .72rem; padding: .42rem .5rem;
  border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px;
  background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow);
  transition: all .2s;
}
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.b:disabled { opacity: .35; cursor: not-allowed; box-shadow: none; }

.state-readout {
  font-size: .66rem; color: var(--bp-dim); letter-spacing: .04em;
  border-top: 1px solid var(--bp-line); padding-top: .4rem;
}
.state-readout b { color: var(--bp-cyan); }
.state-readout .sep { margin: 0 .5rem; opacity: .5; }

.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1rem; margin: .22rem 0; line-height: 1.35; font-size: .66rem; }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
