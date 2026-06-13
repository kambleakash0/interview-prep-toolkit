<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

type ChipKey = 'enc' | 'zip' | 'log'
interface ChipDef { key: ChipKey; label: string; open: string; close: string }

const CHIPS: ChipDef[] = [
  { key: 'enc', label: 'Encrypt', open: 'enc(', close: ')' },
  { key: 'zip', label: 'Compress', open: 'zip(', close: ')' },
  { key: 'log', label: 'Log', open: 'log(', close: ')' },
]
const DEF = Object.fromEntries(CHIPS.map(c => [c.key, c])) as Record<ChipKey, ChipDef>

// rings: ordered OUTER -> INNER. The outermost wraps everything.
const rings = ref<ChipKey[]>(['enc', 'zip'])

// phase: idle | descending | atCore | ascending ; ptr = ring index in play
type Phase = 'idle' | 'descending' | 'atCore' | 'ascending'
const phase = ref<Phase>('idle')
const ptr = ref(-1)            // which ring the pulse is currently entering / leaving
const out = ref('')           // live output string built up so far
const speed = ref(1)          // 0.5x .. 2x  -> step duration = 460 / speed
const auto = ref(false)       // running a full Run sweep
let timer: ReturnType<typeof setTimeout> | null = null

const isOn = (k: ChipKey) => rings.value.includes(k)
const stepMs = computed(() => Math.round(460 / speed.value))

// ---- geometry: outermost ring largest. center radius ~30, each layer +30 ----
const CORE_R = 30
const GAP = 30
function radiusFor(i: number) {            // i = 0 is OUTERMOST
  const depth = rings.value.length - i     // outer -> bigger
  return CORE_R + depth * GAP
}

// pulse position 0..1 across the stack diameter, mapped to an x offset
const pulseR = computed(() => {
  if (phase.value === 'idle') {
    // parked just outside the outermost ring (clamped to stay in the stage)
    const outer = rings.value.length ? radiusFor(0) : CORE_R
    return Math.min(outer + GAP * 0.5, 118)
  }
  if (phase.value === 'atCore') return 0
  // descending: sitting at ring ptr ; ascending: leaving ring ptr
  if (ptr.value < 0 || ptr.value >= rings.value.length) return 0
  return radiusFor(ptr.value)
})

// ---------- toggling a chip ----------
function toggle(k: ChipKey) {
  if (auto.value) return
  resetRun()
  if (isOn(k)) {
    rings.value = rings.value.filter(r => r !== k)   // ring shrinks + fades, others expand
  } else {
    rings.value = [k, ...rings.value]                // new OUTERMOST ring, pushes others in
  }
}

// ---------- reorder: swap ring i with neighbor ----------
function move(i: number, dir: -1 | 1) {
  if (auto.value) return
  const j = i + dir
  if (j < 0 || j >= rings.value.length) return
  resetRun()
  const a = [...rings.value]
  ;[a[i], a[j]] = [a[j], a[i]]
  rings.value = a
}

// ---------- the dive: descend through rings, core, ascend back out ----------
function clearTimer() { if (timer !== null) { clearTimeout(timer); timer = null } }
function resetRun() { clearTimer(); auto.value = false; phase.value = 'idle'; ptr.value = -1; out.value = '' }

// advance phase by exactly one beat. returns false when finished.
function advance(): boolean {
  const n = rings.value.length
  if (phase.value === 'idle') {
    if (n === 0) { phase.value = 'atCore'; ptr.value = -1; out.value = 'data'; return true }
    phase.value = 'descending'; ptr.value = 0
    out.value = DEF[rings.value[0]].open
    return true
  }
  if (phase.value === 'descending') {
    if (ptr.value < n - 1) { ptr.value++; out.value += DEF[rings.value[ptr.value]].open; return true }
    phase.value = 'atCore'; out.value += 'data'; return true     // reached core
  }
  if (phase.value === 'atCore') {
    if (n === 0) { phase.value = 'idle'; ptr.value = -1; return false }  // empty stack: finish cleanly
    phase.value = 'ascending'; ptr.value = n - 1; out.value += DEF[rings.value[ptr.value]].close
    return true
  }
  if (phase.value === 'ascending') {
    if (ptr.value > 0) { ptr.value--; out.value += DEF[rings.value[ptr.value]].close; return true }
    phase.value = 'idle'; return false                            // back outside, done
  }
  return false
}

