<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   BloomFilterLab — a live 32-bit Bloom filter.
   Add words (k hash arrows fan out, bits flip 0->1), Check
   words (k bits light one by one, short-circuit on the first 0),
   and force a false positive. Sliders re-derive m and k from
   n and the target false-positive rate, re-rendering the board.
   ============================================================ */

type Verdict = '' | 'MAYBE' | 'NOT'

// --- tunable params (the Builder/Config inputs) ---
const k = ref(3)                 // num hash functions, slider 1..5
const pPct = ref(2)              // target FP rate %, slider 0.5..20
const n = ref(8)                 // expected elements (drives m)

// m = ceil(-(n*ln p) / (ln2)^2), clamped to a board we can render
const LN2 = Math.log(2)
const rawM = computed(() =>
  Math.ceil(-(n.value * Math.log(pPct.value / 100)) / (LN2 * LN2))
)
const m = computed(() => Math.min(48, Math.max(16, rawM.value)))
// k the formula *would* pick, shown next to the slider for contrast
const idealK = computed(() => Math.max(1, Math.round((m.value / n.value) * LN2)))

// 1M @ p readout for the sidebar (bytes -> MB)
const oneMillion = computed(() => {
  const bits = Math.ceil(-(1_000_000 * Math.log(pPct.value / 100)) / (LN2 * LN2))
  return (bits / 8 / 1_000_000).toFixed(2)
})

// --- board state ---
const bits = ref<boolean[]>(Array(m.value).fill(false))
// provenance: per bit index -> set of words that set it
const owners = reactive<Record<number, string[]>>({})
const words = ref<string[]>([])

// --- transient animation state ---
const word = ref('')
const verdict = ref<Verdict>('')
const flash = ref(false)              // board-level verdict flash
const litBits = ref<number[]>([])     // bits currently pulsing (add or check)
const pulseBits = ref<number[]>([])   // bits doing the 0->1 green pop
const arrows = ref<{ seed: number; bit: number }[]>([])  // hash fan-out labels
const checkBit = ref(-1)              // the single bit a check is inspecting
const failBit = ref(-1)               // the 0 bit that short-circuited a check
const contributors = ref<Record<number, string>>({})     // bit -> word that set it (FP highlight)
const trace = ref('')
const busy = ref(false)

