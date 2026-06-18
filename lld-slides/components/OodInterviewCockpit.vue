<script setup lang="ts">
import { ref, computed, reactive, onBeforeUnmount } from 'vue'

/* ============================================================
   OodInterviewCockpit — the 5-step "Design X" framework, live.
   Click the rail to move between steps; each step is a tiny
   interactive proof of one idea: clarify -> entities -> classes
   -> patterns -> use cases.
   ============================================================ */

type StepId = 1 | 2 | 3 | 4 | 5
interface RailStep { id: StepId; label: string; budget: string }

const RAIL: RailStep[] = [
  { id: 1, label: 'Clarify',  budget: '5m'  },
  { id: 2, label: 'Entities', budget: '5m'  },
  { id: 3, label: 'Classes',  budget: '25m' },
  { id: 4, label: 'Patterns', budget: '7m'  },
  { id: 5, label: 'Use Cases',budget: '10m' },
]

const step = ref<StepId>(1)
function goto(id: StepId) { step.value = id }

const timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) {
  const t = setTimeout(fn, ms); timers.push(t); return t
}
onBeforeUnmount(() => { timers.forEach(clearTimeout) })

/* ---------- STEP 1: clarify scope via interviewer Q&A ---------- */
interface Clarify {
  q: string
  a: string
  feature: string      // requirement chip this question toggles
  inScope: boolean     // does asking pull it INTO scope?
}
const clarifies = reactive<Clarify[]>([
  { q: 'Support moderators?', a: 'No — out of scope. Skip the role hierarchy.',         feature: 'Moderation', inScope: false },
  { q: 'Include tagging?',    a: 'Yes — tags are core. Add a Tag entity.',              feature: 'Tags',       inScope: true  },
  { q: 'Real-time feed?',     a: 'No — batch is fine. Drop the websocket layer.',        feature: 'Live feed',  inScope: false },
])
const asked = ref<number[]>([])
function ask(i: number) {
  if (!asked.value.includes(i)) asked.value.push(i)
}
// requirements that survive the clarify pass = base set minus what we cut + what we kept
const BASE_REQS = ['Post Q&A', 'Vote', 'Comment', 'Reputation']
const scopeReqs = computed(() => {
  const kept = clarifies.filter((c, i) => asked.value.includes(i) && c.inScope).map(c => c.feature)
  const cut  = clarifies.filter((c, i) => asked.value.includes(i) && !c.inScope).map(c => c.feature)
  return { kept, cut, total: BASE_REQS.length + kept.length }
})

/* ---------- STEP 2: noun-extraction into entity tray (cap 6) ---------- */
// the requirements paragraph, tokenised; nouns are clickable
interface Token { t: string; noun?: string }   // noun present => clickable, maps to entity
const PARA: Token[] = [
  { t: 'A ' }, { t: 'user', noun: 'User' }, { t: ' posts a ' },
  { t: 'question', noun: 'Question' }, { t: ' and others post an ' },
  { t: 'answer', noun: 'Answer' }, { t: '. Each adds a ' },
  { t: 'comment', noun: 'Comment' }, { t: ', applies a ' },
  { t: 'tag', noun: 'Tag' }, { t: ', and casts a ' },
  { t: 'vote', noun: 'Vote' }, { t: ' that drives reputation.' },
]
const CORE_ENTITIES = ['User', 'Question', 'Answer', 'Comment', 'Tag', 'Vote']
const tray = ref<string[]>([])
const trayFull = computed(() => tray.value.length >= 6)
function pick(noun?: string) {
  if (!noun) return
  if (tray.value.includes(noun)) { tray.value = tray.value.filter(n => n !== noun); return }
  if (trayFull.value) return
  tray.value.push(noun)
}
const pickedAll = computed(() => CORE_ENTITIES.every(e => tray.value.includes(e)))

