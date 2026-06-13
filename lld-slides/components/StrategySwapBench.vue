<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Slug = 'none' | 'pct' | 'flat'
interface Strat {
  slug: Slug
  name: string
  formula: string
  // pure algorithm: each "concrete strategy" supplies a different quote()
  quote: (s: number) => number
  out: number
}

const SUBTOTAL = 100
const STRATS: Strat[] = [
  { slug: 'none', name: 'NoDiscount',     formula: 'return subtotal',          quote: s => s,            out: 100 },
  { slug: 'pct',  name: 'PercentOff(20)', formula: 'subtotal * (1 - 20/100)',  quote: s => s * 0.8,      out: 80 },
  { slug: 'flat', name: 'FlatFee(15)',    formula: 'subtotal - 15',            quote: s => s - 15,       out: 85 },
]

// phase drives the named visual states
const phase = ref<'unplugged' | 'travel' | 'compute' | 'plugged'>('unplugged')
const docked = ref<Slug | null>(null)        // which strategy is in the socket
const leaving = ref<Slug | null>(null)       // chip sliding back during a SWAP
const tokenOut = ref(false)                  // result token flying back to readout
const reading = ref<number | null>(null)     // readout number (counts up)
const ringFlash = ref(false)                 // ring pulse on the "unchanged" caption

// reactive so stateLabel + the state badge recompute as it flips
const busy = ref(false)
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

const dockedStrat = computed(() => STRATS.find(s => s.slug === docked.value) || null)
const stateLabel = computed(() => {
  if (busy.value && docked.value && phase.value !== 'plugged') return 'SWAPPING'
  if (phase.value === 'unplugged') return 'UNPLUGGED'
  if (phase.value === 'plugged') return 'PLUGGED'
  return 'SWAPPING'
})

function countUp(to: number) {
  reading.value = 0
  const steps = 14
  let i = 0
  const tick = () => {
    i++
    reading.value = Math.round((to * i) / steps)
    if (i < steps) after(22, tick)
    else reading.value = to
  }
  tick()
}

function plug(slug: Slug) {
  if (busy.value) return
  if (docked.value === slug && phase.value === 'plugged') return
  busy.value = true
  clearTimers()
  tokenOut.value = false

  const swapping = docked.value !== null
  if (swapping) {
    leaving.value = docked.value      // old chip fades + slides back to its column
    ringFlash.value = true            // Context flashes a ring to signal a swap
    after(420, () => { ringFlash.value = false })
  }

  // new chip slides left into the socket
  after(swapping ? 200 : 0, () => {
    docked.value = slug
    leaving.value = null
    reading.value = null
    phase.value = 'travel'            // the 100 token journeys into the docked chip
  })

  // token reaches the chip -> chip pulses "computing"
  const base = swapping ? 200 : 0
  after(base + 460, () => { phase.value = 'compute' })

  // result token flies back to the readout and the number counts up
  after(base + 820, () => {
    tokenOut.value = true
    const s = STRATS.find(x => x.slug === slug)!
    countUp(s.out)
  })
  after(base + 1180, () => {
    tokenOut.value = false
    phase.value = 'plugged'
    busy.value = false
  })
}

function reset() {
  if (busy.value) return
  clearTimers()
  docked.value = null
  leaving.value = null
  tokenOut.value = false
  reading.value = null
  ringFlash.value = false
  phase.value = 'unplugged'
}
</script>

