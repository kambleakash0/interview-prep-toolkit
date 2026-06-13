<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

type Card = { name: string; limit: number }
type CState = 'idle' | 'checking' | 'handled' | 'forward'

// base order; reorder swaps Director and VP
const baseOrder: Card[] = [
  { name: 'Lead', limit: 1000 },
  { name: 'Director', limit: 10000 },
  { name: 'VP', limit: 100000 },
]
const swapped: Card[] = [baseOrder[0], baseOrder[2], baseOrder[1]]

const reordered = ref(false)
const chain = computed<Card[]>(() => (reordered.value ? swapped : baseOrder))

const amount = ref(5000)
const active = ref(-1)                       // index of card the token sits on, -1 = none
const states = ref<CState[]>(['idle', 'idle', 'idle'])
const escalate = ref(false)
const banner = ref('')                       // '' | resolved text
const resolvedIdx = ref(-1)
const running = ref(false)

let timer: ReturnType<typeof setInterval> | null = null
let slideTimer: ReturnType<typeof setTimeout> | null = null
let phase: 'spawn' | 'check' | 'done' = 'spawn'
let sliding = false                          // true while a forward-slide timeout is pending
let gen = 0                                  // generation token: invalidates stale timeouts

function fmt(n: number) { return '$' + n.toLocaleString('en-US') }

function clearTimer() {
  if (timer) { clearInterval(timer); timer = null }
  running.value = false
}

function clearSlide() {
  if (slideTimer) { clearTimeout(slideTimer); slideTimer = null }
  sliding = false
}

function reset() {
  gen++                                      // any in-flight timeout is now stale
  clearTimer()
  clearSlide()
  active.value = -1
  states.value = ['idle', 'idle', 'idle']
  escalate.value = false
  banner.value = ''
  resolvedIdx.value = -1
  phase = 'spawn'
}

// one atomic hop/resolution; returns true if the chain reached a terminal state
function advance(): boolean {
  const list = chain.value
  if (phase === 'done') return true
  if (sliding) return false                 // a forward-slide is mid-flight; ignore

  if (phase === 'spawn') {
    // token lands on leftmost card -> CHECKING
    active.value = 0
    setChecking(0)
    phase = 'check'
    return false
  }

  // phase === 'check' : resolve the active card
  const i = active.value
  const c = list[i]
  if (amount.value <= c.limit) {
    setHandled(i)
    banner.value = `${c.name} approved ${fmt(amount.value)}`
    resolvedIdx.value = i
    phase = 'done'
    return true
  }

  // forward
  setForward(i)
  const myGen = gen
  if (i + 1 < list.length) {
    const next = i + 1
    // brief forward flash, then token slides onto the next card as CHECKING
    sliding = true
    slideTimer = setTimeout(() => {
      slideTimer = null
      if (myGen !== gen) return             // run was reset; ignore stale timeout
      setChecking(next)
      active.value = next
      sliding = false
    }, 380)
    return false
  }

  // fell off the end -> escalate
  sliding = true
  phase = 'done'
  slideTimer = setTimeout(() => {
    slideTimer = null
    if (myGen !== gen) return               // run was reset; ignore stale timeout
    setIdle()
    active.value = list.length              // token position past the last card
    escalate.value = true
    banner.value = `${fmt(amount.value)} exceeds all limits; escalate`
    sliding = false
  }, 380)
  return true
}

function setIdle() {
  states.value = states.value.map(() => 'idle') as CState[]
}
function setChecking(i: number) {
  states.value = states.value.map((_, k) => (k === i ? 'checking' : 'idle')) as CState[]
}
function setHandled(i: number) {
  states.value = states.value.map((_, k) => (k === i ? 'handled' : 'idle')) as CState[]
}
function setForward(i: number) {
  states.value = states.value.map((_, k) => (k === i ? 'forward' : 'idle')) as CState[]
}

function submit() {
  if (running.value) return
  reset()
  running.value = true
  const myGen = gen
  // first hop immediately so feedback is instant
  let done = advance()
  if (done) { running.value = false; return }
  timer = setInterval(() => {
    if (myGen !== gen) { clearTimer(); return }
    done = advance()
    if (done) clearTimer()
  }, 600)
}

