<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Phase = 'input' | 'update' | 'render'

const phase = ref<Phase>('input')      // which node the token sits on
const playing = ref(false)
const frames = ref(0)
const updates = ref(0)
const fixed = ref(false)                // fixed-timestep toggle
const catchUp = ref(false)              // 'catch-up' badge during the slow frame
const pendingUpdates = ref(0)           // extra updates queued before render (fixed mode)

// entity on the track: position 0..9, bouncing
const x = ref(0)
const dir = ref(1)
let busy = false
let timer: ReturnType<typeof setTimeout> | null = null

const TICK = 360                        // ms per phase node (kept visible)

// --- three nodes laid out on a board in percent coordinates ---
const NODES: Record<Phase, { x: number; y: number; label: string; sub: string }> = {
  input:  { x: 22, y: 34, label: 'process_input', sub: 'read keys' },
  update: { x: 78, y: 34, label: 'update(dt)',     sub: 'advance world' },
  render: { x: 50, y: 78, label: 'render',          sub: 'draw frame' },
}
// wires: input -> update -> render -> input (the cycle)
const EDGES: [Phase, Phase][] = [['input', 'update'], ['update', 'render'], ['render', 'input']]

function edgeHot(from: Phase): boolean {
  return playing.value && phase.value === from
}

const cells = Array.from({ length: 10 }, (_, i) => i)

function stepEntity() {
  let nx = x.value + dir.value
  if (nx > 9) { nx = 8; dir.value = -1 }
  else if (nx < 0) { nx = 1; dir.value = 1 }
  x.value = nx
}

function clearTimer() { if (timer) { clearTimeout(timer); timer = null } }

// Advance the token through one full tick: input -> [update(s)] -> render.
// In fixed mode a "slow frame" queues a second update (catch-up) before render.
function runTick(auto: boolean) {
  if (busy) return
  busy = true

  // INPUT phase
  phase.value = 'input'
  catchUp.value = false
  pendingUpdates.value = fixed.value ? 2 : 1

  timer = setTimeout(() => {
    doUpdatePhase(auto)
  }, TICK)
}

function doUpdatePhase(auto: boolean) {
  phase.value = 'update'
  updates.value++
  stepEntity()
  pendingUpdates.value--

  if (pendingUpdates.value > 0) {
    // fixed timestep: a second update node fires before render (catch-up)
    catchUp.value = true
    timer = setTimeout(() => {
      phase.value = 'update'
      updates.value++
      stepEntity()
      pendingUpdates.value--
      timer = setTimeout(() => doRenderPhase(auto), TICK)
    }, TICK)
  } else {
    timer = setTimeout(() => doRenderPhase(auto), TICK)
  }
}

function doRenderPhase(auto: boolean) {
  phase.value = 'render'
  frames.value++

  timer = setTimeout(() => {
    phase.value = 'input'
    catchUp.value = false
    busy = false
    if (auto && playing.value) runTick(true)
  }, TICK)
}

function play() {
  if (playing.value) return
  playing.value = true
  if (!busy) runTick(true)
}

function pause() {
  playing.value = false
  // let the in-flight tick finish naturally; just stop re-arming
}

function step() {
  if (playing.value || busy) return
  runTick(false)
}

function reset() {
  playing.value = false
  clearTimer()
  busy = false
  phase.value = 'input'
  frames.value = 0
  updates.value = 0
  catchUp.value = false
  pendingUpdates.value = 0
  x.value = 0
  dir.value = 1
}

function toggleFixed() {
  if (busy) return
  fixed.value = !fixed.value
}

const ratio = computed(() =>
  frames.value === 0 ? '—' : (updates.value / frames.value).toFixed(2))

onUnmounted(clearTimer)
</script>

<template>
  <div class="gl">
    <!-- stage: play field (left) + three-phase cycle (right of it) -->
    <div class="stage">
      <div class="field">
        <div class="flabel">play field · entity steps on every update</div>
        <div class="track">
          <span v-for="c in cells" :key="c" class="cell" :class="{ here: c === x }" />
          <span class="dot" :style="{ left: (x * 10 + 5) + '%' }"
                :class="{ bounce: phase === 'update' }" />
        </div>
        <div class="trow">
          <span class="rd">frames <b>{{ frames }}</b></span>
          <span class="rd">updates <b class="u">{{ updates }}</b></span>
          <span class="rd">upd/frame <b :class="{ u: ratio !== '1.00' && ratio !== '—' }">{{ ratio }}</b></span>
        </div>
      </div>

      <div class="board">
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <marker id="ah" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="var(--bp-line)" />
            </marker>
          </defs>
          <line v-for="([a, b], i) in EDGES" :key="i"
                :x1="NODES[a].x" :y1="NODES[a].y" :x2="NODES[b].x" :y2="NODES[b].y"
                class="wire" :class="{ hot: edgeHot(a) }" marker-end="url(#ah)" />
        </svg>

        <div v-for="(k, key) in NODES" :key="key" class="node" :class="[key, { live: phase === key }]"
             :style="{ left: k.x + '%', top: k.y + '%' }">
          <span class="nt">{{ k.label }}</span>
          <span class="ns">{{ k.sub }}</span>
        </div>

        <transition name="pop">
          <span v-if="catchUp" class="catch"
                :style="{ left: NODES.update.x + '%', top: (NODES.update.y + 22) + '%' }">
            catch-up ×2
          </span>
        </transition>

        <span class="loopmark">while running ↻</span>
      </div>
    </div>

    <!-- controls -->
    <div class="panel">
      <div class="btns">
        <button class="b" :class="{ on: playing }" @click="play">▶ Play</button>
        <button class="b ghost" @click="pause">▮▮ Pause</button>
      </div>
      <div class="btns">
        <button class="b ghost" :disabled="playing" @click="step">▸ Step</button>
        <button class="b ghost" @click="reset">↻ Reset</button>
      </div>

      <label class="tog" :class="{ on: fixed }" @click="toggleFixed">
        <span class="knob" /> fixed timestep
      </label>
      <div class="hint" :class="{ act: fixed }">
        <template v-if="fixed">slow frame → 2 updates, 1 render · time-based</template>
        <template v-else>1 update per render · frame-coupled</template>
      </div>

      <ul class="kpts">
        <li>One loop: input → update(dt) → render, forever</li>
        <li>Update by elapsed time, not by frame count</li>
        <li>Fixed step adds catch-up updates so play stays stable</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.gl { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }

