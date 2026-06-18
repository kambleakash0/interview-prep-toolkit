<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue'

/* ============================================================
   InvertedIndexSearchBoard — the inverted index + pluggable
   ranking Strategy, live. Index the docs once, fire a query,
   watch postings light up and result bars re-rank when you
   flip TF -> TF-IDF. The index never changes; only the
   Strategy decides order.
   ============================================================ */

type Slug = 'tf' | 'tfidf'

interface Doc { id: string; text: string }

/* preset corpus — chosen so a rare term ("ranking") outranks a
   common one ("search") under TF-IDF but not under raw TF, so
   the "engine ranking" query visibly re-sorts. */
const DOCS: Doc[] = [
  { id: 'D1', text: 'search engine search index' },
  { id: 'D2', text: 'a search engine ranks search results' },
  { id: 'D3', text: 'inverted index powers fast search' },
  { id: 'D4', text: 'ranking strategy scores the search engine' },
]

const TERM_RE = /[a-z0-9]+/g
function tokenize(text: string): string[] {
  return text.toLowerCase().match(TERM_RE) ?? []
}

/* ----- the inverted index, built by the Index button ----- */
// term -> { docId: freq }
const postings = reactive<Record<string, Record<string, number>>>({})
const indexed = ref(false)            // has the corpus been indexed yet?
const indexing = ref(false)           // mid-animation
const litTerm = ref('')               // term row pulsing as tokens land
const tokenFly = ref<{ id: number; term: string; doc: string } | null>(null)
const N = DOCS.length

const terms = computed(() => Object.keys(postings).sort())
// df = number of docs a term appears in (length of its postings list)
function df(term: string): number { return Object.keys(postings[term] ?? {}).length }
// max freq across the whole index, for the heat tint
const maxFreq = computed(() => {
  let m = 1
  for (const t of terms.value) for (const d in postings[t]) m = Math.max(m, postings[t][d])
  return m
})
function heat(freq: number): string {
  const a = 0.1 + 0.5 * (freq / maxFreq.value)
  return `rgba(34,211,238,${a.toFixed(3)})`
}

/* ----- query + ranking state ----- */
interface Chip { label: string }
const CHIPS: Chip[] = [
  { label: 'search' },
  { label: 'engine ranking' },
  { label: 'index' },
]
const query = ref('')
const activeQuery = ref('')           // last query actually run
const strategy = ref<Slug>('tf')
const queryTerms = ref<string[]>([])  // tokenized active query (those present in index)
const litDocs = ref<string[]>([])     // docs touched by the query (for connector lines)
const hovDoc = ref('')                // doc card hovered/clicked -> highlight

interface Result { doc: string; score: number }
const results = ref<Result[]>([])     // ranked, descending

let uid = 0
const timers: number[] = []
function later(fn: () => void, ms: number) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

/* ----- build the index, animated term by term ----- */
function buildIndex() {
  if (indexing.value) return
  clearTimers()
  for (const k in postings) delete postings[k]
  indexed.value = false
  indexing.value = true
  litTerm.value = ''
  resetQuery()

  // flatten every (doc, term) occurrence into an ordered emission list
  const emissions: { doc: string; term: string }[] = []
  for (const d of DOCS) for (const t of tokenize(d.text)) emissions.push({ doc: d.id, term: t })

  const step = (i: number) => {
    if (i >= emissions.length) {
      indexing.value = false
      indexed.value = true
      litTerm.value = ''
      tokenFly.value = null
      return
    }
    const e = emissions[i]
    if (!postings[e.term]) postings[e.term] = {}
    postings[e.term][e.doc] = (postings[e.term][e.doc] ?? 0) + 1
    litTerm.value = e.term
    tokenFly.value = { id: ++uid, term: e.term, doc: e.doc }
    later(() => step(i + 1), 150)
  }
  step(0)
}

/* ----- ranking strategies (pluggable scorer) ----- */
// tf: raw term frequency. tfidf: tf * log(1 + N/df) — smoothed,
// always-positive IDF so rare terms dominate without negative bars.
function termScore(term: string, doc: string): number {
  const tf = postings[term]?.[doc] ?? 0
  if (tf === 0) return 0
  if (strategy.value === 'tf') return tf
  const idf = Math.log(1 + N / df(term))
  return tf * idf
}

