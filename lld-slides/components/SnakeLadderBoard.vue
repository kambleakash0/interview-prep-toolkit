<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   SnakeLadderBoard — the board is just a position->position map.
   Roll the dice, watch the token step to next_position, then snap
   along the connector to get_final_position(next): one O(1) lookup
   resolves snakes and ladders identically. Turn rotation is a deque.
   ============================================================ */

const SIZE = 100

// snakes (start > end) and ladders (start < end) — the whole "board"
interface Jump { start: number; end: number; kind: 'snake' | 'ladder' }
const JUMPS: Jump[] = [
  { start: 3,  end: 38, kind: 'ladder' },
  { start: 24, end: 33, kind: 'ladder' },
  { start: 42, end: 93, kind: 'ladder' },
  { start: 72, end: 84, kind: 'ladder' },
  { start: 17, end: 7,  kind: 'snake'  },
  { start: 54, end: 34, kind: 'snake'  },
  { start: 62, end: 19, kind: 'snake'  },
  { start: 98, end: 79, kind: 'snake'  },
]
// the dict the slide's Python builds: { e.start: e.end for e in entities }
const JUMP_MAP: Record<number, number> = {}
for (const j of JUMPS) JUMP_MAP[j.start] = j.end
function getFinalPosition(pos: number): number {
  return JUMP_MAP[pos] ?? pos              // O(1), snake == ladder
}

// --- players + turn queue (deque front = whose turn) ---
type PlayerName = 'Alice' | 'Bob' | 'Charlie'
interface Player { name: PlayerName; pos: number; klass: string }
const players = reactive<Record<PlayerName, Player>>({
  Alice:   { name: 'Alice',   pos: 0, klass: 'p-a' },
  Bob:     { name: 'Bob',     pos: 0, klass: 'p-b' },
  Charlie: { name: 'Charlie', pos: 0, klass: 'p-c' },
})
const queue = ref<PlayerName[]>(['Alice', 'Bob', 'Charlie'])
const active = computed(() => queue.value[0])

type Status = 'NOT_STARTED' | 'RUNNING' | 'FINISHED'
const status = ref<Status>('NOT_STARTED')
const winner = ref<PlayerName | ''>('')

// --- transient UI state for the live trace ---
const dieFace = ref(0)                       // last roll (0 = not rolled yet)
const movingToken = ref<PlayerName | ''>('') // token currently animating
const phase = ref<'' | 'step' | 'jump' | 'skip' | 'win'>('')
const flashJump = ref<number>(-1)            // jump.start whose table row flashes
const showMap = ref(false)                   // snakesAndLadders dict table toggle
const log = ref<{ id: number; text: string; tone: '' | 'good' | 'bad' | 'win' }[]>([])
let logId = 0

// timers, cleaned up on unmount
let busy = false
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

function pushLog(text: string, tone: '' | 'good' | 'bad' | 'win' = '') {
  log.value.unshift({ id: logId++, text, tone })
  if (log.value.length > 7) log.value.length = 7
}

const over = computed(() => status.value === 'FINISHED')

// --- the boustrophedon board: row 0 (bottom) = 1..10 L->R, row 1 = 20..11, etc.
// returns { row, col } in a 10x10 grid where row 0 is the TOP visual row.
function cellPos(n: number): { row: number; col: number } {
  const i = n - 1
  const bandFromBottom = Math.floor(i / 10)
  let col = i % 10
  if (bandFromBottom % 2 === 1) col = 9 - col   // snake back right->left on odd bands
  const row = 9 - bandFromBottom                 // band 0 sits at the visual bottom
  return { row, col }
}
// pixel center of a cell inside the 100%-square board (percent coords for SVG/overlay)
function cellCenter(n: number): { x: number; y: number } {
  const { row, col } = cellPos(n)
  return { x: (col + 0.5) * 10, y: (row + 0.5) * 10 }
}

// connector paths for the SVG overlay (drawn once)
const connectors = computed(() =>
  JUMPS.map(j => {
    const a = cellCenter(j.start)
    const b = cellCenter(j.end)
    const mx = (a.x + b.x) / 2 + (j.kind === 'snake' ? 8 : -8)
    const my = (a.y + b.y) / 2
    return { ...j, d: `M ${a.x} ${a.y} Q ${mx} ${my} ${b.x} ${b.y}`, ax: a.x, ay: a.y, bx: b.x, by: b.y }
  })
)

// which players sit on cell n (to render tokens in the grid)
function tokensOn(n: number): Player[] {
  return (Object.values(players) as Player[]).filter(p => p.pos === n)
}