<template>
  <div class="ss">
    <!-- ============ STAGE ============ -->
    <div class="stage">
      <!-- readout (far left) -->
      <div class="readout" :class="{ live: reading !== null }">
        <div class="rlabel">cart.total</div>
        <div class="rval">
          <span v-if="reading === null" class="dash">— —</span>
          <span v-else class="num">{{ reading }}</span>
        </div>
        <transition name="fly">
          <span v-if="tokenOut" class="rtoken">{{ dockedStrat?.out }}</span>
        </transition>
      </div>

      <!-- fixed Context card -->
      <div class="ctx">
        <div class="ctag">CONTEXT · Cart</div>
        <pre class="code">cart.total({{ SUBTOTAL }})</pre>
        <!-- the socket: where the strategy plugs in -->
        <div class="socket" :class="{ filled: !!docked }">
          <span v-if="!docked" class="shole">socket</span>
          <span class="emit" :class="{ go: phase === 'travel' }">{{ SUBTOTAL }}</span>
        </div>
        <div class="ccap" :class="{ ring: ringFlash }">
          <span class="lock">●</span> Context code unchanged
        </div>
      </div>

      <!-- guide rail -->
      <div class="rail"><span class="track" /></div>

      <!-- strategy column (right) -->
      <div class="column">
        <button
          v-for="s in STRATS"
          :key="s.slug"
          class="chip"
          :class="{
            docked: docked === s.slug,
            leaving: leaving === s.slug,
            compute: docked === s.slug && phase === 'compute',
            idle: docked !== s.slug,
          }"
          @click="plug(s.slug)"
        >
          <span class="cname">{{ s.name }}</span>
          <span class="cform">quote(s): {{ s.formula }}</span>
          <span v-if="docked === s.slug" class="pin">▶ plugged</span>
        </button>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="state" :class="stateLabel.toLowerCase()">
        state: <b>{{ stateLabel }}</b>
      </div>
      <div class="hint">
        <template v-if="phase === 'unplugged'">Click a strategy to plug it into the Context.</template>
        <template v-else>Click another to hot-swap — the Context line never changes.</template>
      </div>
      <button class="reset" @click="reset">◀ reset</button>
      <ul class="kpts bp-dim">
        <li>One socket, many algorithms — the caller delegates blindly</li>
        <li>Swap mid-flight: behavior changes, <b>context stays pinned</b></li>
        <li>Each chip is one ConcreteStrategy.quote()</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ss {
  display: grid;
  grid-template-columns: 1.62fr 1fr;
  gap: 1.5rem;
  width: 100%;
  height: 340px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- stage ---------- */
.stage {
  position: relative;
  display: grid;
  grid-template-columns: 92px 200px 1fr;
  align-items: center;
  gap: 0;
  height: 100%;
  overflow: hidden;
}

/* readout */
.readout {
  position: relative;
  display: flex; flex-direction: column; align-items: center; gap: .3rem;
  padding: .7rem .4rem;
  border: 1px dashed var(--bp-line); border-radius: 12px;
  background: rgba(255,255,255,.02);
  transition: border-color .35s, box-shadow .35s, background .35s;
}
.readout.live { border-style: solid; border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.rlabel { font-size: .56rem; letter-spacing: .06em; color: var(--bp-dim); }
.rval { font-size: 1.7rem; line-height: 1; min-height: 1.7rem; display: flex; align-items: center; }
.dash { color: var(--bp-dim); font-size: 1.1rem; letter-spacing: .1em; }
.num { color: var(--bp-cyan); text-shadow: var(--bp-glow); }
.rtoken {
  position: absolute; right: -10px; top: 42%;
  width: 26px; height: 26px; border-radius: 999px;
  display: flex; align-items: center; justify-content: center;
  font-size: .64rem; color: var(--bp-bg); background: var(--bp-good);
  box-shadow: 0 0 14px rgba(74,222,128,.6);
}

/* context card */
.ctx {
  position: relative;
  display: flex; flex-direction: column; gap: .55rem;
  padding: .8rem .85rem;
  border: 1px solid var(--bp-blue); border-radius: 12px;
  background: linear-gradient(180deg, rgba(56,189,248,.08), rgba(56,189,248,.02));
  z-index: 2;
}
.ctag { font-size: .56rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-blue); }
.code {
  margin: 0; font-family: inherit; font-size: .76rem;
  color: #fff; padding: .35rem .5rem;
  border: 1px solid var(--bp-line); border-radius: 7px;
  background: var(--bp-bg);
}
.socket {
  position: relative;
  height: 42px; border-radius: 9px;
  border: 2px dashed var(--bp-line);
  display: flex; align-items: center; justify-content: center;
  transition: border-color .35s, background .35s;
}
.socket.filled { border-style: solid; border-color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.shole { font-size: .62rem; letter-spacing: .14em; color: var(--bp-dim); text-transform: uppercase; }
/* the 100 token that travels from context into the docked chip */
.emit {
  position: absolute; left: 6px;
  width: 24px; height: 24px; border-radius: 999px;
  display: flex; align-items: center; justify-content: center;
  font-size: .6rem; color: var(--bp-bg); background: var(--bp-cyan);
  box-shadow: var(--bp-glow);
  opacity: 0; transform: translateX(0);
  transition: none;
}
.emit.go { animation: emit 0.46s ease-in forwards; }
@keyframes emit {
  0%   { opacity: 1; transform: translateX(0) scale(1); }
  85%  { opacity: 1; }
  100% { opacity: 0; transform: translateX(190px) scale(.7); }
}

/* caption + ring flash */
.ccap {
  position: relative;
  font-size: .58rem; color: var(--bp-dim);
  display: flex; align-items: center; gap: .35rem;
  padding: .2rem .4rem; border-radius: 7px;
}
.ccap .lock { color: var(--bp-good); font-size: .5rem; }
.ccap.ring { animation: ring .42s ease; }
@keyframes ring {
  0%   { box-shadow: 0 0 0 0 rgba(34,211,238,.5); }
  60%  { box-shadow: 0 0 0 6px rgba(34,211,238,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,211,238,0); }
}

/* guide rail between socket and chips */
.rail { position: relative; height: 100%; }
.track {
  position: absolute; top: 50%; left: -8px; right: 8px; height: 2px;
  background: repeating-linear-gradient(90deg, var(--bp-line) 0 6px, transparent 6px 12px);
}

/* strategy chips */
.column { display: flex; flex-direction: column; gap: .55rem; position: relative; z-index: 1; }
.chip {
  position: relative;
  text-align: left; cursor: pointer;
  font-family: inherit;
  display: flex; flex-direction: column; gap: .18rem;
  padding: .5rem .65rem;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(255,255,255,.03);
  color: var(--bp-ink);
  transition: transform .4s cubic-bezier(.4,1.2,.5,1), opacity .4s, border-color .3s, box-shadow .3s, background .3s;
}
.chip.idle:hover { border-color: var(--bp-cyan); color: #fff; }
/* PLUGGED: chip slid left & docked into the socket */
.chip.docked {
  border-color: var(--bp-cyan);
  background: rgba(34,211,238,.12);
  box-shadow: var(--bp-glow);
  transform: translateX(-228px);
}
/* SWAPPING: outgoing chip fades to 30% and slides back to its column */
.chip.leaving { opacity: .3; transform: translateX(0); }
/* computing pulse — one beat scale-up */
.chip.compute { animation: pulse .34s ease; }
@keyframes pulse {
  0%   { transform: translateX(-228px) scale(1); }
  50%  { transform: translateX(-228px) scale(1.05); box-shadow: 0 0 22px rgba(34,211,238,.6); }
  100% { transform: translateX(-228px) scale(1); }
}
.cname { font-size: .76rem; color: var(--bp-cyan); }
.chip.idle .cname { color: var(--bp-ink); }
.chip.docked .cname { color: var(--bp-cyan); }
.cform { font-size: .58rem; color: var(--bp-dim); }
.pin { position: absolute; top: -8px; right: 8px; font-size: .52rem; color: var(--bp-bg); background: var(--bp-cyan); border-radius: 999px; padding: .05rem .45rem; }

/* ---------- controls ---------- */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: flex-start; min-height: 0; overflow: hidden; }
.state {
  font-size: .76rem; color: var(--bp-dim);
  padding: .35rem .7rem; border-radius: 8px;
  border: 1px solid var(--bp-line); background: rgba(255,255,255,.02);
}
.state b { letter-spacing: .08em; }
.state.unplugged b { color: var(--bp-dim); }
.state.plugged { border-color: rgba(34,211,238,.4); }
.state.plugged b { color: var(--bp-cyan); }
.state.swapping { border-color: rgba(251,191,36,.4); }
.state.swapping b { color: var(--bp-warn); }
.hint { font-size: .7rem; color: var(--bp-dim); line-height: 1.4; min-height: 2rem; }
.reset {
  font-family: inherit; font-size: .72rem;
  padding: .35rem .8rem; border-radius: 7px;
  border: 1px solid var(--bp-line); color: var(--bp-dim);
  background: transparent; cursor: pointer;
  transition: border-color .3s, color .3s;
}
.reset:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.kpts { list-style: none; padding: 0; margin: .2rem 0 0; }
.kpts li { position: relative; padding-left: 1.05rem; margin: .32rem 0; font-size: .68rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
.kpts b { color: var(--bp-ink); }

/* result token fly transition */
.fly-enter-active { transition: all .34s ease-out; }
.fly-enter-from { opacity: 0; transform: translateX(60px) scale(.6); }
.fly-leave-active { transition: all .2s; }
.fly-leave-to { opacity: 0; }
</style>