const formula = computed(() =>
  strategy.value === 'tf'
    ? 'score = sum( tf(term, doc) )'
    : 'score = sum( tf * log(1 + N/df) )'
)

function resetQuery() {
  activeQuery.value = ''
  queryTerms.value = []
  litDocs.value = []
  results.value = []
}

/* ----- run a search: union postings, score via Strategy, sort ----- */
function runQuery(raw: string) {
  if (!indexed.value || indexing.value) return
  query.value = raw
  activeQuery.value = raw
  const toks = tokenize(raw).filter(t => postings[t])
  queryTerms.value = toks

  // union the candidate docs across all matched query terms
  const cand = new Set<string>()
  for (const t of toks) for (const d in postings[t]) cand.add(d)
  litDocs.value = [...cand]

  rescore()
}

// re-score the SAME candidate set; only the Strategy changes the order
function rescore() {
  const scored: Result[] = litDocs.value.map(doc => {
    let s = 0
    for (const t of queryTerms.value) s += termScore(t, doc)
    return { doc, score: s }
  })
  scored.sort((a, b) => b.score - a.score)
  results.value = scored
}

function setStrategy(s: Slug) {
  if (strategy.value === s) return
  strategy.value = s
  if (activeQuery.value) rescore()    // bars re-sort; index untouched
}

const maxScore = computed(() => Math.max(1e-6, ...results.value.map(r => r.score)))
function barPct(score: number): number {
  return Math.max(6, Math.round((score / maxScore.value) * 100))
}
function fmt(n: number): string {
  return n === 0 ? '0' : (Math.round(n * 100) / 100).toString()
}

// does a doc participate in the active query? (for connector lines + glow)
function isHit(docId: string): boolean { return litDocs.value.includes(docId) }
// which terms in this doc matched the active query (highlight in doc text)
function docMatchedTerms(): Set<string> { return new Set(queryTerms.value) }
function reset() {
  clearTimers()
  for (const k in postings) delete postings[k]
  indexed.value = false
  indexing.value = false
  litTerm.value = ''
  tokenFly.value = null
  query.value = ''
  strategy.value = 'tf'
  resetQuery()
}
</script>

