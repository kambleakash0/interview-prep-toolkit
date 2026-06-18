<script setup lang="ts">
import { ref, computed, reactive, onBeforeUnmount } from 'vue'

/* ============================================================
   MachineCodingClock — the 90-minute machine-coding round, live.
   A budget timeline runs across the top; click a phase to open
   its checklist. Ticking items burns clock time and drives a
   live build panel: classify words -> classes/methods/enums,
   place the skeleton until it COMPILES, then fire edge cases
   that the guards visibly block. Design overspend glows red.
   ============================================================ */

const TOTAL = 90 // minutes on the clock

type PhaseId = 'clarify' | 'design' | 'skeleton' | 'core' | 'test'
interface Phase {
  id: PhaseId
  label: string
  min: number   // budget low
  max: number   // budget high
  budget: number // minutes this phase costs the cursor when complete
  tone: 'cyan' | 'violet' | 'blue' | 'good' | 'warn'
}

// segments sized to their budgets; the design slice is deliberately thin
const PHASES: Phase[] = [
  { id: 'clarify',  label: 'Clarify',  min: 3,  max: 5,  budget: 4,  tone: 'cyan'   },
  { id: 'design',   label: 'Design',   min: 5,  max: 10, budget: 9,  tone: 'violet' },
  { id: 'skeleton', label: 'Skeleton', min: 10, max: 15, budget: 13, tone: 'blue'   },
  { id: 'core',     label: 'Core',     min: 40, max: 50, budget: 45, tone: 'good'   },
  { id: 'test',     label: 'Edge & Test', min: 20, max: 25, budget: 19, tone: 'warn' },
]

const phase = ref<PhaseId>('clarify')
function goto(id: PhaseId) { phase.value = id }
const curPhase = computed(() => PHASES.find(p => p.id === phase.value)!)

const timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) {
  const t = setTimeout(fn, ms); timers.push(t); return t
}
onBeforeUnmount(() => { timers.forEach(clearTimeout) })

/* ---------- per-phase checklists; ticking burns clock time ---------- */
interface Check { id: string; text: string }
const CHECKS: Record<PhaseId, Check[]> = {
  clarify: [
    { id: 'io',    text: 'Nail I/O format + return shapes' },
    { id: 'valid', text: 'Validate inputs? graded tests?' },
    { id: 'scope', text: 'Split MUST vs NICE-to-have' },
  ],
  design: [
    { id: 'nva',   text: 'Noun-verb-adjective the prompt' },
    { id: 'cls',   text: 'Settle on 5-7 classes' },
    { id: 'store', text: 'Map<id,entity> vs List; enum vs bool' },
  ],
  skeleton: [
    { id: 'fields',text: 'Model fields + constructors' },
    { id: 'facade',text: 'StackOverflow manager (Facade)' },
    { id: 'compile',text: 'Make it COMPILE by minute 10' },
  ],
  core: [
    { id: 'enums', text: 'Bottom-up: enums -> models' },
    { id: 'svc',   text: 'service methods + Map stores' },
    { id: 'main',  text: 'Main as a runnable test harness' },
  ],
  test: [
    { id: 'bound', text: 'Boundary + null/empty' },
    { id: 'dup',   text: 'Dedup + auth (self-vote)' },
    { id: 'state', text: 'State + order; fix now, no TODO' },
  ],
}
// ticked[phaseId] = set of check ids
const ticked = reactive<Record<PhaseId, string[]>>({
  clarify: [], design: [], skeleton: [], core: [], test: [],
})
function isTicked(p: PhaseId, id: string) { return ticked[p].includes(id) }
function toggleCheck(id: string) {
  const list = ticked[phase.value]
  const i = list.indexOf(id)
  if (i >= 0) list.splice(i, 1)
  else list.push(id)
}
function phaseDone(p: PhaseId) { return ticked[p].length >= CHECKS[p].length }

// elapsed clock cursor = sum of budgets of completed phases + partial of current
const elapsedMin = computed(() => {
  let mins = 0
  for (const p of PHASES) {
    const done = ticked[p.id].length
    const frac = done / CHECKS[p.id].length
    mins += p.budget * frac
  }
  return Math.round(mins)
})
const cursorPct = computed(() => Math.min(100, (elapsedMin.value / TOTAL) * 100))

