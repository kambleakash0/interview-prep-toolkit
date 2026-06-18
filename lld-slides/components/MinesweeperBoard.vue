<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   MinesweeperBoard — a grid of Cell state machines.
   First click is always safe: mines are DEFERRED, scattered
   after the first reveal around a carved 3x3 safe zone, then a
   0-count reveal floods outward via an iterative BFS that stops
   at numbered cells. Win/loss is DERIVED each turn, never stored.
   ============================================================ */

type CellState = 'HIDDEN' | 'REVEALED' | 'FLAGGED'
interface Cell {
  state: CellState
  mine: boolean
  adj: number          // 0-8 neighbour mine count
  scatter: boolean     // transient flag for the placement animation
}

interface Preset { slug: Diff; name: string; rows: number; cols: number; mines: number }
type Diff = 'EASY' | 'MEDIUM' | 'HARD'

// BoardFactory presets — difficulty is CONFIG, not a subclass (Factory Method)
const PRESETS: Preset[] = [
  { slug: 'EASY',   name: 'EASY',   rows: 8, cols: 8, mines: 8  },
  { slug: 'MEDIUM', name: 'MEDIUM', rows: 8, cols: 8, mines: 12 },
  { slug: 'HARD',   name: 'HARD',   rows: 8, cols: 8, mines: 16 },
]

// --- difficulty / board geometry ---
const diff = ref<Diff>('EASY')
const preset = computed<Preset>(() => PRESETS.find(p => p.slug === diff.value)!)
const rows = computed(() => preset.value.rows)
const cols = computed(() => preset.value.cols)
const mineCount = computed(() => preset.value.mines)

// --- reactive board state ---
const grid = ref<Cell[]>([])
const armed = ref(false)               // have mines been scattered yet?
const status = ref<'IN_PROGRESS' | 'WON' | 'LOST'>('IN_PROGRESS')
const revealInternals = ref(false)     // x-ray overlay

// --- stats (StatsTracker observer) ---
const stats = reactive({ games: 0, wins: 0, losses: 0 })
const statPulse = ref<'win' | 'loss' | ''>('')

// --- first-click-safe animation overlay ---
const placing = ref(false)             // mine-scatter animation in flight
const safeZone = ref<number[]>([])     // carved 3x3 indices to highlight

// --- cascade (BFS flood) state ---
const cascadeQueue = ref<number[]>([]) // remaining frontier for Step mode
const cascadeOpened = ref<number[]>([])// indices opened by the live cascade (for counter)
const lastCascade = ref(0)             // size of the most recent cascade
const stepMode = ref(false)            // pause the flood; advance with Step
const boomAt = ref(-1)                 // index of the mine that ended the game

// --- trace caption ---
const traceLine = ref('build_board(EASY) -> 8x8, 8 mines deferred')

// timers, cleaned up on unmount
let busy = false
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

// --- seeded RNG so every round is reproducible (mulberry32) ---
const seed = ref(0x1337)
function makeRng(s: number) {
  let a = s >>> 0
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// --- geometry helpers ---
const idx = (r: number, c: number) => r * cols.value + c
function neighbors(i: number): number[] {
  const r = Math.floor(i / cols.value)
  const c = i % cols.value
  const out: number[] = []
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue
      const nr = r + dr, nc = c + dc
      if (nr >= 0 && nr < rows.value && nc >= 0 && nc < cols.value) out.push(idx(nr, nc))
    }
  }
  return out
}

// --- derived values (computed, never stored) ---
const total = computed(() => rows.value * cols.value)
const revealed = computed(() => grid.value.filter(c => c.state === 'REVEALED').length)
const flagged = computed(() => grid.value.filter(c => c.state === 'FLAGGED').length)
const safeCells = computed(() => total.value - mineCount.value)
const derivedWon = computed(() => armed.value && revealed.value === safeCells.value && status.value !== 'LOST')

// --- lifecycle: build a fresh board (BoardFactory) ---
function buildBoard() {
  clearTimers()
  busy = false
  placing.value = false
  safeZone.value = []
  cascadeQueue.value = []
  cascadeOpened.value = []
  lastCascade.value = 0
  boomAt.value = -1
  armed.value = false
  status.value = 'IN_PROGRESS'
  grid.value = Array.from({ length: total.value }, () => ({
    state: 'HIDDEN' as CellState, mine: false, adj: 0, scatter: false,
  }))
  traceLine.value = `build_board(${diff.value}) -> ${rows.value}x${cols.value}, ${mineCount.value} mines deferred`
}
buildBoard()