/* ---------- STEP 3: class canvas, edges, extract-interface ---------- */
interface Box { id: string; x: number; y: number }
// fixed pretty layout for the 6 core entities on the canvas
const BOXES: Box[] = [
  { id: 'User',     x: 18,  y: 12 },
  { id: 'Question', x: 152, y: 12 },
  { id: 'Answer',   x: 152, y: 96 },
  { id: 'Comment',  x: 288, y: 12 },
  { id: 'Tag',      x: 288, y: 96 },
  { id: 'Vote',     x: 18,  y: 96 },
]
interface Edge { id: string; from: string; to: string; label: string; comp: boolean }
// the relationships the learner can toggle on; comp = composition (filled diamond)
const EDGES: Edge[] = [
  { id: 'q-a', from: 'Question', to: 'Answer',  label: 'owns',  comp: true  },
  { id: 'q-t', from: 'Question', to: 'Tag',     label: 'has',   comp: false },
  { id: 'a-v', from: 'Answer',   to: 'Vote',    label: 'gets',  comp: true  },
  { id: 'u-q', from: 'User',     to: 'Question',label: 'asks',  comp: false },
]
const drawn = ref<string[]>([])
function toggleEdge(id: string) {
  drawn.value.includes(id)
    ? (drawn.value = drawn.value.filter(e => e !== id))
    : drawn.value.push(id)
}
const compMode = ref(true)   // toggle: show composition styling vs flatten to association
const extracted = ref(false) // interfaces lifted?
function box(id: string) { return BOXES.find(b => b.id === id)! }
// center point of a box (box is 116x66)
function cx(id: string) { return box(id).x + 58 }
function cy(id: string) { return box(id).y + 33 }

/* ---------- STEP 4: pattern shelf, drop onto target class ---------- */
interface Pattern {
  id: string; name: string; target: string
  what: string; why: string; how: string
}
const PATTERNS: Pattern[] = [
  { id: 'strategy', name: 'Strategy', target: 'Reputation',
    what: 'Swappable reputation rules', why: 'Scoring policy changes often',
    how: 'ReputationStrategy.score(event)' },
  { id: 'observer', name: 'Observer', target: 'Notify',
    what: 'Fan-out notifications', why: 'Many watchers, one event',
    how: 'subject.notify(observers)' },
  { id: 'facade',   name: 'Facade',   target: 'StackOverflow',
    what: 'One entry-point API', why: 'Hide subsystem wiring',
    how: 'so.voteOnContent(...)' },
]
// drop slots on the diagram; correct id matches a pattern target
interface Slot { id: string; label: string; accepts: string }
const SLOTS: Slot[] = [
  { id: 'Reputation',    label: 'Reputation rules', accepts: 'strategy' },
  { id: 'Notify',        label: 'Notification hub',  accepts: 'observer' },
  { id: 'StackOverflow', label: 'StackOverflow mgr', accepts: 'facade'   },
  { id: 'Vote',          label: 'Vote (value obj)',  accepts: '__none'   },
]
const placed = reactive<Record<string, string>>({})  // slotId -> patternId (correct only)
const selPattern = ref<string>('')                    // currently armed pattern
const badDrop = ref('')                               // slotId flashing "don't pattern-drop"
const activeTip = ref('')                             // slotId whose tooltip shows
function armPattern(id: string) { selPattern.value = selPattern.value === id ? '' : id }
function dropOn(slot: Slot) {
  if (!selPattern.value) return
  if (slot.accepts === selPattern.value) {
    placed[slot.id] = selPattern.value
    activeTip.value = slot.id
    selPattern.value = ''
  } else {
    badDrop.value = slot.id
    later(() => { if (badDrop.value === slot.id) badDrop.value = '' }, 1100)
  }
}
const patternOf = (id: string) => PATTERNS.find(p => p.id === id)

/* ---------- STEP 5: walk vote-on-answer, with edge-case traps ---------- */
interface FlowStep { k: string; label: string }
const FLOW: FlowStep[] = [
  { k: 'vote',  label: 'vote()' },
  { k: 'obj',   label: 'new Vote' },
  { k: 'score', label: 'score++' },
  { k: 'strat', label: 'ReputationStrategy(+10)' },
  { k: 'rep',   label: 'author.reputation' },
  { k: 'notify',label: 'Observer.notify()' },
]
const flowAt = ref(-1)            // index of token along FLOW; -1 = not started
const flowRunning = ref(false)
const trapSelf = ref(false)       // self-vote trap armed
const trapDup = ref(false)        // duplicate-vote trap armed
const thrown = ref('')            // exception text, '' when none
const flowDone = ref(false)

