<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   LruCacheBoard — a capacity-3 LRU cache, live.
   Top: the doubly linked list (HEAD=MRU .. TAIL=LRU sentinels).
   Bottom: the dict as key chips, each arrow fanning to its node.
   Fire put/get and watch move_to_front slide nodes to the head
   and a capacity overflow evict the tail + del map[node.key].
   ============================================================ */

const CAP = 3

interface Node {
  id: number          // stable identity so transitions/arrows track the node
  key: string
  value: string
}

// ---- reactive cache state ----
// list order is MRU -> LRU (index 0 == head side, just after dummy HEAD)
const list = ref<Node[]>([])
// dict: key -> node id (mirrors map[key] = *node ref*, not the value)
const map = reactive<Record<string, number>>({})

let nextId = 1
function fresh(key: string, value: string): Node {
  return { id: nextId++, key, value }
}

// ---- op-log narration (mirrors the engine trace) ----
interface LogLine { id: number; text: string; kind: 'hit' | 'miss' | 'put' | 'evict' | 'info' }
const logLines = ref<LogLine[]>([])
let logId = 1
function log(text: string, kind: LogLine['kind']) {
  logLines.value.push({ id: logId++, text, kind })
  if (logLines.value.length > 6) logLines.value.shift()
}

// ---- transient highlight flags the template binds to ----
const touchedId = ref<number | null>(null)   // node sliding to head (get-hit / put-update)
const evictId = ref<number | null>(null)      // tail node flashing red before detach
const enteringId = ref<number | null>(null)   // freshly inserted node
const missFlash = ref(false)                  // get-miss "null" flash
const caption = ref('')

// busy guard + timer registry, cleaned up on unmount (mirrors the references)
let busy = false
const timers: number[] = []
function after(ms: number, fn: () => void) { timers.push(window.setTimeout(fn, ms)) }
function clearTimers() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearTimers)

// recency tint 0 (MRU/warm) .. 1 (LRU/cold), used for the meter + node hue
function recency(i: number): number {
  if (list.value.length <= 1) return 0
  return i / (list.value.length - 1)
}

const sizeText = computed(() => `${list.value.length}/${CAP}`)
const atCap = computed(() => list.value.length >= CAP)

// ---- core mechanics, each step narrated ----

function moveToFront(id: number) {
  const i = list.value.findIndex(n => n.id === id)
  if (i <= 0) return
  const [node] = list.value.splice(i, 1)
  list.value.unshift(node)
}

function get(rawKey: string) {
  if (busy) return
  const key = rawKey.trim()
  if (!key) return
  busy = true
  clearTimers()
  touchedId.value = null
  evictId.value = null
  enteringId.value = null
  missFlash.value = false

  const nodeId = map[key]
  caption.value = `get(${key}) -> map.get(${key})`

  if (nodeId === undefined) {
    // get-miss: flash null, no list mutation
    missFlash.value = true
    caption.value = `get(${key}) -> miss -> return null`
    log(`get ${key} -> miss -> null`, 'miss')
    after(900, () => { missFlash.value = false; busy = false })
    return
  }

  // get-hit: light the node, then move_to_front
  touchedId.value = nodeId
  caption.value = `get(${key}) -> hit -> list.move_to_front(node)`
  after(420, () => {
    moveToFront(nodeId)
    const node = list.value.find(n => n.id === nodeId)
    caption.value = `get(${key}) -> hit -> return ${node?.value}`
    log(`get ${key} -> hit -> move_to_front`, 'hit')
    after(620, () => { touchedId.value = null; busy = false })
  })
}