// the 10x10 cell numbers, top-left to bottom-right, following the snake numbering
const boardCells = computed(() => {
  const rows: number[][] = []
  for (let band = 9; band >= 0; band--) {
    const base = band * 10
    const left = base + 1
    const right = base + 10
    const ltr = band % 2 === 0
    const row: number[] = []
    for (let c = 0; c < 10; c++) row.push(ltr ? left + c : right - c)
    rows.push(row)
  }
  return rows.flat()
})

// --- dice ---
function rollDice(): number {
  return Math.floor(Math.random() * 6) + 1   // Dice(1, 6).roll()
}

// --- take_turn pipeline, animated: roll -> step -> resolve map -> rules ---
function rollTurn() {
  if (busy || over.value) return
  busy = true
  clearTimers()
  flashJump.value = -1
  phase.value = ''
  if (status.value === 'NOT_STARTED') {
    status.value = 'RUNNING'
    pushLog('Game.play() -> status = RUNNING')
  }
  takeTurn(false)
}

// one take_turn(player); `extra` marks a recursive bonus roll from a 6
function takeTurn(extra: boolean) {
  const name = active.value
  const p = players[name]
  const roll = rollDice()
  dieFace.value = roll
  movingToken.value = name

  const next = p.pos + roll
  const prefix = extra ? 'extra turn -> ' : ''

  // rule 1: overshoot the board -> skip, pass play on
  if (next > SIZE) {
    phase.value = 'skip'
    pushLog(`${prefix}${name} rolled ${roll}: ${p.pos}+${roll}=${next} > 100, turn skipped`, 'bad')
    after(720, () => { phase.value = ''; rotateAndFinish(roll) })
    return
  }

  // rule 2: land exactly on 100 -> win
  if (next === SIZE) {
    phase.value = 'step'
    p.pos = SIZE
    pushLog(`${prefix}${name} rolled ${roll}, advances ${next - roll}->100`, 'good')
    after(560, () => {
      phase.value = 'win'
      winner.value = name
      status.value = 'FINISHED'
      pushLog(`${name} landed on 100 — WINNER!`, 'win')
      after(700, () => { movingToken.value = ''; busy = false })
    })
    return
  }

  // rule 3: normal move — step to next_position first...
  phase.value = 'step'
  p.pos = next
  const final = getFinalPosition(next)
  pushLog(`${prefix}${name} rolled ${roll}, steps to ${next}`)

  after(540, () => {
    if (final !== next) {
      // ...then the AHA: one map lookup snaps along the connector
      phase.value = 'jump'
      flashJump.value = next
      const jk = JUMP_MAP[next] > next ? 'ladder' : 'snake'
      p.pos = final
      pushLog(
        `get_final_position(${next}) -> ${final}: ${jk === 'ladder' ? 'climbs ladder' : 'bitten by snake'} ${next}->${final}`,
        jk === 'ladder' ? 'good' : 'bad',
      )
      after(780, () => { flashJump.value = -1; phase.value = ''; afterMove(roll) })
    } else {
      pushLog(`get_final_position(${next}) -> ${next}: plain square (map.get default)`)
      after(220, () => { phase.value = ''; afterMove(roll) })
    }
  })
}

// after a non-terminal move: a 6 grants a recursive extra turn, else rotate
function afterMove(roll: number) {
  if (roll === 6) {
    pushLog(`rolled 6 -> recursive take_turn(${active.value}), extra turn!`, 'good')
    after(420, () => takeTurn(true))
    return
  }
  rotateAndFinish(roll)
}

// deque rotation: pop the front player, append to back; turn passes on
function rotateAndFinish(_roll: number) {
  const front = queue.value.shift()
  if (front) queue.value.push(front)
  pushLog(`deque.rotate -> next up: ${active.value}`)
  movingToken.value = ''
  busy = false
}

function reset() {
  clearTimers()
  busy = false
  players.Alice.pos = 0
  players.Bob.pos = 0
  players.Charlie.pos = 0
  queue.value = ['Alice', 'Bob', 'Charlie']
  status.value = 'NOT_STARTED'
  winner.value = ''
  dieFace.value = 0
  movingToken.value = ''
  phase.value = ''
  flashJump.value = -1
  log.value = []
  pushLog('Game.Builder.build() -> board + dice + 3 players validated')
}

function toggleMap() { showMap.value = !showMap.value }

// dice pip layout (1..6) for the rendered die
const PIPS: Record<number, number[]> = {
  1: [4],
  2: [0, 8],
  3: [0, 4, 8],
  4: [0, 2, 6, 8],
  5: [0, 2, 4, 6, 8],
  6: [0, 2, 3, 5, 6, 8],
}
const diePips = computed(() => (dieFace.value ? PIPS[dieFace.value] : []))