function step() {
  if (running.value) return        // don't fight the auto-player
  if (phase === 'done') reset()
  advance()
}

function toggleReorder() {
  if (running.value) return
  reordered.value = !reordered.value
  reset()
}

onBeforeUnmount(() => { clearTimer(); clearSlide() })

// token left offset (in card-slot units) for CSS transform
const tokenPos = computed(() => Math.max(active.value, 0))
const tokenVisible = computed(() => active.value >= 0)
</script>

<template>
  <div class="ac">
    <!-- ===== stage ===== -->
    <div class="stage">
      <div class="row">
        <!-- traveling token rides above the cards -->
        <div
          class="token"
          :class="{ on: tokenVisible, drop: escalate, frozen: resolvedIdx >= 0 }"
          :style="{ '--p': tokenPos }"
        >
          <span class="amt">{{ fmt(amount) }}</span>
        </div>

        <template v-for="(c, i) in chain" :key="c.name">
          <div class="card" :class="states[i]">
            <div class="cname">{{ c.name }}</div>
            <div class="clim">≤ {{ fmt(c.limit) }}</div>
            <div class="cstate">
              <span v-if="states[i] === 'checking'">CHECKING</span>
              <span v-else-if="states[i] === 'handled'">HANDLED</span>
              <span v-else-if="states[i] === 'forward'">FORWARD →</span>
              <span v-else>IDLE</span>
            </div>
          </div>
          <div
            v-if="i < chain.length - 1"
            class="link"
            :class="{ flash: states[i] === 'forward' }"
          >
            <span class="arr">→</span>
          </div>
        </template>

        <!-- escalation sink -->
        <div class="escbox" :class="{ on: escalate }">
          <span class="arr down">↓</span>
          <span class="elbl">ESCALATE</span>
        </div>
      </div>

      <div class="banner" :class="{ ok: resolvedIdx >= 0, esc: escalate }">
        <span v-if="banner">{{ resolvedIdx >= 0 ? '● ' : '▲ ' }}{{ banner }}</span>
        <span v-else class="muted">submit a request to trace the chain</span>
      </div>
    </div>

    <!-- ===== controls ===== -->
    <div class="panel">
      <div class="amtrow">
        <span class="albl">amount</span>
        <b class="aval">{{ fmt(amount) }}</b>
      </div>
      <input
        class="slider" type="range" min="0" max="300000" step="500"
        v-model.number="amount" :disabled="running"
      />

      <div class="btns">
        <button class="b play" :disabled="running" @click="submit">▶ submit</button>
        <button class="b" :disabled="running" @click="step">▸ step</button>
        <button class="b ghost" @click="reset">⟳ reset</button>
      </div>

      <label class="tog" :class="{ on: reordered }" @click="toggleReorder">
        <span class="knob" /> reorder {{ reordered ? 'ON' : 'OFF' }}
      </label>

      <ul class="kpts bp-dim text-sm">
        <li>Each card handles if amount ≤ its limit, else forwards</li>
        <li>Token falls off the end → nobody handles, escalate</li>
        <li>Reorder swaps Director/VP — a new card responds</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ac {
  display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.5rem;
  width: 100%; height: 340px; box-sizing: border-box;
  font-family: "Fira Code", monospace; overflow: hidden;
}

/* ---- stage ---- */
.stage {
  display: flex; flex-direction: column; justify-content: center; gap: 1.3rem;
  min-width: 0; overflow: visible;
}
.row { position: relative; display: flex; align-items: center; gap: 0; padding-top: 34px; min-height: 150px; }