function setDiff(d: Diff) {
  if (busy) return
  diff.value = d
  buildBoard()
}

// re-arm with a fresh seed so the next round differs but stays reproducible
function reset() {
  seed.value = (seed.value * 1103515245 + 12345) >>> 0
  buildBoard()
}

// --- MinePlacementStrategy: scatter mines AFTER first click, carve safe zone ---
function placeMines(safeIdx: number) {
  const rng = makeRng(seed.value)
  const safe = new Set<number>([safeIdx, ...neighbors(safeIdx)])
  safeZone.value = [...safe]
  const candidates: number[] = []
  for (let i = 0; i < total.value; i++) if (!safe.has(i)) candidates.push(i)
  // Fisher-Yates over the candidate pool with the seeded RNG
  for (let i = candidates.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1))
    ;[candidates[i], candidates[j]] = [candidates[j], candidates[i]]
  }
  const chosen = candidates.slice(0, Math.min(mineCount.value, candidates.length))
  for (const m of chosen) grid.value[m].mine = true
  // compute 0-8 adjacency counts
  for (let i = 0; i < total.value; i++) {
    if (grid.value[i].mine) continue
    grid.value[i].adj = neighbors(i).filter(n => grid.value[n].mine).length
  }
  return chosen
}

// --- StatsTracker observer fires on game-over ---
function notifyGameOver(won: boolean) {
  stats.games += 1
  if (won) { stats.wins += 1; statPulse.value = 'win' }
  else { stats.losses += 1; statPulse.value = 'loss' }
  after(900, () => { statPulse.value = '' })
}

// --- left-click: reveal ---
function reveal(i: number) {
  if (busy || status.value !== 'IN_PROGRESS') return
  const cell = grid.value[i]
  if (cell.state !== 'HIDDEN') return   // FLAGGED is reveal-immune (Cell state machine)

  // FIRST CLICK: defer placement, carve safe zone, animate the scatter
  if (!armed.value) {
    busy = true
    traceLine.value = `first reveal(${i}) -> carve 3x3 safe zone, defer mines`
    const chosen = placeMines(i)
    placing.value = true
    // pulse the scattered mines into place
    chosen.forEach((m, k) => {
      after(120 + k * 28, () => { grid.value[m].scatter = true })
    })
    after(140 + chosen.length * 28 + 360, () => {
      chosen.forEach(m => { grid.value[m].scatter = false })
      placing.value = false
      armed.value = true
      traceLine.value = `MinePlacementStrategy.scatter() -> ${chosen.length} mines, counts computed`
      after(220, () => {
        safeZone.value = []
        busy = false
        doReveal(i)
      })
    })
    return
  }
  doReveal(i)
}

// --- the actual reveal + iterative flood-fill (queue, not recursion) ---
function doReveal(i: number) {
  if (busy) return
  const cell = grid.value[i]
  if (cell.state !== 'HIDDEN') return

  if (cell.mine) {
    cell.state = 'REVEALED'
    boomAt.value = i
    status.value = 'LOST'
    traceLine.value = `reveal(${i}) -> mine! status = LOST (derived)`
    revealAllMines()
    notifyGameOver(false)
    return
  }

  // BFS flood that stops at numbered cells
  cascadeOpened.value = []
  const q: number[] = [i]
  const opened: number[] = []
  while (q.length) {
    const cur = q.shift()!
    const cc = grid.value[cur]
    if (cc.state !== 'HIDDEN') continue
    cc.state = 'REVEALED'
    opened.push(cur)
    if (cc.adj === 0) {
      for (const n of neighbors(cur)) {
        if (grid.value[n].state === 'HIDDEN' && !grid.value[n].mine) q.push(n)
      }
    }
  }

  lastCascade.value = opened.length
  if (stepMode.value && opened.length > 1) {
    // re-hide everything and replay the flood one frame at a time
    for (const o of opened) grid.value[o].state = 'HIDDEN'
    runCascade(opened)
  } else {
    cascadeOpened.value = opened
    after(60, () => { cascadeOpened.value = [] })
    traceLine.value = opened.length > 1
      ? `flood_fill(${i}) -> opened ${opened.length} cells (stopped at numbers)`
      : `reveal(${i}) -> ${grid.value[i].adj} (numbered, no flood)`
    checkWin()
  }
}

