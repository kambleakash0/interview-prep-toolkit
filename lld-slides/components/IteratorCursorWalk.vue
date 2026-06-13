<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

type Mode = 'forward' | 'reverse' | 'even'

const BOOKS = ['Dune', 'Hyperion', 'Neuromancer', 'Foundation']
const CELL_W = 124        // px per cell slot (matches .cell width + gap in CSS)

const mode = ref<Mode>('forward')

// the target index-sequence the mode dictates over the 4-cell collection
const sequence = computed<number[]>(() => {
  if (mode.value === 'reverse') return [3, 2, 1, 0]
  if (mode.value === 'even') return [0, 2]
  return [0, 1, 2, 3]
})

interface Cursor {
  id: number
  color: 'cyan' | 'violet'
  step: number            // index INTO sequence; -1 PARKED, 0..len-1 ON_CELL, len DONE (past last target)
}

let nextId = 1
const cursors = ref<Cursor[]>([{ id: nextId++, color: 'cyan', step: -1 }])
const active = ref(1)     // id of the cursor next() drives
const consumed = ref<{ id: number; label: string }[]>([])
const pulseCell = ref(-1) // cell index currently pulsing
const busy = ref(false)   // reactive so buttons disable mid-animation
let consumedKey = 0

// pending timers so we can guard against leaks on unmount
let pendingTimers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) {
  const t = setTimeout(() => {
    pendingTimers = pendingTimers.filter(x => x !== t)
    fn()
  }, ms)
  pendingTimers.push(t)
  return t
}
function clearTimers() {
  pendingTimers.forEach(t => clearTimeout(t))
  pendingTimers = []
}
onBeforeUnmount(clearTimers)

// active cursor; falls back to the first cursor if the id ever drifts
const activeCursor = computed<Cursor>(() => {
  return cursors.value.find(c => c.id === active.value) ?? cursors.value[0]
})

// physical cell index a cursor sits on (-1 parked, last target when done)
function cellOf(c: Cursor): number {
  if (c.step < 0) return -1
  const seq = sequence.value
  return seq[Math.min(c.step, seq.length - 1)]
}
function isDone(c: Cursor) { return c.step >= sequence.value.length }
function isParked(c: Cursor) { return c.step < 0 }

// has_next() for the ACTIVE cursor — drives the badge
const hasNext = computed(() => activeCursor.value.step + 1 < sequence.value.length)
// can we advance right now? (guards the next() button)
const canNext = computed(() => hasNext.value && !busy.value)

// pixel x for a cursor token along the row
function tokenX(c: Cursor): number {
  if (c.step < 0) return -CELL_W * 0.62            // parked: left of the row
  const seq = sequence.value
  if (c.step >= seq.length) {                       // DONE: past the last target
    const last = seq[seq.length - 1]
    return last * CELL_W + CELL_W * 0.62
  }
  return cellOf(c) * CELL_W + CELL_W / 2
}

function stateLabel(c: Cursor): string {
  if (isParked(c)) return 'PARKED'
  if (isDone(c)) return 'DONE'
  return `ON_CELL_${cellOf(c)}`
}

function doNext() {
  if (busy.value) return
  const c = activeCursor.value
  const seq = sequence.value
  if (c.step + 1 >= seq.length + 1) return           // already past last target
  if (c.step + 1 > seq.length) return                // no target remains
  if (c.step >= seq.length) return                   // already DONE
  busy.value = true
  c.step += 1                                         // token slides (CSS transition on x)
  const last = c.step === seq.length - 1              // landed on final target
  const landed = cellOf(c)
  // arrival pulse, then a ghost label arcs up into Consumed
  later(() => { pulseCell.value = landed }, 200)
  later(() => {
    pulseCell.value = -1
    consumed.value.push({ id: consumedKey++, label: BOOKS[landed] })
    if (last) {
      // glide past the last target into the DONE state, badge flips FALSE
      later(() => { c.step += 1; busy.value = false }, 260)
    } else {
      busy.value = false
    }
  }, 520)
}

function setMode(m: Mode) {
  if (busy.value || m === mode.value) return
  mode.value = m
  softReset()                                        // clear consumed, park tokens
}

function addCursor() {
  if (busy.value || cursors.value.length >= 2) return
  const id = nextId++
  cursors.value.push({ id, color: 'violet', step: -1 })
  active.value = id
}

function pick(id: number) { if (!busy.value) active.value = id }

function softReset() {
  consumed.value = []
  pulseCell.value = -1
  cursors.value.forEach(c => { c.step = -1 })
}

function reset() {
  if (busy.value) return
  clearTimers()
  consumed.value = []
  pulseCell.value = -1
  cursors.value = [{ id: nextId++, color: 'cyan', step: -1 }]
  active.value = cursors.value[0].id
  mode.value = 'forward'
}

