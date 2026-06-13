<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

type CardState = 'idle' | 'active' | 'done' | 'skipped'
type Origin = 'inherited' | 'overridden' | 'hook'
type Recipe = 'tea' | 'coffee'

interface Step {
  id: string
  label: string
  origin: Origin
  hook?: boolean       // wants_condiments? card
  optional?: boolean   // add_condiments — may be skipped
}

// fixed, locked skeleton — order owned by the base class
const STEPS: Step[] = [
  { id: 'boil',   label: 'boil_water()',        origin: 'inherited' },
  { id: 'brew',   label: 'brew()',              origin: 'overridden' },
  { id: 'pour',   label: 'pour_in_cup()',       origin: 'inherited' },
  { id: 'want',   label: 'wants_condiments?',   origin: 'hook', hook: true },
  { id: 'cond',   label: 'add_condiments()',    origin: 'overridden', optional: true },
]

// subclass-supplied bodies for the OVERRIDDEN steps + the hook's returned value
const BODY: Record<Recipe, Record<string, string>> = {
  tea:    { brew: 'Steeping the tea',  cond: 'Adding lemon' },
  coffee: { brew: 'Dripping coffee',   cond: 'Adding sugar and milk' },
}
const TRANSCRIPT: Record<string, string> = {
  boil: 'Boiling water',
  pour: 'Pouring into cup',
}

const recipe = ref<Recipe>('tea')
const states = ref<CardState[]>(STEPS.map(() => 'idle'))
const cursor = ref(-1)          // index the token currently sits on; -1 = above pipeline
const log = ref<string[]>([])
const running = ref(false)
const arcing = ref(false)       // token visibly arcs around add_condiments (Tea)
let timer: ReturnType<typeof setTimeout> | null = null

// hook returns FALSE for tea (skip condiments), TRUE for coffee
const wantsCondiments = computed(() => recipe.value === 'coffee')

function bodyOf(id: string): string {
  const sub = BODY[recipe.value]
  if (id in sub) return sub[id]
  if (id in TRANSCRIPT) return TRANSCRIPT[id]
  if (id === 'want') return `return ${wantsCondiments.value ? 'TRUE' : 'FALSE'}`
  return ''
}

const ORIGIN_LABEL: Record<Origin, string> = {
  inherited: 'INHERITED', overridden: 'OVERRIDDEN', hook: 'HOOK',
}

function clearTimer() {
  if (timer !== null) { clearTimeout(timer); timer = null }
}

function resetCards() {
  clearTimer()
  states.value = STEPS.map(() => 'idle')
  cursor.value = -1
  log.value = []
  running.value = false
  arcing.value = false
}

function setRecipe(r: Recipe) {
  if (recipe.value === r && cursor.value === -1) return
  recipe.value = r
  resetCards()   // toggle rewrites bodies/chip and resets all cards to IDLE
}

// land the token on card i: ACTIVE -> (emit) -> DONE, honoring the hook decision
function landOn(i: number, onSettled: () => void) {
  const step = STEPS[i]
  // SKIP add_condiments when the hook said FALSE (Tea)
  if (step.optional && !wantsCondiments.value) {
    arcing.value = true
    states.value[i] = 'skipped'
    cursor.value = i
    timer = setTimeout(() => { arcing.value = false; onSettled() }, 450)
    return
  }
  cursor.value = i
  states.value[i] = 'active'
  timer = setTimeout(() => {
    states.value[i] = 'done'
    const line = bodyOf(step.id)
    if (step.id === 'want') log.value.push(`# hook -> ${wantsCondiments.value ? 'TRUE' : 'FALSE'}`)
    else log.value.push(line)
    onSettled()
  }, 450)
}

function run() {
  if (running.value) return
  resetCards()
  running.value = true
  log.value.push(`-- ${recipe.value === 'tea' ? 'Tea' : 'Coffee'} --`)
  const advance = (i: number) => {
    if (i >= STEPS.length) {
      timer = setTimeout(() => { running.value = false }, 200)
      return
    }
    landOn(i, () => { timer = setTimeout(() => advance(i + 1), 160) })
  }
  timer = setTimeout(() => advance(0), 250)
}

// Step: advance the token exactly one card per click, instantly settling it
function step() {
  if (running.value) return
  // if a full pass has already settled, start a fresh pass on this click
  if (cursor.value >= 0 && states.value.every(s => s !== 'idle')) resetCards()
  // find next idle card from cursor onward
  let next = cursor.value + 1
  while (next < STEPS.length && states.value[next] !== 'idle') next++
  if (next >= STEPS.length) return
  if (next === 0) log.value.push(`-- ${recipe.value === 'tea' ? 'Tea' : 'Coffee'} --`)
  const s = STEPS[next]
  if (s.optional && !wantsCondiments.value) {
    states.value[next] = 'skipped'
    cursor.value = next
    return
  }
  states.value[next] = 'done'
  cursor.value = next
  if (s.id === 'want') log.value.push(`# hook -> ${wantsCondiments.value ? 'TRUE' : 'FALSE'}`)
  else log.value.push(bodyOf(s.id))
}

