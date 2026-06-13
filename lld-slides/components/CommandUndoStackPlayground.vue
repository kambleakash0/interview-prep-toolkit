<script setup lang="ts">
import { ref, computed } from 'vue'

type Kind = 'lightOn' | 'lightOff' | 'temp'
interface Card { id: number; label: string; kind: Kind; prev: number | boolean }

const MAX_STACK = 5

const lightOn = ref(false)
const temp = ref(20)
const tempShown = ref(20)        // tween-counted display value
const stack = ref<Card[]>([])
const wiring = ref(false)

const phase = ref<'idle' | 'pushing' | 'popping'>('idle')
const spawnFrom = ref('')        // which button a card is flying out of
const popping = ref<Card | null>(null)
const busy = ref(false)
let uid = 0
let tweenTimer: number | undefined
let phaseTimer: number | undefined

const empty = computed(() => stack.value.length === 0)
const full = computed(() => stack.value.length >= MAX_STACK)
const stateName = computed(() =>
  phase.value === 'pushing' ? 'PUSHING'
  : phase.value === 'popping' ? 'POPPING'
  : empty.value ? 'EMPTY' : 'READY')

function tweenTemp(to: number) {
  if (tweenTimer) { clearInterval(tweenTimer); tweenTimer = undefined }
  const from = tempShown.value
  const steps = 12
  let i = 0
  tweenTimer = window.setInterval(() => {
    i++
    tempShown.value = Math.round(from + (to - from) * (i / steps))
    if (i >= steps) {
      tempShown.value = to
      clearInterval(tweenTimer)
      tweenTimer = undefined
    }
  }, 18)
}

function run(kind: Kind) {
  if (busy.value || full.value) return
  busy.value = true
  phase.value = 'pushing'
  spawnFrom.value = kind

  const label = kind === 'lightOn' ? 'Light On' : kind === 'lightOff' ? 'Light Off' : 'Set Temp 25'
  const prev: number | boolean = kind === 'temp' ? temp.value : lightOn.value
  const card: Card = { id: ++uid, label, kind, prev }

  // card spawns at the button, then settles into the stack
  stack.value = [card, ...stack.value]

  // receiver animates forward in lockstep
  if (kind === 'lightOn') lightOn.value = true
  else if (kind === 'lightOff') lightOn.value = false
  else { temp.value = 25; tweenTemp(25) }

  if (phaseTimer) clearTimeout(phaseTimer)
  phaseTimer = window.setTimeout(() => {
    spawnFrom.value = ''
    phase.value = 'idle'
    busy.value = false
    phaseTimer = undefined
  }, 250)
}

function undo() {
  if (busy.value || empty.value) return
  busy.value = true
  phase.value = 'popping'
  const card = stack.value[0]
  popping.value = card

  // reverse the receiver using the card's captured prior state
  if (card.kind === 'temp') { temp.value = card.prev as number; tweenTemp(card.prev as number) }
  else lightOn.value = card.prev as boolean

  if (phaseTimer) clearTimeout(phaseTimer)
  phaseTimer = window.setTimeout(() => {
    stack.value = stack.value.slice(1)
    popping.value = null
    phase.value = 'idle'
    busy.value = false
    phaseTimer = undefined
  }, 250)
}

function reset() {
  if (tweenTimer) { clearInterval(tweenTimer); tweenTimer = undefined }
  if (phaseTimer) { clearTimeout(phaseTimer); phaseTimer = undefined }
  lightOn.value = false; temp.value = 20; tempShown.value = 20
  stack.value = []; popping.value = null; spawnFrom.value = ''
  phase.value = 'idle'; busy.value = false
}
</script>

