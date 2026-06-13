<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

// ---- model ----
const abstractions = [
  { name: 'Alert', prefix: 'ALERT: ' },
  { name: 'Receipt', prefix: 'RECEIPT: ' },
]
const baseImpls = [
  { name: 'Email', tag: 'email' },
  { name: 'SMS', tag: 'sms' },
]
const pushImpl = { name: 'Push', tag: 'push' }

const hasPush = ref(false)
const impls = computed(() => hasPush.value ? [...baseImpls, pushImpl] : [...baseImpls])

const absIdx = ref(0)
const implIdx = ref(1)            // start wired Alert -> SMS

// keep implIdx valid when Push toggles off
function clampImpl() {
  if (implIdx.value >= impls.value.length) implIdx.value = impls.value.length - 1
}

// ---- geometry (SVG 360 x 280 viewBox) ----
const LX = 150                    // right edge x of left column anchors
const RX = 210                    // left edge x of right column anchors
const rowY = (i: number, n: number) => {
  // two anchors share the same vertical midpoint as three anchors
  if (n <= 2) return 84 + i * 112  // -> 84, 196   (mid 140)
  return 56 + i * 84               // -> 56, 140, 224 (mid 140)
}
const leftAnchor = computed(() => ({ x: LX, y: rowY(absIdx.value, abstractions.length) }))
const rightAnchor = computed(() => ({ x: RX, y: rowY(implIdx.value, impls.value.length) }))

// ---- send / dot animation ----
const sending = ref(false)
const dotT = ref(0)               // 0..1 progress along the wire
const output = ref('')
let busy = false
let dotTimer: ReturnType<typeof setInterval> | null = null
let typeTimer: ReturnType<typeof setInterval> | null = null

const dotPos = computed(() => {
  const a = leftAnchor.value, b = rightAnchor.value
  return { x: a.x + (b.x - a.x) * dotT.value, y: a.y + (b.y - a.y) * dotT.value }
})

const delivered = computed(() => {
  const a = abstractions[absIdx.value]
  const im = impls.value[implIdx.value]
  return `[${im.tag}] ${a.prefix}disk full`
})

function clearTimers() {
  if (dotTimer) { clearInterval(dotTimer); dotTimer = null }
  if (typeTimer) { clearInterval(typeTimer); typeTimer = null }
}

function send() {
  if (busy) return
  busy = true
  sending.value = true
  output.value = ''
  dotT.value = 0
  // drive the dot in fixed steps (no timestamps, fully self-contained)
  let frame = 0
  const FRAMES = 16                 // ~400ms at 25ms
  dotTimer = setInterval(() => {
    frame++
    dotT.value = frame / FRAMES
    if (frame >= FRAMES) {
      clearTimers()
      dotT.value = 1
      typeOut()
    }
  }, 25)
}

function typeOut() {
  const full = delivered.value
  let i = 0
  typeTimer = setInterval(() => {
    i++
    output.value = full.slice(0, i)
    if (i >= full.length) {
      clearTimers()
      sending.value = false
      busy = false
    }
  }, 22)
}

// ---- rewire actions ----
function pickAbs(i: number) {
  if (busy) return
  absIdx.value = i
  output.value = ''
}
function pickImpl(i: number) {
  if (busy) return
  implIdx.value = i
  output.value = ''
}
function togglePush() {
  if (busy) return
  hasPush.value = !hasPush.value
  clampImpl()
  output.value = ''
}

// ---- counters ----
const M = computed(() => abstractions.length)
const N = computed(() => impls.value.length)
const bridgeCount = computed(() => M.value + N.value)
const naiveCount = computed(() => M.value * N.value)

// guard the timers against teardown mid-animation
onUnmounted(clearTimers)
</script>