function put(rawKey: string, rawValue: string) {
  if (busy) return
  const key = rawKey.trim()
  const value = (rawValue.trim() || key)
  if (!key) return
  busy = true
  clearTimers()
  touchedId.value = null
  evictId.value = null
  enteringId.value = null
  missFlash.value = false

  // 1) key already present -> update value, move_to_front
  const existingId = map[key]
  if (existingId !== undefined) {
    const node = list.value.find(n => n.id === existingId)!
    node.value = value
    touchedId.value = existingId
    caption.value = `put(${key},${value}) -> key in map -> update + move_to_front`
    after(420, () => {
      moveToFront(existingId)
      log(`put ${key} -> update -> move_to_front`, 'put')
      after(560, () => { touchedId.value = null; busy = false })
    })
    return
  }

  // 2) at capacity -> evict the tail (LRU) and del map[node.key]
  if (atCap.value) {
    const lru = list.value[list.value.length - 1]
    evictId.value = lru.id
    caption.value = `put(${key},${value}) -> at capacity -> remove_last() -> ${lru.key}`
    after(620, () => {
      list.value = list.value.filter(n => n.id !== lru.id)
      delete map[lru.key]                          // node.key needed exactly here
      caption.value = `evict ${lru.key} -> del map[${lru.key}]`
      log(`put ${key} -> full -> evict ${lru.key} -> del map[${lru.key}]`, 'evict')
      evictId.value = null
      after(180, () => insertFront(key, value))
    })
    return
  }

  // 3) room available -> straight insert
  caption.value = `put(${key},${value}) -> add_first(node) + map[${key}]=node`
  insertFront(key, value)
}

function insertFront(key: string, value: string) {
  const node = fresh(key, value)
  list.value.unshift(node)
  map[key] = node.id
  enteringId.value = node.id
  caption.value = `add_first(${key}) -> MRU; map[${key}] -> node`
  log(`put ${key} -> add_first -> map[${key}]=node`, 'put')
  after(620, () => { enteringId.value = null; busy = false })
}

// ---- preset replay of the source sequence ----
interface PresetOp { kind: 'put' | 'get'; key: string; value?: string }
const PRESET: PresetOp[] = [
  { kind: 'put', key: 'a', value: '1' },
  { kind: 'put', key: 'b', value: '2' },
  { kind: 'put', key: 'c', value: '3' },
  { kind: 'get', key: 'a' },
  { kind: 'put', key: 'd', value: '4' },   // at capacity -> evicts b (LRU)
]
const stepIdx = ref(0)                       // next preset op to fire
const autoOn = ref(false)
let autoTimer: number | null = null

function runOp(op: PresetOp) {
  if (op.kind === 'get') get(op.key)
  else put(op.key, op.value ?? op.key)
}

function stepPreset() {
  if (busy) return
  const op = PRESET[stepIdx.value % PRESET.length]
  runOp(op)
  stepIdx.value = (stepIdx.value + 1) % PRESET.length
}

function tickAuto() {
  if (!autoOn.value) return
  if (!busy) stepPreset()
  autoTimer = window.setTimeout(tickAuto, 1300)
  timers.push(autoTimer)
}
function toggleAuto() {
  autoOn.value = !autoOn.value
  if (autoOn.value) tickAuto()
  else if (autoTimer !== null) { clearTimeout(autoTimer); autoTimer = null }
}

// ---- free-form entry ----
const formKey = ref('')
const formVal = ref('')
function doGet() { get(formKey.value); formKey.value = ''; formVal.value = '' }
function doPut() { put(formKey.value, formVal.value); formKey.value = ''; formVal.value = '' }

function reset() {
  clearTimers()
  busy = false
  autoOn.value = false
  autoTimer = null
  list.value = []
  for (const k of Object.keys(map)) delete map[k]
  logLines.value = []
  stepIdx.value = 0
  touchedId.value = null
  evictId.value = null
  enteringId.value = null
  missFlash.value = false
  nextId = 1
  caption.value = 'fresh LRUCache(capacity=3) — dict + DLL, both empty'
}

// dict chips, drawn left-to-right; arrows fan to the matching node column
const dictKeys = computed(() => Object.keys(map))
const peekNext = computed(() => PRESET[stepIdx.value % PRESET.length])
</script>

