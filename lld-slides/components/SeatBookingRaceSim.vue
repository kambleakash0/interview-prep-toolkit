<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   SeatBookingRaceSim — the check-then-act race, hand-driven.
   Two threads share one seat + a ticketsLeft counter. Interleave
   their READ -> CHECK -> WRITE steps by hand (or Run a random
   schedule) and watch the seat double-book. Flip to Locked or
   Optimistic (CAS) and watch the same interleaving serialize.
   The aha: guard the smallest read-modify-write span, not the
   whole method.
   ============================================================ */

type Mode = 'unlocked' | 'locked' | 'cas'
type Phase = 'READ' | 'CHECK' | 'WRITE'
type LaneId = 'A' | 'B'

const PHASES: Phase[] = ['READ', 'CHECK', 'WRITE']

interface Lane {
  id: LaneId
  user: string
  step: number        // -1 = not started, 0..2 = on PHASES[step], 3 = done
  saw: boolean | null // what its READ observed for the seat (free?)
  outcome: '' | 'won' | 'lost' | 'retry'
  waiting: boolean    // blocked on the lock (locked mode)
  retries: number     // CAS retries
}

function freshLane(id: LaneId, user: string): Lane {
  return { id, user, step: -1, saw: null, outcome: '', waiting: false, retries: 0 }
}

const mode = ref<Mode>('unlocked')

// shared contended state
const booked = ref(false)        // seat taken?
const tickets = ref(1)           // ticketsLeft counter
const holder = ref<LaneId | ''>('')  // who holds the lock (locked mode)
const doubleBooked = ref(false)  // the bug fired
const flashSpan = ref(false)     // red flash over the overlapping critical spans

const lanes = reactive<Record<LaneId, Lane>>({
  A: freshLane('A', 'alice'),
  B: freshLane('B', 'bob'),
})

const log = ref<string[]>([])
function emit(line: string) {
  log.value.push(line)
  if (log.value.length > 5) log.value.shift()
}

// timers, cleaned up on unmount
const timers: ReturnType<typeof setTimeout>[] = []
function after(ms: number, fn: () => void) { const t = setTimeout(fn, ms); timers.push(t); return t }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

const running = ref(false)       // auto Run in progress

const modeLabel = computed(() => (
  mode.value === 'unlocked' ? 'NO LOCK' : mode.value === 'locked' ? 'LOCKED' : 'CAS'
))

// a lane can advance if it has steps left, isn't blocked, and (locked) holds/can-take the lock
function canStep(id: LaneId): boolean {
  if (running.value) return false
  const ln = lanes[id]
  if (ln.step >= 3) return false
  const other: LaneId = id === 'A' ? 'B' : 'A'
  if (mode.value === 'locked') {
    // entering the guarded span (the READ step) requires the lock be free
    if (ln.step === -1 && holder.value && holder.value !== id) return false
    if (lanes[other].waiting && holder.value === other) { /* other parked */ }
  }
  return true
}

function stepLane(id: LaneId) {
  if (!canStep(id)) return
  const ln = lanes[id]
  const other: LaneId = id === 'A' ? 'B' : 'A'
  const next = ln.step + 1   // phase index we're moving onto (0..2), 3 = commit done

  // LOCKED: acquire on first phase, release after WRITE
  if (mode.value === 'locked' && ln.step === -1) {
    if (holder.value && holder.value !== id) return
    holder.value = id
    lanes[other].waiting = holder.value === id && lanes[other].step === -1
    emit(`Thread ${id}: acquire(lock)`)
  }

  ln.step = next

  if (next <= 2) {
    const phase = PHASES[next]
    if (phase === 'READ') {
      ln.saw = !booked.value
      emit(`Thread ${id}: READ seat -> ${booked.value ? 'TAKEN' : 'free'}`)
    } else if (phase === 'CHECK') {
      emit(`Thread ${id}: CHECK (saw=${ln.saw ? 'free' : 'taken'})`)
    } else {
      doWrite(id)
    }
    return
  }

  // next === 3 -> the lane has finished its WRITE/commit
  if (mode.value === 'locked') {
    holder.value = ''
    if (lanes[other].waiting) {
      lanes[other].waiting = false
      emit(`Thread ${id}: release(lock) -> ${other} may proceed`)
    } else {
      emit(`Thread ${id}: release(lock)`)
    }
  }
  maybeFinish()
}