// dotted path overlay: ordered pairs of cell-centers the mode hops between
const pathHops = computed(() => {
  const seq = sequence.value
  const hops: { x1: number; x2: number; up: boolean }[] = []
  for (let i = 0; i < seq.length - 1; i++) {
    const a = seq[i], b = seq[i + 1]
    hops.push({
      x1: a * CELL_W + CELL_W / 2,
      x2: b * CELL_W + CELL_W / 2,
      up: Math.abs(b - a) > 1,        // even-only hops arc over a skipped cell
    })
  }
  return hops
})

const MODE_LABEL: Record<Mode, string> = {
  forward: 'i + 1',
  reverse: 'i - 1 from end',
  even: 'skip to next even',
}
</script>

<template>
  <div class="ic">
    <!-- ===================== STAGE ===================== -->
    <div class="stage">
      <!-- fixed client loop — the proof it never changes -->
      <div class="clientbar">
        <span class="cl-tag">client</span>
        <code>while has_next(): next()</code>
        <span class="badge" :class="hasNext ? 'on' : 'off'">
          has_next() · {{ hasNext ? 'TRUE' : 'FALSE' }}
        </span>
      </div>

      <!-- the visible collection -->
      <div class="rowwrap">
        <div class="row">
          <!-- dotted path overlay -->
          <svg class="path" :viewBox="`0 0 ${CELL_W * 4} 40`" preserveAspectRatio="none">
            <g v-for="(h, i) in pathHops" :key="i">
              <path
                :d="h.up
                  ? `M ${h.x1} 28 Q ${(h.x1 + h.x2) / 2} 2 ${h.x2} 28`
                  : `M ${h.x1} 24 L ${h.x2} 24`"
                class="hop" />
              <polygon
                :points="`${h.x2},24 ${h.x2 - (h.x2 > h.x1 ? 7 : -7)},20 ${h.x2 - (h.x2 > h.x1 ? 7 : -7)},28`"
                class="hop-head" />
            </g>
          </svg>

          <div
            v-for="(b, i) in BOOKS"
            :key="b"
            class="cell"
            :class="{ pulse: pulseCell === i, lit: cursors.some(c => cellOf(c) === i) }">
            <span class="idx">[{{ i }}]</span>
            <span class="title">{{ b }}</span>
          </div>

          <!-- cursor tokens ride above the row -->
          <div
            v-for="c in cursors"
            :key="c.id"
            class="token"
            :class="[c.color, { active: c.id === active, done: isDone(c) }]"
            :style="{ transform: `translateX(${tokenX(c)}px)` }">
            <span class="tri">▶</span>
            <span class="tlabel">{{ stateLabel(c) }}</span>
          </div>
        </div>

        <!-- internal storage strip the client never reads -->
        <div class="storage">
          <span class="st-tag">_books (internal storage)</span>
          <span v-for="(b, i) in BOOKS" :key="i" class="slot">{{ b }}</span>
        </div>
      </div>
    </div>

    <!-- ===================== PANEL ===================== -->
    <div class="panel">
      <div class="seg">
        <button :class="{ on: mode === 'forward' }" @click="setMode('forward')">Forward</button>
        <button :class="{ on: mode === 'reverse' }" @click="setMode('reverse')">Reverse</button>
        <button :class="{ on: mode === 'even' }" @click="setMode('even')">Even-only</button>
      </div>
      <div class="modehint">order: <b>{{ MODE_LABEL[mode] }}</b></div>

      <div class="btns">
        <button class="b prime" :disabled="!canNext" @click="doNext">next() ▸</button>
        <button class="b" :disabled="busy || cursors.length >= 2" @click="addCursor">+ Add cursor</button>
        <button class="b ghost" :disabled="busy" @click="reset">⟲ Reset</button>
      </div>

      <!-- cursor selector: which token next() drives -->
      <div class="sel">
        <span class="sl">drive</span>
        <button
          v-for="c in cursors"
          :key="c.id"
          class="pip"
          :class="[c.color, { on: c.id === active }]"
          :disabled="busy"
          @click="pick(c.id)">
          cursor {{ c.id }}<small>{{ stateLabel(c) }}</small>
        </button>
      </div>

      <!-- consumed output list -->
      <div class="consumed">
        <span class="cs-tag">Consumed →</span>
        <transition-group name="arc" tag="div" class="cs-items">
          <span v-for="item in consumed" :key="item.id" class="cs">{{ item.label }}</span>
        </transition-group>
        <span v-if="!consumed.length" class="cs-empty">empty</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ic {
  display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.4rem;
  font-family: "Fira Code", monospace; width: 100%;
  height: 340px; box-sizing: border-box; overflow: hidden;
  align-items: start;
}