// --- animated BFS replay for Step / cascade view ---
let cascadeBatch: number[] = []
function runCascade(order: number[]) {
  busy = true
  cascadeBatch = order
  cascadeQueue.value = [...order]
  cascadeOpened.value = []
  traceLine.value = `flood_fill: replaying ${order.length}-cell cascade in BFS order`
  if (!stepMode.value) {
    pumpCascade()
  }
}
function pumpCascade() {
  if (!cascadeQueue.value.length) {
    busy = false
    traceLine.value = `flood_fill -> opened ${cascadeBatch.length} cells (stopped at numbers)`
    after(80, () => { cascadeOpened.value = [] })
    checkWin()
    return
  }
  const next = cascadeQueue.value.shift()!
  grid.value[next].state = 'REVEALED'
  cascadeOpened.value.push(next)
  after(stepMode.value ? 0 : 70, () => { if (!stepMode.value) pumpCascade() })
}
// Step button: advance exactly one frame of the paused cascade
function stepCascade() {
  if (!cascadeQueue.value.length) return
  const next = cascadeQueue.value.shift()!
  grid.value[next].state = 'REVEALED'
  cascadeOpened.value.push(next)
  if (!cascadeQueue.value.length) {
    busy = false
    traceLine.value = `flood_fill -> opened ${cascadeBatch.length} cells (stopped at numbers)`
    checkWin()
  }
}
// Replay button: re-hide the last cascade and walk it again
function replayCascade() {
  if (busy || !cascadeBatch.length) return
  for (const o of cascadeBatch) {
    if (grid.value[o].state === 'REVEALED') grid.value[o].state = 'HIDDEN'
  }
  status.value = status.value === 'WON' ? 'IN_PROGRESS' : status.value
  runCascade(cascadeBatch)
}

function revealAllMines() {
  for (const c of grid.value) if (c.mine && c.state === 'HIDDEN') c.state = 'REVEALED'
}

// --- win is DERIVED, then we just transition + notify ---
function checkWin() {
  if (status.value !== 'IN_PROGRESS') return
  if (derivedWon.value) {
    status.value = 'WON'
    traceLine.value = `revealed(${revealed.value}) == total - mines -> status = WON (derived)`
    notifyGameOver(true)
  }
}

// --- right-click: toggle flag (HIDDEN <-> FLAGGED) ---
function flag(i: number) {
  if (busy || status.value !== 'IN_PROGRESS') return
  const cell = grid.value[i]
  if (cell.state === 'REVEALED') return
  cell.state = cell.state === 'FLAGGED' ? 'HIDDEN' : 'FLAGGED'
  traceLine.value = cell.state === 'FLAGGED'
    ? `flag(${i}) -> FLAGGED (reveal-immune)`
    : `unflag(${i}) -> HIDDEN`
}