// the WRITE step — where the bug or the fix shows up
function doWrite(id: LaneId) {
  const ln = lanes[id]
  if (mode.value === 'unlocked') {
    // non-atomic: it writes based on the stale READ, never re-checking
    if (ln.saw) {
      const wasBooked = booked.value
      booked.value = true
      tickets.value -= 1
      ln.outcome = 'won'
      emit(`Thread ${id}: WRITE book(seat) -> ok`)
      if (wasBooked) {
        // the second writer also "succeeded" -> double book
        doubleBooked.value = true
        flashSpan.value = true
        emit(`!! DOUBLE-BOOKED: ticketsLeft=${tickets.value}`)
        after(1400, () => { flashSpan.value = false })
      }
    }
  } else if (mode.value === 'locked') {
    // serialized: re-check under the lock, loser fails cleanly
    if (booked.value) {
      ln.outcome = 'lost'
      emit(`Thread ${id}: seat taken -> return False (clean)`)
    } else {
      booked.value = true
      tickets.value -= 1
      ln.outcome = 'won'
      emit(`Thread ${id}: book(seat) -> ok, ticketsLeft=${tickets.value}`)
    }
  } else {
    // CAS: compare-and-swap on the seat; loser retries instead of waiting
    if (!booked.value && ln.saw) {
      booked.value = true
      tickets.value -= 1
      ln.outcome = 'won'
      emit(`Thread ${id}: CAS(free->taken) -> ok`)
    } else {
      ln.outcome = 'retry'
      ln.retries += 1
      ln.saw = false
      emit(`Thread ${id}: CAS fail -> retry #${ln.retries} -> return False`)
    }
  }
}

function maybeFinish() {
  if (lanes.A.step >= 3 && lanes.B.step >= 3) {
    if (!doubleBooked.value) emit('schedule complete')
  }
}

// Run: pick a random valid interleaving and play it step by step
function run() {
  if (running.value) return
  reset(false)
  running.value = true
  // build a randomized order of 6 atomic steps (3 per lane), respecting per-lane order
  const seq: LaneId[] = []
  let ca = 0, cb = 0
  while (ca < 3 || cb < 3) {
    const pickA = cb >= 3 ? true : ca >= 3 ? false : Math.random() < 0.5
    if (pickA) { seq.push('A'); ca++ } else { seq.push('B'); cb++ }
  }
  emit(`Run: interleaving ${seq.join(' ')}`)
  let i = 0
  const drive = () => {
    if (i >= seq.length) {
      // play the final release/commit pops if locked left a lane at step 2
      finishTrailing(() => { running.value = false })
      return
    }
    const id = seq[i++]
    // in locked mode a step may be blocked; if so, swap to the holder's pending step
    if (mode.value === 'locked' && lanes[id].step === -1 && holder.value && holder.value !== id) {
      // skip blocked lane this tick, retry it later by re-pushing
      seq.push(id)
      after(180, drive)
      return
    }
    forceStep(id)
    after(620, drive)
  }
  after(300, drive)
}

// step ignoring the running guard (used by run's own scheduler)
function forceStep(id: LaneId) {
  const wasRunning = running.value
  running.value = false
  stepLane(id)
  running.value = wasRunning
}

// after the 6 phase-steps, pop any lane still at step 2 to release locks
function finishTrailing(done: () => void) {
  const pending: LaneId[] = []
  if (lanes.A.step === 2) pending.push('A')
  if (lanes.B.step === 2) pending.push('B')
  let i = 0
  const pop = () => {
    if (i >= pending.length) { done(); return }
    forceStep(pending[i++])
    after(420, pop)
  }
  pop()
}

