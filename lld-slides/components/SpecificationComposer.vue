<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Conn = 'AND' | 'OR'
type SpecKey = 'isActive' | 'isPremium' | 'notBanned'

interface User {
  name: string
  active: boolean
  tier: 'premium' | 'free'
  banned: boolean
}

const USERS: User[] = [
  { name: 'ada',  active: true,  tier: 'premium', banned: false },
  { name: 'lin',  active: true,  tier: 'free',    banned: false },
  { name: 'rex',  active: false, tier: 'premium', banned: false },
  { name: 'mara', active: true,  tier: 'premium', banned: true },
  { name: 'omar', active: true,  tier: 'premium', banned: false },
]

// builder state: each spec is on/off; notBanned carries a NOT toggle
const specs = ref<Record<SpecKey, boolean>>({ isActive: true, isPremium: true, notBanned: true })
const negated = ref(true)              // the NOT on the banned clause
const conn = ref<Conn>('AND')          // single connector AND/OR across the chain

// per-card evaluation: '' (pending) | 'pass' | <first failing clause / reason>
const verdict = ref<string[]>(USERS.map(() => ''))
const busy = ref(false)
const timers: ReturnType<typeof setTimeout>[] = []

function later(fn: () => void, ms: number) { timers.push(setTimeout(fn, ms)) }
function clearAll() { timers.forEach(clearTimeout); timers.length = 0 }

const ORDER: SpecKey[] = ['isActive', 'isPremium', 'notBanned']

function clauseLabel(k: SpecKey): string {
  if (k === 'isActive') return 'isActive'
  if (k === 'isPremium') return 'isPremium'
  return negated.value ? 'NOT banned' : 'banned'
}
function clausePasses(k: SpecKey, u: User): boolean {
  if (k === 'isActive') return u.active
  if (k === 'isPremium') return u.tier === 'premium'
  return negated.value ? !u.banned : u.banned
}

// the active clauses, in order
const activeClauses = computed(() => ORDER.filter(k => specs.value[k]))

// human-readable composed predicate
const predicateText = computed(() => {
  const parts = activeClauses.value.map(clauseLabel)
  if (parts.length === 0) return 'ALL (no specs)'
  return parts.join('  ' + conn.value + '  ')
})

// pure evaluation: returns 'pass' or a short failure reason
function evalUser(u: User): string {
  const cl = activeClauses.value
  if (cl.length === 0) return 'pass'              // empty spec matches everything
  if (conn.value === 'AND') {
    for (const k of cl) if (!clausePasses(k, u)) return clauseLabel(k)
    return 'pass'
  } else {
    // OR: passes if any clause holds; otherwise none of them did
    for (const k of cl) if (clausePasses(k, u)) return 'pass'
    return 'no clause held'
  }
}

const matches = computed(() => verdict.value.filter(v => v === 'pass').length)

// re-run evaluation across all cards with a stagger
function reevaluate() {
  if (busy.value) return
  busy.value = true
  clearAll()
  verdict.value = USERS.map(() => '')             // visual "pending" wave
  USERS.forEach((u, i) => {
    later(() => {
      verdict.value[i] = evalUser(u)
      if (i === USERS.length - 1) busy.value = false
    }, 150 * (i + 1))
  })
}

function toggleSpec(k: SpecKey) { if (busy.value) return; specs.value[k] = !specs.value[k]; reevaluate() }
function toggleNot() { if (busy.value) return; negated.value = !negated.value; reevaluate() }
function setConn(c: Conn) { if (busy.value) return; if (conn.value === c) return; conn.value = c; reevaluate() }
function reset() {
  clearAll(); busy.value = false
  specs.value = { isActive: true, isPremium: true, notBanned: true }
  negated.value = true
  conn.value = 'AND'
  reevaluate()
}

// kick off initial evaluation
reset()

onUnmounted(clearAll)

function attr(u: User) {
  return [
    { t: 'active', ok: u.active, v: u.active ? 'true' : 'false' },
    { t: 'tier', ok: u.tier === 'premium', v: u.tier },
    { t: 'banned', ok: !u.banned, v: u.banned ? 'true' : 'false' },
  ]
}
</script>