function resetFlow() {
  flowAt.value = -1; flowRunning.value = false; thrown.value = ''; flowDone.value = false
}
function playFlow() {
  if (flowRunning.value) return
  resetFlow()
  flowRunning.value = true
  // traps fire at the very first hop — guards run before mutation
  if (trapSelf.value || trapDup.value) {
    flowAt.value = 0
    later(() => {
      thrown.value = trapSelf.value
        ? 'IllegalVote: cannot vote on your own answer'
        : 'DuplicateVote: this user already voted'
      flowRunning.value = false
    }, 420)
    return
  }
  const hop = (i: number) => {
    if (i >= FLOW.length) {
      flowDone.value = true; flowRunning.value = false; return
    }
    flowAt.value = i
    later(() => hop(i + 1), 520)
  }
  later(() => hop(0), 200)
}
</script>

<template>
  <div class="ck">
    <!-- ===== top rail: 5 steps + budget clock ===== -->
    <div class="rail">
      <template v-for="(s, i) in RAIL" :key="s.id">
        <button class="rstep" :class="{ on: step === s.id, done: step > s.id }" @click="goto(s.id)">
          <span class="rnum">{{ s.id }}</span>
          <span class="rlbl">{{ s.label }}</span>
          <span class="rbud">{{ s.budget }}</span>
        </button>
        <span v-if="i < RAIL.length - 1" class="rconn" :class="{ lit: step > s.id }" />
      </template>
      <span class="clock">budget&nbsp;<b>50m</b></span>
    </div>

    <!-- ===== stage: one panel per step ===== -->
    <div class="stage">

      <!-- ---------- STEP 1 ---------- -->
      <div v-if="step === 1" class="panel s1">
        <div class="col">
          <div class="ttl">Ask before you code</div>
          <div class="qa">
            <div v-for="(c, i) in clarifies" :key="c.q" class="qline">
              <button class="qbtn" :class="{ used: asked.includes(i) }" @click="ask(i)">
                <span class="bullet">?</span>{{ c.q }}
              </button>
              <transition name="reveal">
                <span v-if="asked.includes(i)" class="ans" :class="c.inScope ? 'in' : 'out'">
                  {{ c.a }}
                </span>
              </transition>
            </div>
          </div>
          <div class="aha">Every answer shrinks or shapes the build — scope is a choice.</div>
        </div>
        <div class="col">
          <div class="ttl">Live requirements&nbsp;<span class="cnt">{{ scopeReqs.total }}</span></div>
          <div class="chips">
            <span v-for="r in BASE_REQS" :key="r" class="chip base">{{ r }}</span>
            <span v-for="r in scopeReqs.kept" :key="r" class="chip add">+ {{ r }}</span>
            <span v-for="r in scopeReqs.cut" :key="r" class="chip cut">— {{ r }}</span>
          </div>
          <div class="legend">
            <span class="lg base">core</span>
            <span class="lg add">in-scope</span>
            <span class="lg cut">cut</span>
          </div>
        </div>
      </div>

      <!-- ---------- STEP 2 ---------- -->
      <div v-else-if="step === 2" class="panel s2">
        <div class="col wide">
          <div class="ttl">Click the nouns</div>
          <p class="para">
            <template v-for="(tok, i) in PARA" :key="i"><span
              v-if="tok.noun" class="noun" :class="{ on: tray.includes(tok.noun) }"
              @click="pick(tok.noun)">{{ tok.t }}</span><span v-else>{{ tok.t }}</span></template>
          </p>
          <div class="hintline">Verbs <code>vote()</code> / <code>comment()</code> become interfaces in Step 3.</div>
        </div>
        <div class="col">
          <div class="ttl">Entity tray
            <span class="cap" :class="{ full: trayFull }">{{ tray.length }}/6</span>
          </div>
          <div class="etray">
            <transition-group name="pop">
              <span v-for="e in tray" :key="e" class="ent" @click="pick(e)">{{ e }}</span>
            </transition-group>
            <span v-if="!tray.length" class="trayempty">click nouns to extract entities</span>
          </div>
          <div v-if="pickedAll" class="aha good">All 6 core entities found — stop here.</div>
          <div v-else-if="trayFull" class="aha warn">Tray capped at 6 — extra nouns are noise.</div>
        </div>
      </div>

      <!-- ---------- STEP 3 ---------- -->
      <div v-else-if="step === 3" class="panel s3">
        <div class="canvas">
          <svg class="edges" viewBox="0 0 404 162" preserveAspectRatio="none">
            <defs>
              <marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3"
                      orient="auto" markerUnits="userSpaceOnUse">
                <path d="M0,0 L7,3 L0,6" fill="none" stroke="var(--bp-cyan)" stroke-width="1.2" />
              </marker>
            </defs>
            <g v-for="e in EDGES" :key="e.id" v-show="drawn.includes(e.id)">
              <line :x1="cx(e.from)" :y1="cy(e.from)" :x2="cx(e.to)" :y2="cy(e.to)"
                    :class="{ comp: e.comp && compMode }"
                    :marker-end="(e.comp && compMode) ? '' : 'url(#arrow)'" />
              <polygon v-if="e.comp && compMode"
                :points="`${cx(e.from)-7},${cy(e.from)} ${cx(e.from)},${cy(e.from)-5} ${cx(e.from)+7},${cy(e.from)} ${cx(e.from)},${cy(e.from)+5}`"
                class="diamond" />
              <text :x="(cx(e.from)+cx(e.to))/2" :y="(cy(e.from)+cy(e.to))/2 - 3" class="elbl">{{ e.label }}</text>
            </g>
          </svg>
          <div v-for="b in BOXES" :key="b.id" class="cbox"
               :style="{ left: b.x + 'px', top: b.y + 'px' }">
            <span class="bname">{{ b.id }}</span>
            <transition name="pop">
              <span v-if="extracted && (b.id === 'Question' || b.id === 'Answer')" class="ifaces">
                <span class="ib">Commentable</span><span class="ib">Votable</span>
              </span>
            </transition>
          </div>
        </div>
        <div class="col">
          <div class="ttl">Draw relationships</div>
          <div class="edgebtns">
            <button v-for="e in EDGES" :key="e.id" class="eb"
                    :class="{ on: drawn.includes(e.id) }" @click="toggleEdge(e.id)">
              {{ e.from }}<span class="rel">{{ e.comp ? '◆' : '→' }}</span>{{ e.to }}
            </button>
          </div>
          <label class="tog" :class="{ on: compMode }" @click="compMode = !compMode">
            <span class="knob" /> composition {{ compMode ? 'ON' : 'flat' }}
          </label>
          <button class="b play" :class="{ done: extracted }" @click="extracted = !extracted">
            {{ extracted ? '✓ interfaces lifted' : 'extract interface →' }}
          </button>
          <div class="legend">
            <span class="lg comp">◆ composition</span>
            <span class="lg assoc">→ association</span>
          </div>
        </div>
      </div>

      <!-- ---------- STEP 4 ---------- -->
      <div v-else-if="step === 4" class="panel s4">
        <div class="col">
          <div class="ttl">Pattern shelf</div>
          <div class="shelf">
            <button v-for="p in PATTERNS" :key="p.id" class="pcard"
                    :class="{ armed: selPattern === p.id, used: Object.values(placed).includes(p.id) }"
                    @click="armPattern(p.id)">
              {{ p.name }}
            </button>
          </div>
          <div class="hintline">Arm a pattern, then drop it on the class it actually solves.</div>
        </div>
        <div class="col wide">
          <div class="ttl">Diagram targets</div>
          <div class="slots">
            <div v-for="sl in SLOTS" :key="sl.id" class="slot"
                 :class="{ ok: placed[sl.id], bad: badDrop === sl.id, armed: selPattern }"
                 @click="dropOn(sl)">
              <span class="sname">{{ sl.id }}</span>
              <span class="sdesc">{{ sl.label }}</span>
              <span v-if="placed[sl.id]" class="ptag">{{ patternOf(placed[sl.id])?.name }}</span>
              <span v-if="badDrop === sl.id" class="bad-msg">don't pattern-drop</span>
              <transition name="reveal">
                <div v-if="activeTip === sl.id && placed[sl.id]" class="tip">
                  <div><b>What</b> {{ patternOf(placed[sl.id])?.what }}</div>
                  <div><b>Why</b> {{ patternOf(placed[sl.id])?.why }}</div>
                  <div><b>How</b> <code>{{ patternOf(placed[sl.id])?.how }}</code></div>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>

      <!-- ---------- STEP 5 ---------- -->
      <div v-else class="panel s5">
        <div class="col wide">
          <div class="ttl">Walk: vote on an answer</div>
          <div class="flow">
            <template v-for="(f, i) in FLOW" :key="f.k">
              <div class="fstep"
                   :class="{ on: flowAt === i, past: flowAt > i || flowDone,
                             halt: thrown && flowAt === i }">
                {{ f.label }}
              </div>
              <span v-if="i < FLOW.length - 1" class="farr"
                    :class="{ lit: flowAt > i || flowDone }">→</span>
            </template>
          </div>
          <transition name="reveal">
            <div v-if="thrown" class="exc">⚠ {{ thrown }}</div>
            <div v-else-if="flowDone" class="aha good">Flow complete — score, reputation, notify all fired.</div>
          </transition>
        </div>
        <div class="col">
          <div class="ttl">Controls</div>
          <button class="b play" :disabled="flowRunning" @click="playFlow">▶ play flow</button>
          <button class="b ghost" @click="resetFlow">⟲ reset</button>
          <label class="tog trap" :class="{ on: trapSelf }" @click="trapSelf = !trapSelf; trapDup && (trapDup = false)">
            <span class="knob" /> trap: self-vote
          </label>
          <label class="tog trap" :class="{ on: trapDup }" @click="trapDup = !trapDup; trapSelf && (trapSelf = false)">
            <span class="knob" /> trap: duplicate vote
          </label>
          <div class="hintline">Arm a trap, then play — the guard throws before any mutation.</div>
        </div>
      </div>
    </div>

    <!-- aha strip -->
    <div class="footer">
      Scope and patterns are deliberate choices, not reflexes — the framework forces both.
    </div>
  </div>