.card {
  position: relative; z-index: 1;
  width: 124px; flex: 0 0 124px;
  display: flex; flex-direction: column; gap: .25rem;
  padding: .65rem .7rem; border: 1px solid var(--bp-line); border-radius: 11px;
  background: rgba(255,255,255,.02); transition: border-color .3s, background .3s, box-shadow .3s;
}
.card.checking { border-color: var(--bp-cyan); animation: pulse 1s ease-in-out infinite; }
.card.handled {
  border-color: var(--bp-good);
  background: rgba(74,222,128,.14); box-shadow: 0 0 18px rgba(74,222,128,.4);
}
.card.forward { border-color: var(--bp-warn); box-shadow: 0 0 14px rgba(251,191,36,.35); }
@keyframes pulse {
  0%,100% { box-shadow: 0 0 4px rgba(34,211,238,.25); }
  50%     { box-shadow: var(--bp-glow); }
}
.cname { font-size: .82rem; color: var(--bp-ink); font-weight: 600; }
.card.handled .cname { color: #fff; }
.clim { font-size: .66rem; color: var(--bp-dim); }
.cstate { font-size: .58rem; letter-spacing: .08em; color: var(--bp-dim); }
.card.checking .cstate { color: var(--bp-cyan); }
.card.handled .cstate { color: var(--bp-good); }
.card.forward .cstate { color: var(--bp-warn); }

.link { flex: 0 0 38px; display: flex; align-items: center; justify-content: center; }
.link .arr { color: var(--bp-line); font-size: 1.1rem; transition: color .3s; }
.link.flash .arr { color: var(--bp-warn); text-shadow: 0 0 8px rgba(251,191,36,.6); }

/* ---- traveling token ---- */
/* slot width = card(124) + link(38) = 162px; token centered over a card */
.token {
  position: absolute; top: 0; left: 0;
  width: 54px; height: 26px; margin-left: 35px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 999px; background: var(--bp-cyan); color: var(--bp-bg);
  font-size: .58rem; font-weight: 700;
  box-shadow: var(--bp-glow);
  opacity: 0; transform: translateX(0) translateY(0);
  transition: transform .4s cubic-bezier(.4,.1,.3,1), opacity .3s, top .35s, background .3s;
  z-index: 3; pointer-events: none;
}
.token.on { opacity: 1; transform: translateX(calc(var(--p) * 162px)); }
.token.frozen { background: var(--bp-good); }
.token.drop { top: 88px; opacity: 1; background: var(--bp-bad); }
.token .amt { white-space: nowrap; }

/* ---- escalate sink ---- */
.escbox {
  margin-left: 14px; align-self: flex-end; margin-bottom: -4px;
  display: flex; flex-direction: column; align-items: center; gap: .1rem;
  opacity: .25; transition: all .35s;
}
.escbox.on { opacity: 1; }
.escbox .arr.down { color: var(--bp-bad); font-size: 1.05rem; }
.escbox .elbl {
  font-size: .56rem; letter-spacing: .08em; color: var(--bp-bad);
  border: 1px solid rgba(251,113,133,.45); border-radius: 999px; padding: .1rem .45rem;
  background: var(--bp-bg);
}

/* ---- banner ---- */
.banner {
  font-size: .76rem; padding: .5rem .8rem; border-radius: 9px;
  border: 1px solid var(--bp-line); color: var(--bp-dim);
  background: rgba(255,255,255,.02); transition: all .3s; min-height: 1.2rem;
}
.banner.ok { color: var(--bp-good); border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.06); }
.banner.esc { color: var(--bp-bad); border-color: rgba(251,113,133,.4); background: rgba(251,113,133,.06); }
.banner .muted { color: var(--bp-dim); opacity: .7; }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: stretch; min-width: 0; }
.amtrow { display: flex; align-items: baseline; justify-content: space-between; }
.albl { font-size: .62rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.aval { font-size: 1rem; color: var(--bp-cyan); }

.slider { width: 100%; appearance: none; height: 4px; border-radius: 999px;
  background: var(--bp-line); outline: none; cursor: pointer; }
.slider:disabled { opacity: .4; cursor: not-allowed; }
.slider::-webkit-slider-thumb {
  appearance: none; width: 15px; height: 15px; border-radius: 999px;
  background: var(--bp-cyan); box-shadow: var(--bp-glow); cursor: pointer;
}
.slider::-moz-range-thumb {
  width: 15px; height: 15px; border: 0; border-radius: 999px;
  background: var(--bp-cyan); box-shadow: var(--bp-glow); cursor: pointer;
}

.btns { display: flex; gap: .45rem; }
.b { flex: 1; font-family: inherit; font-size: .74rem; padding: .42rem .5rem;
  border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px;
  background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.play { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem;
  color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line);
  position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px;
  border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(167,139,250,.4); }
.tog.on .knob::after { left: 16px; background: var(--bp-violet); }
.tog.on { color: var(--bp-violet); }

.kpts { margin-top: .15rem; }
</style>