function setMode(m: Mode) {
  if (running.value) return
  mode.value = m
  reset(false)
}

function reset(clearLog = true) {
  clearTimers()
  running.value = false
  booked.value = false
  tickets.value = 1
  holder.value = ''
  doubleBooked.value = false
  flashSpan.value = false
  Object.assign(lanes.A, freshLane('A', 'alice'))
  Object.assign(lanes.B, freshLane('B', 'bob'))
  if (clearLog) log.value = []
}

// ---- view helpers ----
const seatLabel = computed(() => (doubleBooked.value ? 'DOUBLE-BOOKED' : booked.value ? 'BOOKED' : 'AVAILABLE'))
const seatClass = computed(() => (doubleBooked.value ? 'bad' : booked.value ? 'held' : 'free'))

function phaseClass(id: LaneId, i: number) {
  const ln = lanes[id]
  const inSpan = flashSpan.value && (i >= 0)   // whole RMW span flashes red on the bug
  return {
    on: ln.step === i,
    past: ln.step > i,
    flash: inSpan && doubleBooked.value,
  }
}

function laneStateText(id: LaneId): string {
  const ln = lanes[id]
  if (ln.waiting) return 'waiting on lock'
  if (ln.outcome === 'won') return 'booked'
  if (ln.outcome === 'lost') return 'failed cleanly'
  if (ln.outcome === 'retry') return `retried x${ln.retries}, failed`
  if (ln.step === -1) return 'idle'
  return PHASES[ln.step] ?? 'committing'
}

const laneGreyed = (id: LaneId) => lanes[id].waiting

// live Python: the booking method, with the lock wrapper toggled by mode
const pyLines = computed(() => {
  const wrap = mode.value === 'locked'
  const cas = mode.value === 'cas'
  const L: { t: string; cls?: string }[] = []
  L.push({ t: 'def book(self, seat_id, user):' })
  if (cas) {
    L.push({ t: '    while True:', cls: 'add' })
    L.push({ t: '        cur = self._seats[seat_id]  # snapshot', cls: 'add' })
    L.push({ t: '        if cur is TAKEN:' })
    L.push({ t: '            return False        # loser, no wait' })
    L.push({ t: '        if self._cas(seat_id, cur, TAKEN):', cls: 'add' })
    L.push({ t: '            return True         # swapped in' })
    L.push({ t: '        # CAS lost -> loop and retry', cls: 'dim' })
  } else {
    if (wrap) L.push({ t: '    with self._lock:               # smallest span', cls: 'add' })
    const ind = wrap ? '        ' : '    '
    L.push({ t: `${ind}if seat_id in self._booked:` })
    L.push({ t: `${ind}    return False           # loser fails clean` })
    L.push({ t: `${ind}self._booked.add(seat_id)  # read-modify-write` })
    L.push({ t: `${ind}return True` })
    if (!wrap) L.push({ t: '    # check-then-act is NOT atomic -> race', cls: 'bad' })
  }
  return L
})
</script>