<template>
  <div class="br">
    <!-- ===== STAGE ===== -->
    <div class="stage">
      <div class="grid">
        <!-- left axis -->
        <div class="col left">
          <div class="axis-label">Abstraction</div>
          <button
            v-for="(a, i) in abstractions" :key="a.name"
            class="node nabs"
            :class="{ sel: i === absIdx, dim: i !== absIdx }"
            @click="pickAbs(i)"
          >
            <span class="nname">{{ a.name }}</span>
            <span class="nrole">send()</span>
          </button>
        </div>

        <!-- connector -->
        <svg class="wire" viewBox="0 0 360 280" preserveAspectRatio="none">
          <line
            class="link" :class="{ hot: sending }"
            :x1="leftAnchor.x" :y1="leftAnchor.y"
            :x2="rightAnchor.x" :y2="rightAnchor.y"
          />
          <circle class="anc" :cx="leftAnchor.x" :cy="leftAnchor.y" r="4" />
          <circle class="anc" :cx="rightAnchor.x" :cy="rightAnchor.y" r="4" />
          <circle
            v-if="sending" class="dot"
            :cx="dotPos.x" :cy="dotPos.y" r="5"
          />
          <text class="wlabel" :x="180" :y="leftAnchor.y < rightAnchor.y ? 16 : 270">self.channel</text>
        </svg>

        <!-- right axis -->
        <div class="col right">
          <div class="axis-label">Implementor</div>
          <button
            v-for="(im, i) in impls" :key="im.name"
            class="node nimpl"
            :class="{ sel: i === implIdx, dim: i !== implIdx }"
            @click="pickImpl(i)"
          >
            <span class="nname">{{ im.name }}</span>
            <span class="nrole">deliver()</span>
          </button>
        </div>
      </div>

      <!-- output strip -->
      <div class="out" :class="{ live: sending || output }">
        <span class="caret">▸</span>
        <span class="otext">{{ output || 'press Send to deliver through the wired channel' }}</span>
        <span v-if="sending" class="cur">_</span>
      </div>
    </div>

    <!-- ===== CONTROLS ===== -->
    <div class="panel">
      <button class="b send" :disabled="busy" @click="send">▶ Send</button>

      <div class="wiring">
        <span class="wnode">{{ abstractions[absIdx].name }}</span>
        <span class="warrow">→</span>
        <span class="wnode imp">{{ impls[implIdx].name }}</span>
        <span class="whint">click a box to rewire</span>
      </div>

      <label class="tog" :class="{ on: hasPush }" @click="togglePush">
        <span class="knob" /> add Push?
      </label>

      <div class="counters">
        <div class="cline good">
          <span class="clab">classes written</span>
          <b>{{ M }} + {{ N }} = {{ bridgeCount }}</b>
        </div>
        <div class="cline strike">
          <span class="clab">naive subclasses</span>
          <s>{{ M }} × {{ N }} = {{ naiveCount }}</s>
        </div>
      </div>

      <ul class="kpts bp-dim text-sm">
        <li>One swappable reference joins two independent axes</li>
        <li>Rewiring moves the live bridge — no class is recreated</li>
        <li>M + N classes, not M × N: watch the gap when Push joins</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.br {
  display: grid;
  grid-template-columns: 1.55fr 1fr;
  gap: 1.5rem;
  width: 100%;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---- stage ---- */
.stage { display: flex; flex-direction: column; gap: .7rem; min-width: 0; }
.grid {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 360px 1fr;
  align-items: stretch;
  height: 280px;
  overflow: hidden;
}
.col { display: flex; flex-direction: column; gap: 1.1rem; justify-content: center; min-width: 0; }
.col.right { align-items: flex-end; }
.axis-label { position: absolute; top: 0; font-size: .6rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-dim); }
.col.right .axis-label { right: 0; }

.node {
  font-family: inherit; position: relative;
  display: flex; flex-direction: column; gap: .15rem; align-items: flex-start;
  width: 138px; max-width: 100%; padding: .5rem .65rem;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(255,255,255,.03); color: var(--bp-ink);
  cursor: pointer; transition: all .25s;
}
.col.right .node { align-items: flex-end; }
.node .nname { font-size: .82rem; color: #fff; }
.node .nrole { font-size: .58rem; color: var(--bp-dim); }
.node.nabs.sel { border-color: var(--bp-violet); box-shadow: 0 0 18px rgba(167,139,250,.35); background: rgba(167,139,250,.1); }
.node.nimpl.sel { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); background: rgba(34,211,238,.1); }
.node.dim { opacity: .4; }
.node:hover { opacity: 1; }

/* ---- wire (SVG) ---- */
.wire {
  position: absolute; left: 50%; top: 0; transform: translateX(-50%);
  width: 360px; height: 280px; pointer-events: none; overflow: visible;
}
.link { stroke: var(--bp-line); stroke-width: 2; transition: x1 .25s ease, y1 .25s ease, x2 .25s ease, y2 .25s ease, stroke .2s, stroke-width .2s; }
.link.hot { stroke: var(--bp-cyan); stroke-width: 4; filter: drop-shadow(0 0 6px rgba(34,211,238,.6)); }
.anc { fill: var(--bp-cyan); transition: cx .25s ease, cy .25s ease; }
.dot { fill: #fff; filter: drop-shadow(0 0 8px rgba(34,211,238,.9)); }
.wlabel { fill: var(--bp-dim); font-family: "Fira Code", monospace; font-size: 9px; text-anchor: middle; }

/* ---- output strip ---- */
.out {
  display: flex; align-items: center; gap: .5rem;
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02); padding: .5rem .7rem;
  font-size: .78rem; color: var(--bp-dim); min-height: 38px; transition: all .25s;
}
.out.live { border-color: var(--bp-cyan); color: #fff; box-shadow: var(--bp-glow); }
.out .caret { color: var(--bp-cyan); }
.out .otext { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.out .cur { color: var(--bp-cyan); animation: blink .8s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .75rem; align-items: flex-start; min-width: 0; }
.b { font-family: inherit; font-size: .82rem; padding: .45rem .95rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }

.wiring { display: flex; align-items: center; gap: .45rem; font-size: .76rem; flex-wrap: wrap; }
.wnode { color: var(--bp-violet); border: 1px solid rgba(167,139,250,.4); border-radius: 6px; padding: .1rem .45rem; }
.wnode.imp { color: var(--bp-cyan); border-color: rgba(34,211,238,.4); }
.warrow { color: var(--bp-dim); }
.whint { font-size: .6rem; color: var(--bp-dim); width: 100%; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .76rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(34,211,238,.4); }
.tog.on .knob::after { left: 16px; background: var(--bp-cyan); }
.tog.on { color: var(--bp-cyan); }

.counters { display: flex; flex-direction: column; gap: .3rem; border: 1px solid var(--bp-line); border-radius: 9px; padding: .55rem .7rem; width: 100%; }
.cline { display: flex; justify-content: space-between; align-items: baseline; gap: .8rem; font-size: .74rem; }
.cline .clab { color: var(--bp-dim); font-size: .64rem; }
.cline.good b { color: var(--bp-good); }
.cline.strike s { color: var(--bp-dim); opacity: .65; }

.kpts { list-style: none; padding: 0; margin: .15rem 0 0; }
.kpts li { position: relative; padding-left: 1.05rem; margin: .3rem 0; font-size: .68rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
.kpts b { color: var(--bp-ink); }
</style>
