<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   TrieTypeaheadExplorer — autocomplete, live.
   Type a prefix: watch the O(L) Trie walk, then a DFS sweep
   collects the subtree's words into a candidate pool. A pluggable
   ranking Strategy (Alphabetical / Frequency) picks the top-k —
   flipping the Strategy re-ranks WITHOUT re-walking the Trie.
   ============================================================ */

type RankSlug = 'freq' | 'alpha'

/* ---------- trie model (built once from the seed dictionary) ---------- */
interface TrieNode {
  id: number
  ch: string                       // edge char into this node ('' for root)
  path: string                     // accumulated prefix at this node
  isWord: boolean
  frequency: number
  children: Record<string, number> // ch -> node id
  parent: number                   // node id, -1 for root
}

const SEED = [
  'apple', 'application', 'apply', 'app',
  'banana', 'band', 'bank',
  'cat', 'car', 'card', 'care',
  'dog', 'door', 'down',
  'search', 'sea', 'seal', 'season',
]

const nodes = reactive<TrieNode[]>([])
function freshTrie() {
  nodes.length = 0
  nodes.push({ id: 0, ch: '', path: '', isWord: false, frequency: 0, children: {}, parent: -1 })
}
function insertWord(raw: string) {
  const w = raw.toLowerCase().replace(/[^a-z]/g, '')
  if (!w) return ''
  let cur = 0
  for (const ch of w) {
    const child = nodes[cur].children[ch]
    if (child === undefined) {
      const id = nodes.length
      nodes.push({
        id, ch, path: nodes[cur].path + ch, isWord: false,
        frequency: 0, children: {}, parent: cur,
      })
      nodes[cur].children[ch] = id
      cur = id
    } else {
      cur = child
    }
  }
  nodes[cur].isWord = true
  nodes[cur].frequency += 1
  return w
}
freshTrie()
SEED.forEach(insertWord)

/* ---------- tidy layout: x by depth, y packed per leaf order ----------
   Classic "reingold-tidier-ish" layout: assign each leaf a slot in a
   DFS order, then each internal node centers over its children. */
const layout = reactive<Record<number, { x: number; y: number }>>({})
const SVG_W = 560
const SVG_H = 250
const COL = 64                     // px per depth level
const PAD_X = 30
function relayout() {
  for (const k in layout) delete layout[k]
  let leafY = 0
  const ys: Record<number, number> = {}
  const depthOf = (id: number) => nodes[id].path.length
  const dfs = (id: number): number => {
    const kids = Object.keys(nodes[id].children).sort()
      .map(ch => nodes[id].children[ch])
    let y: number
    if (kids.length === 0) {
      y = leafY
      leafY += 1
    } else {
      const cy = kids.map(dfs)
      y = (cy[0] + cy[cy.length - 1]) / 2
    }
    ys[id] = y
    return y
  }
  dfs(0)
  const rows = Math.max(1, leafY - 1)
  for (const id in ys) {
    const n = Number(id)
    layout[n] = {
      x: PAD_X + depthOf(n) * COL,
      y: 22 + (ys[n] / rows) * (SVG_H - 44),
    }
  }
}
relayout()

const visibleNodes = computed(() => nodes.filter(n => n.id !== 0))
const edges = computed(() =>
  nodes.flatMap(n =>
    Object.values(n.children).map(cid => ({ from: n.id, to: cid }))),
)

/* ---------- controls ---------- */
const prefix = ref('')
const k = ref(5)
const ranker = ref<RankSlug>('freq')
const insertField = ref('')

/* ---------- walk / dfs animation state ---------- */
const walkPath = ref<number[]>([])     // node ids on the O(L) walk (incl. matched depth)
const prefixNode = ref<number>(-1)     // -1 = root / none, -2 = miss
const subtreeIds = ref<Set<number>>(new Set())
const dfsActive = ref<number>(-1)      // node currently pulsed by the DFS sweep
const visited = ref<Set<number>>(new Set())
const stepCount = ref(0)               // the "O(L)" walk counter
const candidates = ref<[string, number][]>([])   // collected (word, freq) pool
const collecting = ref(false)
const miss = ref(false)                // prefix not in trie

