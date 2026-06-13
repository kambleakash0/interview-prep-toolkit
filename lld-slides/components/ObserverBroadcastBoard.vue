<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

type OState = 'idle' | 'receiving' | 'received'
interface Obs {
  id: string
  name: string
  glyph: string
  subscribed: boolean
  state: OState
  lastSeen: number | null
  y: number          // vertical centre (%) of the card for wire routing
}

const STAGE_H = 300        // px height of the stage; pulses ride within it

const temp = ref(21)
const display = ref(21)    // animated value shown in the subject card
const dirty = ref(false)
const MIN = 15
const MAX = 30

const observers = ref<Obs[]>([
  { id: 'phone',  name: 'PhoneDisplay', glyph: '▰', subscribed: true,  state: 'idle', lastSeen: null, y: 18 },
  { id: 'logger', name: 'Logger',       glyph: '≡', subscribed: true,  state: 'idle', lastSeen: null, y: 50 },
  { id: 'alert',  name: 'Alert',        glyph: '▲', subscribed: false, state: 'idle', lastSeen: null, y: 82 },
])

// in-flight pulses: one per subscribed observer on each publish
const pulses = ref<{ key: number; y: number; t: number }[]>([])
let pulseKey = 0
let busy = false
let stepTimer: number | null = null
const flightTimers: number[] = []

const subCount = computed(() => observers.value.filter(o => o.subscribed).length)

function clearStepTimer() {
  if (stepTimer !== null) { clearInterval(stepTimer); stepTimer = null }
}

function clearFlightTimers() {
  flightTimers.forEach(id => clearTimeout(id))
  flightTimers.length = 0
}

function after(ms: number, fn: () => void) {
  flightTimers.push(window.setTimeout(fn, ms))
}

function animateTo(target: number) {
  clearStepTimer()
  stepTimer = window.setInterval(() => {
    if (display.value < target) display.value += 1
    else if (display.value > target) display.value -= 1
    if (display.value === target) clearStepTimer()
  }, 60)
}

function step(d: number) {
  const next = Math.min(MAX, Math.max(MIN, temp.value + d))
  if (next === temp.value) return
  temp.value = next
  dirty.value = true
  animateTo(next)
}

function publish() {
  if (busy) return
  const targets = observers.value.filter(o => o.subscribed)
  if (targets.length === 0) { dirty.value = false; return }
  busy = true
  dirty.value = false

  // spawn one travelling dot per subscribed observer, mark RECEIVING
  targets.forEach(o => {
    o.state = 'receiving'
    const key = pulseKey++
    pulses.value.push({ key, y: o.y, t: temp.value })
  })

  // on arrival (~620ms): set RECEIVED, update last-seen, pulse
  after(620, () => {
    targets.forEach(o => {
      o.state = 'received'
      o.lastSeen = temp.value
    })
    pulses.value = []
    // relax the RECEIVED pulse back to idle shortly after
    after(520, () => {
      targets.forEach(o => { if (o.state === 'received') o.state = 'idle' })
      busy = false
    })
  })
}

function toggle(o: Obs) {
  o.subscribed = !o.subscribed
}

function reset() {
  clearStepTimer()
  clearFlightTimers()
  pulses.value = []
  observers.value.forEach(o => { o.lastSeen = null; o.state = 'idle' })
  temp.value = 21
  display.value = 21
  dirty.value = false
  busy = false
}

onBeforeUnmount(() => {
  clearStepTimer()
  clearFlightTimers()
})
</script>