<template>
  <div class="iib">
    <!-- ============ LEFT: document corpus ============ -->
    <div class="col docs">
      <div class="ctag">Corpus · {{ N }} docs</div>
      <div class="doclist">
        <div
          v-for="d in DOCS"
          :key="d.id"
          class="doc"
          :class="{ hit: isHit(d.id), focus: hovDoc === d.id }"
          @mouseenter="hovDoc = d.id"
          @mouseleave="hovDoc = ''"
          @click="hovDoc = hovDoc === d.id ? '' : d.id"
        >
          <span class="did">{{ d.id }}</span>
          <span class="dtext">
            <template v-for="(w, i) in d.text.split(' ')" :key="i"><span
              :class="{ qmatch: activeQuery && docMatchedTerms().has(w.toLowerCase()) }"
            >{{ w }}</span><span v-if="i < d.text.split(' ').length - 1"> </span></template>
          </span>
        </div>
      </div>
      <div class="hint">
        One <b>Tokenizer</b> (split + lowercase) feeds index <i>and</i> query.
      </div>
    </div>

    <!-- ============ CENTER: inverted index table ============ -->
    <div class="col indexcol">
      <div class="ctag">
        Inverted index
        <span class="sub">term &#8594; postings (docId:freq)</span>
      </div>

      <div class="table">
        <div v-if="!terms.length" class="empty">
          <span v-if="indexing">building index&hellip;</span>
          <span v-else>press <b>Index</b> to flip docs &#8594; index</span>
        </div>
        <div
          v-for="t in terms"
          :key="t"
          class="trow"
          :class="{ lit: litTerm === t, qrow: queryTerms.includes(t) }"
        >
          <span class="term">{{ t }}</span>
          <span class="postings">
            <span
              v-for="d in DOCS"
              v-show="postings[t] && postings[t][d.id]"
              :key="d.id"
              class="cell"
              :class="{ qcell: queryTerms.includes(t) && litDocs.includes(d.id) }"
              :style="{ background: heat(postings[t]?.[d.id] || 1) }"
            >{{ d.id }}<i>:{{ postings[t]?.[d.id] }}</i></span>
          </span>
          <span class="df">df {{ df(t) }}</span>
        </div>

        <!-- a token flying from doc into the table during indexing -->
        <transition name="fly">
          <span v-if="tokenFly" :key="tokenFly.id" class="flytoken">
            {{ tokenFly.term }}<i>&#8592;{{ tokenFly.doc }}</i>
          </span>
        </transition>
      </div>

      <div class="ixhint">
        Built <b>once</b>. Lookup is O(1) per term — no full scan.
      </div>
    </div>

    <!-- ============ RIGHT: query + ranked results ============ -->
    <div class="col searchcol">
      <div class="ctag">Search</div>

      <div class="qbar">
        <input
          v-model="query"
          class="qinput"
          :disabled="!indexed"
          placeholder="type a query…"
          spellcheck="false"
          @keyup.enter="runQuery(query)"
        />
        <button class="go" :disabled="!indexed || !query" @click="runQuery(query)">run</button>
      </div>

      <div class="chips">
        <button
          v-for="c in CHIPS"
          :key="c.label"
          class="chip"
          :class="{ on: activeQuery === c.label }"
          :disabled="!indexed"
          @click="runQuery(c.label)"
        >{{ c.label }}</button>
      </div>

      <!-- Strategy toggle: re-scores the SAME candidates -->
      <div class="strat">
        <span class="slabel">Ranking Strategy</span>
        <div class="seg">
          <button class="segb" :class="{ on: strategy === 'tf' }" @click="setStrategy('tf')">TF</button>
          <button class="segb" :class="{ on: strategy === 'tfidf' }" @click="setStrategy('tfidf')">TF-IDF</button>
        </div>
      </div>
      <div class="formula"><span class="fk">&fnof;</span> {{ formula }}</div>

      <!-- ranked horizontal bars -->
      <div class="bars">
        <transition-group name="rank">
          <div v-for="(r, i) in results" :key="r.doc" class="barrow">
            <span class="rank">{{ i + 1 }}</span>
            <span class="bdoc" :class="{ focus: hovDoc === r.doc }">{{ r.doc }}</span>
            <span class="track">
              <span
                class="fill"
                :class="{ top: i === 0 }"
                :style="{ width: barPct(r.score) + '%' }"
              />
            </span>
            <span class="bscore">{{ fmt(r.score) }}</span>
          </div>
        </transition-group>
        <div v-if="activeQuery && !results.length" class="nohit">no postings for "{{ activeQuery }}"</div>
        <div v-else-if="!activeQuery" class="nohit dim">run a query to rank documents</div>
      </div>
    </div>

    <!-- ============ controls + connector overlay ============ -->
    <div class="ctrls">
      <button class="run" :disabled="indexing" @click="buildIndex">
        <span class="dot" :class="{ done: indexed }" /> {{ indexed ? 'Re-index' : 'Index corpus' }}
      </button>
      <button class="ghost" @click="reset">&#9851; reset</button>
      <span class="aha">
        Index built once; the pluggable <b>Strategy</b> decides order. TF vs TF-IDF disagree on
        <code>engine ranking</code> — flip it and watch the bars re-sort.
      </span>
    </div>
  </div>
</template>

<style scoped>
.iib {
  position: relative;
  width: 100%;
  height: 364px;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: 0.92fr 1.18fr 1.04fr;
  grid-template-rows: 1fr auto;
  gap: 0.9rem;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}
.col { display: flex; flex-direction: column; gap: .45rem; min-width: 0; min-height: 0; }
.ctag {
  font-size: .58rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--bp-cyan); display: flex; align-items: baseline; gap: .4rem;
}
.ctag .sub { font-size: .5rem; color: var(--bp-dim); text-transform: none; letter-spacing: 0; }

