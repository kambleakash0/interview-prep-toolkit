<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Sym = 'X' | 'O' | ''
type StratSlug = 'row' | 'col' | 'diag' | 'corners'

interface Strat {
  slug: StratSlug
  name: string
}

// the spine of make_move, mirrored as labeled steps in the trace panel
type StepId = 'reject' | 'validate' | 'place' | 'strat' | 'draw' | 'switch'

const BASE_STRATS: Strat[] = [
  { slug: 'row',  name: 'Row' },
  { slug: 'col',  name: 'Column' },
  { slug: 'diag', name: 'Diagonal' },
]
const CORNERS: Strat[] = [{ slug: 'corners', name: 'FourCorners' }]

// --- reactive game state ---
const cells = ref<Sym[]>(Array(9).fill(''))
const current = ref<Sym>('X')
const status = ref<'IN_PROGRESS' | 'WINNER_X' | 'WINNER_O' | 'DRAW'>('IN_PROGRESS')
const winLine = ref<number[]>([])           // the 3 (or 4) completing cells to highlight
const score = ref<{ X: number; O: number; DRAW: number }>({ X: 0, O: 0, DRAW: 0 })
const cornersOn = ref(false)

// --- trace state ---
const activeStep = ref<StepId | ''>('')      // which pipeline step is lit
const stratResult = ref<Record<StratSlug, '' | 'true' | 'false'>>({
  row: '', col: '', diag: '', corners: '',
})
const activeStrat = ref<StratSlug | ''>('')  // which strategy chip is mid-check
const traceLine = ref('')                    // bottom caption echoing the call
const observerFire = ref(false)              // the "Observer fired" pulse to scoreboard
const scorePulse = ref<'X' | 'O' | 'DRAW' | ''>('')

const strats = computed<Strat[]>(() =>
  cornersOn.value ? [...BASE_STRATS, ...CORNERS] : [...BASE_STRATS]
)
const over = computed(() => status.value !== 'IN_PROGRESS')
const statusText = computed(() => {
  switch (status.value) {
    case 'WINNER_X': return 'WINNER_X'
    case 'WINNER_O': return 'WINNER_O'
    case 'DRAW':     return 'DRAW'
    default:         return 'IN_PROGRESS'
  }
})

// timers, cleaned up on unmount
let busy = false
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