/* ---------- stage ---------- */
.stage { display: flex; flex-direction: column; gap: .9rem; min-width: 0; }
.clientbar {
  display: flex; align-items: center; gap: .65rem;
  padding: .5rem .7rem; border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02);
}
.cl-tag { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.clientbar code { font-size: .82rem; color: var(--bp-ink); }
.badge {
  margin-left: auto; font-size: .64rem; padding: .18rem .55rem; border-radius: 999px;
  border: 1px solid var(--bp-line); transition: all .3s; white-space: nowrap;
}
.badge.on { color: var(--bp-good); border-color: rgba(74,222,128,.45); background: rgba(74,222,128,.07); }
.badge.off { color: var(--bp-bad); border-color: rgba(251,113,133,.45); background: rgba(251,113,133,.08); }

.rowwrap { display: flex; flex-direction: column; gap: .55rem; min-width: 0; }
.row { position: relative; display: flex; gap: 16px; padding-top: 34px; }
.path { position: absolute; top: 26px; left: 0; width: 100%; height: 40px; pointer-events: none; overflow: visible; }
.hop { fill: none; stroke: var(--bp-violet); stroke-width: 1.4; stroke-dasharray: 4 4; opacity: .55; }
.hop-head { fill: var(--bp-violet); opacity: .7; }

.cell {
  width: 108px; height: 76px; box-sizing: border-box; flex: 0 0 auto;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .25rem;
  border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.025);
  transition: all .3s;
}
.cell.lit { border-color: var(--bp-cyan); background: rgba(34,211,238,.08); box-shadow: var(--bp-glow); }
.cell.pulse { animation: pop .42s ease; border-color: var(--bp-cyan); }
@keyframes pop { 0% { transform: scale(1); } 45% { transform: scale(1.09); box-shadow: var(--bp-glow); } 100% { transform: scale(1); } }
.idx { font-size: .58rem; color: var(--bp-dim); }
.title { font-size: .78rem; color: #fff; }

/* cursor tokens */
.token {
  position: absolute; top: 0; left: -16px; width: 32px;
  display: flex; flex-direction: column; align-items: center; gap: 1px;
  transition: transform .22s ease; pointer-events: none;
}
.token .tri { font-size: .7rem; line-height: 1; transform: rotate(90deg); }
.token .tlabel {
  font-size: .5rem; white-space: nowrap; padding: .04rem .3rem; border-radius: 4px;
  border: 1px solid currentColor; background: var(--bp-bg);
}
.token.cyan { color: var(--bp-cyan); }
.token.violet { color: var(--bp-violet); }
.token.active .tri { filter: drop-shadow(0 0 6px currentColor); }
.token:not(.active) { opacity: .55; }
.token.done .tri { transform: rotate(90deg) scale(.8); opacity: .5; }

/* internal storage strip */
.storage {
  display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
  padding: .4rem .6rem; border: 1px dashed var(--bp-line); border-radius: 8px;
  background: rgba(255,255,255,.012); opacity: .5;
}
.st-tag { font-size: .56rem; color: var(--bp-dim); letter-spacing: .04em; }
.slot {
  font-size: .6rem; color: var(--bp-dim); padding: .08rem .4rem;
  border: 1px solid var(--bp-line); border-radius: 5px;
}

/* ---------- panel ---------- */
.panel { display: flex; flex-direction: column; gap: .6rem; align-items: flex-start; min-width: 0; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg button {
  font-family: inherit; font-size: .7rem; padding: .38rem .7rem;
  background: transparent; color: var(--bp-dim); cursor: pointer; border: none;
}
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.modehint { font-size: .64rem; color: var(--bp-dim); }
.modehint b { color: var(--bp-violet); }

.btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.b {
  font-family: inherit; font-size: .72rem; padding: .42rem .7rem;
  border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 7px;
  background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s;
}
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.prime { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); box-shadow: none; }
.b:disabled { opacity: .32; cursor: not-allowed; box-shadow: none; }

.sel { display: flex; align-items: center; gap: .45rem; flex-wrap: wrap; }
.sl { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.pip {
  font-family: inherit; font-size: .64rem; padding: .25rem .5rem; cursor: pointer;
  border: 1px solid currentColor; border-radius: 7px; background: var(--bp-bg);
  display: flex; flex-direction: column; line-height: 1.25; opacity: .55; transition: all .2s;
}
.pip:disabled { cursor: not-allowed; }
.pip small { font-size: .5rem; color: var(--bp-dim); }
.pip.cyan { color: var(--bp-cyan); }
.pip.violet { color: var(--bp-violet); }
.pip.on { opacity: 1; box-shadow: 0 0 10px currentColor; }

.consumed {
  display: flex; align-items: center; gap: .45rem; flex-wrap: wrap;
  width: 100%; min-height: 44px; box-sizing: border-box; padding: .45rem .6rem;
  border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02);
}
.cs-tag { font-size: .6rem; color: var(--bp-dim); }
.cs-items { display: inline-flex; flex-wrap: wrap; gap: .3rem; }
.cs {
  font-size: .66rem; padding: .12rem .5rem; border-radius: 999px;
  border: 1px solid var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.08);
}
.cs-empty { font-size: .62rem; color: var(--bp-dim); opacity: .6; }
.arc-enter-active { transition: all .4s cubic-bezier(.2,.8,.3,1); }
.arc-enter-from { opacity: 0; transform: translateY(-22px) scale(.7); }
</style>