<template>
  <div class="sc">
    <div class="stage">
      <!-- builder strip -->
      <div class="builder">
        <div class="chip" :class="{ on: specs.isActive }" @click="toggleSpec('isActive')">
          <span class="kn" /><span class="lab">isActive</span>
        </div>
        <button class="conn" :class="{ live: specs.isActive && specs.isPremium }" @click="setConn(conn === 'AND' ? 'OR' : 'AND')">{{ conn }}</button>
        <div class="chip" :class="{ on: specs.isPremium }" @click="toggleSpec('isPremium')">
          <span class="kn" /><span class="lab">isPremium</span>
        </div>
        <button class="conn" :class="{ live: specs.isPremium && specs.notBanned }" @click="setConn(conn === 'AND' ? 'OR' : 'AND')">{{ conn }}</button>
        <div class="chip notchip" :class="{ on: specs.notBanned }" @click="toggleSpec('notBanned')">
          <span class="kn" />
          <button class="not" :class="{ act: negated }" @click.stop="toggleNot">¬</button>
          <span class="lab">{{ negated ? 'NOT banned' : 'banned' }}</span>
        </div>
      </div>

      <!-- composed predicate, read like a sentence -->
      <div class="pred">
        <span class="pl">rule =</span>
        <code>{{ predicateText }}</code>
      </div>

      <!-- candidate cards -->
      <div class="cards">
        <div v-for="(u, i) in USERS" :key="u.name" class="card"
             :class="{ pass: verdict[i] === 'pass', fail: verdict[i] && verdict[i] !== 'pass', pending: verdict[i] === '' }">
          <div class="chead">
            <span class="uname">{{ u.name }}</span>
            <span class="mark" v-if="verdict[i] === 'pass'">✓</span>
            <span class="mark x" v-else-if="verdict[i]">✗</span>
          </div>
          <div class="rows">
            <span v-for="a in attr(u)" :key="a.t" class="ar" :class="{ no: !a.ok }">
              {{ a.t }}=<b>{{ a.v }}</b>
            </span>
          </div>
          <div class="why" :class="{ show: verdict[i] && verdict[i] !== 'pass' }">
            <template v-if="verdict[i] && verdict[i] !== 'pass'">fails: {{ verdict[i] }}</template>
            <template v-else> </template>
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="count" :class="{ zero: matches === 0 }">
        matches <b>{{ matches }}</b> / {{ USERS.length }}
      </div>

      <div class="legend">
        <div class="lg"><span class="sw on" /> spec on</div>
        <div class="lg"><span class="sw" /> spec off</div>
        <div class="lg"><span class="dot good" /> satisfied</div>
        <div class="lg"><span class="dot bad" /> first failing clause</div>
      </div>

      <button class="b ghost" @click="reset">⟳ reset (all on)</button>

      <ul class="kpts">
        <li>Each rule is an object with <code>is_satisfied()</code></li>
        <li>Compose with AND / OR / NOT into a bigger rule</li>
        <li>One predicate, re-read across every candidate</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.sc { display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.4rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.stage { min-width: 0; display: flex; flex-direction: column; gap: .5rem; overflow: hidden; }

/* builder strip */
.builder { display: flex; align-items: stretch; gap: .4rem; flex-wrap: nowrap; flex: none; }
.chip { display: inline-flex; align-items: center; gap: .45rem; padding: .35rem .55rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02); cursor: pointer; user-select: none; transition: all .25s; }
.chip.on { border-color: var(--bp-cyan); background: rgba(34,211,238,.1); box-shadow: var(--bp-glow); }
.chip .kn { width: 22px; height: 13px; border-radius: 999px; background: var(--bp-line); position: relative; flex: none; transition: background .25s; }
.chip .kn::after { content: ''; position: absolute; top: 2px; left: 2px; width: 9px; height: 9px; border-radius: 999px; background: var(--bp-dim); transition: all .25s; }
.chip.on .kn { background: rgba(34,211,238,.4); } .chip.on .kn::after { left: 11px; background: var(--bp-cyan); }
.chip .lab { font-size: .72rem; color: var(--bp-dim); white-space: nowrap; }
.chip.on .lab { color: var(--bp-cyan); }
.notchip .not { font-family: inherit; font-size: .8rem; line-height: 1; padding: .1rem .35rem; border: 1px solid var(--bp-line); border-radius: 6px; background: transparent; color: var(--bp-dim); cursor: pointer; }
.notchip .not.act { border-color: var(--bp-violet); color: var(--bp-violet); background: rgba(167,139,250,.12); }
.conn { font-family: inherit; font-size: .64rem; letter-spacing: .06em; padding: 0 .5rem; border: 1px dashed var(--bp-line); border-radius: 7px; background: transparent; color: var(--bp-dim); cursor: pointer; align-self: center; transition: all .25s; }
.conn.live { border-style: solid; border-color: var(--bp-blue); color: var(--bp-blue); }