// --- winning-strategy implementations (pure checks over the grid) ---
const LINES: Record<Exclude<StratSlug, 'corners'>, number[][]> = {
  row:  [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
  col:  [[0, 3, 6], [1, 4, 7], [2, 5, 8]],
  diag: [[0, 4, 8], [2, 4, 6]],
}
const CORNER_CELLS = [0, 2, 6, 8]

function checkStrat(slug: StratSlug, sym: Sym): number[] | null {
  if (slug === 'corners') {
    return CORNER_CELLS.every(i => cells.value[i] === sym) ? [...CORNER_CELLS] : null
  }
  for (const line of LINES[slug]) {
    if (line.every(i => cells.value[i] === sym)) return line
  }
  return null
}

function resetStratResults() {
  stratResult.value = { row: '', col: '', diag: '', corners: '' }
}

// --- make_move pipeline, animated step by step ---
function play(idx: number) {
  if (busy) return
  busy = true
  clearTimers()
  resetStratResults()
  activeStrat.value = ''
  observerFire.value = false
  scorePulse.value = ''

  const sym = current.value

  // step 1: reject-if-over
  activeStep.value = 'reject'
  traceLine.value = `make_move(${idx}, ${sym})`
  if (over.value) {
    traceLine.value = 'game over -> move rejected'
    after(650, () => { activeStep.value = ''; busy = false })
    return
  }

  // step 2: validate-empty
  after(260, () => {
    activeStep.value = 'validate'
    if (cells.value[idx] !== '') {
      traceLine.value = `cell ${idx} occupied -> rejected`
      after(650, () => { activeStep.value = ''; busy = false })
      return
    }

    // step 3: place
    after(260, () => {
      activeStep.value = 'place'
      cells.value[idx] = sym
      traceLine.value = `board.place(${idx}, ${sym})`

      // step 4: iterate the strategy list — chips flash in sequence
      after(280, () => {
        activeStep.value = 'strat'
        runStrategies(sym, idx)
      })
    })
  })
}

function runStrategies(sym: Sym, idx: number) {
  const list = strats.value
  let won: number[] | null = null
  let wonAt = -1

  const step = (i: number) => {
    if (i >= list.length) {
      // no strategy fired
      after(220, () => afterStrategies(sym, won, wonAt))
      return
    }
    const s = list[i]
    activeStrat.value = s.slug
    const hit = checkStrat(s.slug, sym)
    stratResult.value[s.slug] = hit ? 'true' : 'false'
    traceLine.value = `${s.name}.check_win(board, ${sym}) -> ${hit ? 'true' : 'false'}`
    if (hit && !won) { won = hit; wonAt = i }
    after(320, () => step(i + 1))
  }
  step(0)
}

function afterStrategies(sym: Sym, won: number[] | null, _wonAt: number) {
  activeStrat.value = ''

  if (won) {
    // a strategy fired -> terminal state, highlight + notify observers
    winLine.value = won
    status.value = sym === 'X' ? 'WINNER_X' : 'WINNER_O'
    traceLine.value = `status = WINNER_${sym} (terminal)`
    after(360, () => {
      observerFire.value = true            // Observer pattern: Game notifies, does not record
      traceLine.value = 'notify(observers) -> Scoreboard.update(game)'
      after(520, () => {
        score.value[sym as 'X' | 'O'] += 1
        scorePulse.value = sym
        observerFire.value = false
        after(700, () => { scorePulse.value = ''; activeStep.value = ''; busy = false })
      })
    })
    return
  }

  // step 5: draw-check
  after(80, () => {
    activeStep.value = 'draw'
    const full = cells.value.every(c => c !== '')
    if (full) {
      status.value = 'DRAW'
      traceLine.value = 'board.is_full() -> DRAW (terminal)'
      after(360, () => {
        observerFire.value = true
        traceLine.value = 'notify(observers) -> Scoreboard.update(game)'
        after(520, () => {
          score.value.DRAW += 1
          scorePulse.value = 'DRAW'
          observerFire.value = false
          after(700, () => { scorePulse.value = ''; activeStep.value = ''; busy = false })
        })
      })
      return
    }

    // step 6: switch-turn
    after(220, () => {
      activeStep.value = 'switch'
      current.value = sym === 'X' ? 'O' : 'X'
      traceLine.value = `switch_turn -> ${current.value}`
      after(360, () => { activeStep.value = ''; busy = false })
    })
  })
}

function newGame() {
  clearTimers()
  busy = false
  cells.value = Array(9).fill('')
  current.value = 'X'
  status.value = 'IN_PROGRESS'
  winLine.value = []
  resetStratResults()
  activeStrat.value = ''
  activeStep.value = ''
  traceLine.value = 'create_game() -> fresh Board, Scoreboard survives'
  observerFire.value = false
  scorePulse.value = ''
}

function toggleCorners() {
  if (busy) return
  cornersOn.value = !cornersOn.value
}

// pipeline steps for the trace rail
const STEPS: { id: StepId; label: string }[] = [
  { id: 'reject',   label: 'reject_if_over' },
  { id: 'validate', label: 'validate_empty' },
  { id: 'place',    label: 'board.place' },
  { id: 'strat',    label: 'check strategies' },
  { id: 'draw',     label: 'draw_check' },
  { id: 'switch',   label: 'switch_turn' },
]
</script>

<template>
  <div class="tt">
    <!-- ============ LEFT: playable board ============ -->
    <div class="boardcol">
      <div class="bhead">
        <span class="btag">Board · 3x3</span>
        <span class="turn">
          turn:
          <b :class="current === 'X' ? 'x' : 'o'">{{ current }}</b>
        </span>
        <span class="status" :class="status.toLowerCase()">{{ statusText }}</span>
      </div>

      <div class="grid">
        <button
          v-for="(c, i) in cells"
          :key="i"
          class="cell"
          :class="{ filled: !!c, win: winLine.includes(i), x: c === 'X', o: c === 'O' }"
          :disabled="!!c || over || busy"
          @click="play(i)"
        >
          <span v-if="c" class="mark">{{ c }}</span>
        </button>

        <!-- observer pulse travels from board toward the scoreboard -->
        <transition name="fire">
          <span v-if="observerFire" class="obs">Observer fired -&gt;</span>
        </transition>
      </div>

      <!-- singleton scoreboard, persists across games -->
      <div class="score">
        <span class="slabel">Scoreboard <i>(Singleton)</i></span>
        <span class="tally" :class="{ pulse: scorePulse === 'X' }">
          X <b>{{ score.X }}</b>
        </span>
        <span class="tally" :class="{ pulse: scorePulse === 'O' }">
          O <b>{{ score.O }}</b>
        </span>
        <span class="tally draw" :class="{ pulse: scorePulse === 'DRAW' }">
          DRAW <b>{{ score.DRAW }}</b>
        </span>
      </div>
    </div>

    <!-- ============ RIGHT: engine trace ============ -->
    <div class="tracecol">
      <div class="ttag">make_move pipeline</div>

      <div class="rail">
        <template v-for="(s, i) in STEPS" :key="s.id">
          <div
            class="step"
            :class="{ on: activeStep === s.id, done: activeStep === '' && false }"
          >
            <span class="sdot" />
            <span class="slabel2">{{ s.label }}</span>

            <!-- the strategy list expands inside the "check strategies" step -->
            <div v-if="s.id === 'strat'" class="chips">
              <span
                v-for="st in strats"
                :key="st.slug"
                class="chip"
                :class="{
                  active: activeStrat === st.slug,
                  hit: stratResult[st.slug] === 'true',
                  miss: stratResult[st.slug] === 'false',
                  extra: st.slug === 'corners',
                }"
              >
                {{ st.name }}
                <i v-if="stratResult[st.slug]">= {{ stratResult[st.slug] }}</i>
              </span>
            </div>
          </div>
          <span v-if="i < STEPS.length - 1" class="link" :class="{ lit: activeStep === s.id }" />
        </template>
      </div>

      <div class="caption">
        <span class="ck">&gt;</span>
        <span class="ctext">{{ traceLine || 'click a cell to drive a move' }}</span>
      </div>

      <!-- ============ controls ============ -->
      <div class="ctrls">
        <button
          class="tog"
          :class="{ on: cornersOn }"
          :disabled="busy"
          @click="toggleCorners"
        >
          <span class="knob" /> FourCorners {{ cornersOn ? 'ON' : 'OFF' }}
        </button>
        <button class="ng" @click="newGame">&#9851; Reset / New Game</button>
      </div>
      <div class="ctrlhint">
        +1 class, +1 chip — board untouched. Scoreboard survives reset.
      </div>
    </div>
  </div>