/* ---------- documents ---------- */
.doclist { display: flex; flex-direction: column; gap: .4rem; min-height: 0; }
.doc {
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02); padding: .35rem .5rem;
  cursor: pointer; transition: all .25s; display: flex; flex-direction: column; gap: .15rem;
}
.doc:hover { border-color: var(--bp-cyan); background: rgba(34,211,238,.05); }
.doc.hit { border-color: rgba(34,211,238,.5); background: rgba(34,211,238,.08); box-shadow: var(--bp-glow); }
.doc.focus { border-color: var(--bp-cyan); }
.did { font-size: .58rem; color: var(--bp-blue); letter-spacing: .06em; }
.dtext { font-size: .62rem; color: var(--bp-dim); line-height: 1.4; }
.dtext .qmatch { color: var(--bp-cyan); text-shadow: var(--bp-glow); border-bottom: 1px solid var(--bp-cyan); }
.hint { font-size: .55rem; color: var(--bp-dim); line-height: 1.4; margin-top: auto; }
.hint b { color: var(--bp-ink); }

/* ---------- inverted index table ---------- */
.indexcol { min-width: 0; }
.table {
  position: relative; flex: 1; min-height: 0; overflow-y: auto;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: rgba(7,11,20,.5); padding: .35rem .4rem;
  display: flex; flex-direction: column; gap: .18rem;
}
.table::-webkit-scrollbar { width: 6px; }
.table::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.empty { margin: auto; font-size: .6rem; color: var(--bp-dim); text-align: center; }
.empty b { color: var(--bp-cyan); }
.trow {
  display: flex; align-items: center; gap: .4rem;
  padding: .14rem .3rem; border-radius: 6px;
  border: 1px solid transparent; transition: all .2s;
}
.trow.lit { border-color: var(--bp-cyan); background: rgba(34,211,238,.1); box-shadow: var(--bp-glow); }
.trow.qrow { border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.06); }
.term { font-size: .6rem; color: var(--bp-ink); width: 5.6rem; flex: none; overflow: hidden; text-overflow: ellipsis; }
.trow.qrow .term { color: var(--bp-good); }
.postings { display: flex; gap: .25rem; flex: 1; flex-wrap: wrap; }
.cell {
  font-size: .52rem; color: #fff; border: 1px solid var(--bp-line);
  border-radius: 5px; padding: .04rem .3rem; transition: all .2s; white-space: nowrap;
}
.cell i { font-style: normal; color: var(--bp-cyan); opacity: .9; }
.cell.qcell { border-color: var(--bp-good); box-shadow: 0 0 10px rgba(74,222,128,.4); }
.df { font-size: .5rem; color: var(--bp-dim); flex: none; }
.flytoken {
  position: absolute; right: .5rem; bottom: .4rem;
  font-size: .55rem; color: var(--bp-bg); background: var(--bp-cyan);
  border-radius: 999px; padding: .08rem .45rem; box-shadow: var(--bp-glow); white-space: nowrap;
}
.flytoken i { font-style: normal; opacity: .8; margin-left: .15rem; }
.fly-enter-active { transition: all .15s ease-out; }
.fly-enter-from { opacity: 0; transform: translateX(-22px) scale(.8); }
.fly-leave-active { transition: all .12s; }
.fly-leave-to { opacity: 0; transform: translateX(14px) scale(.7); }
.ixhint { font-size: .55rem; color: var(--bp-dim); }
.ixhint b { color: var(--bp-good); }

/* ---------- search column ---------- */
.searchcol { min-width: 0; }
.qbar { display: flex; gap: .4rem; }
.qinput {
  flex: 1; min-width: 0; font-family: inherit; font-size: .66rem;
  color: var(--bp-ink); background: rgba(7,11,20,.6);
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .35rem .5rem; outline: none;
  transition: border-color .2s;
}
.qinput:focus { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.qinput:disabled { opacity: .4; }
.qinput::placeholder { color: var(--bp-dim); }
.go {
  font-family: inherit; font-size: .64rem; color: #fff; cursor: pointer;
  border: 1px solid var(--bp-cyan); border-radius: 8px; padding: .35rem .65rem;
  background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); transition: all .2s;
}
.go:hover:not(:disabled) { background: rgba(34,211,238,.22); }
.go:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.chips { display: flex; gap: .35rem; flex-wrap: wrap; }
.chip {
  font-family: inherit; font-size: .58rem; color: var(--bp-dim); cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 999px; padding: .18rem .55rem;
  background: var(--bp-bg-2); transition: all .2s;
}
.chip:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-ink); }
.chip.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); }
.chip:disabled { opacity: .35; cursor: not-allowed; }