<template>
  <div class="lru">
    <!-- ============ header ============ -->
    <div class="lhead">
      <span class="ltag">LRUCache · capacity 3</span>
      <span class="size" :class="{ full: atCap }">size {{ sizeText }}</span>
      <span class="meter">
        <i class="mlabel warm">MRU</i>
        <span class="bar"><span class="grad" /></span>
        <i class="mlabel cold">LRU</i>
      </span>
    </div>

    <!-- ============ doubly linked list stage ============ -->
    <div class="stage">
      <div class="row">
        <!-- dummy HEAD sentinel (MRU side) -->
        <div class="sentinel">
          <span class="sname">HEAD</span>
          <span class="ssub">dummy · MRU</span>
        </div>

        <span class="dll-link" />

        <transition-group name="slide" tag="div" class="nodes">
          <div
            v-for="(n, i) in list"
            :key="n.id"
            class="node"
            :class="{
              touched: touchedId === n.id,
              evict: evictId === n.id,
              entering: enteringId === n.id,
            }"
            :style="{
              '--warm': String(1 - recency(i)),
              '--cold': String(recency(i)),
            }"
          >
            <span class="ncol">
              <span class="nkey">{{ n.key }}</span>
              <span class="neq">=</span>
              <span class="nval">{{ n.value }}</span>
            </span>
            <span class="nrole">{{ i === 0 ? 'MRU' : (i === list.length - 1 ? 'LRU' : '') }}</span>
            <span class=" port" :data-key="n.key" />
          </div>
        </transition-group>

        <span class="dll-link" />

        <!-- dummy TAIL sentinel (LRU side) -->
        <div class="sentinel">
          <span class="sname">TAIL</span>
          <span class="ssub">dummy · LRU</span>
        </div>
      </div>

      <!-- empty-state / miss overlay -->
      <transition name="fade">
        <span v-if="!list.length && !missFlash" class="empty">empty list — put a key to begin</span>
      </transition>
      <transition name="fade">
        <span v-if="missFlash" class="nullflash">return null</span>
      </transition>
    </div>

    <!-- ============ dict row ============ -->
    <div class="dict">
      <span class="dlabel">dict <i>key -&gt; *node</i></span>
      <transition-group name="pop" tag="div" class="dchips">
        <span
          v-for="k in dictKeys"
          :key="k"
          class="dchip"
          :class="{
            touched: list.find(n => n.id === touchedId)?.key === k,
            evict: list.find(n => n.id === evictId)?.key === k,
          }"
        >
          {{ k }}<span class="darr">-&gt;</span><i>node</i>
        </span>
      </transition-group>
      <span v-if="!dictKeys.length" class="dempty">map = {}</span>
    </div>

    <!-- ============ op log + caption ============ -->
    <div class="caption">
      <span class="ck">&gt;</span>
      <span class="ctext">{{ caption || 'fire a preset or put a key to drive the cache' }}</span>
    </div>

    <!-- ============ controls ============ -->
    <div class="ctrls">
      <div class="presetbox">
        <span class="cgroup">replay sequence</span>
        <div class="prow">
          <span
            v-for="(op, i) in PRESET"
            :key="i"
            class="pstep"
            :class="{ next: i === (stepIdx % PRESET.length) }"
          >{{ op.kind }} {{ op.key }}<b v-if="op.value">={{ op.value }}</b></span>
        </div>
        <div class="pbtns">
          <button class="b play" :disabled="busy" @click="stepPreset">
            step &rarr; <span class="peek">{{ peekNext.kind }} {{ peekNext.key }}</span>
          </button>
          <button class="b" :class="{ on: autoOn }" @click="toggleAuto">
            {{ autoOn ? 'pause' : 'auto-play' }}
          </button>
          <button class="b ghost" @click="reset">reset</button>
        </div>
      </div>

      <div class="freebox">
        <span class="cgroup">free-form</span>
        <div class="frow">
          <input v-model="formKey" class="inp" placeholder="key" maxlength="3" @keyup.enter="doPut" />
          <input v-model="formVal" class="inp" placeholder="value" maxlength="3" @keyup.enter="doPut" />
          <button class="b" :disabled="busy || !formKey.trim()" @click="doGet">get</button>
          <button class="b play" :disabled="busy || !formKey.trim()" @click="doPut">put</button>
        </div>
        <ul class="oplog">
          <li v-for="l in logLines" :key="l.id" :class="l.kind">{{ l.text }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lru {
  width: 100%;
  height: 360px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: .5rem;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- header ---------- */
.lhead { display: flex; align-items: center; gap: .7rem; }
.ltag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-cyan); }
.size { font-size: .58rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 999px; padding: .1rem .5rem; transition: all .25s; }
.size.full { color: var(--bp-warn); border-color: rgba(251,191,36,.5); background: rgba(251,191,36,.1); }
.meter { display: flex; align-items: center; gap: .35rem; margin-left: auto; }
.mlabel { font-size: .52rem; font-style: normal; letter-spacing: .06em; }
.mlabel.warm { color: var(--bp-bad); }
.mlabel.cold { color: var(--bp-blue); }
.bar { width: 84px; height: 6px; border-radius: 999px; overflow: hidden; border: 1px solid var(--bp-line); }
.grad { display: block; width: 100%; height: 100%; background: linear-gradient(90deg, var(--bp-bad), var(--bp-warn) 45%, var(--bp-blue)); opacity: .8; }