<template>
  <div class="rs">
    <!-- ===== mode rail + shared state ===== -->
    <div class="topbar">
      <div class="modes">
        <button class="mbtn" :class="{ on: mode === 'unlocked' }" :disabled="running" @click="setMode('unlocked')">
          <span class="mdot" /> No Lock
        </button>
        <button class="mbtn" :class="{ on: mode === 'locked' }" :disabled="running" @click="setMode('locked')">
          <span class="mdot lock" /> Locked
        </button>
        <button class="mbtn" :class="{ on: mode === 'cas' }" :disabled="running" @click="setMode('cas')">
          <span class="mdot cas" /> Optimistic (CAS)
        </button>
      </div>
      <div class="shared">
        <span class="slbl">shared</span>
        <span class="seat" :class="seatClass">
          <span class="stag">seat 12A</span>
          <span class="sval">{{ seatLabel }}</span>
        </span>
        <span class="ctr" :class="{ neg: tickets < 0, zero: tickets === 0 }">
          ticketsLeft <b>{{ tickets }}</b>
        </span>
      </div>
    </div>

    <!-- ===== main: lanes + python panel ===== -->
    <div class="body">
      <!-- thread lanes -->
      <div class="lanes">
        <div v-for="id in (['A','B'] as LaneId[])" :key="id" class="lane"
             :class="{ greyed: laneGreyed(id), holds: holder === id && mode === 'locked' }">
          <div class="lhead">
            <span class="lname">Thread {{ id }}</span>
            <span class="luser">{{ lanes[id].user }}()</span>
            <span class="lstate" :class="{
              won: lanes[id].outcome === 'won',
              lost: lanes[id].outcome === 'lost',
              retry: lanes[id].outcome === 'retry',
              wait: lanes[id].waiting }">{{ laneStateText(id) }}</span>
          </div>
          <div class="track">
            <!-- lock bracket wraps only the RMW span in locked mode -->
            <span v-if="mode === 'locked'" class="bracket" :class="{ live: holder === id }">
              <span class="blbl">lock</span>
            </span>
            <template v-for="(p, i) in PHASES" :key="p">
              <span class="tok" :class="phaseClass(id, i)">{{ p }}</span>
              <span v-if="i < PHASES.length - 1" class="arr" :class="{ lit: lanes[id].step > i }">-&gt;</span>
            </template>
            <button class="stepb" :disabled="!canStep(id)" @click="stepLane(id)">step {{ id }}</button>
          </div>
        </div>

        <!-- controls + event log -->
        <div class="controls">
          <button class="b play" :disabled="running" @click="run">&#9654; Run (random interleave)</button>
          <button class="b ghost" :disabled="running" @click="reset(true)">&#8635; reset</button>
          <div class="hint" v-if="mode === 'unlocked'">
            Advance both READs before either WRITE — both see <i>free</i>, both write, seat double-books.
          </div>
          <div class="hint" v-else-if="mode === 'locked'">
            Lock guards only READ-CHECK-WRITE. Second thread greys out, waits, then fails cleanly.
          </div>
          <div class="hint" v-else>
            No blocking: the loser's compare fails on the swapped value and it retries instead of waiting.
          </div>
        </div>

        <div class="logbox">
          <div class="logh">event log</div>
          <div v-for="(l, i) in log" :key="i" class="logl"
               :class="{ bad: l.startsWith('!!'), ok: l.includes('-> ok') || l.includes('proceed') }">{{ l }}</div>
          <div v-if="!log.length" class="logl dim">drive a thread or hit Run...</div>
        </div>
      </div>

      <!-- live python panel -->
      <div class="pyp" :class="{ flag: mode === 'unlocked' }">
        <div class="pyh">
          <span class="pytag">SeatManager.book</span>
          <span class="pymode" :class="mode">{{ modeLabel }}</span>
        </div>
        <pre class="pycode"><code v-for="(ln, i) in pyLines" :key="i" class="pyln" :class="ln.cls">{{ ln.t }}</code></pre>
        <div class="pyfoot">
          <span v-if="mode === 'unlocked'" class="bad">bug: non-atomic check-then-act</span>
          <span v-else-if="mode === 'locked'" class="good">guard the smallest span, not the method</span>
          <span v-else class="good">lock-free: swap or retry, never block</span>
        </div>
      </div>
    </div>

    <!-- aha strip -->
    <div class="footer">
      Get single-threaded logic right first — then name the race (check-then-act) and lock exactly the read-modify-write span.
    </div>
  </div>
</template>

<style scoped>
.rs {
  width: 100%; height: 360px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: .55rem;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}

/* ---------- top bar ---------- */
.topbar { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.modes { display: flex; gap: .4rem; }
.mbtn {
  display: inline-flex; align-items: center; gap: .4rem;
  font-family: inherit; font-size: .66rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(255,255,255,.02); color: var(--bp-dim);
  padding: .3rem .55rem; transition: all .2s;
}
.mbtn:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-ink); }
.mbtn.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.mbtn:disabled { opacity: .45; cursor: not-allowed; }
.mdot { width: 8px; height: 8px; border-radius: 999px; background: var(--bp-bad); flex: none; }
.mdot.lock { background: var(--bp-good); }
.mdot.cas { background: var(--bp-violet); }