function step() {
  if (auto.value) return
  if (phase.value === 'idle' && out.value !== '') resetRun()      // a finished run -> start fresh
  advance()
}

function run() {
  if (auto.value) return
  resetRun()
  auto.value = true
  const tick = () => {
    const more = advance()
    if (more) { timer = setTimeout(tick, stepMs.value) }
    else { auto.value = false; clearTimer() }
  }
  timer = setTimeout(tick, 20)
}

onBeforeUnmount(clearTimer)

// is ring i flashing right now? (the pulse is sitting on it)
function flashing(i: number) {
  return (phase.value === 'descending' || phase.value === 'ascending') && ptr.value === i
}
const coreHot = computed(() => phase.value === 'atCore')

const phaseLabel = computed(() => {
  if (phase.value === 'idle') return out.value ? 'done - unwound' : 'idle'
  const k = rings.value[ptr.value]
  if (phase.value === 'descending') return k ? `descending . ${DEF[k].label} open` : 'descending'
  if (phase.value === 'atCore') return 'at core . insert data'
  return k ? `ascending . ${DEF[k].label} close` : 'ascending'
})
</script>

<template>
  <div class="dec">
    <!-- ================= STAGE ================= -->
    <div class="stage">
      <div class="palette">
        <span class="plabel">layers</span>
        <button v-for="c in CHIPS" :key="c.key" class="chip" :class="{ on: isOn(c.key) }"
          @click="toggle(c.key)">
          <span class="bullet">{{ isOn(c.key) ? '●' : '◇' }}</span>{{ c.label }}
        </button>
      </div>

      <div class="onion">
        <!-- concentric rings, outer -> inner -->
        <div v-for="(k, i) in rings" :key="k" class="ring" :class="{ flash: flashing(i) }"
          :style="{ width: radiusFor(i) * 2 + 'px', height: radiusFor(i) * 2 + 'px' }">
          <span class="rtag">{{ DEF[k].label }}</span>
          <span class="arrows">
            <button class="ar" :disabled="i === 0 || auto" @click="move(i, -1)" title="move out">▲</button>
            <button class="ar" :disabled="i === rings.length - 1 || auto" @click="move(i, 1)" title="move in">▼</button>
          </span>
        </div>

        <!-- core node -->
        <div class="core" :class="{ hot: coreHot }">data</div>

        <!-- pulse dot rides the radius (right side) -->
        <span class="pulse" :class="{ live: phase !== 'idle' }"
          :style="{ transform: `translate(${pulseR}px,-50%)`, transitionDuration: stepMs + 'ms' }" />
      </div>

      <div class="readout">
        <span class="rl">output</span>
        <code class="ostr">{{ out || '∅' }}</code>
      </div>
    </div>

    <!-- ================= CONTROLS ================= -->
    <div class="panel">
      <div class="btns">
        <button class="b run" :disabled="auto" @click="run">▶ Run</button>
        <button class="b" :disabled="auto" @click="step">▸ Step</button>
        <button class="b ghost" @click="resetRun">⟳ reset</button>
      </div>

      <div class="phase" :class="phase">{{ phaseLabel }}</div>

      <label class="spd">
        speed <b>{{ speed.toFixed(2) }}x</b>
        <input type="range" min="0.5" max="2" step="0.25" v-model.number="speed" :disabled="auto" />
      </label>

      <ul class="kpts">
        <li>Each ring is a decorator wrapping the one inside it</li>
        <li>Run dives outer to core (open tags), unwinds core to out (close tags)</li>
        <li>Reorder with arrows or toggle a layer - the path and string both change</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.dec { display: grid; grid-template-columns: 1.45fr 1fr; gap: 1.5rem;
  width: 100%; height: 340px; box-sizing: border-box; overflow: hidden;
  font-family: "Fira Code", monospace; }
.dec * { box-sizing: border-box; }

/* ---------- stage ---------- */
.stage { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .5rem; min-height: 0; }
.palette { display: flex; align-items: center; gap: .55rem; }
.plabel { font-size: .6rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-dim); }
.chip { font-family: inherit; font-size: .72rem; display: inline-flex; align-items: center; gap: .35rem;
  padding: .3rem .7rem; border: 1px solid var(--bp-line); border-radius: 999px; color: var(--bp-dim);
  background: rgba(255,255,255,.02); cursor: pointer; transition: all .25s; }
