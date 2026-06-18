<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   PatternDiagnosisBench — pattern picking as DIAGNOSIS, not recall.
   Click a real interview code smell; it routes through a decision
   node to the GoF pattern that dissolves it, expanding the benefit,
   the cost, and a before/after Python snapshot. Flip "Trap mode"
   to force a choice between the classic near-misses first.
   ============================================================ */

type PatId = 'strategy' | 'state' | 'factory' | 'builder'
           | 'observer' | 'decorator' | 'composite' | 'adapter'

interface Pattern {
  id: PatId
  name: string
  benefit: string        // one-line "what it buys you"
  cost: string           // the tradeoff you say out loud
  before: string[]       // tangled conditional / smelly code
  after: string[]        // clean polymorphic call
}

// the right-column dictionary: every pattern the bench can land on
const PATTERNS: Record<PatId, Pattern> = {
  strategy: {
    id: 'strategy', name: 'Strategy',
    benefit: 'swap the algorithm without touching the caller',
    cost: 'one class per variant + a registry to pick it',
    before: ['if method == "air":', '    cost = 9 * w', 'elif method == "ground":', '    cost = 4 * w'],
    after: ['rate = RATES[method]', 'cost = rate.price(w)'],
  },
  state: {
    id: 'state', name: 'State',
    benefit: 'the object drives its own legal transitions',
    cost: 'a class per state; flow is spread across them',
    before: ['if self.status == "OPEN":', '    ...', 'elif self.status == "SHIPPED":', '    ...'],
    after: ['self.state.ship(self)', '# state decides what is legal'],
  },
  factory: {
    id: 'factory', name: 'Factory',
    benefit: 'callers ask for WHAT, not WHICH concrete class',
    cost: 'an indirection layer between you and `new`',
    before: ['p = PayPal() if x else Stripe()', '# new Concrete() everywhere'],
    after: ['p = PaymentFactory.create(x)', '# one place knows the types'],
  },
  builder: {
    id: 'builder', name: 'Builder',
    benefit: 'assemble step-by-step; no telescoping constructors',
    cost: 'extra builder object + a final `.build()`',
    before: ['Pizza(True, False, True,', '      None, 12, "L", ...)'],
    after: ['Pizza.builder()', '  .cheese().size("L").build()'],
  },
  observer: {
    id: 'observer', name: 'Observer',
    benefit: 'one change fans out to many, decoupled',
    cost: 'lifecycle/leaks; ordering is non-obvious',
    before: ['cart.add(i)', 'tax.recompute(); ui.draw()', 'analytics.track()'],
    after: ['cart.add(i)', '# subscribers notified', 'cart.notify()'],
  },
  decorator: {
    id: 'decorator', name: 'Decorator',
    benefit: 'compose behavior at runtime, not by subclassing',
    cost: 'many small wrappers; deep call chains',
    before: ['class MilkSoyWhipCoffee(', '      Coffee): ...', '# subclass explosion'],
    after: ['c = Whip(Soy(Milk(Coffee())))', '# stack at runtime'],
  },
  composite: {
    id: 'composite', name: 'Composite',
    benefit: 'treat a leaf and a group through one interface',
    cost: 'leaf must stub group-only operations',
    before: ['if isinstance(n, File):', '    n.size', 'else:', '    sum(child sizes...)'],
    after: ['node.size()', '# leaf and folder agree'],
  },
  adapter: {
    id: 'adapter', name: 'Adapter',
    benefit: 'translate a mismatched 3rd-party interface',
    cost: 'a thin shim to maintain as the SDK shifts',
    before: ['sdk.makePayment(amt)', '# our code calls .charge()'],
    after: ['class PayAdapter:', '  def charge(self, a):', '    sdk.makePayment(a)'],
  },
}

interface Symptom {
  id: string
  text: string           // the recognizable interview moment
  keyword: string        // the trigger substring to highlight in `text`
  answer: PatId          // the pattern that dissolves it
  decision: string       // the decision-node question
  picked: string         // the routing answer ("caller -> Strategy")
  trap?: PatId           // the classic near-miss it's confused with
  discriminator?: string // one-liner splitting answer vs trap
}