// --- per-cell view helpers ---
function cellChar(c: Cell): string {
  if (c.state === 'FLAGGED') return 'F'
  if (c.state === 'REVEALED') {
    if (c.mine) return '*'
    return c.adj > 0 ? String(c.adj) : ''
  }
  // hidden: x-ray overlay shows true content
  if (revealInternals.value) return c.mine ? '*' : (c.adj > 0 ? String(c.adj) : '')
  return ''
}
const NUM_CLASS = ['', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8']

const statusText = computed(() =>
  status.value === 'WON' ? 'WON' : status.value === 'LOST' ? 'LOST' : 'IN_PROGRESS')
const winRate = computed(() => stats.games ? Math.round((stats.wins / stats.games) * 100) : 0)
</script>

<template>
  <div class="ms">
    <!-- ============ LEFT: playable board ============ -->
    <div class="boardcol">
      <div class="bhead">
        <span class="btag">Board · {{ rows }}x{{ cols }}</span>
        <div class="diffs">
          <button
            v-for="p in PRESETS"
            :key="p.slug"
            class="diffbtn"
            :class="{ on: diff === p.slug }"
            :disabled="busy"
            @click="setDiff(p.slug)"
          >{{ p.name }}</button>
        </div>
        <span class="status" :class="status.toLowerCase()">{{ statusText }}</span>
      </div>

      <div
        class="grid"
        :class="{ xray: revealInternals }"
        :style="{ gridTemplateColumns: `repeat(${cols}, 1fr)` }"
        @contextmenu.prevent
      >
        <button
          v-for="(c, i) in grid"
          :key="i"
          class="cell"
          :class="[
            c.state.toLowerCase(),
            c.state === 'REVEALED' && !c.mine ? NUM_CLASS[c.adj] : '',
            {
              mine: c.state === 'REVEALED' && c.mine,
              boom: i === boomAt,
              safez: safeZone.includes(i),
              scatter: c.scatter,
              opening: cascadeOpened.includes(i),
              xrayed: revealInternals && c.state === 'HIDDEN',
              xmine: revealInternals && c.state === 'HIDDEN' && c.mine,
            },
          ]"
          :disabled="status !== 'IN_PROGRESS' || busy"
          @click="reveal(i)"
          @contextmenu.prevent="flag(i)"
        >
          <span class="mark">{{ cellChar(c) }}</span>
        </button>
      </div>

      <div class="bfoot">
        <span class="hintkey"><b>L-click</b> reveal</span>
        <span class="hintkey"><b>R-click</b> flag</span>
        <span class="cascade" :class="{ live: cascadeOpened.length }">
          cascade opened: <b>{{ cascadeOpened.length || lastCascade }}</b>
        </span>
      </div>
    </div>

    <!-- ============ RIGHT: derived state + controls ============ -->
    <div class="panelcol">
      <div class="ptag">derived state <i>(computed, not stored)</i></div>

      <div class="derived">
        <div class="drow">
          <span class="dk">revealed</span>
          <span class="dv">{{ revealed }}<i> / {{ safeCells }} safe</i></span>
        </div>
        <div class="drow">
          <span class="dk">mineCount</span>
          <span class="dv">{{ mineCount }}<i> deferred</i></span>
        </div>
        <div class="drow">
          <span class="dk">flagged</span>
          <span class="dv">{{ flagged }}</span>
        </div>
        <div class="drow win">
          <span class="dk">won = revealed == total - mines</span>
          <span class="dv" :class="{ yes: derivedWon }">{{ derivedWon ? 'true' : 'false' }}</span>
        </div>
        <div class="drow loss">
          <span class="dk">lost = mine_revealed</span>
          <span class="dv" :class="{ yes: status === 'LOST' }">{{ status === 'LOST' ? 'true' : 'false' }}</span>
        </div>
      </div>

      <!-- StatsTracker (Observer) -->
      <div class="statline">
        <span class="slabel">StatsTracker <i>(Observer)</i></span>
        <span class="stat">games <b>{{ stats.games }}</b></span>
        <span class="stat win" :class="{ pulse: statPulse === 'win' }">wins <b>{{ stats.wins }}</b></span>
        <span class="stat loss" :class="{ pulse: statPulse === 'loss' }">losses <b>{{ stats.losses }}</b></span>
        <span class="stat rate">{{ winRate }}%</span>
      </div>

      <!-- caption echoing the engine call -->
      <div class="caption">
        <span class="ck">&gt;</span>
        <span class="ctext">{{ traceLine }}</span>
      </div>

      <!-- controls -->
      <div class="ctrls">
        <button class="tog" :class="{ on: revealInternals }" @click="revealInternals = !revealInternals">
          <span class="knob" /> Reveal internals {{ revealInternals ? 'ON' : 'OFF' }}
        </button>
        <button class="tog" :class="{ on: stepMode }" :disabled="busy" @click="stepMode = !stepMode">
          <span class="knob" /> Cascade: {{ stepMode ? 'STEP' : 'auto' }}
        </button>
      </div>
      <div class="ctrls">
        <button class="b" :disabled="!cascadeQueue.length" @click="stepCascade">Step +1</button>
        <button class="b" :disabled="busy || !lastCascade" @click="replayCascade">Replay flood</button>
        <button class="b reset" @click="reset">Reset / re-arm</button>
      </div>
      <div class="ctrlhint">
        First click carves a 3x3 safe zone (highlighted) before mines scatter — placement is
        deferred, not fixed at construction.
      </div>
    </div>
  </div>
</template>