const atEnd = computed(() => states.value.every(s => s !== 'idle'))

onBeforeUnmount(clearTimer)
</script>

<template>
  <div class="tm">
    <!-- STAGE: locked pipeline -->
    <div class="stage">
      <div class="frame">
        <span class="lock" title="order fixed by base class">
          <i class="pad" />LOCKED
        </span>

        <span class="token" :class="{ run: running, arc: arcing }"
              :style="{ '--row': cursor < 0 ? 0 : cursor + 1 }" />

        <div class="pipe">
          <div v-for="(s, i) in STEPS" :key="s.id"
               class="card" :class="[states[i], 'o-' + s.origin]"
               title="order fixed by base class">
            <div class="chead">
              <span class="cstep">{{ i + 1 }}</span>
              <span class="clabel">{{ s.label }}</span>
              <span class="badge" :class="'b-' + s.origin">{{ ORIGIN_LABEL[s.origin] }}</span>
            </div>
            <div class="cbody">
              <template v-if="s.hook">
                <span class="ret" :class="{ yes: wantsCondiments, no: !wantsCondiments }">
                  return {{ wantsCondiments ? 'TRUE' : 'FALSE' }}
                </span>
              </template>
              <template v-else>
                <span class="quote">"{{ bodyOf(s.id) }}"</span>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- transcript -->
      <div class="term">
        <div class="tbar"><span class="tdot" /><span class="tdot" /><span class="tdot" />stdout</div>
        <div class="tlines">
          <div v-for="(l, i) in log" :key="i" class="tline"
               :class="{ head: l.startsWith('--'), hook: l.startsWith('#') }">
            <span class="caret">{{ l.startsWith('--') || l.startsWith('#') ? ' ' : '▸' }}</span>{{ l }}
          </div>
          <div v-if="!log.length" class="tline empty">› awaiting prepare()</div>
        </div>
      </div>
    </div>

    <!-- CONTROLS -->
    <div class="panel">
      <div class="seg">
        <button :class="{ on: recipe === 'tea' }" @click="setRecipe('tea')">TEA</button>
        <button :class="{ on: recipe === 'coffee' }" @click="setRecipe('coffee')">COFFEE</button>
      </div>
      <div class="btns">
        <button class="b play" :disabled="running" @click="run">▶ run prepare()</button>
        <button class="b" :disabled="running || atEnd" @click="step">▸ step</button>
        <button class="b ghost" @click="resetCards">⟲ reset</button>
      </div>
      <div class="hint">
        <span class="hpad" /> base class owns the order — subclasses fill steps, never reorder
      </div>
      <ul class="kpts">
        <li><b>INHERITED</b> steps come straight from the base class</li>
        <li><b>OVERRIDDEN</b> steps swap body per subclass (Tea / Coffee)</li>
        <li>The <b>HOOK</b> decides whether add_condiments runs at all</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.tm {
  display: grid;
  grid-template-columns: 1.62fr 1fr;
  gap: 1.4rem;
  width: 100%;
  height: 340px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}
.stage { display: grid; grid-template-columns: 1.15fr .85fr; gap: 1rem; min-height: 0; }

/* ---- locked frame ---- */
.frame {
  position: relative;
  border: 1px solid var(--bp-line);
  border-radius: 12px;
  padding: .55rem .6rem .55rem 1.6rem;
  background: rgba(255, 255, 255, .02);
  overflow: hidden;
  min-height: 0;
}
.lock { position: absolute; top: 6px; right: 10px; display: inline-flex; align-items: center; gap: .3rem; font-size: .56rem; letter-spacing: .12em; color: var(--bp-warn); border: 1px solid var(--bp-warn); border-radius: 999px; padding: .08rem .5rem; background: var(--bp-bg); }
.pad { width: 8px; height: 7px; border: 1px solid var(--bp-warn); border-radius: 2px; position: relative; }
.pad::before { content: ''; position: absolute; left: 1px; top: -4px; width: 4px; height: 5px; border: 1px solid var(--bp-warn); border-bottom: 0; border-radius: 3px 3px 0 0; }