// the left rail of clickable code smells
const SYMPTOMS: Symptom[] = [
  {
    id: 'ship',
    text: 'a growing if/else picks a shipping algorithm',
    keyword: 'if/else picks',
    answer: 'strategy',
    decision: 'who chooses the behavior?',
    picked: 'the caller picks -> Strategy',
    trap: 'state',
    discriminator: 'caller picks the algorithm vs object drives its own transitions',
  },
  {
    id: 'order',
    text: 'an order behaves differently in OPEN vs SHIPPED vs CLOSED',
    keyword: 'OPEN vs SHIPPED vs CLOSED',
    answer: 'state',
    decision: 'who chooses the behavior?',
    picked: 'the object itself -> State',
    trap: 'strategy',
    discriminator: 'object drives its own transitions vs caller picks the algorithm',
  },
  {
    id: 'pay',
    text: 'new PaymentX() is scattered across the codebase',
    keyword: 'new PaymentX()',
    answer: 'factory',
    decision: 'creation: hide WHICH or hide HOW?',
    picked: 'hide WHICH class -> Factory',
    trap: 'builder',
    discriminator: 'Factory hides WHICH class is built vs Builder hides HOW it is assembled',
  },
  {
    id: 'ctor',
    text: 'a telescoping constructor takes 9 positional args',
    keyword: 'telescoping constructor',
    answer: 'builder',
    decision: 'creation: hide WHICH or hide HOW?',
    picked: 'hide HOW it is assembled -> Builder',
    trap: 'factory',
    discriminator: 'Builder hides HOW it is assembled vs Factory hides WHICH class is built',
  },
  {
    id: 'cart',
    text: 'editing the cart must update tax, UI, and analytics',
    keyword: 'update tax, UI, and analytics',
    answer: 'observer',
    decision: 'does one change fan out to many?',
    picked: 'one event, many listeners -> Observer',
  },
  {
    id: 'coffee',
    text: 'add milk/soy/whip behavior live without subclassing',
    keyword: 'without subclassing',
    answer: 'decorator',
    decision: 'wrap to add behavior, or freeze it in a subclass?',
    picked: 'compose at runtime -> Decorator',
    trap: 'composite',
    discriminator: 'Decorator wraps to add behavior vs Composite unifies a part/whole tree',
  },
  {
    id: 'fs',
    text: 'a tree of files-and-folders treated uniformly',
    keyword: 'files-and-folders treated uniformly',
    answer: 'composite',
    decision: 'wrap to add behavior, or unify a part/whole tree?',
    picked: 'leaf and group alike -> Composite',
    trap: 'decorator',
    discriminator: 'Composite unifies a part/whole tree vs Decorator wraps to add behavior',
  },
  {
    id: 'sdk',
    text: 'a 3rd-party SDK exposes the wrong method names',
    keyword: 'wrong method names',
    answer: 'adapter',
    decision: 'is the interface simply mismatched?',
    picked: 'translate the interface -> Adapter',
  },
]

const sel = ref<string>('')            // selected symptom id
const trapMode = ref(false)            // forced near-miss choice before reveal
const solved = ref<number>(0)          // running correct-diagnosis counter
const cleared = ref<string[]>([])      // symptom ids already diagnosed correctly

// diagnostic-flow state machine: idle -> routing -> (choose) -> done
type Phase = 'idle' | 'routing' | 'choose' | 'wrong' | 'done'
const phase = ref<Phase>('idle')
const trapPick = ref<PatId | ''>('')   // which near-miss the learner chose
const shakeBad = ref(false)            // wrong-pick shake flag

// timers, cleaned up on unmount (mirrors the reference components)
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

const current = computed<Symptom | null>(
  () => SYMPTOMS.find(s => s.id === sel.value) ?? null,
)
const target = computed<Pattern | null>(
  () => current.value ? PATTERNS[current.value.answer] : null,
)
// in trap mode, the two chips offered as a forced choice (answer + near-miss)
const choices = computed<Pattern[]>(() => {
  const c = current.value
  if (!c || !c.trap) return c ? [PATTERNS[c.answer]] : []
  const pair = [PATTERNS[c.answer], PATTERNS[c.trap]]
  // stable order so the answer isn't always first
  return c.id.charCodeAt(0) % 2 ? pair : [pair[1], pair[0]]
})
// split the smell text around its trigger keyword for the highlight animation
const smellParts = computed(() => {
  const c = current.value
  if (!c) return { pre: '', hit: '', post: '' }
  const i = c.text.indexOf(c.keyword)
  if (i < 0) return { pre: c.text, hit: '', post: '' }
  return { pre: c.text.slice(0, i), hit: c.keyword, post: c.text.slice(i + c.keyword.length) }
})
const revealed = computed(() => phase.value === 'done')