.stage { display: grid; grid-template-rows: auto 1fr; gap: .8rem; min-width: 0; min-height: 0; }

/* ---- play field ---- */
.field { display: flex; flex-direction: column; gap: .5rem; padding: .7rem .8rem; border: 1px solid var(--bp-line); border-radius: 11px; background: rgba(255,255,255,.02); }
.flabel { font-size: .58rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }
.track { position: relative; display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; height: 30px; }
.cell { border: 1px solid var(--bp-line); border-radius: 4px; background: rgba(56,189,248,.03); transition: all .25s; }
.cell.here { border-color: var(--bp-cyan); background: rgba(34,211,238,.12); }
.dot { position: absolute; top: 50%; width: 16px; height: 16px; border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow); transform: translate(-50%, -50%); transition: left .3s cubic-bezier(.5,1.6,.5,1); }
.dot.bounce { animation: pulse .3s ease; }
@keyframes pulse { 50% { transform: translate(-50%, -50%) scale(1.35); } }
.trow { display: flex; gap: 1rem; }
.rd { font-size: .68rem; color: var(--bp-dim); }
.rd b { color: var(--bp-cyan); font-size: .9rem; margin-left: .25rem; }
.rd b.u { color: var(--bp-warn); }

/* ---- cycle board ---- */
.board { position: relative; width: 100%; min-height: 0; overflow: visible; padding: 0 18% 14px; box-sizing: border-box; }
.wires { position: absolute; inset: 0 18% 14px; width: auto; height: auto; }
.wire { stroke: var(--bp-line); stroke-width: .6; transition: stroke .3s, stroke-width .3s; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: 1.1; filter: drop-shadow(0 0 3px var(--bp-cyan)); }

.node { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; gap: .08rem; padding: .38rem .6rem; border-radius: 9px; border: 1px solid var(--bp-line); background: rgba(11,19,36,.94); white-space: nowrap; transition: all .25s; z-index: 1; }
.node .nt { font-size: .74rem; color: var(--bp-ink); }
.node .ns { font-size: .54rem; color: var(--bp-dim); }
.node.input  { border-color: var(--bp-violet); }
.node.update { border-color: var(--bp-blue); }
.node.render { border-color: var(--bp-line); }
.node.live { box-shadow: var(--bp-glow); border-color: var(--bp-cyan); z-index: 2; }
.node.live .nt { color: #fff; }
.node.update.live .ns { color: var(--bp-warn); }

.catch { position: absolute; transform: translate(-50%, -50%); font-size: .55rem; color: var(--bp-warn); border: 1px solid var(--bp-warn); border-radius: 999px; padding: .08rem .45rem; background: var(--bp-bg); white-space: nowrap; z-index: 3; }

.loopmark { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-size: .58rem; color: var(--bp-dim); letter-spacing: .06em; pointer-events: none; }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .7rem; min-width: 0; }
.btns { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .76rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); flex: 1; }
.b.on { background: rgba(34,211,238,.28); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.b:disabled { opacity: .4; cursor: not-allowed; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; color: var(--bp-dim); cursor: pointer; user-select: none; width: fit-content; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex-shrink: 0; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(251,191,36,.4); } .tog.on .knob::after { left: 16px; background: var(--bp-warn); }
.tog.on { color: var(--bp-warn); }

.hint { font-size: .62rem; color: var(--bp-dim); padding: .4rem .6rem; border: 1px solid var(--bp-line); border-radius: 8px; }
.hint.act { color: var(--bp-warn); border-color: rgba(251,191,36,.3); background: rgba(251,191,36,.05); }

.kpts { list-style: none; padding: 0; margin: .1rem 0 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .26rem 0; font-size: .72rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }

.pop-enter-active, .pop-leave-active { transition: all .25s; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translate(-50%, -50%) scale(.6); }
</style>