<style scoped>
.ms {
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  gap: 1.4rem;
  width: 100%;
  height: 358px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- board column ---------- */
.boardcol { display: flex; flex-direction: column; gap: .55rem; min-width: 0; }
.bhead { display: flex; align-items: center; gap: .55rem; flex-wrap: wrap; }
.btag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-blue); }
.diffs { display: flex; gap: .25rem; }
.diffbtn {
  font-family: inherit; font-size: .54rem; letter-spacing: .04em;
  border: 1px solid var(--bp-line); border-radius: 6px;
  background: rgba(255,255,255,.02); color: var(--bp-dim);
  padding: .12rem .4rem; cursor: pointer; transition: all .2s;
}
.diffbtn:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-ink); }
.diffbtn.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); }
.diffbtn:disabled { opacity: .45; cursor: not-allowed; }
.status { font-size: .56rem; letter-spacing: .06em; padding: .12rem .5rem; border-radius: 999px; border: 1px solid var(--bp-line); color: var(--bp-dim); margin-left: auto; }
.status.won { color: var(--bp-good); border-color: rgba(74,222,128,.5); background: rgba(74,222,128,.1); }
.status.lost { color: var(--bp-bad); border-color: rgba(251,113,133,.5); background: rgba(251,113,133,.1); }

.grid {
  position: relative;
  display: grid;
  gap: 3px;
  width: 100%;
  aspect-ratio: 1 / 1;
  max-height: 244px;
  max-width: 244px;
}
.cell {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--bp-line); border-radius: 4px;
  background: rgba(56,189,248,.05);
  cursor: pointer; font-family: inherit; padding: 0;
  transition: border-color .2s, background .2s, box-shadow .25s, transform .15s;
}
.cell:not(:disabled):hover { border-color: var(--bp-cyan); background: rgba(34,211,238,.1); }
.cell:disabled { cursor: default; }
.cell .mark { font-size: .78rem; line-height: 1; font-weight: 700; }

/* hidden vs revealed */
.cell.hidden { background: rgba(56,189,248,.06); }
.cell.revealed { background: rgba(7,11,20,.55); border-color: rgba(56,189,248,.08); cursor: default; }
.cell.flagged { background: rgba(251,191,36,.12); border-color: rgba(251,191,36,.5); }
.cell.flagged .mark { color: var(--bp-warn); }