function selectSymptom(s: Symptom) {
  if (sel.value === s.id && phase.value !== 'idle') return
  clearTimers()
  sel.value = s.id
  trapPick.value = ''
  shakeBad.value = false
  phase.value = 'routing'
  // animate the keyword highlight -> decision node -> chip
  if (trapMode.value && s.trap) {
    after(900, () => { phase.value = 'choose' })
  } else {
    after(1050, () => { phase.value = 'done'; markSolved(s.id) })
  }
}

function markSolved(id: string) {
  if (!cleared.value.includes(id)) {
    cleared.value.push(id)
    solved.value += 1
  }
}

function choose(p: Pattern) {
  const c = current.value
  if (!c || phase.value !== 'choose') return
  trapPick.value = p.id
  if (p.id === c.answer) {
    phase.value = 'done'
    markSolved(c.id)
  } else {
    // wrong near-miss: shake + show the discriminator, let them retry
    phase.value = 'wrong'
    shakeBad.value = true
    after(450, () => { shakeBad.value = false })
    after(1500, () => {
      if (phase.value === 'wrong') { phase.value = 'choose'; trapPick.value = '' }
    })
  }
}

function toggleTrap() {
  trapMode.value = !trapMode.value
  // re-run the current diagnosis under the new mode
  const c = current.value
  if (c) { clearTimers(); sel.value = ''; after(40, () => selectSymptom(c)) }
}

function reset() {
  clearTimers()
  sel.value = ''
  phase.value = 'idle'
  trapPick.value = ''
  shakeBad.value = false
  solved.value = 0
  cleared.value = []
}
</script>

<template>
  <div class="pdb">
    <!-- ===== header: title + trap toggle + counter ===== -->
    <div class="head">
      <span class="htag">Pattern Diagnosis Bench</span>
      <button class="tog" :class="{ on: trapMode }" @click="toggleTrap">
        <span class="knob" /> Trap mode {{ trapMode ? 'ON' : 'OFF' }}
      </button>
      <span class="counter">
        diagnosed <b>{{ solved }}</b><i>/{{ SYMPTOMS.length }}</i>
      </span>
      <button class="rst" @click="reset">&#9851; reset</button>
    </div>

    <!-- ===== body: 3 columns — symptoms | decision flow | pattern ===== -->
    <div class="body">

      <!-- ---------- LEFT: clickable symptom cards ---------- -->
      <div class="symcol">
        <div class="coltag">Code smell</div>
        <div class="symlist">
          <button
            v-for="s in SYMPTOMS"
            :key="s.id"
            class="sym"
            :class="{ on: sel === s.id, cleared: cleared.includes(s.id) }"
            @click="selectSymptom(s)"
          >
            <span class="sdot" />
            <span class="stext">{{ s.text }}</span>
          </button>
        </div>
      </div>

      <!-- ---------- MIDDLE: diagnostic flow / decision node ---------- -->
      <div class="flowcol">
        <div class="coltag">Diagnose</div>

        <div v-if="!current" class="empty">
          <div class="ehint">click a smell &mdash;</div>
          <div class="esub">name the pain first, then reach for the pattern that dissolves it.</div>
        </div>

        <template v-else>
          <!-- the smell text, with its trigger keyword lighting up -->
          <div class="smell">
            <span>{{ smellParts.pre }}</span><span
              class="kw" :class="{ lit: phase !== 'idle' }">{{ smellParts.hit }}</span><span>{{ smellParts.post }}</span>
          </div>

          <!-- the arrow + decision node -->
          <div class="route">
            <span class="arrow" :class="{ lit: phase !== 'idle' }">&darr;</span>
            <div class="node" :class="{ lit: phase !== 'routing' && phase !== 'idle' }">
              <span class="nq">{{ current.decision }}</span>
              <span class="na">{{ current.picked }}</span>
            </div>
            <span class="arrow" :class="{ lit: revealed || phase === 'choose' || phase === 'wrong' }">&darr;</span>
          </div>

          <!-- TRAP: forced choice between the near-misses -->
          <div v-if="phase === 'choose' || phase === 'wrong'" class="trap">
            <div class="tprompt">Which one? &mdash; pick before the reveal</div>
            <div class="tchoices" :class="{ shake: shakeBad }">
              <button
                v-for="p in choices"
                :key="p.id"
                class="tchip"
                :class="{ bad: phase === 'wrong' && trapPick === p.id }"
                @click="choose(p)"
              >{{ p.name }}</button>
            </div>
            <div v-if="phase === 'wrong'" class="disc">
              <span class="dx">&#10007;</span> {{ current.discriminator }}
            </div>
          </div>
        </template>
      </div>

      <!-- ---------- RIGHT: matching pattern chip, expands on reveal ---------- -->
      <div class="patcol">
        <div class="coltag">Pattern</div>

        <transition name="reveal">
          <div v-if="revealed && target" class="pchip" :key="target.id">
            <div class="pname">{{ target.name }}</div>
            <div class="prow good"><span class="pl">+</span>{{ target.benefit }}</div>
            <div class="prow cost"><span class="pl">&minus;</span>{{ target.cost }}</div>

            <div class="snap">
              <div class="snapcol">
                <div class="snaplbl bad">before</div>
                <pre class="code">{{ target.before.join('\n') }}</pre>
              </div>
              <div class="snaparr">&rarr;</div>
              <div class="snapcol">
                <div class="snaplbl ok">after</div>
                <pre class="code ok">{{ target.after.join('\n') }}</pre>
              </div>
            </div>
          </div>
        </transition>

        <div v-if="!revealed" class="pwait">
          <span v-if="!current">pattern lands here</span>
          <span v-else-if="phase === 'routing'">routing&hellip;</span>
          <span v-else>make the call &mdash;</span>
        </div>
      </div>
    </div>

    <!-- ===== footer aha ===== -->
    <div class="footer">
      Patterns are answers to named pains, not vocabulary &mdash; say it:
      <code>see &lt;smell&gt;, add &lt;pattern&gt; for &lt;benefit&gt;, accept &lt;cost&gt;</code>.
    </div>
  </div>