/* predicate sentence */
.pred { display: flex; align-items: baseline; gap: .5rem; padding: .4rem .65rem; border: 1px solid var(--bp-line); border-radius: 8px; background: rgba(56,189,248,.04); flex: none; min-width: 0; }
.pred .pl { font-size: .66rem; color: var(--bp-dim); flex: none; }
.pred code { font-size: .74rem; color: var(--bp-cyan); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }

/* candidate cards */
.cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: .5rem; flex: 1 1 auto; min-height: 0; }
.card { display: flex; flex-direction: column; gap: .3rem; padding: .5rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.02); transition: border-color .3s, background .3s, opacity .3s, box-shadow .3s; min-width: 0; overflow: hidden; }
.card.pending { opacity: .55; }
.card.pass { border-color: var(--bp-good); background: rgba(74,222,128,.12); box-shadow: 0 0 16px rgba(74,222,128,.28); }
.card.fail { opacity: .42; border-color: var(--bp-line); }
.chead { display: flex; align-items: center; justify-content: space-between; gap: .25rem; min-width: 0; }
.uname { font-size: .78rem; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mark { font-size: .82rem; color: var(--bp-good); flex: none; }
.mark.x { color: var(--bp-bad); }
.rows { display: flex; flex-direction: column; gap: .12rem; }
.ar { font-size: .56rem; color: var(--bp-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ar b { color: var(--bp-ink); font-weight: 400; }
.ar.no b { color: var(--bp-bad); }
.why { font-size: .54rem; min-height: .72rem; color: var(--bp-bad); opacity: 0; transition: opacity .3s; line-height: 1.1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: auto; }
.why.show { opacity: 1; }

/* panel */
.panel { display: flex; flex-direction: column; gap: .8rem; min-width: 0; overflow: hidden; }
.count { font-size: .82rem; color: var(--bp-dim); padding: .5rem .7rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(74,222,128,.05); }
.count b { font-size: 1.2rem; color: var(--bp-good); margin: 0 .2rem; }
.count.zero { background: rgba(251,113,133,.05); } .count.zero b { color: var(--bp-bad); }
.legend { display: grid; grid-template-columns: 1fr 1fr; gap: .3rem .6rem; }
.lg { display: inline-flex; align-items: center; gap: .4rem; font-size: .62rem; color: var(--bp-dim); min-width: 0; }
.sw { width: 18px; height: 11px; border-radius: 999px; background: var(--bp-line); flex: none; position: relative; }
.sw.on { background: rgba(34,211,238,.5); }
.sw.on::after { content: ''; position: absolute; top: 1.5px; right: 1.5px; width: 8px; height: 8px; border-radius: 999px; background: var(--bp-cyan); }
.dot { width: 9px; height: 9px; border-radius: 999px; flex: none; }
.dot.good { background: var(--bp-good); box-shadow: 0 0 8px rgba(74,222,128,.6); }
.dot.bad { background: var(--bp-bad); }
.b { font-family: inherit; font-size: .76rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); width: fit-content; }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .3rem 0; font-size: .7rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
.kpts code { font-size: .66rem; color: var(--bp-cyan); }
</style>