/* numbered cells — gradient cyan -> violet -> bad as the count climbs */
.cell.n1 .mark { color: #6ee7f5; }
.cell.n2 .mark { color: var(--bp-good); }
.cell.n3 .mark { color: var(--bp-blue); }
.cell.n4 .mark { color: var(--bp-violet); }
.cell.n5 .mark { color: var(--bp-warn); }
.cell.n6 .mark { color: #fca5a5; }
.cell.n7 .mark { color: var(--bp-bad); }
.cell.n8 .mark { color: #fff; }

/* mines */
.cell.mine { background: rgba(251,113,133,.18); border-color: rgba(251,113,133,.5); }
.cell.mine .mark { color: var(--bp-bad); text-shadow: 0 0 12px rgba(251,113,133,.6); }
.cell.boom { background: rgba(251,113,133,.4); box-shadow: 0 0 18px rgba(251,113,133,.7); animation: boom .45s ease; }
@keyframes boom { 0% { transform: scale(1); } 40% { transform: scale(1.25); } 100% { transform: scale(1); } }

/* first-click safe zone */
.cell.safez { border-color: var(--bp-good); background: rgba(74,222,128,.16); box-shadow: 0 0 12px rgba(74,222,128,.4); }

/* mine scatter pulse */
.cell.scatter { animation: scatter .42s ease; }
@keyframes scatter {
  0% { transform: scale(.4); }
  50% { transform: scale(1.18); box-shadow: 0 0 14px rgba(167,139,250,.7); border-color: var(--bp-violet); }
  100% { transform: scale(1); }
}

/* cascade open pulse */
.cell.opening { border-color: var(--bp-cyan); box-shadow: 0 0 12px rgba(34,211,238,.6); animation: openpulse .4s ease; }
@keyframes openpulse { 0% { transform: scale(.85); } 55% { transform: scale(1.12); } 100% { transform: scale(1); } }

/* x-ray overlay on hidden cells */
.grid.xray .cell.xrayed { background: rgba(56,189,248,.04); border-style: dashed; }
.cell.xrayed .mark { opacity: .42; font-weight: 400; }
.cell.xmine .mark { color: var(--bp-bad); opacity: .65; }

/* board footer */
.bfoot { display: flex; align-items: center; gap: .55rem; flex-wrap: wrap; margin-top: auto; }
.hintkey { font-size: .56rem; color: var(--bp-dim); }
.hintkey b { color: var(--bp-cyan); font-weight: 700; }
.cascade { font-size: .56rem; color: var(--bp-dim); margin-left: auto; border: 1px solid var(--bp-line); border-radius: 999px; padding: .1rem .5rem; transition: all .25s; }
.cascade b { color: var(--bp-cyan); margin-left: .1rem; }
.cascade.live { border-color: var(--bp-cyan); background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }

/* ---------- panel column ---------- */
.panelcol { display: flex; flex-direction: column; gap: .5rem; min-width: 0; }
.ptag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-cyan); }
.ptag i { color: var(--bp-dim); text-transform: none; letter-spacing: 0; font-style: italic; }

.derived {
  display: flex; flex-direction: column; gap: .22rem;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(255,255,255,.015); padding: .5rem .6rem;
}
.drow { display: flex; align-items: baseline; justify-content: space-between; gap: .5rem; }
.dk { font-size: .62rem; color: var(--bp-dim); }
.dv { font-size: .68rem; color: #fff; }
.dv i { font-size: .56rem; color: var(--bp-dim); font-style: normal; margin-left: .3rem; }
.drow.win .dk, .drow.loss .dk { font-size: .56rem; color: var(--bp-dim); }
.drow.win { border-top: 1px solid var(--bp-line); padding-top: .22rem; margin-top: .1rem; }
.dv.yes { color: var(--bp-good); text-shadow: var(--bp-glow); }
.drow.loss .dv.yes { color: var(--bp-bad); text-shadow: 0 0 12px rgba(251,113,133,.5); }

/* stats observer line */
.statline {
  display: flex; align-items: center; gap: .45rem; flex-wrap: wrap;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: linear-gradient(180deg, rgba(167,139,250,.06), rgba(167,139,250,.01));
  padding: .4rem .6rem;
}
.slabel { font-size: .54rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-violet); }
.slabel i { color: var(--bp-dim); text-transform: none; letter-spacing: 0; font-style: italic; }
.stat { font-size: .6rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 7px; padding: .08rem .4rem; transition: all .3s; }
.stat b { color: var(--bp-ink); margin-left: .25rem; }
.stat.win b { color: var(--bp-good); }
.stat.loss b { color: var(--bp-bad); }
.stat.rate { color: var(--bp-cyan); border-color: rgba(34,211,238,.3); margin-left: auto; }
.stat.pulse { transform: scale(1.06); }
.stat.win.pulse { border-color: var(--bp-good); background: rgba(74,222,128,.16); box-shadow: 0 0 14px rgba(74,222,128,.5); }
.stat.loss.pulse { border-color: var(--bp-bad); background: rgba(251,113,133,.16); box-shadow: 0 0 14px rgba(251,113,133,.5); }

/* caption */
.caption {
  display: flex; gap: .4rem; align-items: baseline;
  font-size: .62rem; color: var(--bp-ink);
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6); padding: .4rem .55rem;
  min-height: 1.85rem;
}
.ck { color: var(--bp-cyan); }
.ctext { color: var(--bp-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* controls */
.ctrls { display: flex; gap: .5rem; flex-wrap: wrap; }
.tog {
  display: inline-flex; align-items: center; gap: .5rem;
  font-family: inherit; font-size: .62rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .3rem .55rem; background: transparent; cursor: pointer;
  transition: all .25s;
}
.tog .knob { width: 26px; height: 14px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: none; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 10px; height: 10px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on { color: var(--bp-cyan); border-color: rgba(34,211,238,.5); }
.tog.on .knob { background: rgba(34,211,238,.4); }
.tog.on .knob::after { left: 14px; background: var(--bp-cyan); }
.tog:disabled { opacity: .4; cursor: not-allowed; }
.b {
  font-family: inherit; font-size: .62rem; color: var(--bp-ink);
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .3rem .55rem; background: rgba(255,255,255,.03);
  cursor: pointer; transition: all .2s;
}
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b:disabled { opacity: .4; cursor: not-allowed; }
.b.reset { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); margin-left: auto; }
.b.reset:hover { background: rgba(34,211,238,.2); }
.ctrlhint { font-size: .56rem; color: var(--bp-dim); line-height: 1.4; margin-top: .05rem; }
</style>