</template>

<style scoped>
.ck {
  width: 100%; height: 360px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: .7rem;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}

/* ---------- rail ---------- */
.rail { display: flex; align-items: center; gap: 0; }
.rstep {
  display: flex; align-items: center; gap: .4rem;
  font-family: inherit; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02); color: var(--bp-dim);
  padding: .3rem .55rem; transition: all .25s;
}
.rstep:hover { border-color: var(--bp-cyan); color: var(--bp-ink); }
.rstep.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.rstep.done { color: var(--bp-good); border-color: rgba(74,222,128,.35); }
.rnum { font-size: .6rem; border: 1px solid currentColor; border-radius: 5px; padding: 0 .3rem; opacity: .8; }
.rlbl { font-size: .72rem; }
.rbud { font-size: .56rem; color: var(--bp-cyan); border: 1px solid var(--bp-line); border-radius: 4px; padding: 0 .3rem; }
.rstep.on .rbud { color: #fff; }
.rconn { flex: 1; height: 2px; background: var(--bp-line); margin: 0 .25rem; transition: background .3s; min-width: 10px; }
.rconn.lit { background: linear-gradient(90deg, var(--bp-good), var(--bp-line)); }
.clock { margin-left: auto; font-size: .64rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 999px; padding: .2rem .6rem; }
.clock b { color: var(--bp-cyan); }

/* ---------- stage ---------- */
.stage { flex: 1; min-height: 0; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.015); padding: .8rem .9rem; overflow: hidden; }
.panel { display: grid; gap: 1.1rem; height: 100%; }
.s1, .s2, .s4 { grid-template-columns: 1.3fr 1fr; }
.s3 { grid-template-columns: 1.35fr 1fr; }
.s5 { grid-template-columns: 1.5fr .9fr; }
.col { display: flex; flex-direction: column; gap: .5rem; min-width: 0; min-height: 0; }
.col.wide { min-width: 0; }
.ttl { font-size: .66rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-cyan); }
.cnt, .cap { font-size: .58rem; color: var(--bp-bg); background: var(--bp-cyan); border-radius: 999px; padding: .05rem .4rem; margin-left: .3rem; }
.cap { background: var(--bp-line); color: var(--bp-dim); }
.cap.full { background: var(--bp-warn); color: var(--bp-bg); }