</template>

<style scoped>
.pdb {
  width: 100%; height: 360px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: .55rem;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}

/* ---------- header ---------- */
.head { display: flex; align-items: center; gap: .7rem; }
.htag { font-size: .64rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-cyan); }
.counter { margin-left: auto; font-size: .64rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 999px; padding: .18rem .6rem; }
.counter b { color: var(--bp-good); font-size: .76rem; }
.counter i { color: var(--bp-dim); font-style: normal; opacity: .7; }
.rst { font-family: inherit; font-size: .62rem; color: var(--bp-dim); cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 7px; padding: .22rem .55rem;
  background: rgba(255,255,255,.02); transition: all .2s; }
.rst:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }

/* trap toggle (reuses the reference toggle anatomy) */
.tog { display: inline-flex; align-items: center; gap: .5rem; font-family: inherit;
  font-size: .64rem; color: var(--bp-dim); border: 1px solid var(--bp-line);
  border-radius: 8px; padding: .26rem .6rem; background: transparent; cursor: pointer; transition: all .25s; }
.tog .knob { width: 28px; height: 15px; border-radius: 999px; background: var(--bp-line);
  position: relative; transition: background .3s; flex: none; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 11px; height: 11px;
  border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on { color: var(--bp-violet); border-color: rgba(167,139,250,.5); }
.tog.on .knob { background: rgba(167,139,250,.4); }
.tog.on .knob::after { left: 15px; background: var(--bp-violet); }

/* ---------- body ---------- */
.body {
  flex: 1; min-height: 0; display: grid;
  grid-template-columns: 1.15fr 1fr 1.05fr; gap: .7rem;
  border: 1px solid var(--bp-line); border-radius: 12px;
  background: rgba(255,255,255,.015); padding: .7rem .75rem;
}
.coltag { font-size: .56rem; text-transform: uppercase; letter-spacing: .1em;
  color: var(--bp-blue); margin-bottom: .45rem; }

/* ---------- left: symptoms ---------- */
.symcol { display: flex; flex-direction: column; min-width: 0; min-height: 0; }
.symlist { display: flex; flex-direction: column; gap: .3rem; overflow-y: auto; padding-right: 2px; }
.symlist::-webkit-scrollbar { width: 5px; }
.symlist::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.sym { display: flex; align-items: flex-start; gap: .45rem; text-align: left;
  font-family: inherit; font-size: .6rem; line-height: 1.3; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .32rem .45rem;
  background: rgba(255,255,255,.02); color: var(--bp-dim); transition: all .2s; }
.sym:hover { border-color: var(--bp-cyan); color: var(--bp-ink); }
.sym.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.sym .sdot { width: 7px; height: 7px; border-radius: 999px; background: var(--bp-line);
  flex: none; margin-top: .28rem; transition: all .25s; }
.sym.on .sdot { background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.sym.cleared .sdot { background: var(--bp-good); box-shadow: 0 0 12px rgba(74,222,128,.6); }
.stext { min-width: 0; }

/* ---------- middle: diagnostic flow ---------- */
.flowcol { display: flex; flex-direction: column; min-width: 0; min-height: 0;
  border-left: 1px solid var(--bp-line); border-right: 1px solid var(--bp-line);
  padding: 0 .7rem; }
.empty { margin: auto 0; }
.ehint { font-size: .72rem; color: var(--bp-cyan); }
.esub { font-size: .58rem; color: var(--bp-dim); line-height: 1.5; margin-top: .35rem; }
.smell { font-size: .62rem; line-height: 1.4; color: var(--bp-dim); }
.kw { color: var(--bp-dim); border-radius: 4px; padding: 0 2px; transition: all .35s; }
.kw.lit { color: #fff; background: rgba(251,191,36,.16); box-shadow: 0 0 12px rgba(251,191,36,.35); }
.route { display: flex; flex-direction: column; align-items: center; gap: .28rem; margin: .5rem 0; }
.arrow { font-size: .8rem; color: var(--bp-line); transition: color .3s; }
.arrow.lit { color: var(--bp-cyan); }
.node { width: 100%; box-sizing: border-box; border: 1px solid var(--bp-line); border-radius: 9px;
  padding: .4rem .5rem; background: var(--bp-bg-2); display: flex; flex-direction: column;
  gap: .2rem; opacity: .45; transition: all .35s; }
.node.lit { opacity: 1; border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.nq { font-size: .56rem; color: var(--bp-dim); }
.na { font-size: .62rem; color: var(--bp-cyan); }
.node.lit .na { color: #fff; }

/* trap choice */
.trap { display: flex; flex-direction: column; gap: .35rem; }
.tprompt { font-size: .56rem; color: var(--bp-violet); letter-spacing: .04em; }
.tchoices { display: flex; gap: .4rem; }
.tchoices.shake { animation: shake .42s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
.tchip { flex: 1; font-family: inherit; font-size: .64rem; cursor: pointer;
  border: 1px solid rgba(167,139,250,.45); border-radius: 8px; padding: .34rem .4rem;
  background: rgba(167,139,250,.08); color: var(--bp-ink); transition: all .2s; }
.tchip:hover { border-color: var(--bp-violet); box-shadow: 0 0 14px rgba(167,139,250,.4); color: #fff; }
.tchip.bad { border-color: var(--bp-bad); background: rgba(251,113,133,.14); color: var(--bp-bad); }
.disc { font-size: .55rem; color: var(--bp-bad); line-height: 1.4;
  border: 1px solid rgba(251,113,133,.4); background: rgba(251,113,133,.08);
  border-radius: 7px; padding: .3rem .45rem; }
.disc .dx { font-weight: 700; margin-right: .2rem; }

/* ---------- right: pattern chip ---------- */
.patcol { display: flex; flex-direction: column; min-width: 0; min-height: 0; position: relative; }
.pchip { display: flex; flex-direction: column; gap: .3rem; }
.pname { font-size: .82rem; color: #fff; border-bottom: 1px solid var(--bp-line);
  padding-bottom: .25rem; text-shadow: var(--bp-glow); }
.prow { font-size: .58rem; line-height: 1.35; display: flex; gap: .35rem; }
.prow .pl { font-weight: 700; flex: none; }
.prow.good { color: var(--bp-good); }
.prow.cost { color: var(--bp-warn); }
.snap { display: flex; align-items: stretch; gap: .3rem; margin-top: .15rem; }
.snapcol { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: .18rem; }
.snaplbl { font-size: .5rem; text-transform: uppercase; letter-spacing: .08em; }
.snaplbl.bad { color: var(--bp-bad); }
.snaplbl.ok { color: var(--bp-good); }
.snaparr { align-self: center; color: var(--bp-cyan); font-size: .8rem; }
.code { margin: 0; font-family: "Fira Code", monospace; font-size: .5rem; line-height: 1.4;
  color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 6px;
  background: rgba(7,11,20,.6); padding: .32rem .4rem; white-space: pre; overflow-x: auto; }
.code::-webkit-scrollbar { height: 4px; }
.code::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.code.ok { color: var(--bp-good); border-color: rgba(74,222,128,.3); background: rgba(74,222,128,.05); }
.pwait { position: absolute; inset: 1.4rem 0 0; display: flex; align-items: center;
  justify-content: center; font-size: .6rem; color: var(--bp-dim); opacity: .6; }

/* ---------- footer ---------- */
.footer { font-size: .58rem; color: var(--bp-dim); border-top: 1px solid var(--bp-line);
  padding-top: .35rem; line-height: 1.4; }
.footer code { color: var(--bp-cyan); font-size: .94em; }

/* ---------- transitions ---------- */
.reveal-enter-active { transition: all .32s ease; }
.reveal-enter-from { opacity: 0; transform: translateY(6px) scale(.97); }
</style>