<template>
  <div class="ob">
    <!-- STAGE -->
    <div class="stage">
      <!-- subject -->
      <div class="subject" :class="{ dirty }">
        <div class="tag">SUBJECT · WeatherStation</div>
        <div class="dial">
          <button class="stp" @click="step(-1)">−</button>
          <div class="read">
            <b>{{ display }}</b><span class="unit">°C</span>
          </div>
          <button class="stp" @click="step(1)">+</button>
        </div>
        <button class="pub" :class="{ ready: dirty }" @click="publish">
          ▶ notify()
          <span v-if="dirty" class="ddot" />
        </button>
        <div class="subnote">{{ subCount }} subscribed</div>
      </div>

      <!-- wires + pulses -->
      <div class="wires">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none">
          <line
            v-for="o in observers" :key="o.id"
            x1="0" y1="50" x2="100" :y2="o.y"
            class="wire"
            :class="{ off: !o.subscribed }"
          />
        </svg>
        <!-- travelling notification dots -->
        <span
          v-for="p in pulses" :key="p.key"
          class="pulse"
          :style="{ '--ty': ((p.y / 100 - 0.5) * STAGE_H) + 'px' }"
        >{{ p.t }}</span>
      </div>

      <!-- observers -->
      <div class="cards">
        <div
          v-for="o in observers" :key="o.id"
          class="card"
          :class="{ sub: o.subscribed, recv: o.state === 'received', live: o.state === 'receiving' }"
        >
          <div class="head">
            <span class="gl">{{ o.glyph }}</span>
            <span class="nm">{{ o.name }}</span>
            <label class="tog" :class="{ on: o.subscribed }" @click="toggle(o)">
              <span class="knob" />
            </label>
          </div>
          <div class="seen">
            last-seen
            <b v-if="o.lastSeen !== null">{{ o.lastSeen }}°C</b>
            <b v-else class="dash">—</b>
          </div>
          <div class="status">{{ o.subscribed ? 'SUBSCRIBED' : 'UNSUBSCRIBED' }}</div>
        </div>
      </div>
    </div>

    <!-- PANEL -->
    <div class="panel">
      <button class="b ghost" @click="reset">⟲ reset last-seen</button>
      <div class="legend">
        <span class="lg"><i class="sw on" /> subscribed → solid wire</span>
        <span class="lg"><i class="sw off" /> unsubscribed → dashed, skipped</span>
      </div>
      <ul class="kpts bp-dim text-sm">
        <li>Step the temp, then <b>notify()</b> — one dot fans out per listener</li>
        <li>Unsubscribe Alert and re-notify: the wave reaches fewer cards</li>
        <li>The subject never names its observers — it just iterates the list</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ob { display: grid; grid-template-columns: 1.62fr 1fr; gap: 1.5rem; height: 340px; font-family: "Fira Code", monospace; color: var(--bp-ink); }

/* ---- stage grid: subject | wires | observer cards ---- */
.stage { display: grid; grid-template-columns: auto 150px 1fr; align-items: stretch; gap: 0; height: 300px; }

/* ---- subject ---- */
.subject {
  align-self: center;
  display: flex; flex-direction: column; gap: .7rem; align-items: center;
  padding: 1rem .9rem; border: 1px solid var(--bp-cyan); border-radius: 14px;
  background: rgba(34,211,238,.08); box-shadow: var(--bp-glow); transition: all .3s; width: 180px;
}
.subject.dirty { border-color: var(--bp-warn); box-shadow: 0 0 18px rgba(251,191,36,.4); }
.tag { font-size: .56rem; letter-spacing: .06em; color: var(--bp-dim); text-transform: uppercase; text-align: center; }
.dial { display: flex; align-items: center; gap: .55rem; }
.stp {
  font-family: inherit; font-size: 1rem; line-height: 1; width: 30px; height: 30px;
  border: 1px solid var(--bp-line); color: var(--bp-cyan); border-radius: 8px;
  background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s;
}
.stp:hover { border-color: var(--bp-cyan); background: rgba(34,211,238,.12); }
.read { min-width: 64px; text-align: center; }
.read b { font-size: 1.7rem; color: #fff; }
.read .unit { font-size: .8rem; color: var(--bp-dim); margin-left: 1px; }
.pub {
  position: relative; font-family: inherit; font-size: .8rem; padding: .45rem 1rem;
  border: 1px solid var(--bp-line); color: var(--bp-dim); border-radius: 9px;
  background: rgba(255,255,255,.03); cursor: pointer; transition: all .25s;
}
.pub.ready { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); }
.ddot { position: absolute; top: -4px; right: -4px; width: 10px; height: 10px; border-radius: 999px; background: var(--bp-warn); box-shadow: 0 0 8px var(--bp-warn); animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: .3; } }
.subnote { font-size: .6rem; color: var(--bp-dim); }