.shared { display: flex; align-items: center; gap: .55rem; margin-left: auto; }
.slbl { font-size: .54rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-dim); }
.seat {
  display: inline-flex; flex-direction: column; align-items: center; gap: .05rem;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .22rem .6rem;
  transition: all .3s;
}
.seat .stag { font-size: .5rem; color: var(--bp-dim); letter-spacing: .06em; }
.seat .sval { font-size: .66rem; font-weight: 700; letter-spacing: .04em; }
.seat.free { border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.07); }
.seat.free .sval { color: var(--bp-good); }
.seat.held { border-color: rgba(251,191,36,.45); background: rgba(251,191,36,.08); }
.seat.held .sval { color: var(--bp-warn); }
.seat.bad { border-color: var(--bp-bad); background: rgba(251,113,133,.14); box-shadow: 0 0 18px rgba(251,113,133,.5); animation: shake .4s; }
.seat.bad .sval { color: var(--bp-bad); }
.ctr { font-size: .64rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 7px; padding: .22rem .5rem; transition: all .3s; }
.ctr b { color: var(--bp-cyan); margin-left: .25rem; }
.ctr.zero b { color: var(--bp-good); }
.ctr.neg { border-color: var(--bp-bad); background: rgba(251,113,133,.1); }
.ctr.neg b { color: var(--bp-bad); }

/* ---------- body ---------- */
.body { flex: 1; min-height: 0; display: grid; grid-template-columns: 1.45fr 1fr; gap: .9rem; }

/* lanes column */
.lanes { display: flex; flex-direction: column; gap: .5rem; min-width: 0; min-height: 0; }
.lane {
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(255,255,255,.015); padding: .4rem .55rem;
  transition: all .3s;
}
.lane.holds { border-color: rgba(74,222,128,.4); box-shadow: 0 0 14px rgba(74,222,128,.22); }
.lane.greyed { opacity: .42; filter: grayscale(.6); }
.lhead { display: flex; align-items: center; gap: .5rem; margin-bottom: .35rem; }
.lname { font-size: .64rem; color: var(--bp-cyan); letter-spacing: .04em; }
.luser { font-size: .56rem; color: var(--bp-dim); }
.lstate { margin-left: auto; font-size: .54rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 999px; padding: .04rem .45rem; transition: all .25s; }
.lstate.won { color: var(--bp-good); border-color: rgba(74,222,128,.45); background: rgba(74,222,128,.1); }
.lstate.lost { color: var(--bp-warn); border-color: rgba(251,191,36,.45); }
.lstate.retry { color: var(--bp-violet); border-color: rgba(167,139,250,.45); }
.lstate.wait { color: var(--bp-bad); border-color: rgba(251,113,133,.45); background: rgba(251,113,133,.08); }

.track { position: relative; display: flex; align-items: center; gap: .35rem; }
.tok {
  font-size: .6rem; letter-spacing: .04em;
  border: 1px solid var(--bp-line); border-radius: 6px;
  padding: .24rem .5rem; color: var(--bp-dim); background: rgba(255,255,255,.02);
  transition: all .25s;
}
.tok.on { color: #fff; border-color: var(--bp-cyan); background: rgba(34,211,238,.16); box-shadow: var(--bp-glow); }
.tok.past { color: var(--bp-good); border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.06); }
.tok.flash { color: var(--bp-bad); border-color: var(--bp-bad); background: rgba(251,113,133,.18); animation: redpulse .6s ease-in-out 2; }
.arr { color: var(--bp-line); font-size: .62rem; transition: color .25s; }
.arr.lit { color: var(--bp-cyan); }
.stepb {
  margin-left: auto; font-family: inherit; font-size: .56rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 6px; padding: .24rem .55rem;
  background: rgba(34,211,238,.06); color: var(--bp-ink); transition: all .2s;
}
.stepb:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.stepb:disabled { opacity: .35; cursor: not-allowed; }