const statusText = computed(() => {
  if (status.value === 'FINISHED') return `FINISHED · ${winner.value}`
  if (status.value === 'RUNNING') return 'RUNNING'
  return 'NOT_STARTED'
})
</script>

<template>
  <div class="sl">
    <!-- ============ LEFT: the live board ============ -->
    <div class="boardcol">
      <div class="bhead">
        <span class="btag">Board · 10x10 · size=100</span>
        <span class="status" :class="status.toLowerCase()">{{ statusText }}</span>
      </div>

      <div class="boardwrap">
        <div class="grid">
          <div
            v-for="n in boardCells"
            :key="n"
            class="cell"
            :class="{
              jstart: JUMP_MAP[n] !== undefined,
              ladder: JUMP_MAP[n] !== undefined && JUMP_MAP[n] > n,
              snake: JUMP_MAP[n] !== undefined && JUMP_MAP[n] < n,
              flash: flashJump === n,
              goal: n === SIZE,
            }"
          >
            <span class="num">{{ n }}</span>
            <span class="toks">
              <span
                v-for="p in tokensOn(n)"
                :key="p.name"
                class="tok"
                :class="[p.klass, { moving: movingToken === p.name }]"
                :title="p.name"
              >{{ p.name[0] }}</span>
            </span>
          </div>
        </div>

        <!-- snake/ladder connectors -->
        <svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path
            v-for="c in connectors"
            :key="c.start"
            :d="c.d"
            class="conn"
            :class="[c.kind, { lit: flashJump === c.start }]"
          />
          <circle
            v-for="c in connectors"
            :key="'s' + c.start"
            :cx="c.ax" :cy="c.ay" r="1.1"
            class="end" :class="c.kind"
          />
        </svg>
      </div>
    </div>

    <!-- ============ RIGHT: engine + controls + log ============ -->
    <div class="tracecol">
      <!-- turn deque -->
      <div class="ttag">turn deque · take_turn(front)</div>
      <div class="queue">
        <span
          v-for="(name, i) in queue"
          :key="name"
          class="qchip"
          :class="[players[name].klass, { front: i === 0, win: winner === name }]"
        >
          <span class="qdot" />{{ name }}
          <i>{{ players[name].pos }}</i>
        </span>
      </div>

      <!-- dice + map toggle row -->
      <div class="enginerow">
        <div class="die" :class="phase">
          <span v-if="dieFace" class="pips">
            <span
              v-for="slot in 9"
              :key="slot"
              class="pip"
              :class="{ on: diePips.includes(slot - 1) }"
            />
          </span>
          <span v-else class="dieq">?</span>
        </div>
        <div class="phaselabel">
          <span class="pk">&gt;</span>
          <span class="ptext" :class="phase">
            {{
              phase === 'step' ? 'p.position = next' :
              phase === 'jump' ? 'board.get_final_position(next)  O(1)' :
              phase === 'skip' ? 'next > 100 -> overshoot, skip' :
              phase === 'win'  ? 'next == 100 -> status = FINISHED' :
              'dice.roll() in [1..6]'
            }}
          </span>
        </div>
      </div>

      <!-- snakesAndLadders dict, revealed on toggle -->
      <div v-if="showMap" class="maptable">
        <div class="mhead">jumps = &#123; start: end &#125;  ·  one map, both kinds</div>
        <div class="mgrid">
          <span
            v-for="j in JUMPS"
            :key="j.start"
            class="mrow"
            :class="[j.kind, { flash: flashJump === j.start }]"
          >{{ j.start }} <em>-&gt;</em> {{ j.end }}</span>
        </div>
      </div>

      <!-- decision log -->
      <div v-else class="logbox">
        <div class="logtag">engine log</div>
        <div class="loglist">
          <div
            v-for="entry in log"
            :key="entry.id"
            class="logrow"
            :class="entry.tone"
          >{{ entry.text }}</div>
          <div v-if="!log.length" class="logempty">press Roll to drive a turn</div>
        </div>
      </div>

      <!-- controls -->
      <div class="ctrls">
        <button class="roll" :disabled="busy || over" @click="rollTurn">
          &#9856; Roll · {{ active }}
        </button>
        <button class="tog" :class="{ on: showMap }" @click="toggleMap">
          <span class="knob" /> jumps dict {{ showMap ? 'ON' : 'OFF' }}
        </button>
        <button class="ng" @click="reset">&#9851; Reset</button>
      </div>
      <div class="ctrlhint">
        No cells stored — <b>get_final_position(p) = map.get(p, p)</b> is O(1); a snake and a ladder are the same lookup.
      </div>
    </div>
  </div>