</template>

<style scoped>
.tt {
  display: grid;
  grid-template-columns: 1fr 1.25fr;
  gap: 1.5rem;
  width: 100%;
  height: 360px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- board column ---------- */
.boardcol { display: flex; flex-direction: column; gap: .6rem; min-width: 0; }
.bhead { display: flex; align-items: center; gap: .6rem; flex-wrap: wrap; }
.btag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-blue); }
.turn { font-size: .68rem; color: var(--bp-dim); margin-left: auto; }
.turn b { font-size: .82rem; }
.turn b.x { color: var(--bp-cyan); }
.turn b.o { color: var(--bp-violet); }
.status { font-size: .56rem; letter-spacing: .06em; padding: .12rem .5rem; border-radius: 999px; border: 1px solid var(--bp-line); color: var(--bp-dim); }
.status.winner_x { color: var(--bp-cyan); border-color: rgba(34,211,238,.5); background: rgba(34,211,238,.1); }
.status.winner_o { color: var(--bp-violet); border-color: rgba(167,139,250,.5); background: rgba(167,139,250,.1); }
.status.draw { color: var(--bp-warn); border-color: rgba(251,191,36,.5); background: rgba(251,191,36,.1); }

.grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 6px;
  width: 100%;
  aspect-ratio: 1 / 1;
  max-height: 232px;
  max-width: 232px;
}
.cell {
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(255,255,255,.02);
  cursor: pointer; font-family: inherit;
  transition: border-color .25s, background .25s, box-shadow .3s, transform .15s;
}
.cell:not(:disabled):hover { border-color: var(--bp-cyan); background: rgba(34,211,238,.06); }
.cell:disabled { cursor: default; }
.cell .mark { font-size: 1.7rem; line-height: 1; }
.cell.x .mark { color: var(--bp-cyan); text-shadow: var(--bp-glow); }
.cell.o .mark { color: var(--bp-violet); text-shadow: 0 0 18px rgba(167,139,250,.5); }
.cell.win {
  border-color: var(--bp-good);
  background: rgba(74,222,128,.14);
  box-shadow: 0 0 18px rgba(74,222,128,.5);
  animation: winpop .4s ease;
}
@keyframes winpop { 0% { transform: scale(1); } 45% { transform: scale(1.08); } 100% { transform: scale(1); } }

/* observer pulse */
.obs {
  position: absolute; right: -6px; bottom: -4px;
  font-size: .56rem; color: var(--bp-bg); background: var(--bp-good);
  border-radius: 999px; padding: .12rem .5rem;
  box-shadow: 0 0 16px rgba(74,222,128,.6);
  white-space: nowrap;
}
.fire-enter-active { transition: all .4s ease-out; }
.fire-enter-from { opacity: 0; transform: translate(-30px, -10px) scale(.7); }
.fire-leave-active { transition: all .3s; }
.fire-leave-to { opacity: 0; transform: translate(40px, 30px) scale(.6); }