/* ---------- step 1 ---------- */
.qa { display: flex; flex-direction: column; gap: .45rem; }
.qline { display: flex; flex-direction: column; gap: .2rem; }
.qbtn { text-align: left; font-family: inherit; font-size: .72rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .32rem .55rem;
  background: rgba(34,211,238,.06); color: var(--bp-ink); transition: all .2s; }
.qbtn:hover { border-color: var(--bp-cyan); }
.qbtn.used { opacity: .55; }
.bullet { color: var(--bp-cyan); margin-right: .4rem; font-weight: 700; }
.ans { font-size: .62rem; padding-left: 1.1rem; }
.ans.in { color: var(--bp-good); }
.ans.out { color: var(--bp-bad); }
.chips { display: flex; flex-wrap: wrap; gap: .35rem; align-content: flex-start; }
.chip { font-size: .62rem; border-radius: 999px; padding: .18rem .55rem; border: 1px solid var(--bp-line); }
.chip.base { color: var(--bp-ink); background: rgba(255,255,255,.03); }
.chip.add { color: var(--bp-good); border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.08); }
.chip.cut { color: var(--bp-bad); border-color: rgba(251,113,133,.4); background: rgba(251,113,133,.08); text-decoration: line-through; }
.legend { display: flex; gap: .6rem; margin-top: auto; }
.lg { font-size: .54rem; color: var(--bp-dim); display: inline-flex; align-items: center; gap: .25rem; }
.lg.base::before, .lg.add::before, .lg.cut::before { content: ''; width: 8px; height: 8px; border-radius: 999px; }
.lg.base::before { background: var(--bp-ink); }
.lg.add::before { background: var(--bp-good); }
.lg.cut::before { background: var(--bp-bad); }
.aha { font-size: .6rem; color: var(--bp-dim); margin-top: auto; line-height: 1.4; }
.aha.good { color: var(--bp-good); }
.aha.warn { color: var(--bp-warn); }