<template>
  <div class="cmd">
    <!-- ============ STAGE ============ -->
    <div class="stage">
      <!-- RECEIVER -->
      <div class="col receiver">
        <div class="ctitle">RECEIVER</div>
        <div class="widget">
          <div class="wlabel">Light</div>
          <span class="bulb" :class="{ on: lightOn }" />
          <div class="wstate" :class="{ go: lightOn }">{{ lightOn ? 'ON' : 'OFF' }}</div>
        </div>
        <div class="widget">
          <div class="wlabel">Thermostat</div>
          <div class="thermo" :class="{ hot: temp >= 25 }">{{ tempShown }}<small>°</small></div>
        </div>
      </div>

      <!-- wiring rail between receiver and invoker -->
      <div class="rail" :class="{ dim: wiring }">
        <span class="line" />
        <span class="atag">action()</span>
      </div>

      <!-- INVOKER undo-stack -->
      <div class="col invoker">
        <div class="ctitle">
          INVOKER
          <span class="badge" :class="{ lit: wiring }">Command</span>
        </div>
        <div class="stackcol">
          <div v-if="empty" class="placeholder">Nothing to undo</div>

          <transition-group name="card" tag="div" class="cards">
            <div
              v-for="c in stack"
              :key="c.id"
              class="card"
              :class="{
                spawn: c.kind === spawnFrom && stack[0] && stack[0].id === c.id,
                pop: popping && popping.id === c.id,
                top: stack[0] && stack[0].id === c.id
              }"
            >
              <div class="card-edge">
                <span class="verb" :class="{ undoing: popping && popping.id === c.id }">
                  {{ popping && popping.id === c.id ? 'undo' : 'execute' }}
                </span>
                <span v-if="wiring" class="wire">←</span>
              </div>
              <div class="card-label">{{ c.label }}</div>
              <div v-if="c.kind === 'temp'" class="card-prev">prev={{ c.prev }}</div>
            </div>
          </transition-group>
        </div>
        <div class="phase" :class="phase">{{ stateName }}</div>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="ctitle small">TRIGGERS</div>
      <div class="btns">
        <button class="b" :disabled="full" @click="run('lightOn')">● Light On</button>
        <button class="b" :disabled="full" @click="run('lightOff')">◯ Light Off</button>
        <button class="b" :disabled="full" @click="run('temp')">▲ Set Temp 25</button>
        <button class="b undo" :disabled="empty" @click="undo">↩ Undo</button>
      </div>

      <label class="tog" :class="{ on: wiring }" @click="wiring = !wiring">
        <span class="knob" /> Show wiring
      </label>
      <div v-if="wiring" class="wirenote">Invoker only knows execute() / undo()</div>

      <button class="b ghost" @click="reset">⟳ reset</button>

      <ul class="kpts bp-dim text-sm">
        <li>Each action becomes a card holding its <b>execute</b> + captured <b>prev</b></li>
        <li>Undo pops the top card and reverses with the value it stored</li>
        <li>Push N, undo N — receiver returns to the start (LIFO)</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.cmd { display: grid; grid-template-columns: 1.65fr 1fr; gap: 1.4rem; width: 100%; font-family: "Fira Code", monospace; height: 340px; box-sizing: border-box; }
.cmd *, .cmd *::before, .cmd *::after { box-sizing: border-box; }

/* ---- stage ---- */
.stage { display: grid; grid-template-columns: 1fr 64px 1.05fr; align-items: stretch; gap: 0; min-width: 0; min-height: 0; }
.col { display: flex; flex-direction: column; gap: .7rem; min-width: 0; min-height: 0; }
.ctitle { font-size: .6rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bp-dim); display: flex; align-items: center; gap: .5rem; }
.ctitle.small { margin-bottom: .1rem; }

/* receiver widgets */
.receiver { padding: .7rem .8rem; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.02); overflow: hidden; }
.widget { display: flex; flex-direction: column; align-items: center; gap: .35rem; padding: .55rem .4rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.02); }
.wlabel { font-size: .62rem; color: var(--bp-dim); align-self: flex-start; }
.bulb { width: 34px; height: 34px; border-radius: 999px; border: 2px solid var(--bp-dim); background: transparent; transition: all .35s ease; }
.bulb.on { border-color: var(--bp-warn); background: var(--bp-warn); box-shadow: 0 0 22px rgba(251,191,36,.7); }
.wstate { font-size: .66rem; letter-spacing: .12em; color: var(--bp-dim); transition: color .3s; }
.wstate.go { color: var(--bp-warn); }
.thermo { font-size: 1.7rem; color: var(--bp-cyan); line-height: 1; transition: color .35s; }
.thermo small { font-size: .9rem; color: var(--bp-dim); }
.thermo.hot { color: var(--bp-bad); }