.chip .bullet { font-size: .7rem; }
.chip.on { color: var(--bp-cyan); border-color: var(--bp-cyan); background: rgba(34,211,238,.1); box-shadow: var(--bp-glow); }

/* ---------- onion ---------- */
.onion { position: relative; width: 250px; height: 250px; flex: 0 0 auto;
  display: flex; align-items: center; justify-content: center; }
.ring { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  border: 1px solid var(--bp-line); border-radius: 50%;
  background: radial-gradient(circle, transparent 55%, rgba(56,189,248,.05) 100%);
  transition: width .28s ease, height .28s ease, border-color .2s, box-shadow .2s; }
.ring.flash { border-color: var(--bp-cyan); box-shadow: 0 0 16px rgba(34,211,238,.55), inset 0 0 12px rgba(34,211,238,.25); }
.rtag { position: absolute; top: -2px; left: 50%; transform: translate(-50%,-50%);
  font-size: .56rem; color: var(--bp-ink); background: var(--bp-bg); padding: 0 .3rem; white-space: nowrap; }
.arrows { position: absolute; right: -3px; top: 50%; transform: translate(50%,-50%);
  display: flex; flex-direction: column; background: var(--bp-bg); border-radius: 4px; }
.ar { font-family: inherit; font-size: .5rem; line-height: 1; padding: .1rem .12rem; border: 1px solid var(--bp-line);
  color: var(--bp-dim); background: var(--bp-bg-2); cursor: pointer; }
.ar:first-child { border-radius: 4px 4px 0 0; border-bottom: 0; }
.ar:last-child { border-radius: 0 0 4px 4px; }
.ar:hover:not(:disabled) { color: var(--bp-cyan); border-color: var(--bp-cyan); }
.ar:disabled { opacity: .25; cursor: not-allowed; }

.core { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: .72rem; color: var(--bp-bg); font-weight: 700; background: var(--bp-cyan);
  box-shadow: var(--bp-glow); transition: all .25s; z-index: 2; }
.core.hot { transform: translate(-50%,-50%) scale(1.18); box-shadow: 0 0 26px rgba(34,211,238,.9); background: var(--bp-ink); }

.pulse { position: absolute; top: 50%; left: 50%; width: 12px; height: 12px; margin-left: -6px; border-radius: 50%;
  background: var(--bp-violet); box-shadow: 0 0 14px rgba(167,139,250,.9); opacity: 0;
  transition-property: transform; transition-timing-function: ease-in-out; z-index: 3; }
.pulse.live { opacity: 1; }

/* ---------- readout ---------- */
.readout { display: flex; align-items: center; gap: .6rem; }
.rl { font-size: .6rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-dim); }
.ostr { font-family: inherit; font-size: .9rem; color: var(--bp-cyan); padding: .25rem .7rem;
  border: 1px solid var(--bp-line); border-radius: 8px; background: rgba(34,211,238,.06);
  min-width: 130px; max-width: 100%; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ---------- panel ---------- */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: flex-start; justify-content: center; min-height: 0; }
.btns { display: flex; gap: .5rem; flex-wrap: wrap; }
.b { font-family: inherit; font-size: .78rem; padding: .42rem .8rem; border: 1px solid var(--bp-line);
  color: var(--bp-ink); border-radius: 8px; background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.run { border-color: var(--bp-cyan); color: var(--bp-ink); background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .4; cursor: not-allowed; }

.phase { font-size: .72rem; padding: .35rem .7rem; border-radius: 7px; border: 1px solid var(--bp-line);
  color: var(--bp-dim); transition: all .25s; min-width: 180px; }
.phase.descending { color: var(--bp-cyan); border-color: rgba(34,211,238,.4); }
.phase.atCore { color: var(--bp-ink); border-color: var(--bp-cyan); background: rgba(34,211,238,.1); }
.phase.ascending { color: var(--bp-violet); border-color: rgba(167,139,250,.4); }

.spd { display: flex; align-items: center; gap: .55rem; font-size: .72rem; color: var(--bp-dim); }
.spd b { color: var(--bp-cyan); }
.spd input { accent-color: var(--bp-cyan); width: 120px; cursor: pointer; }
.spd input:disabled { opacity: .4; cursor: not-allowed; }

.kpts { margin: .2rem 0 0; padding-left: 1.1rem; font-size: .72rem; color: var(--bp-dim); line-height: 1.5; }
.kpts li { margin: 0; }
</style>