/* scoreboard */
.score {
  display: flex; align-items: center; gap: .55rem; flex-wrap: wrap;
  padding: .45rem .6rem; margin-top: auto;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: linear-gradient(180deg, rgba(74,222,128,.06), rgba(74,222,128,.01));
}
.slabel { font-size: .56rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-good); }
.slabel i { color: var(--bp-dim); text-transform: none; letter-spacing: 0; font-style: italic; }
.tally { font-size: .68rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 7px; padding: .1rem .5rem; transition: all .3s; }
.tally b { color: var(--bp-cyan); margin-left: .25rem; }
.tally.draw b { color: var(--bp-warn); }
.tally.pulse { border-color: var(--bp-good); background: rgba(74,222,128,.16); box-shadow: 0 0 16px rgba(74,222,128,.5); animation: tpulse .55s ease; }
@keyframes tpulse { 0% { transform: scale(1); } 40% { transform: scale(1.14); } 100% { transform: scale(1); } }

/* ---------- trace column ---------- */
.tracecol { display: flex; flex-direction: column; gap: .5rem; min-width: 0; }
.ttag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-cyan); }

.rail { display: flex; flex-direction: column; }
.step {
  display: flex; align-items: center; gap: .5rem;
  padding: .2rem .5rem;
  border: 1px solid transparent; border-radius: 8px;
  transition: all .25s;
}
.step.on {
  border-color: var(--bp-cyan);
  background: rgba(34,211,238,.1);
  box-shadow: var(--bp-glow);
}
.sdot { width: 8px; height: 8px; border-radius: 999px; background: var(--bp-line); flex: none; transition: all .25s; }
.step.on .sdot { background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.slabel2 { font-size: .68rem; color: var(--bp-dim); }
.step.on .slabel2 { color: #fff; }
.link { width: 1px; height: 7px; margin-left: 14px; background: var(--bp-line); transition: background .25s; }
.link.lit { background: var(--bp-cyan); box-shadow: var(--bp-glow); }

/* strategy chips inside the strat step */
.chips { display: flex; gap: .35rem; flex-wrap: wrap; margin-left: auto; }
.chip {
  font-size: .56rem; letter-spacing: .04em;
  padding: .12rem .45rem; border-radius: 999px;
  border: 1px solid var(--bp-line); color: var(--bp-dim);
  background: var(--bp-bg-2);
  transition: all .2s;
}
.chip i { font-style: normal; opacity: .85; margin-left: .15rem; }
.chip.active { border-color: var(--bp-cyan); color: #fff; box-shadow: var(--bp-glow); transform: translateY(-1px); }
.chip.hit { border-color: var(--bp-good); color: var(--bp-good); background: rgba(74,222,128,.12); }
.chip.miss { color: var(--bp-dim); }
.chip.extra { border-style: dashed; border-color: var(--bp-violet); color: var(--bp-violet); }
.chip.extra.hit { border-style: solid; border-color: var(--bp-good); color: var(--bp-good); }

/* caption */
.caption {
  display: flex; gap: .4rem; align-items: baseline;
  font-size: .64rem; color: var(--bp-ink);
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6);
  padding: .4rem .55rem;
  min-height: 1.9rem;
}
.ck { color: var(--bp-cyan); }
.ctext { color: var(--bp-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* controls */
.ctrls { display: flex; gap: .55rem; flex-wrap: wrap; margin-top: .1rem; }
.tog {
  display: inline-flex; align-items: center; gap: .5rem;
  font-family: inherit; font-size: .68rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .35rem .65rem; background: transparent; cursor: pointer;
  transition: all .25s;
}
.tog .knob { width: 28px; height: 15px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: none; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 11px; height: 11px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on { color: var(--bp-violet); border-color: rgba(167,139,250,.5); }
.tog.on .knob { background: rgba(167,139,250,.4); }
.tog.on .knob::after { left: 15px; background: var(--bp-violet); }
.tog:disabled { opacity: .4; cursor: not-allowed; }
.ng {
  font-family: inherit; font-size: .68rem; color: #fff;
  border: 1px solid var(--bp-cyan); border-radius: 8px;
  padding: .35rem .7rem; background: rgba(34,211,238,.12);
  cursor: pointer; box-shadow: var(--bp-glow);
  transition: all .2s;
}
.ng:hover { background: rgba(34,211,238,.2); }
.ctrlhint { font-size: .58rem; color: var(--bp-dim); line-height: 1.4; }
</style>