</template>

<style scoped>
.sl {
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  gap: 1.3rem;
  width: 100%;
  height: 362px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- board column ---------- */
.boardcol { display: flex; flex-direction: column; gap: .5rem; min-width: 0; }
.bhead { display: flex; align-items: center; gap: .6rem; }
.btag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-blue); }
.status { margin-left: auto; font-size: .56rem; letter-spacing: .06em; padding: .12rem .5rem; border-radius: 999px; border: 1px solid var(--bp-line); color: var(--bp-dim); }
.status.running  { color: var(--bp-cyan); border-color: rgba(34,211,238,.5); background: rgba(34,211,238,.1); }
.status.finished { color: var(--bp-good); border-color: rgba(74,222,128,.5); background: rgba(74,222,128,.12); }

.boardwrap { position: relative; width: 318px; height: 318px; max-width: 100%; }
.grid {
  position: absolute; inset: 0;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  grid-template-rows: repeat(10, 1fr);
  gap: 1px;
  border: 1px solid var(--bp-line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--bp-line);
}
.cell {
  position: relative;
  background: var(--bp-bg-2);
  display: flex; align-items: flex-start; justify-content: flex-start;
  overflow: hidden;
}
.cell .num { font-size: .42rem; color: var(--bp-dim); padding: 1px 0 0 2px; opacity: .7; line-height: 1; }
.cell.jstart .num { opacity: 1; font-weight: 700; }
.cell.ladder { background: rgba(74,222,128,.07); }
.cell.ladder .num { color: var(--bp-good); }
.cell.snake { background: rgba(251,113,133,.07); }
.cell.snake .num { color: var(--bp-bad); }
.cell.goal { background: rgba(34,211,238,.12); }
.cell.goal .num { color: var(--bp-cyan); }
.cell.flash { box-shadow: inset 0 0 0 2px var(--bp-warn); animation: cflash .8s ease; z-index: 3; }
@keyframes cflash { 0% { background: rgba(251,191,36,.45); } 100% {} }

/* player tokens inside cells */
.toks { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 1px; flex-wrap: wrap; }
.tok {
  width: 13px; height: 13px; border-radius: 999px;
  display: flex; align-items: center; justify-content: center;
  font-size: .46rem; font-weight: 700; color: var(--bp-bg);
  box-shadow: 0 0 6px rgba(0,0,0,.5);
  transition: transform .25s;
}
.tok.p-a { background: var(--bp-cyan); }
.tok.p-b { background: var(--bp-violet); }
.tok.p-c { background: var(--bp-warn); }
.tok.moving { transform: scale(1.35); box-shadow: 0 0 12px currentColor; z-index: 4; }

/* connector overlay */
.overlay { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }
.conn { fill: none; stroke-width: .9; stroke-linecap: round; opacity: .55; transition: opacity .25s, stroke-width .25s; }
.conn.ladder { stroke: var(--bp-good); stroke-dasharray: 2 1.4; }
.conn.snake { stroke: var(--bp-bad); }
.conn.lit { opacity: 1; stroke-width: 1.8; filter: drop-shadow(0 0 3px currentColor); }
.end { opacity: .7; }
.end.ladder { fill: var(--bp-good); }
.end.snake { fill: var(--bp-bad); }

/* ---------- trace column ---------- */
.tracecol { display: flex; flex-direction: column; gap: .45rem; min-width: 0; }
.ttag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-cyan); }