let busy = false
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

/* ---------- the suggest() pipeline, animated ---------- */
function runSuggest() {
  clearTimers()
  busy = true
  walkPath.value = [0]
  prefixNode.value = -1
  subtreeIds.value = new Set()
  visited.value = new Set()
  candidates.value = []
  dfsActive.value = -1
  miss.value = false
  collecting.value = false

  const p = prefix.value.toLowerCase()
  stepCount.value = 0

  // empty prefix -> root subtree (whole dictionary)
  if (!p) {
    prefixNode.value = 0
    after(180, () => collectSubtree(0))
    return
  }

  // O(L) walk: one hop per character
  const hop = (cur: number, i: number) => {
    if (i >= p.length) {
      prefixNode.value = cur
      after(220, () => collectSubtree(cur))
      return
    }
    const ch = p[i]
    const next = nodes[cur].children[ch]
    stepCount.value = i + 1
    if (next === undefined) {
      // dead edge -> prefix absent
      miss.value = true
      prefixNode.value = -2
      busy = false
      return
    }
    walkPath.value = [...walkPath.value, next]
    after(220, () => hop(next, i + 1))
  }
  after(150, () => hop(0, 0))
}

/* DFS sweep over the prefix subtree, pulsing nodes in visit order and
   dropping each terminal into the candidate pool. */
function collectSubtree(rootId: number) {
  collecting.value = true
  const order: number[] = []
  const sub = new Set<number>()
  const found: [string, number][] = []
  const dfs = (id: number) => {
    order.push(id)
    sub.add(id)
    if (nodes[id].isWord) found.push([nodes[id].path, nodes[id].frequency])
    for (const ch of Object.keys(nodes[id].children).sort()) {
      dfs(nodes[id].children[ch])
    }
  }
  dfs(rootId)
  subtreeIds.value = sub

  // pulse nodes in visit order; reveal each word as its node lights up
  const STEP = order.length > 22 ? 70 : 120
  const tick = (i: number) => {
    if (i >= order.length) {
      candidates.value = found
      dfsActive.value = -1
      collecting.value = false
      busy = false
      return
    }
    const id = order[i]
    dfsActive.value = id
    visited.value = new Set([...visited.value, id])
    if (nodes[id].isWord) {
      candidates.value = [...candidates.value, [nodes[id].path, nodes[id].frequency]]
    }
    after(STEP, () => tick(i + 1))
  }
  tick(0)
}

/* ---------- ranking strategies (decoupled from traversal) ---------- */
function rankFreq(c: [string, number][], n: number): [string, number][] {
  // heapq.nlargest(k, key=(freq, word)) — stable bounded top-k
  return [...c].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, n)
}
function rankAlpha(c: [string, number][], n: number): [string, number][] {
  return [...c].sort((a, b) => a[0].localeCompare(b[0])).slice(0, n)
}
// suggestions re-derive from the SAME candidate pool — no re-walk, counter frozen
const suggestions = computed<[string, number][]>(() =>
  ranker.value === 'freq'
    ? rankFreq(candidates.value, k.value)
    : rankAlpha(candidates.value, k.value),
)
const totalFound = computed(() => candidates.value.length)
const rankNote = computed(() =>
  ranker.value === 'freq'
    ? `heapq.nlargest(${k.value}, key=(freq, word))`
    : `sorted(cands)[:${k.value}]`,
)

/* ---------- input handlers ---------- */
function onType(e: Event) {
  prefix.value = (e.target as HTMLInputElement).value.replace(/[^a-zA-Z]/g, '')
  runSuggest()
}
function clearPrefix() {
  prefix.value = ''
  runSuggest()
}
function doInsert() {
  const w = insertWord(insertField.value)
  if (!w) return
  relayout()
  insertField.value = ''
  prefix.value = w
  flashInsert.value = w
  after(900, () => { if (flashInsert.value === w) flashInsert.value = '' })
  runSuggest()
}
const flashInsert = ref('')