// design overspend: design cursor share > 20% of the clock => red meter
const designSharePct = computed(() => {
  const d = PHASES.find(p => p.id === 'design')!
  const frac = ticked.design.length / CHECKS.design.length
  return Math.round((d.budget * frac / TOTAL) * 100)
})
// overspend is a teaching flag: thin slice is the lesson, so we flag if the
// learner lingers in design (all ticked) while skeleton/core untouched
const designOverspend = computed(() =>
  phaseDone('design') && ticked.skeleton.length === 0 && ticked.core.length === 0
)

/* ---------- DESIGN: classify words of the prompt sentence ---------- */
type WClass = 'class' | 'method' | 'enum' | 'plain'
interface Word { t: string; truth?: Exclude<WClass, 'plain'> }
// the one-sentence Stack Overflow prompt, tokenised; only tagged words score
const PROMPT: Word[] = [
  { t: 'A ' }, { t: 'user', truth: 'class' }, { t: ' can ' },
  { t: 'ask', truth: 'method' }, { t: ' a ' }, { t: 'question', truth: 'class' },
  { t: ', then others ' }, { t: 'vote', truth: 'method' }, { t: ' it ' },
  { t: 'up', truth: 'enum' }, { t: ' or ' }, { t: 'down', truth: 'enum' },
  { t: '.' },
]
// learner's chosen tag per word index
const tagged = reactive<Record<number, Exclude<WClass, 'plain'>>>({})
const armedClass = ref<Exclude<WClass, 'plain'>>('class') // which bucket the click drops into
function setArmed(c: Exclude<WClass, 'plain'>) { armedClass.value = c }
function classify(i: number) {
  const w = PROMPT[i]
  if (!w.truth) return
  if (tagged[i] === armedClass.value) { delete tagged[i]; return }
  tagged[i] = armedClass.value
}
function wordCorrect(i: number) {
  return PROMPT[i].truth && tagged[i] === PROMPT[i].truth
}
function wordWrong(i: number) {
  return PROMPT[i].truth && tagged[i] !== undefined && tagged[i] !== PROMPT[i].truth
}
const allClassified = computed(() =>
  PROMPT.every((w, i) => !w.truth || wordCorrect(i))
)
// derived buckets from CORRECT classifications, shown as chips
const buckets = computed(() => {
  const out: Record<Exclude<WClass, 'plain'>, string[]> = { class: [], method: [], enum: [] }
  PROMPT.forEach((w, i) => { if (wordCorrect(i)) out[w.truth!].push(w.t) })
  return out
})

/* ---------- SKELETON/CORE: class graph + Compiles? badge ---------- */
interface Node { id: string; x: number; y: number }
const NODES: Node[] = [
  { id: 'User',          x: 8,   y: 8  },
  { id: 'Question',      x: 116, y: 8  },
  { id: 'Vote',         x: 116, y: 70 },
  { id: 'Answer',        x: 8,   y: 70 },
  { id: 'StackOverflow', x: 62,  y: 132 },
]
interface Link { from: string; to: string }
const LINKS: Link[] = [
  { from: 'User', to: 'Question' },
  { from: 'Question', to: 'Vote' },
  { from: 'User', to: 'Answer' },
  { from: 'StackOverflow', to: 'User' },
  { from: 'StackOverflow', to: 'Question' },
]
// a node is "placed" once Skeleton's fields/facade checks are ticked
const placed = computed<string[]>(() => {
  const out: string[] = []
  if (isTicked('skeleton', 'fields')) out.push('User', 'Question', 'Vote', 'Answer')
  if (isTicked('skeleton', 'facade')) out.push('StackOverflow')
  return out
})
function nodePlaced(id: string) { return placed.value.includes(id) }
function linkLive(l: Link) { return nodePlaced(l.from) && nodePlaced(l.to) }
function nx(id: string) { return NODES.find(n => n.id === id)!.x + 49 }
function ny(id: string) { return NODES.find(n => n.id === id)!.y + 17 }
// compiles only once the skeleton's COMPILE check is ticked AND all nodes placed
const compiles = computed(() =>
  isTicked('skeleton', 'compile') && placed.value.length >= NODES.length
)