/* ---------- step 2 ---------- */
.para { font-size: .8rem; line-height: 1.85; color: var(--bp-dim); margin: 0; }
.noun { color: var(--bp-ink); cursor: pointer; border-bottom: 1px dashed var(--bp-line); transition: all .2s; padding: 0 1px; }
.noun:hover { color: var(--bp-cyan); border-color: var(--bp-cyan); }
.noun.on { color: var(--bp-cyan); border-bottom: 2px solid var(--bp-cyan); text-shadow: var(--bp-glow); }
.hintline { font-size: .6rem; color: var(--bp-dim); margin-top: auto; }
.hintline code { color: var(--bp-cyan); }
.etray { flex: 1; display: flex; flex-wrap: wrap; gap: .4rem; align-content: flex-start;
  border: 1px dashed var(--bp-line); border-radius: 10px; padding: .55rem; min-height: 90px; }
.ent { font-size: .68rem; color: #fff; cursor: pointer; border: 1px solid var(--bp-cyan);
  background: rgba(34,211,238,.12); border-radius: 7px; padding: .25rem .55rem; box-shadow: var(--bp-glow); }
.ent:hover { background: rgba(251,113,133,.12); border-color: var(--bp-bad); }
.trayempty { font-size: .6rem; color: var(--bp-dim); opacity: .7; }

/* ---------- step 3 ---------- */
.canvas { position: relative; width: 404px; height: 162px; align-self: center; }
.edges { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.edges line { stroke: var(--bp-cyan); stroke-width: 1.4; opacity: .85; }
.edges line.comp { stroke: var(--bp-violet); }
.diamond { fill: var(--bp-violet); stroke: var(--bp-violet); }
.elbl { fill: var(--bp-dim); font-size: 7px; font-family: "Fira Code", monospace; text-anchor: middle; }
.cbox { position: absolute; width: 116px; height: 66px; box-sizing: border-box;
  border: 1px solid var(--bp-line); border-radius: 8px; background: var(--bp-bg-2);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .2rem; }
.bname { font-size: .68rem; color: var(--bp-ink); }
.ifaces { display: flex; gap: .25rem; }
.ib { font-size: .48rem; color: var(--bp-violet); border: 1px solid rgba(167,139,250,.4);
  background: rgba(167,139,250,.1); border-radius: 999px; padding: .04rem .3rem; }
.edgebtns { display: flex; flex-direction: column; gap: .3rem; }
.eb { font-family: inherit; font-size: .58rem; cursor: pointer; text-align: left;
  border: 1px solid var(--bp-line); border-radius: 7px; padding: .26rem .45rem;
  background: rgba(255,255,255,.02); color: var(--bp-dim); transition: all .2s;
  display: flex; align-items: center; gap: .25rem; }
.eb:hover { border-color: var(--bp-cyan); color: var(--bp-ink); }
.eb.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.1); }
.eb .rel { color: var(--bp-violet); }

/* ---------- step 4 ---------- */
.shelf { display: flex; flex-direction: column; gap: .4rem; }
.pcard { font-family: inherit; font-size: .74rem; cursor: pointer; text-align: left;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .4rem .6rem;
  background: rgba(167,139,250,.06); color: var(--bp-ink); transition: all .2s; }