/* ---------- DLL stage ---------- */
.stage {
  position: relative;
  border: 1px solid var(--bp-line); border-radius: 12px;
  background: rgba(255,255,255,.015);
  padding: .7rem .8rem;
  min-height: 96px;
  display: flex; align-items: center;
}
.row { display: flex; align-items: stretch; gap: .35rem; width: 100%; }
.nodes { display: flex; align-items: stretch; gap: .5rem; flex: 1; min-width: 0; }

.sentinel {
  flex: none; width: 58px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .15rem;
  border: 1px dashed var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02);
  opacity: .65;
}
.sname { font-size: .62rem; color: var(--bp-dim); letter-spacing: .06em; }
.ssub { font-size: .44rem; color: var(--bp-dim); opacity: .8; }

.dll-link { flex: none; align-self: center; width: 14px; height: 1px; background: var(--bp-line); }

.node {
  position: relative;
  flex: 1 1 0; min-width: 60px; max-width: 120px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .2rem;
  padding: .5rem .35rem;
  border-radius: 10px;
  /* warm (MRU) -> cold (LRU) tint mixing red and blue accents */
  border: 1px solid rgba(56,189,248,.28);
  background:
    linear-gradient(180deg,
      rgba(251,113,133, calc(0.16 * var(--warm, 0))),
      rgba(56,189,248,  calc(0.16 * var(--cold, 0))) ),
    rgba(11,19,36,.9);
  box-shadow: 0 0 0 transparent;
  transition: border-color .3s, box-shadow .3s, transform .25s, background .3s;
}
.ncol { display: flex; align-items: baseline; gap: .15rem; }
.nkey { font-size: .92rem; color: #fff; }
.neq { font-size: .7rem; color: var(--bp-dim); }
.nval { font-size: .82rem; color: var(--bp-cyan); }
.nrole { font-size: .46rem; letter-spacing: .08em; color: var(--bp-dim); min-height: .55rem; }
.port { display: none; }

.node.touched {
  border-color: var(--bp-cyan);
  box-shadow: var(--bp-glow);
  transform: translateY(-3px);
}
.node.entering {
  border-color: var(--bp-good);
  box-shadow: 0 0 18px rgba(74,222,128,.5);
  animation: pop-in .5s ease;
}
.node.evict {
  border-color: var(--bp-bad);
  box-shadow: 0 0 20px rgba(251,113,133,.6);
  animation: evict-flash .6s ease;
}
@keyframes pop-in { 0% { transform: scale(.7); opacity: 0; } 60% { transform: scale(1.08); } 100% { transform: scale(1); } }
@keyframes evict-flash { 0%,100% { transform: translateX(0); } 25% { transform: translateX(4px); } 75% { transform: translateX(-4px); } }

.empty, .nullflash {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
  font-size: .66rem; letter-spacing: .04em;
}
.empty { color: var(--bp-dim); }
.nullflash {
  color: var(--bp-bad); font-size: .9rem;
  border: 1px solid rgba(251,113,133,.5); background: rgba(251,113,133,.12);
  border-radius: 8px; padding: .25rem .8rem; box-shadow: 0 0 18px rgba(251,113,133,.4);
}

/* list slide transitions: move_to_front reorders cleanly */
.slide-move { transition: transform .42s cubic-bezier(.4,0,.2,1); }
.slide-enter-active { transition: all .4s ease; }
.slide-enter-from { opacity: 0; transform: translateY(-14px) scale(.85); }
.slide-leave-active { transition: all .35s ease; position: absolute; }
.slide-leave-to { opacity: 0; transform: translateY(16px) scale(.7); }

/* ---------- dict row ---------- */
.dict {
  display: flex; align-items: center; gap: .55rem; flex-wrap: wrap;
  border: 1px solid var(--bp-line); border-radius: 10px;
  background: linear-gradient(180deg, rgba(167,139,250,.06), rgba(167,139,250,.01));
  padding: .4rem .6rem; min-height: 1.9rem;
}
.dlabel { font-size: .56rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-violet); }
.dlabel i { font-style: italic; text-transform: none; letter-spacing: 0; color: var(--bp-dim); margin-left: .25rem; }
.dchips { display: flex; gap: .4rem; flex-wrap: wrap; }
.dchip {
  display: inline-flex; align-items: center; gap: .15rem;
  font-size: .64rem; color: var(--bp-ink);
  border: 1px solid rgba(167,139,250,.35); border-radius: 7px;
  background: rgba(167,139,250,.08); padding: .14rem .45rem;
  transition: all .25s;
}
.dchip .darr { color: var(--bp-dim); margin: 0 .1rem; }
.dchip i { font-style: italic; color: var(--bp-violet); }
.dchip.touched { border-color: var(--bp-cyan); color: #fff; box-shadow: var(--bp-glow); }
.dchip.evict { border-color: var(--bp-bad); color: var(--bp-bad); background: rgba(251,113,133,.12); }
.dempty { font-size: .6rem; color: var(--bp-dim); opacity: .7; }

/* ---------- caption ---------- */
.caption {
  display: flex; gap: .4rem; align-items: baseline;
  font-size: .64rem;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6);
  padding: .35rem .55rem; min-height: 1.7rem;
}
.ck { color: var(--bp-cyan); }
.ctext { color: var(--bp-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ---------- controls ---------- */
.ctrls { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; flex: 1; min-height: 0; }
.presetbox, .freebox { display: flex; flex-direction: column; gap: .35rem; min-width: 0; }
.cgroup { font-size: .54rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }

.prow { display: flex; gap: .3rem; flex-wrap: wrap; }
.pstep {
  font-size: .56rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 6px;
  padding: .12rem .4rem; background: rgba(255,255,255,.02);
  transition: all .2s;
}
.pstep b { color: var(--bp-cyan); font-weight: 400; }
.pstep.next { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }

.pbtns, .frow { display: flex; gap: .4rem; flex-wrap: wrap; align-items: center; }
.b {
  font-family: inherit; font-size: .66rem; cursor: pointer;
  border: 1px solid var(--bp-line); color: var(--bp-ink);
  border-radius: 8px; padding: .3rem .55rem;
  background: rgba(255,255,255,.03); transition: all .2s;
}
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.play { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.on { border-color: var(--bp-violet); color: var(--bp-violet); background: rgba(167,139,250,.12); box-shadow: 0 0 16px rgba(167,139,250,.4); }
.b.ghost { color: var(--bp-dim); box-shadow: none; }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.peek { font-size: .56rem; color: var(--bp-cyan); opacity: .9; }

.inp {
  font-family: inherit; font-size: .68rem; color: #fff;
  border: 1px solid var(--bp-line); border-radius: 7px;
  background: var(--bp-bg-2); padding: .26rem .4rem;
  width: 52px; outline: none; transition: border-color .2s;
}
.inp::placeholder { color: var(--bp-dim); opacity: .7; }
.inp:focus { border-color: var(--bp-cyan); }

.oplog {
  list-style: none; margin: .1rem 0 0; padding: .3rem .45rem;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.5);
  flex: 1; min-height: 0; overflow-y: auto;
  font-size: .54rem; line-height: 1.55;
}
.oplog li { color: var(--bp-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.oplog li::before { content: '> '; color: var(--bp-line); }
.oplog li.hit { color: var(--bp-good); }
.oplog li.miss { color: var(--bp-bad); }
.oplog li.put { color: var(--bp-cyan); }
.oplog li.evict { color: var(--bp-warn); }
.oplog::-webkit-scrollbar { width: 5px; }
.oplog::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }

/* ---------- transitions ---------- */
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.pop-enter-active { transition: all .3s ease; }
.pop-enter-from { opacity: 0; transform: scale(.6); }
.pop-leave-active { transition: all .25s ease; position: absolute; }
.pop-leave-to { opacity: 0; transform: scale(.6); }
</style>