/* ---------- EDGE CASES: fire a case, watch the guard block it ---------- */
interface EdgeCase {
  id: string; label: string; call: string; guard: string
}
const CASES: EdgeCase[] = [
  { id: 'self', label: 'self-vote',     call: 'q.vote(author, UP)',  guard: 'voter.id == author.id -> reject' },
  { id: 'dup',  label: 'duplicate vote', call: 'q.vote(u, UP) x2',    guard: 'voter.id in votes -> reject' },
  { id: 'empty',label: 'empty title',   call: 'ask_question(u, "")', guard: 'not title.strip() -> reject' },
]
const fired = ref('')        // case id currently firing
const blocked = ref('')      // case id that was blocked (sticky result)
const firing = ref(false)
function fireCase(c: EdgeCase) {
  if (firing.value) return
  // guards only exist once the test-phase hardening checks are ticked
  firing.value = true
  fired.value = c.id
  blocked.value = ''
  later(() => {
    blocked.value = c.id
    firing.value = false
  }, 560)
}
const guardsArmed = computed(() => ticked.test.length > 0)

function resetAll() {
  for (const p of PHASES) ticked[p.id].length = 0
  for (const k of Object.keys(tagged)) delete tagged[Number(k)]
  fired.value = ''; blocked.value = ''; firing.value = false
  phase.value = 'clarify'
}
</script>

<template>
  <div class="mc">
    <!-- ===== top: 90-minute budget timeline ===== -->
    <div class="timeline">
      <div class="tlbar">
        <button
          v-for="p in PHASES" :key="p.id"
          class="seg" :class="[p.tone, { on: phase === p.id, done: phaseDone(p.id) }]"
          :style="{ flex: p.budget }"
          @click="goto(p.id)"
        >
          <span class="seglbl">{{ p.label }}</span>
          <span class="segbud">{{ p.min }}-{{ p.max }}m</span>
        </button>
        <!-- live clock cursor riding the timeline -->
        <div class="cursor" :style="{ left: cursorPct + '%' }">
          <span class="cdot" />
          <span class="cmin">{{ elapsedMin }}m</span>
        </div>
      </div>
      <div class="tlfoot">
        <span class="budmeter" :class="{ over: designOverspend }">
          design budget <b>{{ designSharePct }}%</b>
          <span class="capnote">of {{ TOTAL }}m · cap 20%</span>
        </span>
        <span class="clock">clock <b>{{ elapsedMin }}/{{ TOTAL }}m</b></span>
      </div>
    </div>

    <!-- ===== stage: left checklist | right live build ===== -->
    <div class="stage">
      <!-- ---- left: phase checklist ---- -->
      <div class="col checks">
        <div class="ttl" :class="curPhase.tone">{{ curPhase.label }} checklist</div>
        <button
          v-for="c in CHECKS[phase]" :key="c.id"
          class="chk" :class="{ on: isTicked(phase, c.id) }"
          @click="toggleCheck(c.id)"
        >
          <span class="cbox">{{ isTicked(phase, c.id) ? '✓' : '' }}</span>
          <span class="ctxt">{{ c.text }}</span>
        </button>

        <div v-if="designOverspend" class="aha warn">
          Design is ticked but nothing is built — momentum lives in Skeleton/Core. Move on.
        </div>
        <div v-else class="aha">
          Tick items to burn the clock. Design is a thin slice; what RUNS wins.
        </div>
      </div>

      <!-- ---- right: live build panel, swaps by phase ---- -->
      <div class="col build">
        <!-- DESIGN: word classifier -->
        <template v-if="phase === 'design'">
          <div class="ttl violet">Noun-verb-adjective the prompt</div>
          <div class="armrow">
            <button class="arm class"  :class="{ on: armedClass === 'class' }"  @click="setArmed('class')">noun -> class</button>
            <button class="arm method" :class="{ on: armedClass === 'method' }" @click="setArmed('method')">verb -> method</button>
            <button class="arm enum"   :class="{ on: armedClass === 'enum' }"   @click="setArmed('enum')">state -> enum</button>
          </div>
          <p class="prompt">
            <template v-for="(w, i) in PROMPT" :key="i"><span
              v-if="w.truth" class="word"
              :class="{ ok: wordCorrect(i), bad: wordWrong(i), tagged: tagged[i] }"
              @click="classify(i)">{{ w.t }}<sub v-if="tagged[i]" class="wtag">{{ tagged[i] }}</sub></span><span
              v-else>{{ w.t }}</span></template>
          </p>
          <div class="bgrid">
            <div class="bbox class"><b>classes</b> {{ buckets.class.join(', ') || '—' }}</div>
            <div class="bbox method"><b>methods</b> {{ buckets.method.join(', ') || '—' }}</div>
            <div class="bbox enum"><b>enums</b> {{ buckets.enum.join(', ') || '—' }}</div>
          </div>
          <div class="aha" :class="{ good: allClassified }">
            {{ allClassified ? 'All words classified — that IS your class list.' : 'Arm a bucket, then click the matching word.' }}
          </div>
        </template>

        <!-- TEST: edge-case cards vs guards -->
        <template v-else-if="phase === 'test'">
          <div class="ttl warn">Fire an edge case</div>
          <div class="cases">
            <div
              v-for="c in CASES" :key="c.id"
              class="case" :class="{ firing: fired === c.id && firing, blocked: blocked === c.id }"
            >
              <div class="crow">
                <button class="firebtn" :disabled="firing || !guardsArmed" @click="fireCase(c)">fire</button>
                <span class="cname">{{ c.label }}</span>
                <code class="ccall">{{ c.call }}</code>
              </div>
              <transition name="reveal">
                <div v-if="blocked === c.id" class="guardline">
                  <span class="shield">BLOCKED</span> {{ c.guard }}
                </div>
              </transition>
            </div>
          </div>
          <div class="aha" :class="{ good: blocked, warn: !guardsArmed }">
            {{ !guardsArmed ? 'Tick a hardening item first — no guard, no block.'
               : (blocked ? 'The guard threw before any mutation. State stays clean.'
               : 'Fire a case — the guard rejects it at the boundary.') }}
          </div>
        </template>

        <!-- CLARIFY / SKELETON / CORE: class graph + Compiles badge -->
        <template v-else>
          <div class="bhead">
            <span class="ttl blue">Class graph</span>
            <span class="cbadge" :class="{ green: compiles }">
              Compiles? {{ compiles ? 'YES' : 'no' }}
            </span>
          </div>
          <div class="graph">
            <svg class="glinks" viewBox="0 0 222 166" preserveAspectRatio="none">
              <g v-for="(l, i) in LINKS" :key="i" v-show="linkLive(l)">
                <line :x1="nx(l.from)" :y1="ny(l.from)" :x2="nx(l.to)" :y2="ny(l.to)" />
              </g>
            </svg>
            <div
              v-for="n in NODES" :key="n.id"
              class="gnode" :class="{ live: nodePlaced(n.id), mgr: n.id === 'StackOverflow' }"
              :style="{ left: n.x + 'px', top: n.y + 'px' }"
            >{{ n.id }}</div>
          </div>
          <div class="aha" :class="{ good: compiles }">
            {{ compiles ? 'Skeleton compiles — now fill bottom-up, it stays green.'
               : 'Open the Skeleton phase and tick fields + Facade to place classes.' }}
          </div>
        </template>
      </div>
    </div>

    <!-- footer -->
    <div class="footer">
      <span>Design is a thin slice — the round is won by a skeleton that compiles and a Main that RUNS.</span>
      <button class="reset" @click="resetAll">&#9851; reset</button>
    </div>
  </div>