function resetAll() {
  clearTimers()
  busy = false
  freshTrie()
  SEED.forEach(insertWord)
  relayout()
  prefix.value = ''
  k.value = 5
  ranker.value = 'freq'
  insertField.value = ''
  flashInsert.value = ''
  runSuggest()
}

// initial fan-out over the whole dictionary
runSuggest()

/* node visual class helper */
function nodeKind(n: TrieNode): string {
  if (n.id === prefixNode.value) return 'prefix'
  if (dfsActive.value === n.id) return 'pulse'
  if (subtreeIds.value.has(n.id) && visited.value.has(n.id)) return 'sub'
  if (walkPath.value.includes(n.id)) return 'walk'
  return ''
}
function maxFreq(): number {
  return Math.max(1, ...candidates.value.map(c => c[1]))
}
</script>

<template>
  <div class="tx">
    <!-- ============ LEFT: driver / controls ============ -->
    <div class="drive">
      <div class="dtag">suggest(prefix, k)</div>

      <!-- prefix input -->
      <div class="field">
        <span class="flbl">prefix</span>
        <div class="inwrap">
          <span class="caret">&gt;</span>
          <input
            class="pin"
            :value="prefix"
            placeholder="type e.g. ap"
            spellcheck="false"
            @input="onType"
          />
          <button v-if="prefix" class="xbtn" @click="clearPrefix">x</button>
        </div>
      </div>

      <!-- O(L) walk counter + miss flag -->
      <div class="metric">
        <span class="mlbl">O(L) walk</span>
        <span class="mval">{{ stepCount }}<i> hop{{ stepCount === 1 ? '' : 's' }}</i></span>
        <span class="mlen">L = {{ prefix.length }}</span>
        <span v-if="miss" class="missflag">prefix absent &rarr; []</span>
      </div>

      <!-- ranking strategy toggle -->
      <div class="field">
        <span class="flbl">RankingStrategy</span>
        <div class="seg">
          <button
            class="sopt"
            :class="{ on: ranker === 'freq' }"
            @click="ranker = 'freq'"
          >Frequency</button>
          <button
            class="sopt"
            :class="{ on: ranker === 'alpha' }"
            @click="ranker = 'alpha'"
          >Alphabetical</button>
        </div>
      </div>

      <!-- k limit slider -->
      <div class="field">
        <span class="flbl">limit k <b>{{ k }}</b></span>
        <input
          class="slider"
          type="range"
          min="1"
          max="10"
          v-model.number="k"
        />
      </div>

      <!-- insert word -->
      <div class="field">
        <span class="flbl">insert(word)</span>
        <div class="inwrap insert">
          <input
            class="pin"
            v-model="insertField"
            placeholder="grow a branch"
            spellcheck="false"
            @keyup.enter="doInsert"
          />
          <button class="addbtn" @click="doInsert">+ insert</button>
        </div>
      </div>

      <div class="rnote">
        <span class="rk">rank:</span> <code>{{ rankNote }}</code>
      </div>
      <button class="reset" @click="resetAll">&#9851; reset dictionary</button>
    </div>

    <!-- ============ RIGHT: trie diagram + suggestions ============ -->
    <div class="stage">
      <div class="stagehead">
        <span class="stag">Trie &middot; {{ visibleNodes.length }} nodes</span>
        <span class="legend">
          <span class="lg walk">walk</span>
          <span class="lg sub">subtree</span>
          <span class="lg word">word + freq</span>
        </span>
      </div>

      <div class="diagram">
        <svg :viewBox="`0 0 ${SVG_W} ${SVG_H}`" class="trie" preserveAspectRatio="xMinYMid meet">
          <!-- edges -->
          <line
            v-for="e in edges"
            :key="e.from + '-' + e.to"
            :x1="layout[e.from].x"
            :y1="layout[e.from].y"
            :x2="layout[e.to].x"
            :y2="layout[e.to].y"
            class="edge"
            :class="{
              walk: walkPath.includes(e.from) && walkPath.includes(e.to),
              sub: subtreeIds.has(e.to) && visited.has(e.to),
            }"
          />
          <!-- root marker -->
          <g>
            <circle :cx="layout[0].x" :cy="layout[0].y" r="9" class="root" />
            <text :x="layout[0].x" :y="layout[0].y + 3" class="rtxt">/</text>
          </g>
          <!-- nodes -->
          <g
            v-for="n in visibleNodes"
            :key="n.id"
            class="node"
            :class="[nodeKind(n), { word: n.isWord, hot: flashInsert && n.path === flashInsert }]"
          >
            <circle
              v-if="n.isWord"
              :cx="layout[n.id].x"
              :cy="layout[n.id].y"
              r="11"
              class="ring"
            />
            <circle
              :cx="layout[n.id].x"
              :cy="layout[n.id].y"
              r="8"
              class="disc"
            />
            <text :x="layout[n.id].x" :y="layout[n.id].y + 3" class="ch">{{ n.ch }}</text>
            <!-- frequency badge on word nodes -->
            <g v-if="n.isWord">
              <circle :cx="layout[n.id].x + 11" :cy="layout[n.id].y - 9" r="6" class="fbg" />
              <text :x="layout[n.id].x + 11" :y="layout[n.id].y - 6.5" class="ftxt">{{ n.frequency }}</text>
            </g>
          </g>
        </svg>
      </div>

      <!-- suggestion panel -->
      <div class="sugg">
        <div class="sughead">
          <span class="sutag">
            <span v-if="collecting" class="live">DFS collecting&hellip;</span>
            <span v-else>top-{{ k }} of {{ totalFound }}</span>
          </span>
          <span class="reorder">re-rank is in-place &mdash; Trie untouched</span>
        </div>
        <div class="chips">
          <transition-group name="rank">
            <span
              v-for="(s, i) in suggestions"
              :key="s[0]"
              class="sc"
              :class="{ top: i === 0 && ranker === 'freq' }"
            >
              <span class="rank-i">{{ i + 1 }}</span>
              {{ s[0] }}
              <i class="fb">{{ s[1] }}</i>
            </span>
          </transition-group>
          <span v-if="!suggestions.length && !collecting" class="empty">
            no completions under this prefix
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tx {
  display: grid;
  grid-template-columns: 0.9fr 2.1fr;
  gap: 1.1rem;
  width: 100%;
  height: 360px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- left driver ---------- */
.drive { display: flex; flex-direction: column; gap: .55rem; min-width: 0; }
.dtag { font-size: .58rem; letter-spacing: .07em; text-transform: uppercase; color: var(--bp-cyan); }
.field { display: flex; flex-direction: column; gap: .25rem; }
.flbl { font-size: .56rem; letter-spacing: .05em; text-transform: uppercase; color: var(--bp-dim); }
.flbl b { color: var(--bp-cyan); margin-left: .25rem; font-size: .68rem; }

.inwrap {
  display: flex; align-items: center; gap: .35rem;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6); padding: .25rem .45rem;
}
.inwrap:focus-within { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.caret { color: var(--bp-cyan); font-size: .72rem; }
.pin {
  flex: 1; min-width: 0; background: transparent; border: 0; outline: none;
  font-family: inherit; font-size: .8rem; color: #fff; letter-spacing: .04em;
}
.pin::placeholder { color: var(--bp-dim); opacity: .6; }
.xbtn {
  border: 0; background: transparent; color: var(--bp-dim); cursor: pointer;
  font-family: inherit; font-size: .7rem; padding: 0 .2rem;
}
.xbtn:hover { color: var(--bp-bad); }

/* metric row */
.metric {
  display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(34,211,238,.05); padding: .3rem .5rem;
}
.mlbl { font-size: .54rem; text-transform: uppercase; letter-spacing: .05em; color: var(--bp-dim); }
.mval { font-size: 1rem; color: var(--bp-cyan); text-shadow: var(--bp-glow); }
.mval i { font-size: .56rem; color: var(--bp-dim); font-style: normal; margin-left: .15rem; }
.mlen { font-size: .56rem; color: var(--bp-dim); margin-left: auto; }
.missflag { flex-basis: 100%; font-size: .56rem; color: var(--bp-bad); }

/* segmented toggle */
.seg { display: flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; }
.sopt {
  flex: 1; font-family: inherit; font-size: .64rem; cursor: pointer;
  border: 0; background: transparent; color: var(--bp-dim);
  padding: .3rem .25rem; transition: all .2s;
}
.sopt:first-child { border-right: 1px solid var(--bp-line); }
.sopt:hover { color: var(--bp-ink); }
.sopt.on { color: #fff; background: rgba(34,211,238,.14); box-shadow: inset 0 0 14px rgba(34,211,238,.25); }

/* slider */
.slider { -webkit-appearance: none; appearance: none; width: 100%; height: 4px;
  border-radius: 999px; background: var(--bp-line); outline: none; cursor: pointer; }
.slider::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none; width: 14px; height: 14px; border-radius: 999px;
  background: var(--bp-cyan); box-shadow: var(--bp-glow); border: 0; cursor: pointer;
}
.slider::-moz-range-thumb {
  width: 14px; height: 14px; border-radius: 999px; background: var(--bp-cyan);
  box-shadow: var(--bp-glow); border: 0; cursor: pointer;
}

/* insert */
.inwrap.insert { padding-right: .25rem; }
.addbtn {
  font-family: inherit; font-size: .6rem; cursor: pointer; white-space: nowrap;
  border: 1px solid var(--bp-violet); border-radius: 6px; color: var(--bp-violet);
  background: rgba(167,139,250,.12); padding: .2rem .45rem; transition: all .2s;
}
.addbtn:hover { background: rgba(167,139,250,.24); color: #fff; }

.rnote { font-size: .58rem; color: var(--bp-dim); margin-top: auto; }
.rnote .rk { color: var(--bp-violet); }
.rnote code { color: var(--bp-cyan); font-size: .56rem; }

.reset {
  font-family: inherit; font-size: .64rem; color: var(--bp-dim); cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; background: transparent;
  padding: .3rem .5rem; transition: all .2s; text-align: left;
}
.reset:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }

/* ---------- right stage ---------- */
.stage { display: flex; flex-direction: column; gap: .45rem; min-width: 0; }
.stagehead { display: flex; align-items: center; gap: .6rem; }
.stag { font-size: .58rem; letter-spacing: .07em; text-transform: uppercase; color: var(--bp-blue); }
.legend { display: flex; gap: .6rem; margin-left: auto; }
.lg { font-size: .52rem; color: var(--bp-dim); display: inline-flex; align-items: center; gap: .25rem; }
.lg::before { content: ''; width: 8px; height: 8px; border-radius: 999px; }
.lg.walk::before { background: var(--bp-cyan); }
.lg.sub::before { background: var(--bp-violet); }
.lg.word::before { background: var(--bp-good); }

.diagram {
  flex: 1; min-height: 0;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(7,11,20,.5); padding: .3rem;
  overflow: hidden;
}
.trie { width: 100%; height: 100%; display: block; }

.edge { stroke: var(--bp-line); stroke-width: 1.3; transition: stroke .25s, stroke-width .25s; }
.edge.sub { stroke: rgba(167,139,250,.55); stroke-width: 1.6; }
.edge.walk { stroke: var(--bp-cyan); stroke-width: 2.2; filter: drop-shadow(0 0 4px rgba(34,211,238,.6)); }

.root { fill: var(--bp-bg-2); stroke: var(--bp-dim); stroke-width: 1.3; }
.rtxt { fill: var(--bp-dim); font-size: 9px; text-anchor: middle; font-family: "Fira Code", monospace; }

.node .disc { fill: var(--bp-bg-2); stroke: var(--bp-line); stroke-width: 1.3; transition: all .25s; }
.node .ch { fill: var(--bp-dim); font-size: 9px; text-anchor: middle; font-family: "Fira Code", monospace; transition: fill .25s; }
.node .ring { fill: none; stroke: rgba(74,222,128,.5); stroke-width: 1.4; }

/* word nodes (terminal) */
.node.word .disc { stroke: var(--bp-good); }
.node.word .ch { fill: var(--bp-good); }
.fbg { fill: var(--bp-bg); stroke: var(--bp-good); stroke-width: 1; }
.ftxt { fill: var(--bp-good); font-size: 7px; text-anchor: middle; font-family: "Fira Code", monospace; }

/* walk highlight */
.node.walk .disc { stroke: var(--bp-cyan); fill: rgba(34,211,238,.12); }
.node.walk .ch { fill: #fff; }

/* subtree (visited by DFS) */
.node.sub .disc { stroke: var(--bp-violet); fill: rgba(167,139,250,.1); }
.node.sub .ch { fill: var(--bp-ink); }

/* prefix node — the landing point */
.node.prefix .disc { stroke: var(--bp-cyan); fill: rgba(34,211,238,.22); stroke-width: 2; filter: drop-shadow(0 0 6px rgba(34,211,238,.7)); }
.node.prefix .ch { fill: #fff; }

/* DFS pulse */
.node.pulse .disc { stroke: var(--bp-violet); fill: rgba(167,139,250,.4); stroke-width: 2; filter: drop-shadow(0 0 7px rgba(167,139,250,.8)); }
.node.pulse .ch { fill: #fff; }

/* freshly inserted */
.node.hot .disc { stroke: var(--bp-good); fill: rgba(74,222,128,.3); animation: pop .5s ease; }
@keyframes pop { 0% { transform-box: fill-box; transform-origin: center; transform: scale(.4); } 60% { transform: scale(1.3); } 100% { transform: scale(1); } }

/* ---------- suggestions ---------- */
.sugg {
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: linear-gradient(180deg, rgba(74,222,128,.05), rgba(74,222,128,.01));
  padding: .4rem .55rem; min-height: 74px;
}
.sughead { display: flex; align-items: baseline; gap: .6rem; margin-bottom: .35rem; }
.sutag { font-size: .56rem; text-transform: uppercase; letter-spacing: .05em; color: var(--bp-good); }
.live { color: var(--bp-violet); }
.reorder { font-size: .54rem; color: var(--bp-dim); margin-left: auto; }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; align-content: flex-start; }
.sc {
  display: inline-flex; align-items: center; gap: .3rem;
  font-size: .68rem; color: var(--bp-ink);
  border: 1px solid var(--bp-line); border-radius: 999px;
  background: var(--bp-bg-2); padding: .14rem .45rem .14rem .2rem;
  transition: all .2s;
}
.sc .rank-i {
  font-size: .54rem; color: var(--bp-bg); background: var(--bp-dim);
  border-radius: 999px; width: 15px; height: 15px;
  display: inline-flex; align-items: center; justify-content: center;
}
.sc .fb { font-style: normal; font-size: .56rem; color: var(--bp-good);
  border: 1px solid rgba(74,222,128,.4); border-radius: 999px; padding: 0 .3rem; }
.sc.top { border-color: var(--bp-cyan); background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.sc.top .rank-i { background: var(--bp-cyan); }
.empty { font-size: .6rem; color: var(--bp-dim); opacity: .7; }

/* re-rank reorder transition — proves swap is in-place */
.rank-move { transition: transform .4s ease; }
.rank-enter-active { transition: all .3s ease; }
.rank-enter-from { opacity: 0; transform: scale(.7); }
.rank-leave-active { transition: all .2s ease; position: absolute; }
.rank-leave-to { opacity: 0; transform: scale(.7); }
</style>