/* lock bracket spanning the RMW tokens */
.bracket {
  position: absolute; left: -4px; top: -7px; bottom: -5px;
  width: calc(100% - 78px);
  border: 1px dashed rgba(74,222,128,.45); border-radius: 8px;
  pointer-events: none; transition: all .3s;
}
.bracket.live { border-style: solid; border-color: var(--bp-good); box-shadow: 0 0 14px rgba(74,222,128,.3); }
.blbl {
  position: absolute; top: -8px; left: 8px;
  font-size: .46rem; letter-spacing: .1em; text-transform: uppercase;
  color: var(--bp-good); background: var(--bp-bg); padding: 0 .25rem;
}

/* controls */
.controls { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; }
.b {
  font-family: inherit; font-size: .64rem; padding: .36rem .6rem; cursor: pointer;
  border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px;
  background: rgba(255,255,255,.03); transition: all .2s;
}
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.play { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.hint { flex: 1 1 100%; font-size: .56rem; color: var(--bp-dim); line-height: 1.35; }
.hint i { color: var(--bp-good); font-style: normal; }

/* event log */
.logbox {
  flex: 1; min-height: 0; border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(7,11,20,.6); padding: .4rem .55rem; overflow: hidden;
  display: flex; flex-direction: column; gap: .12rem;
}
.logh { font-size: .5rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bp-dim); margin-bottom: .15rem; }
.logl { font-size: .56rem; color: var(--bp-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.45; }
.logl.bad { color: var(--bp-bad); font-weight: 700; }
.logl.ok { color: var(--bp-good); }
.logl.dim { color: var(--bp-dim); opacity: .7; }

/* ---------- python panel ---------- */
.pyp {
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: var(--bp-bg-2); padding: .5rem .6rem;
  display: flex; flex-direction: column; gap: .4rem; min-width: 0;
  transition: all .3s;
}
.pyp.flag { border-color: rgba(251,113,133,.4); }
.pyh { display: flex; align-items: center; gap: .5rem; }
.pytag { font-size: .56rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-cyan); }
.pymode { margin-left: auto; font-size: .5rem; letter-spacing: .08em; border-radius: 999px; padding: .05rem .45rem; border: 1px solid var(--bp-line); }
.pymode.unlocked { color: var(--bp-bad); border-color: rgba(251,113,133,.45); background: rgba(251,113,133,.1); }
.pymode.locked { color: var(--bp-good); border-color: rgba(74,222,128,.45); background: rgba(74,222,128,.1); }
.pymode.cas { color: var(--bp-violet); border-color: rgba(167,139,250,.45); background: rgba(167,139,250,.1); }
.pycode { margin: 0; display: flex; flex-direction: column; }
.pyln {
  font-family: "Fira Code", monospace; font-size: .58rem; line-height: 1.55;
  color: var(--bp-dim); white-space: pre; transition: all .25s;
}
.pyln.add { color: var(--bp-good); background: rgba(74,222,128,.08); border-radius: 3px; }
.pyln.bad { color: var(--bp-bad); }
.pyln.dim { color: var(--bp-dim); opacity: .65; }
.pyfoot { font-size: .54rem; margin-top: auto; line-height: 1.35; }
.pyfoot .good { color: var(--bp-good); }
.pyfoot .bad { color: var(--bp-bad); }

/* ---------- footer ---------- */
.footer { font-size: .58rem; color: var(--bp-dim); border-top: 1px solid var(--bp-line); padding-top: .3rem; letter-spacing: .03em; line-height: 1.35; }

/* ---------- animations ---------- */
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-4px)} 75%{transform:translateX(4px)} }
@keyframes redpulse { 0%,100%{box-shadow:0 0 0 rgba(251,113,133,0)} 50%{box-shadow:0 0 16px rgba(251,113,133,.7)} }
</style>