/* ---- pipeline of cards ---- */
.pipe { display: flex; flex-direction: column; gap: .34rem; position: relative; }
.card { cursor: not-allowed; border: 1px solid var(--bp-line); border-radius: 8px; padding: .3rem .5rem; background: rgba(255, 255, 255, .015); transition: opacity .3s, border-color .3s, box-shadow .3s, background .3s; opacity: .55; }
.card.idle { opacity: .5; }
.card.active { opacity: 1; border-color: var(--bp-cyan); box-shadow: var(--bp-glow); background: rgba(34, 211, 238, .1); animation: ring 1s ease-in-out infinite; }
.card.done { opacity: 1; border-color: var(--bp-cyan); border-width: 1px; background: rgba(34, 211, 238, .05); }
.card.skipped { opacity: .32; border-style: dashed; }
.card.skipped .clabel, .card.skipped .quote { text-decoration: line-through; }
@keyframes ring { 0%, 100% { box-shadow: 0 0 10px rgba(34, 211, 238, .35); } 50% { box-shadow: 0 0 22px rgba(34, 211, 238, .7); } }
.chead { display: flex; align-items: center; gap: .4rem; }
.cstep { font-size: .56rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 4px; padding: 0 .28rem; }
.clabel { font-size: .72rem; color: var(--bp-ink); flex: 1; }
.card.done .clabel { color: var(--bp-ink); }
.badge { font-size: .5rem; letter-spacing: .06em; padding: .05rem .35rem; border-radius: 999px; border: 1px solid var(--bp-line); }
.b-inherited { color: var(--bp-dim); }
.b-overridden { color: var(--bp-violet); border-color: rgba(167, 139, 250, .4); background: rgba(167, 139, 250, .08); }
.b-hook { color: var(--bp-warn); border-color: rgba(251, 191, 36, .4); background: rgba(251, 191, 36, .08); }
.cbody { margin-top: .12rem; padding-left: 1.1rem; }
.quote { font-size: .6rem; color: var(--bp-dim); }
.card.done .quote { color: var(--bp-cyan); }
.ret { font-size: .58rem; padding: .02rem .35rem; border-radius: 4px; }
.ret.yes { color: var(--bp-good); border: 1px solid rgba(74, 222, 128, .4); background: rgba(74, 222, 128, .08); }
.ret.no  { color: var(--bp-bad);  border: 1px solid rgba(251, 113, 133, .4); background: rgba(251, 113, 133, .08); }

/* ---- travelling token (left gutter) ---- */
.token {
  position: absolute;
  left: 6px;
  top: .55rem;
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: var(--bp-cyan);
  box-shadow: var(--bp-glow);
  opacity: 0;
  /* each row is ~ card height (38px) + gap (.34rem ~ 5.4px) */
  transform: translateY(calc((var(--row, 0) - 1) * 43.4px));
  transition: transform .42s ease, opacity .25s, left .42s ease;
}
.token.run { opacity: 1; }
.token.arc { left: 22px; }

/* ---- transcript ---- */
.term { border: 1px solid var(--bp-line); border-radius: 10px; background: var(--bp-bg-2); display: flex; flex-direction: column; overflow: hidden; min-height: 0; }
.tbar { display: flex; align-items: center; gap: .3rem; font-size: .56rem; color: var(--bp-dim); padding: .3rem .55rem; border-bottom: 1px solid var(--bp-line); letter-spacing: .1em; flex: 0 0 auto; }
.tdot { width: 6px; height: 6px; border-radius: 999px; background: var(--bp-line); }
.tdot:first-child { background: rgba(251, 113, 133, .6); }
.tdot:nth-child(2) { background: rgba(251, 191, 36, .6); }
.tlines { padding: .4rem .55rem; display: flex; flex-direction: column; gap: .12rem; overflow: auto; flex: 1 1 auto; min-height: 0; }
.tline { font-size: .62rem; color: var(--bp-ink); white-space: nowrap; animation: slip .25s ease; }
.tline .caret { color: var(--bp-cyan); margin-right: .3rem; }
.tline.head { color: var(--bp-violet); font-weight: 600; }
.tline.hook { color: var(--bp-warn); }
.tline.empty { color: var(--bp-dim); opacity: .6; animation: none; }
@keyframes slip { from { opacity: 0; transform: translateX(-6px); } to { opacity: 1; transform: translateX(0); } }

/* ---- controls ---- */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: flex-start; min-height: 0; overflow: hidden; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg button { font-family: inherit; font-size: .74rem; padding: .4rem 1.1rem; background: transparent; color: var(--bp-dim); cursor: pointer; border: 0; }
.seg button.on { background: rgba(34, 211, 238, .14); color: var(--bp-cyan); }
.btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.b { font-family: inherit; font-size: .74rem; padding: .42rem .7rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px; background: rgba(255, 255, 255, .03); cursor: pointer; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.play { border-color: var(--bp-cyan); color: var(--bp-ink); background: rgba(34, 211, 238, .12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .35; cursor: not-allowed; }
.hint { font-size: .64rem; color: var(--bp-dim); display: flex; align-items: center; gap: .4rem; line-height: 1.3; }
.hpad { flex: 0 0 auto; width: 9px; height: 8px; border: 1px solid var(--bp-warn); border-radius: 2px; position: relative; }
.hpad::before { content: ''; position: absolute; left: 1.5px; top: -4px; width: 4px; height: 5px; border: 1px solid var(--bp-warn); border-bottom: 0; border-radius: 3px 3px 0 0; }
.kpts { margin: .1rem 0 0; padding-left: 1.1rem; font-size: .68rem; color: var(--bp-dim); line-height: 1.5; }
.kpts b { color: var(--bp-ink); }
</style>