</template>

<style scoped>
.mc {
  width: 100%; height: 360px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: .6rem;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}

/* ---------- timeline ---------- */
.timeline { display: flex; flex-direction: column; gap: .35rem; }
.tlbar { position: relative; display: flex; gap: 3px; height: 38px; }
.seg {
  position: relative; font-family: inherit; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 7px;
  background: rgba(255,255,255,.02); color: var(--bp-dim);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 1px; min-width: 0; overflow: hidden; transition: all .25s; padding: 0 .2rem;
}
.seg:hover { color: var(--bp-ink); }
.seglbl { font-size: .62rem; white-space: nowrap; }
.segbud { font-size: .5rem; opacity: .7; }
.seg.cyan:hover   { border-color: var(--bp-cyan); }
.seg.violet:hover { border-color: var(--bp-violet); }
.seg.blue:hover   { border-color: var(--bp-blue); }
.seg.good:hover   { border-color: var(--bp-good); }
.seg.warn:hover   { border-color: var(--bp-warn); }
.seg.on { color: #fff; box-shadow: var(--bp-glow); }
.seg.on.cyan   { border-color: var(--bp-cyan);   background: rgba(34,211,238,.14); }
.seg.on.violet { border-color: var(--bp-violet); background: rgba(167,139,250,.14); box-shadow: 0 0 22px rgba(167,139,250,.4); }
.seg.on.blue   { border-color: var(--bp-blue);   background: rgba(56,189,248,.14); }
.seg.on.good   { border-color: var(--bp-good);   background: rgba(74,222,128,.14); box-shadow: 0 0 22px rgba(74,222,128,.35); }
.seg.on.warn   { border-color: var(--bp-warn);   background: rgba(251,191,36,.14); box-shadow: 0 0 22px rgba(251,191,36,.35); }
.seg.done::after {
  content: '✓'; position: absolute; top: 2px; right: 4px;
  font-size: .5rem; color: var(--bp-good);
}

/* clock cursor */
.cursor {
  position: absolute; top: -7px; bottom: -7px; width: 0;
  pointer-events: none; transition: left .45s cubic-bezier(.4,0,.2,1);
}
.cdot {
  position: absolute; top: 0; bottom: 0; left: -1px; width: 2px;
  background: var(--bp-cyan); box-shadow: var(--bp-glow);
}
.cmin {
  position: absolute; top: -14px; left: 50%; transform: translateX(-50%);
  font-size: .52rem; color: var(--bp-cyan); white-space: nowrap;
  background: var(--bp-bg); padding: 0 .2rem; border-radius: 3px;
}

.tlfoot { display: flex; align-items: center; justify-content: space-between; font-size: .58rem; color: var(--bp-dim); }
.budmeter { display: inline-flex; align-items: baseline; gap: .35rem; border: 1px solid var(--bp-line); border-radius: 999px; padding: .12rem .6rem; transition: all .3s; }
.budmeter b { color: var(--bp-good); }
.budmeter .capnote { font-size: .5rem; opacity: .65; }
.budmeter.over { border-color: var(--bp-bad); background: rgba(251,113,133,.1); color: var(--bp-bad); animation: pulseBad 1.1s infinite; }
.budmeter.over b { color: var(--bp-bad); }
@keyframes pulseBad { 0%,100% { box-shadow: 0 0 0 rgba(251,113,133,0); } 50% { box-shadow: 0 0 14px rgba(251,113,133,.55); } }
.clock b { color: var(--bp-cyan); }

/* ---------- stage ---------- */
.stage {
  flex: 1; min-height: 0; display: grid; grid-template-columns: 1fr 1.25fr; gap: .9rem;
  border: 1px solid var(--bp-line); border-radius: 12px;
  background: rgba(255,255,255,.015); padding: .75rem .85rem; overflow: hidden;
}
.col { display: flex; flex-direction: column; gap: .45rem; min-width: 0; min-height: 0; }
.ttl { font-size: .64rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-cyan); }
.ttl.violet { color: var(--bp-violet); }
.ttl.blue { color: var(--bp-blue); }
.ttl.good { color: var(--bp-good); }
.ttl.warn { color: var(--bp-warn); }
.ttl.cyan { color: var(--bp-cyan); }