.strat { display: flex; align-items: center; gap: .5rem; margin-top: .1rem; }
.slabel { font-size: .55rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-violet); }
.seg { display: flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; margin-left: auto; }
.segb {
  font-family: inherit; font-size: .6rem; color: var(--bp-dim); cursor: pointer;
  background: transparent; border: none; padding: .22rem .6rem; transition: all .2s;
}
.segb:hover { color: var(--bp-ink); }
.segb.on { color: #fff; background: rgba(167,139,250,.2); box-shadow: 0 0 14px rgba(167,139,250,.35); }
.formula { font-size: .56rem; color: var(--bp-dim); display: flex; gap: .3rem; align-items: baseline; }
.formula .fk { color: var(--bp-violet); }

/* ---------- ranked bars ---------- */
.bars { display: flex; flex-direction: column; gap: .3rem; flex: 1; min-height: 0; margin-top: .1rem; }
.barrow { display: flex; align-items: center; gap: .4rem; }
.rank { font-size: .55rem; color: var(--bp-dim); width: .8rem; flex: none; text-align: center; }
.bdoc { font-size: .6rem; color: var(--bp-blue); width: 1.4rem; flex: none; transition: color .2s; }
.bdoc.focus { color: var(--bp-cyan); text-shadow: var(--bp-glow); }
.track { flex: 1; height: 13px; border-radius: 999px; background: rgba(255,255,255,.04); border: 1px solid var(--bp-line); overflow: hidden; }
.fill {
  display: block; height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, rgba(34,211,238,.35), var(--bp-cyan));
  transition: width .55s cubic-bezier(.4,0,.2,1);
}
.fill.top { background: linear-gradient(90deg, rgba(74,222,128,.4), var(--bp-good)); box-shadow: 0 0 14px rgba(74,222,128,.5); }
.bscore { font-size: .56rem; color: var(--bp-ink); width: 2.1rem; flex: none; text-align: right; }
.nohit { font-size: .58rem; color: var(--bp-bad); margin: auto 0; }
.nohit.dim { color: var(--bp-dim); }
.rank-move { transition: transform .55s cubic-bezier(.4,0,.2,1); }

/* ---------- controls ---------- */
.ctrls {
  grid-column: 1 / -1;
  display: flex; align-items: center; gap: .6rem; flex-wrap: wrap;
  border-top: 1px solid var(--bp-line); padding-top: .45rem;
}
.run {
  display: inline-flex; align-items: center; gap: .45rem;
  font-family: inherit; font-size: .66rem; color: #fff; cursor: pointer;
  border: 1px solid var(--bp-cyan); border-radius: 8px; padding: .34rem .7rem;
  background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); transition: all .2s;
}
.run:hover:not(:disabled) { background: rgba(34,211,238,.22); }
.run:disabled { opacity: .5; cursor: not-allowed; }
.run .dot { width: 8px; height: 8px; border-radius: 999px; background: var(--bp-dim); transition: all .25s; }
.run .dot.done { background: var(--bp-good); box-shadow: 0 0 12px rgba(74,222,128,.6); }
.ghost {
  font-family: inherit; font-size: .64rem; color: var(--bp-dim); cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .34rem .6rem;
  background: transparent; transition: all .2s;
}
.ghost:hover { border-color: var(--bp-cyan); color: var(--bp-ink); }
.aha { font-size: .56rem; color: var(--bp-dim); line-height: 1.4; flex: 1; min-width: 12rem; }
.aha b { color: var(--bp-violet); }
.aha code { color: var(--bp-cyan); background: rgba(34,211,238,.08); border: 1px solid var(--bp-line); border-radius: 4px; padding: 0 .3rem; }
</style>