.queue { display: flex; gap: .4rem; flex-wrap: wrap; }
.qchip {
  display: inline-flex; align-items: center; gap: .3rem;
  font-size: .62rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 999px;
  padding: .14rem .5rem; background: var(--bp-bg-2);
  transition: all .25s;
}
.qchip i { font-style: normal; color: var(--bp-ink); opacity: .8; }
.qchip .qdot { width: 8px; height: 8px; border-radius: 999px; background: var(--bp-line); }
.qchip.p-a .qdot { background: var(--bp-cyan); }
.qchip.p-b .qdot { background: var(--bp-violet); }
.qchip.p-c .qdot { background: var(--bp-warn); }
.qchip.front { border-color: var(--bp-cyan); color: #fff; box-shadow: var(--bp-glow); transform: translateY(-1px); }
.qchip.win { border-color: var(--bp-good); color: var(--bp-good); background: rgba(74,222,128,.14); }

/* dice + phase */
.enginerow { display: flex; align-items: center; gap: .7rem; }
.die {
  width: 40px; height: 40px; flex: none;
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: var(--bp-bg-2);
  display: flex; align-items: center; justify-content: center;
  transition: all .25s;
}
.die.step, .die.jump { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.die.skip { border-color: var(--bp-bad); box-shadow: 0 0 16px rgba(251,113,133,.5); }
.die.win { border-color: var(--bp-good); box-shadow: 0 0 16px rgba(74,222,128,.5); }
.die .dieq { font-size: 1.1rem; color: var(--bp-dim); }
.pips { display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(3, 1fr); gap: 2px; width: 26px; height: 26px; }
.pip { width: 100%; height: 100%; border-radius: 999px; background: transparent; }
.pip.on { background: var(--bp-cyan); box-shadow: 0 0 4px var(--bp-cyan); }

.phaselabel { display: flex; gap: .35rem; align-items: baseline; min-width: 0; }
.pk { color: var(--bp-cyan); }
.ptext { font-size: .64rem; color: var(--bp-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ptext.jump { color: var(--bp-cyan); }
.ptext.skip { color: var(--bp-bad); }
.ptext.win  { color: var(--bp-good); }

/* jumps dict table */
.maptable {
  flex: 1; min-height: 0;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6);
  padding: .45rem .55rem; overflow-y: auto;
}
.mhead { font-size: .56rem; color: var(--bp-violet); letter-spacing: .04em; margin-bottom: .35rem; }
.mgrid { display: grid; grid-template-columns: 1fr 1fr; gap: .25rem .6rem; }
.mrow {
  font-size: .64rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 6px;
  padding: .1rem .45rem; transition: all .2s;
}
.mrow em { font-style: normal; opacity: .6; }
.mrow.ladder { color: var(--bp-good); border-color: rgba(74,222,128,.25); }
.mrow.snake { color: var(--bp-bad); border-color: rgba(251,113,133,.25); }
.mrow.flash { box-shadow: var(--bp-glow); transform: scale(1.05); border-color: var(--bp-warn); background: rgba(251,191,36,.12); }

/* log */
.logbox {
  flex: 1; min-height: 0;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6);
  padding: .4rem .55rem; display: flex; flex-direction: column; gap: .2rem;
  overflow: hidden;
}
.logtag { font-size: .54rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-dim); }
.loglist { display: flex; flex-direction: column; gap: .15rem; overflow-y: auto; }
.logrow {
  font-size: .6rem; line-height: 1.3; color: var(--bp-ink);
  border-left: 2px solid var(--bp-line); padding-left: .4rem;
}
.logrow.good { color: var(--bp-good); border-color: var(--bp-good); }
.logrow.bad { color: var(--bp-bad); border-color: var(--bp-bad); }
.logrow.win { color: var(--bp-cyan); border-color: var(--bp-cyan); text-shadow: var(--bp-glow); font-weight: 700; }
.logempty { font-size: .6rem; color: var(--bp-dim); opacity: .7; }

/* scrollbars */
.maptable::-webkit-scrollbar, .loglist::-webkit-scrollbar { width: 5px; }
.maptable::-webkit-scrollbar-thumb, .loglist::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }

/* controls */
.ctrls { display: flex; gap: .5rem; flex-wrap: wrap; }
.roll {
  font-family: inherit; font-size: .66rem; color: #fff;
  border: 1px solid var(--bp-cyan); border-radius: 8px;
  padding: .35rem .7rem; background: rgba(34,211,238,.14);
  cursor: pointer; box-shadow: var(--bp-glow); transition: all .2s;
}
.roll:hover:not(:disabled) { background: rgba(34,211,238,.24); }
.roll:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.tog {
  display: inline-flex; align-items: center; gap: .45rem;
  font-family: inherit; font-size: .64rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .3rem .6rem; background: transparent; cursor: pointer; transition: all .25s;
}
.tog .knob { width: 26px; height: 14px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: none; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 10px; height: 10px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on { color: var(--bp-violet); border-color: rgba(167,139,250,.5); }
.tog.on .knob { background: rgba(167,139,250,.4); }
.tog.on .knob::after { left: 14px; background: var(--bp-violet); }
.ng {
  font-family: inherit; font-size: .64rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .3rem .65rem; background: transparent; cursor: pointer; transition: all .2s;
}
.ng:hover { color: var(--bp-ink); border-color: var(--bp-cyan); }
.ctrlhint { font-size: .57rem; color: var(--bp-dim); line-height: 1.4; margin-top: .05rem; }
.ctrlhint b { color: var(--bp-cyan); font-weight: 600; }
</style>