/* wiring rail */
.rail { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: opacity .3s; }
.rail .line { width: 100%; height: 2px; background: var(--bp-line); }
.rail .atag { position: absolute; font-size: .54rem; color: var(--bp-dim); background: var(--bp-bg); padding: 0 .25rem; }
.rail.dim { opacity: .25; }

/* invoker stack */
.invoker { padding: .7rem .8rem; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.02); overflow: hidden; }
.badge { font-size: .55rem; text-transform: none; letter-spacing: .04em; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 999px; padding: .05rem .4rem; transition: all .3s; }
.badge.lit { color: var(--bp-violet); border-color: rgba(167,139,250,.6); box-shadow: 0 0 12px rgba(167,139,250,.35); }
.stackcol { position: relative; flex: 1; min-height: 0; border: 1px dashed var(--bp-line); border-radius: 10px; padding: .4rem; overflow: hidden; }
.cards { display: flex; flex-direction: column; gap: .3rem; }
.placeholder { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: .72rem; color: var(--bp-dim); letter-spacing: .04em; }

.card { position: relative; border: 1px solid var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); padding: .25rem .5rem .3rem; transition: all .25s ease; }
.card.top { box-shadow: var(--bp-glow); border-color: var(--bp-cyan); background: rgba(34,211,238,.14); }
.card-edge { display: flex; align-items: center; justify-content: space-between; }
.verb { font-size: .52rem; letter-spacing: .1em; color: var(--bp-good); text-transform: uppercase; }
.verb.undoing { color: var(--bp-bad); }
.wire { color: var(--bp-violet); font-size: .72rem; filter: drop-shadow(0 0 6px rgba(167,139,250,.6)); }
.card-label { font-size: .76rem; color: #fff; }
.card-prev { font-size: .58rem; color: var(--bp-warn); }

/* pop: lift out the top card on undo */
.card.pop { animation: lift .25s ease forwards; }
@keyframes lift { to { transform: translateY(-30px); opacity: 0; } }

/* transition-group: cards drop in on push and lower cards shift smoothly */
.card-enter-active, .card-leave-active { transition: all .25s ease; }
.card-enter-from { opacity: 0; transform: translateY(-26px); }
.card-leave-to { opacity: 0; transform: translateY(-30px); }
.card-leave-active { position: absolute; left: .4rem; right: .4rem; }
.card-move { transition: transform .25s ease; }

.phase { font-size: .58rem; letter-spacing: .1em; color: var(--bp-dim); text-align: right; }
.phase.pushing { color: var(--bp-good); }
.phase.popping { color: var(--bp-bad); }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .6rem; align-items: flex-start; min-width: 0; overflow: hidden; }
.btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.b { font-family: inherit; font-size: .72rem; padding: .42rem .7rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 7px; background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.undo { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.1); box-shadow: var(--bp-glow); }
.b.undo:hover:not(:disabled) { background: rgba(34,211,238,.18); }
.b.ghost { color: var(--bp-dim); box-shadow: none; }
.b:disabled { opacity: .35; cursor: not-allowed; box-shadow: none; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(167,139,250,.4); } .tog.on .knob::after { left: 16px; background: var(--bp-violet); }
.tog.on { color: var(--bp-violet); }
.wirenote { font-size: .62rem; color: var(--bp-violet); border-left: 2px solid var(--bp-violet); padding-left: .5rem; }
.kpts { margin-top: .1rem; }
.kpts b { color: var(--bp-cyan); }
</style>