/* ---- wires ---- */
.wires { position: relative; height: 100%; }
.wires svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.wire { stroke: var(--bp-cyan); stroke-width: 1.4; opacity: .85; vector-effect: non-scaling-stroke; transition: all .3s; }
.wire.off { stroke: var(--bp-dim); opacity: .28; stroke-dasharray: 4 4; }

/* travelling notification dot — rides the wire left→right; --ty tilts the path */
.pulse {
  position: absolute; left: 0; top: 50%; width: 22px; height: 22px; margin: -11px 0 0 -11px;
  display: flex; align-items: center; justify-content: center;
  font-size: .56rem; color: var(--bp-bg); font-weight: 700;
  border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow);
  animation: ride .62s ease-in forwards;
}
@keyframes ride {
  from { left: 0; top: 50%; transform: translateY(0) scale(.7); opacity: 0; }
  12%  { opacity: 1; }
  to   { left: 100%; transform: translateY(var(--ty)) scale(1); opacity: 1; }
}

/* ---- observer cards ---- */
.cards { display: flex; flex-direction: column; justify-content: space-between; height: 100%; padding: 2px 0; }
.card {
  display: flex; flex-direction: column; gap: .28rem; padding: .5rem .65rem;
  border: 1px solid var(--bp-line); border-radius: 11px; background: rgba(255,255,255,.02);
  opacity: .5; transition: transform .25s, opacity .25s, border-color .25s, box-shadow .25s;
}
.card.sub { opacity: 1; border-color: var(--bp-cyan); background: rgba(34,211,238,.05); }
.card.live { box-shadow: 0 0 12px rgba(34,211,238,.3); }
.card.recv { transform: scale(1.08); border-color: var(--bp-good); box-shadow: 0 0 18px rgba(74,222,128,.45); }
.head { display: flex; align-items: center; gap: .45rem; }
.gl { font-size: .9rem; color: var(--bp-cyan); width: 16px; text-align: center; }
.nm { font-size: .76rem; color: var(--bp-ink); flex: 1; }
.seen { font-size: .62rem; color: var(--bp-dim); display: flex; justify-content: space-between; align-items: baseline; }
.seen b { font-size: .82rem; color: var(--bp-cyan); }
.seen b.dash { color: var(--bp-dim); }
.status { font-size: .52rem; letter-spacing: .08em; color: var(--bp-dim); }
.card.sub .status { color: var(--bp-cyan); }

/* subscribe toggle */
.tog { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; cursor: pointer; transition: background .3s; flex: none; }
.tog .knob { position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on { background: rgba(34,211,238,.4); }
.tog.on .knob { left: 16px; background: var(--bp-cyan); }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .8rem; align-items: flex-start; }
.b { font-family: inherit; font-size: .76rem; padding: .42rem .8rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px; background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s; }
.b.ghost { color: var(--bp-dim); }
.b:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.legend { display: flex; flex-direction: column; gap: .35rem; }
.lg { display: flex; align-items: center; gap: .5rem; font-size: .64rem; color: var(--bp-dim); }
.sw { width: 22px; height: 2px; flex: none; }
.sw.on { background: var(--bp-cyan); }
.sw.off { background: repeating-linear-gradient(90deg, var(--bp-dim) 0 4px, transparent 4px 8px); opacity: .6; }
.kpts { margin-top: .2rem; }
.kpts b { color: var(--bp-cyan); }
</style>