.pcard:hover { border-color: var(--bp-violet); }
.pcard.armed { border-color: var(--bp-violet); box-shadow: 0 0 16px rgba(167,139,250,.45); color: #fff; background: rgba(167,139,250,.16); }
.pcard.used { opacity: .5; }
.slots { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; flex: 1; }
.slot { position: relative; border: 1px dashed var(--bp-line); border-radius: 9px; padding: .45rem .55rem;
  background: rgba(255,255,255,.02); cursor: pointer; transition: all .2s;
  display: flex; flex-direction: column; gap: .15rem; }
.slot.armed { border-color: var(--bp-violet); border-style: solid; }
.slot.ok { border-style: solid; border-color: var(--bp-good); background: rgba(74,222,128,.08); box-shadow: 0 0 14px rgba(74,222,128,.3); }
.slot.bad { border-color: var(--bp-bad); background: rgba(251,113,133,.1); animation: shake .4s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-4px)} 75%{transform:translateX(4px)} }
.sname { font-size: .68rem; color: var(--bp-ink); }
.sdesc { font-size: .54rem; color: var(--bp-dim); }
.ptag { font-size: .54rem; color: var(--bp-good); border: 1px solid rgba(74,222,128,.4); border-radius: 999px; padding: .03rem .35rem; align-self: flex-start; }
.bad-msg { font-size: .56rem; color: var(--bp-bad); }
.tip { position: absolute; z-index: 5; left: 0; top: 100%; margin-top: .3rem; width: 200px;
  border: 1px solid rgba(74,222,128,.4); border-radius: 8px; background: var(--bp-bg);
  padding: .4rem .5rem; font-size: .54rem; line-height: 1.5; color: var(--bp-dim);
  box-shadow: 0 8px 24px rgba(0,0,0,.5); }
.tip b { color: var(--bp-good); margin-right: .3rem; }
.tip code { color: var(--bp-cyan); }

/* ---------- step 5 ---------- */
.flow { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; }
.fstep { font-size: .64rem; border: 1px solid var(--bp-line); border-radius: 7px;
  padding: .28rem .5rem; color: var(--bp-dim); background: rgba(255,255,255,.02); transition: all .25s; }
.fstep.on { color: #fff; border-color: var(--bp-cyan); background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); }
.fstep.past { color: var(--bp-good); border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.06); }
.fstep.halt { color: var(--bp-bad); border-color: var(--bp-bad); background: rgba(251,113,133,.12); }
.farr { color: var(--bp-line); font-size: .8rem; transition: color .25s; }
.farr.lit { color: var(--bp-cyan); }
.exc { font-size: .68rem; color: var(--bp-bad); border: 1px solid rgba(251,113,133,.4);
  background: rgba(251,113,133,.08); border-radius: 8px; padding: .4rem .6rem; }

/* ---------- shared controls ---------- */
.b { font-family: inherit; font-size: .72rem; padding: .42rem .6rem; cursor: pointer;
  border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px;
  background: rgba(255,255,255,.03); transition: all .2s; text-align: center; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.play { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.play.done { border-color: var(--bp-good); color: var(--bp-good); background: rgba(74,222,128,.08); box-shadow: none; }
.b.ghost { color: var(--bp-dim); box-shadow: none; }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .68rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: 0 0 auto; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(34,211,238,.4); }
.tog.on .knob::after { left: 16px; background: var(--bp-cyan); }
.tog.on { color: var(--bp-cyan); }
.tog.trap.on .knob { background: rgba(251,113,133,.4); }
.tog.trap.on .knob::after { background: var(--bp-bad); }
.tog.trap.on { color: var(--bp-bad); }

/* ---------- footer ---------- */
.footer { font-size: .6rem; color: var(--bp-dim); border-top: 1px solid var(--bp-line);
  padding-top: .35rem; letter-spacing: .04em; }

/* ---------- transitions ---------- */
.reveal-enter-active { transition: all .3s ease; }
.reveal-enter-from { opacity: 0; transform: translateY(-4px); }
.pop-enter-active { transition: all .25s ease; }
.pop-enter-from { opacity: 0; transform: scale(.6); }
.pop-leave-active { transition: all .2s ease; position: absolute; }
.pop-leave-to { opacity: 0; transform: scale(.6); }
</style>