/* ---------- checklist ---------- */
.chk {
  display: flex; align-items: center; gap: .55rem; text-align: left;
  font-family: inherit; font-size: .68rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .34rem .55rem;
  background: rgba(255,255,255,.02); color: var(--bp-dim); transition: all .2s;
}
.chk:hover { border-color: var(--bp-cyan); color: var(--bp-ink); }
.chk.on { color: #fff; border-color: var(--bp-good); background: rgba(74,222,128,.08); }
.cbox {
  flex: 0 0 auto; width: 15px; height: 15px; border-radius: 4px;
  border: 1px solid var(--bp-line); display: inline-flex; align-items: center; justify-content: center;
  font-size: .6rem; color: var(--bp-good);
}
.chk.on .cbox { border-color: var(--bp-good); background: rgba(74,222,128,.18); }
.ctxt { line-height: 1.3; }
.aha { font-size: .58rem; color: var(--bp-dim); margin-top: auto; line-height: 1.4; }
.aha.good { color: var(--bp-good); }
.aha.warn { color: var(--bp-warn); }

/* ---------- design: classifier ---------- */
.armrow { display: flex; gap: .35rem; flex-wrap: wrap; }
.arm {
  font-family: inherit; font-size: .56rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 999px; padding: .18rem .5rem;
  background: rgba(255,255,255,.02); color: var(--bp-dim); transition: all .2s;
}
.arm.class.on   { border-color: var(--bp-cyan);   color: #fff; background: rgba(34,211,238,.16); box-shadow: var(--bp-glow); }
.arm.method.on  { border-color: var(--bp-blue);   color: #fff; background: rgba(56,189,248,.16); }
.arm.enum.on    { border-color: var(--bp-violet); color: #fff; background: rgba(167,139,250,.16); }
.prompt { font-size: .76rem; line-height: 2; color: var(--bp-dim); margin: 0; }
.word {
  position: relative; cursor: pointer; color: var(--bp-ink);
  border-bottom: 1px dashed var(--bp-line); padding: 0 1px; transition: all .2s;
}
.word:hover { color: var(--bp-cyan); border-color: var(--bp-cyan); }
.word.tagged { border-bottom-style: solid; }
.word.ok  { color: var(--bp-good); border-color: var(--bp-good); }
.word.bad { color: var(--bp-bad);  border-color: var(--bp-bad); animation: shake .35s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-3px)} 75%{transform:translateX(3px)} }
.wtag { font-size: .42rem; vertical-align: sub; color: var(--bp-dim); margin-left: 1px; }
.bgrid { display: flex; flex-direction: column; gap: .25rem; }
.bbox { font-size: .56rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 6px; padding: .18rem .45rem; }
.bbox b { margin-right: .4rem; text-transform: uppercase; letter-spacing: .06em; }
.bbox.class b  { color: var(--bp-cyan); }
.bbox.method b { color: var(--bp-blue); }
.bbox.enum b   { color: var(--bp-violet); }

/* ---------- class graph ---------- */
.bhead { display: flex; align-items: center; justify-content: space-between; }
.cbadge {
  font-size: .54rem; letter-spacing: .06em; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 999px; padding: .12rem .5rem; transition: all .3s;
}
.cbadge.green { color: var(--bp-good); border-color: var(--bp-good); background: rgba(74,222,128,.12); box-shadow: 0 0 14px rgba(74,222,128,.4); }
.graph { position: relative; width: 222px; height: 166px; align-self: center; }
.glinks { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.glinks line { stroke: var(--bp-cyan); stroke-width: 1.3; opacity: .7; }
.gnode {
  position: absolute; width: 98px; height: 34px; box-sizing: border-box;
  border: 1px dashed var(--bp-line); border-radius: 7px; background: var(--bp-bg-2);
  display: flex; align-items: center; justify-content: center;
  font-size: .58rem; color: var(--bp-dim); transition: all .3s;
}
.gnode.live { border-style: solid; border-color: var(--bp-cyan); color: var(--bp-ink); background: rgba(34,211,238,.06); }
.gnode.mgr { width: 110px; left: 56px !important; }
.gnode.mgr.live { border-color: var(--bp-violet); color: #fff; background: rgba(167,139,250,.1); box-shadow: 0 0 14px rgba(167,139,250,.3); }

/* ---------- edge cases ---------- */
.cases { display: flex; flex-direction: column; gap: .4rem; }
.case { border: 1px solid var(--bp-line); border-radius: 8px; padding: .35rem .5rem; background: rgba(255,255,255,.02); transition: all .25s; }
.case.firing { border-color: var(--bp-warn); background: rgba(251,191,36,.08); }
.case.blocked { border-color: var(--bp-good); background: rgba(74,222,128,.06); }
.crow { display: flex; align-items: center; gap: .5rem; }
.firebtn {
  font-family: inherit; font-size: .56rem; cursor: pointer; flex: 0 0 auto;
  border: 1px solid var(--bp-bad); border-radius: 6px; padding: .14rem .5rem;
  background: rgba(251,113,133,.1); color: var(--bp-bad); transition: all .2s;
}
.firebtn:hover:not(:disabled) { background: rgba(251,113,133,.22); color: #fff; }
.firebtn:disabled { opacity: .4; cursor: not-allowed; }
.cname { font-size: .62rem; color: var(--bp-ink); }
.ccall { font-size: .54rem; color: var(--bp-cyan); margin-left: auto; }
.guardline { font-size: .56rem; color: var(--bp-good); margin-top: .28rem; padding-left: .1rem; }
.shield {
  font-size: .5rem; letter-spacing: .08em; color: var(--bp-bg); background: var(--bp-good);
  border-radius: 4px; padding: .04rem .35rem; margin-right: .4rem;
}

/* ---------- footer ---------- */
.footer {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  font-size: .58rem; color: var(--bp-dim); border-top: 1px solid var(--bp-line);
  padding-top: .35rem; letter-spacing: .03em;
}
.reset {
  font-family: inherit; font-size: .58rem; cursor: pointer; flex: 0 0 auto;
  border: 1px solid var(--bp-line); border-radius: 7px; padding: .2rem .55rem;
  background: rgba(255,255,255,.03); color: var(--bp-dim); transition: all .2s;
}
.reset:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }

/* ---------- transitions ---------- */
.reveal-enter-active { transition: all .3s ease; }
.reveal-enter-from { opacity: 0; transform: translateY(-4px); }
</style>