// --- timers, cleaned up on unmount ---
const timers: ReturnType<typeof setTimeout>[] = []
function after(ms: number, fn: () => void) { timers.push(setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

// --- the hash strategy: one algo (FNV-ish), seeds 0..k-1 make k independent fns ---
function hash(element: string, seed: number, size: number): number {
  let h = 2166136261 ^ (seed * 0x9e3779b1)
  for (let i = 0; i < element.length; i++) {
    h ^= element.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  h ^= h >>> 13
  return Math.abs(h) % size
}

function hashesFor(element: string): number[] {
  const out: number[] = []
  for (let seed = 0; seed < k.value; seed++) out.push(hash(element, seed, m.value))
  return out
}

// --- rebuild the board from scratch (after a slider change or clear) ---
function rebuild(keepWords: string[]) {
  clearTimers()
  busy.value = false
  bits.value = Array(m.value).fill(false)
  for (const key of Object.keys(owners)) delete owners[Number(key)]
  litBits.value = []
  pulseBits.value = []
  arrows.value = []
  checkBit.value = -1
  failBit.value = -1
  verdict.value = ''
  flash.value = false
  contributors.value = {}
  words.value = []
  for (const w of keepWords) {
    for (const b of hashesFor(w)) {
      bits.value[b] = true
      ;(owners[b] ||= []).push(w)
    }
    words.value.push(w)
  }
}

// re-derive m/k live as sliders move; replay the same word set on the new board
function onParamChange() {
  if (busy.value) return
  const keep = [...words.value]
  rebuild(keep)
  trace.value = `Config(n=${n.value}, p=${pPct.value}%) -> m=${m.value}, k=${k.value}`
}

// --- add(element): set k bits atomically, fan k labeled arrows ---
function add() {
  const w = word.value.trim()
  if (!w || busy.value) return
  busy.value = true
  verdict.value = ''
  flash.value = false
  failBit.value = -1
  checkBit.value = -1
  contributors.value = {}
  const targets = hashesFor(w)
  arrows.value = targets.map((bit, seed) => ({ seed, bit }))
  trace.value = `add("${w}") -> set ${k.value} bits`
  litBits.value = [...targets]

  targets.forEach((bit, i) => {
    after(140 + i * 200, () => {
      const wasOff = !bits.value[bit]
      bits.value[bit] = true
      ;(owners[bit] ||= []).push(w)
      if (wasOff) {
        pulseBits.value = [...pulseBits.value, bit]
        after(420, () => { pulseBits.value = pulseBits.value.filter(b => b !== bit) })
      }
    })
  })

  after(160 + targets.length * 200 + 260, () => {
    if (!words.value.includes(w)) words.value.push(w)
    arrows.value = []
    litBits.value = []
    busy.value = false
    word.value = ''
    trace.value = `"${w}" added — ${k.value} bits set, no false negatives possible`
  })
}

// --- might_contain(element): light k bits one by one, early-return on first 0 ---
function check() {
  const w = word.value.trim()
  if (!w || busy.value) return
  busy.value = true
  verdict.value = ''
  flash.value = false
  failBit.value = -1
  checkBit.value = -1
  contributors.value = {}
  arrows.value = []
  const targets = hashesFor(w)
  trace.value = `might_contain("${w}") -> probe ${k.value} bits`
  litBits.value = []

  const probe = (i: number) => {
    if (i >= targets.length) {
      // every bit was 1 -> maybe present
      checkBit.value = -1
      verdict.value = 'MAYBE'
      flash.value = true
      trace.value = `all ${k.value} bits set -> MAYBE PRESENT (could be a false positive)`
      after(1600, () => { flash.value = false; litBits.value = []; busy.value = false })
      return
    }
    const bit = targets[i]
    checkBit.value = bit
    if (!bits.value[bit]) {
      // first 0 -> definitely not, short-circuit
      failBit.value = bit
      verdict.value = 'NOT'
      flash.value = true
      trace.value = `bit ${bit} = 0 -> return False (DEFINITELY NOT, short-circuit)`
      after(1600, () => {
        flash.value = false; litBits.value = []; checkBit.value = -1; busy.value = false
      })
      return
    }
    litBits.value = [...litBits.value, bit]
    after(440, () => probe(i + 1))
  }
  after(180, () => probe(0))
}

// --- false-positive challenge: seed words, then probe a never-added word ---
const SEEDS = ['cat', 'dog', 'fox', 'owl']

function falsePositive() {
  if (busy.value) return
  busy.value = true
  rebuild([])           // fresh board, keep current m/k
  busy.value = true     // rebuild reset it; re-lock for the run
  trace.value = `seeding ${SEEDS.length} words to cover the bit space...`

  // place all seeds instantly so bits are covered
  for (const s of SEEDS) {
    for (const b of hashesFor(s)) {
      bits.value[b] = true
      ;(owners[b] ||= []).push(s)
    }
    words.value.push(s)
  }

  // find a word whose k bits are all already 1 but was never added
  let victim = ''
  let victimBits: number[] = []
  for (const cand of ['ant', 'bee', 'elk', 'ram', 'jay', 'hen', 'pig', 'cow', 'ape', 'eel']) {
    const hs = hashesFor(cand)
    if (hs.every(b => bits.value[b]) && !SEEDS.includes(cand)) {
      victim = cand; victimBits = hs; break
    }
  }

  after(600, () => {
    if (!victim) {
      // no collision at this m/k — honest about it, nudge the sliders
      trace.value = `no collision at m=${m.value}, k=${k.value} — lower bits or k to force one`
      busy.value = false
      return
    }
    word.value = victim
    // highlight which earlier word set each contributing bit
    const map: Record<number, string> = {}
    for (const b of victimBits) map[b] = owners[b]?.[0] ?? '?'
    contributors.value = map
    litBits.value = [...victimBits]
    checkBit.value = -1
    verdict.value = 'MAYBE'
    flash.value = true
    trace.value = `might_contain("${victim}") -> all bits set by other words -> FALSE POSITIVE`
    after(2400, () => { flash.value = false; busy.value = false })
  })
}

function clearAll() {
  rebuild([])
  word.value = ''
  trace.value = 'cleared — bit array zeroed, words dropped'
}

// --- view helpers ---
const setCount = computed(() => bits.value.filter(Boolean).length)
const fillPct = computed(() => Math.round((setCount.value / m.value) * 100))
const verdictText = computed(() =>
  verdict.value === 'MAYBE' ? 'MAYBE PRESENT'
  : verdict.value === 'NOT' ? 'DEFINITELY NOT'
  : ''
)
function tipFor(i: number): string {
  if (contributors.value[i]) return `set by "${contributors.value[i]}"`
  const o = owners[i]
  return o && o.length ? `set by ${o.map(w => '"' + w + '"').join(', ')}` : 'unset (0)'
}
</script>

<template>
  <div class="bf">
    <!-- ===== top bar: input + ops + sliders ===== -->
    <div class="bar">
      <div class="ops">
        <input
          v-model="word"
          class="win"
          spellcheck="false"
          placeholder="word"
          :disabled="busy"
          @keyup.enter="add"
        />
        <button class="op add" :disabled="busy || !word.trim()" @click="add">add</button>
        <button class="op chk" :disabled="busy || !word.trim()" @click="check">check</button>
        <button class="op clr" :disabled="busy" @click="clearAll">clear</button>
      </div>

      <div class="sliders">
        <label class="sl">
          <span class="sk">k <b>{{ k }}</b><i>ideal {{ idealK }}</i></span>
          <input type="range" min="1" max="5" step="1" v-model.number="k"
                 :disabled="busy" @input="onParamChange" />
        </label>
        <label class="sl">
          <span class="sk">p <b>{{ pPct }}%</b></span>
          <input type="range" min="0.5" max="20" step="0.5" v-model.number="pPct"
                 :disabled="busy" @input="onParamChange" />
        </label>
        <span class="mread">m = -(n·ln p)/(ln2)<sup>2</sup> = <b>{{ m }}</b></span>
      </div>
    </div>

    <!-- ===== main: board + sidebar ===== -->
    <div class="main">
      <!-- board column -->
      <div class="boardcol">
        <div class="bhead">
          <span class="btag">BitArray · {{ m }} bits · {{ setCount }} set ({{ fillPct }}%)</span>
          <transition name="flash">
            <span
              v-if="verdict"
              class="verdict"
              :class="{ maybe: verdict === 'MAYBE', not: verdict === 'NOT', flash }"
            >{{ verdictText }}</span>
          </transition>
        </div>

        <!-- hash fan-out labels (which seed targeted which bit) -->
        <div class="fan" :class="{ show: arrows.length }">
          <span v-for="a in arrows" :key="a.seed" class="harrow">
            h<sub>{{ a.seed }}</sub>("{{ word }}") &rarr; {{ a.bit }}
          </span>
          <span v-if="!arrows.length" class="fanidle">k hashes fan out on add</span>
        </div>

        <!-- the bit cells -->
        <div class="cells">
          <div
            v-for="(b, i) in bits"
            :key="i"
            class="cell"
            :class="{
              on: b,
              pulse: pulseBits.includes(i),
              lit: litBits.includes(i),
              probe: checkBit === i,
              fail: failBit === i,
              contrib: contributors[i],
            }"
            :title="tipFor(i)"
          >
            <span class="bv">{{ b ? 1 : 0 }}</span>
            <span class="bi">{{ i }}</span>
            <span v-if="contributors[i]" class="cwho">{{ contributors[i] }}</span>
          </div>
        </div>

        <!-- words added + the running trace -->
        <div class="wrow">
          <span class="wlabel">added:</span>
          <span v-if="!words.length" class="wnone">none yet</span>
          <span v-for="w in words" :key="w" class="wchip">{{ w }}</span>
        </div>
        <div class="caption">
          <span class="ck">&gt;</span>
          <span class="ctext">{{ trace || 'type a word, then add or check' }}</span>
        </div>
      </div>

      <!-- sidebar -->
      <div class="side">
        <button class="fp" :disabled="busy" @click="falsePositive">
          force a false positive &rarr;
        </button>

        <div class="guarantee">
          <div class="grow good">
            <span class="gdot" />
            <div><b>Never a false negative.</b> If a word was added, all k bits are 1 — check can't say NO.</div>
          </div>
          <div class="grow warn">
            <span class="gdot" />
            <div><b>Can say MAYBE wrongly.</b> Other words may have set every bit a stranger hashes to.</div>
          </div>
          <div class="grow">
            <span class="gdot" />
            <div><b>Cost is O(k).</b> add and might_contain touch exactly k bits — no scan, no resize.</div>
          </div>
          <div class="grow">
            <span class="gdot" />
            <div><b>No delete.</b> Clearing a bit could break another word still relying on it.</div>
          </div>
        </div>

        <div class="scale">
          <span class="slbl">1M elements @ {{ pPct }}%</span>
          <span class="sval">&asymp; {{ oneMillion }} MB · {{ idealK }} hashes</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bf {
  width: 100%;
  height: 360px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: .6rem;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- top bar ---------- */
.bar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; flex-wrap: wrap;
}
.ops { display: flex; align-items: center; gap: .4rem; }
.win {
  font-family: inherit; font-size: .72rem; color: var(--bp-ink);
  background: rgba(7,11,20,.6); border: 1px solid var(--bp-line);
  border-radius: 8px; padding: .34rem .55rem; width: 96px; outline: none;
  transition: border-color .2s;
}
.win:focus { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.win:disabled { opacity: .5; }
.op {
  font-family: inherit; font-size: .68rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .34rem .6rem; background: rgba(255,255,255,.03);
  color: var(--bp-ink); transition: all .2s;
}
.op:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.op.add { border-color: rgba(74,222,128,.4); color: var(--bp-good); background: rgba(74,222,128,.08); }
.op.add:hover:not(:disabled) { box-shadow: 0 0 14px rgba(74,222,128,.35); }
.op.chk { border-color: rgba(34,211,238,.4); color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.op.clr { color: var(--bp-dim); }
.op:disabled { opacity: .4; cursor: not-allowed; }

.sliders { display: flex; align-items: center; gap: .9rem; }
.sl { display: flex; flex-direction: column; gap: .12rem; }
.sk { font-size: .58rem; color: var(--bp-dim); letter-spacing: .04em; display: flex; align-items: baseline; gap: .3rem; }
.sk b { color: var(--bp-cyan); font-size: .7rem; }
.sk i { font-style: normal; color: var(--bp-dim); opacity: .7; font-size: .52rem; }
.sl input[type=range] {
  -webkit-appearance: none; appearance: none; width: 96px; height: 3px;
  background: var(--bp-line); border-radius: 999px; outline: none; cursor: pointer;
}
.sl input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none; width: 12px; height: 12px;
  border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow); cursor: pointer;
}
.sl input[type=range]:disabled { opacity: .4; }
.mread { font-size: .58rem; color: var(--bp-dim); }
.mread b { color: var(--bp-cyan); font-size: .7rem; }

/* ---------- main ---------- */
.main { flex: 1; min-height: 0; display: grid; grid-template-columns: 1.55fr 1fr; gap: 1rem; }
.boardcol { display: flex; flex-direction: column; gap: .45rem; min-width: 0; }
.bhead { display: flex; align-items: center; gap: .6rem; }
.btag { font-size: .58rem; letter-spacing: .06em; text-transform: uppercase; color: var(--bp-blue); }
.verdict {
  margin-left: auto; font-size: .6rem; letter-spacing: .08em; font-weight: 700;
  padding: .14rem .55rem; border-radius: 999px; border: 1px solid var(--bp-line);
}
.verdict.maybe { color: var(--bp-warn); border-color: rgba(251,191,36,.5); background: rgba(251,191,36,.12); }
.verdict.not   { color: var(--bp-bad);  border-color: rgba(251,113,133,.5); background: rgba(251,113,133,.12); }
.verdict.flash { animation: vflash .5s ease; }
@keyframes vflash { 0% { transform: scale(1); } 40% { transform: scale(1.12); } 100% { transform: scale(1); } }

/* hash fan-out */
.fan {
  display: flex; flex-wrap: wrap; gap: .35rem; min-height: 1.4rem; align-items: center;
}
.harrow {
  font-size: .56rem; color: var(--bp-cyan);
  border: 1px solid rgba(34,211,238,.4); border-radius: 999px;
  padding: .08rem .45rem; background: rgba(34,211,238,.08);
  animation: pop .3s ease;
}
.fanidle { font-size: .56rem; color: var(--bp-dim); opacity: .6; }
@keyframes pop { from { opacity: 0; transform: scale(.6); } to { opacity: 1; transform: scale(1); } }

/* bit cells */
.cells {
  display: grid; grid-template-columns: repeat(16, 1fr); gap: 4px;
}
.cell {
  position: relative; aspect-ratio: 1 / 1;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 1px solid var(--bp-line); border-radius: 5px;
  background: rgba(255,255,255,.02);
  transition: all .25s;
}
.bv { font-size: .62rem; color: var(--bp-dim); line-height: 1; }
.bi { font-size: .4rem; color: var(--bp-dim); opacity: .45; line-height: 1; margin-top: 1px; }
.cell.on { border-color: rgba(74,222,128,.5); background: rgba(74,222,128,.14); }
.cell.on .bv { color: var(--bp-good); }
.cell.pulse { box-shadow: 0 0 14px rgba(74,222,128,.6); animation: bpop .42s ease; }
@keyframes bpop { 0% { transform: scale(1); } 45% { transform: scale(1.28); } 100% { transform: scale(1); } }
.cell.lit { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.cell.probe { border-color: var(--bp-cyan); background: rgba(34,211,238,.18); box-shadow: var(--bp-glow); transform: scale(1.12); }
.cell.probe .bv { color: #fff; }
.cell.fail { border-color: var(--bp-bad); background: rgba(251,113,133,.18); box-shadow: 0 0 16px rgba(251,113,133,.55); }
.cell.fail .bv { color: var(--bp-bad); }
.cell.contrib { border-color: var(--bp-warn); background: rgba(251,191,36,.16); box-shadow: 0 0 14px rgba(251,191,36,.45); }
.cell.contrib .bv { color: var(--bp-warn); }
.cwho {
  position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
  font-size: .42rem; color: var(--bp-warn); white-space: nowrap; line-height: 1;
}

/* words + caption */
.wrow { display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; min-height: 1.2rem; }
.wlabel { font-size: .56rem; color: var(--bp-dim); text-transform: uppercase; letter-spacing: .06em; }
.wnone { font-size: .58rem; color: var(--bp-dim); opacity: .6; }
.wchip {
  font-size: .58rem; color: var(--bp-good); border: 1px solid rgba(74,222,128,.35);
  border-radius: 999px; padding: .04rem .4rem; background: rgba(74,222,128,.06);
}
.caption {
  display: flex; gap: .4rem; align-items: baseline; margin-top: auto;
  font-size: .62rem; border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6); padding: .38rem .55rem; min-height: 1.8rem;
}
.ck { color: var(--bp-cyan); }
.ctext { color: var(--bp-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ---------- sidebar ---------- */
.side { display: flex; flex-direction: column; gap: .55rem; min-width: 0; }
.fp {
  font-family: inherit; font-size: .68rem; color: var(--bp-warn);
  border: 1px solid rgba(251,191,36,.5); border-radius: 8px;
  padding: .42rem .6rem; background: rgba(251,191,36,.1); cursor: pointer;
  box-shadow: 0 0 16px rgba(251,191,36,.2); transition: all .2s; text-align: left;
}
.fp:hover:not(:disabled) { background: rgba(251,191,36,.18); box-shadow: 0 0 20px rgba(251,191,36,.4); }
.fp:disabled { opacity: .45; cursor: not-allowed; box-shadow: none; }

.guarantee { display: flex; flex-direction: column; gap: .4rem; }
.grow { display: flex; gap: .45rem; font-size: .58rem; line-height: 1.34; color: var(--bp-dim); }
.grow b { color: var(--bp-ink); }
.grow .gdot { width: 7px; height: 7px; border-radius: 999px; background: var(--bp-line); flex: none; margin-top: .28rem; }
.grow.good .gdot { background: var(--bp-good); box-shadow: 0 0 10px rgba(74,222,128,.5); }
.grow.good b { color: var(--bp-good); }
.grow.warn .gdot { background: var(--bp-warn); box-shadow: 0 0 10px rgba(251,191,36,.5); }
.grow.warn b { color: var(--bp-warn); }

.scale {
  margin-top: auto; display: flex; flex-direction: column; gap: .15rem;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .45rem .6rem;
  background: linear-gradient(180deg, rgba(56,189,248,.06), rgba(56,189,248,.01));
}
.slbl { font-size: .54rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-blue); }
.sval { font-size: .66rem; color: var(--bp-cyan); }

/* transitions */
.flash-enter-active { transition: all .25s ease; }
.flash-enter-from { opacity: 0; transform: scale(.7); }
.flash-leave-active { transition: all .3s ease; }
.flash-leave-to { opacity: 0; }
</style>
