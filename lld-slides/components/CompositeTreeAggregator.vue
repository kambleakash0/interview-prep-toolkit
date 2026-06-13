<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

/* ---- fixed tree model ----------------------------------------------------
   cart[ pen(2), kit[ tape(3), glue(5) ] ]   +optional box(4) in kit         */
type N = {
  id: string
  name: string
  kind: 'box' | 'item'
  price?: number
  children?: string[]
  parent?: string
}
const tree = reactive<Record<string, N>>({
  cart: { id: 'cart', name: 'cart', kind: 'box', children: ['pen', 'kit'] },
  pen:  { id: 'pen',  name: 'pen',  kind: 'item', price: 2, parent: 'cart' },
  kit:  { id: 'kit',  name: 'kit',  kind: 'box', children: ['tape', 'glue'], parent: 'cart' },
  tape: { id: 'tape', name: 'tape', kind: 'item', price: 3, parent: 'kit' },
  glue: { id: 'glue', name: 'glue', kind: 'item', price: 5, parent: 'kit' },
})
const hasExtra = ref(false)   // box(4) toggled into kit

/* per-node live render state */
const badge = reactive<Record<string, number | null>>({})   // shown value
const nstate = reactive<Record<string, string>>({})         // idle|active|leaf|resolved|agg|final
const edgeDown = reactive<Record<string, boolean>>({})       // parent->child pulse lit
const chipUp = reactive<Record<string, boolean>>({})         // child->parent chip flying
function clearAll() {
  for (const id of Object.keys(tree)) {
    badge[id] = null; nstate[id] = 'idle'; edgeDown[id] = false; chipUp[id] = false
  }
}
clearAll()

/* ---- frame engine --------------------------------------------------------
   Build a flat list of frames for a query; Step/Play both consume it.        */
type Frame =
  | { t: 'down'; node: string }                 // edge parent->node lights, node becomes active
  | { t: 'leaf'; node: string }                 // leaf flashes, badge = own price
  | { t: 'chip'; node: string; sum: number }    // child chip arrives at parent, parent badge=sum
  | { t: 'done'; node: string }                 // root locks final total

const frames = ref<Frame[]>([])
const fi = ref(0)                                // next frame index
const rootId = ref<string | null>(null)
const stack = ref<string[]>([])                  // call-stack echo lines
const busy = ref(false)                          // reactive: a Play sweep is running
let timer: number | null = null
let gen = 0                                       // query generation; stale timers no-op

function kids(id: string): string[] {
  return (tree[id].children || []).filter(c => tree[c])
}

/* depth-first: emit frames mirroring cost() recursion */
function buildFrames(id: string, out: Frame[]): number {
  const n = tree[id]
  out.push({ t: 'down', node: id })
  if (n.kind === 'item') {
    out.push({ t: 'leaf', node: id })
    return n.price!
  }
  let sum = 0
  for (const c of kids(id)) {
    const cv = buildFrames(c, out)
    sum += cv
    out.push({ t: 'chip', node: c, sum })       // chip rides up to THIS box, badge=running sum
  }
  return sum
}

function startQuery(id: string) {
  if (busy.value) return
  stopPlay()
  clearAll()
  gen++
  rootId.value = id
  stack.value = []
  const out: Frame[] = []
  buildFrames(id, out)
  out.push({ t: 'done', node: id })
  frames.value = out
  fi.value = 0
  nstate[id] = 'active'                          // clicked node lights immediately
}

/* apply exactly one frame */
function applyFrame(f: Frame) {
  const myGen = gen
  if (f.t === 'down') {
    const p = tree[f.node].parent
    if (p) edgeDown[f.node] = true               // light incoming edge
    nstate[f.node] = 'active'
    stack.value.push(`cost(${tree[f.node].name})`)
  } else if (f.t === 'leaf') {
    nstate[f.node] = 'leaf'
    badge[f.node] = tree[f.node].price!
    stack.value.pop()
    setTimeout(() => {
      if (myGen === gen && nstate[f.node] === 'leaf') nstate[f.node] = 'resolved'
    }, 240)
  } else if (f.t === 'chip') {
    chipUp[f.node] = true
    const p = tree[f.node].parent!
    nstate[p] = 'agg'
    badge[p] = f.sum
    setTimeout(() => { if (myGen === gen) chipUp[f.node] = false }, 300)
    // when a box's last child has returned, fold its own stack line
    if (kids(p)[kids(p).length - 1] === f.node) {
      if (stack.value[stack.value.length - 1] === `cost(${tree[p].name})`) stack.value.pop()
    }
  } else if (f.t === 'done') {
    nstate[f.node] = 'final'
    stack.value = []
  }
}

function step() {
  if (busy.value) return
  // nothing queued: a bare Step starts a default query on cart
  if (!rootId.value) startQuery('cart')
  if (fi.value >= frames.value.length) return
  applyFrame(frames.value[fi.value])
  fi.value++
}

function play() {
  if (busy.value) return
  if (!rootId.value || fi.value >= frames.value.length) startQuery('cart')
  busy.value = true
  const myGen = gen
  const tick = () => {
    if (myGen !== gen || fi.value >= frames.value.length) {
      busy.value = false; timer = null; return
    }
    applyFrame(frames.value[fi.value]); fi.value++
    timer = window.setTimeout(tick, 520)
  }
  timer = window.setTimeout(tick, 360)
}

function stopPlay() {
  if (timer != null) { clearTimeout(timer); timer = null }
  busy.value = false
}

function reset() {
  stopPlay()
  gen++
  clearAll()
  frames.value = []; fi.value = 0; rootId.value = null; stack.value = []
}

function toggleExtra() {
  stopPlay()
  gen++
  hasExtra.value = !hasExtra.value
  if (hasExtra.value) {
    tree['box'] = { id: 'box', name: 'box', kind: 'item', price: 4, parent: 'kit' }
    tree['kit'].children = ['tape', 'glue', 'box']
  } else {
    delete tree['box']
    tree['kit'].children = ['tape', 'glue']
  }
  clearAll()
  frames.value = []; fi.value = 0; rootId.value = null; stack.value = []
}

const caption = computed(() => {
  if (rootId.value && nstate[rootId.value] === 'final')
    return `${tree[rootId.value].name}.cost() = ${badge[rootId.value]}`
  if (hasExtra.value && !rootId.value)
    return 'client code unchanged — re-run query'
  if (rootId.value) return `querying ${tree[rootId.value].name} …`
  return 'click any node to query its subtotal'
})

const total = computed(() => (hasExtra.value ? 14 : 10))
</script>

<template>
  <div class="ct">
    <!-- ============ STAGE: the tree ============ -->
    <div class="stage">
      <!-- root: cart -->
      <div class="box root" :class="['s-' + (nstate.cart || 'idle')]" @click="startQuery('cart')">
        <div class="bhead">
          <span class="glyph">◆</span><span class="nm">cart/</span>
          <span class="bdg" :class="{ on: badge.cart != null }">{{ badge.cart != null ? badge.cart : '·' }}</span>
        </div>

        <div class="row">
          <!-- leaf: pen -->
          <div class="edge" :class="{ down: edgeDown.pen, up: chipUp.pen }">
            <span v-if="chipUp.pen" class="chip">{{ badge.pen }}</span>
          </div>
          <div class="item" :class="['s-' + (nstate.pen || 'idle')]" @click.stop="startQuery('pen')">
            <span class="glyph sm">●</span><span class="nm">pen</span>
            <span class="price">$2</span>
            <span class="bdg sm" :class="{ on: badge.pen != null }">{{ badge.pen != null ? badge.pen : '·' }}</span>
          </div>

          <!-- composite: kit -->
          <div class="edge" :class="{ down: edgeDown.kit, up: chipUp.kit }">
            <span v-if="chipUp.kit" class="chip">{{ badge.kit }}</span>
          </div>
          <div class="box" :class="['s-' + (nstate.kit || 'idle')]" @click.stop="startQuery('kit')">
            <div class="bhead">
              <span class="glyph">◆</span><span class="nm">kit/</span>
              <span class="bdg" :class="{ on: badge.kit != null }">{{ badge.kit != null ? badge.kit : '·' }}</span>
            </div>
            <div class="row inner">
              <div class="edge" :class="{ down: edgeDown.tape, up: chipUp.tape }">
                <span v-if="chipUp.tape" class="chip">{{ badge.tape }}</span>
              </div>
              <div class="item" :class="['s-' + (nstate.tape || 'idle')]" @click.stop="startQuery('tape')">
                <span class="glyph sm">●</span><span class="nm">tape</span>
                <span class="price">$3</span>
                <span class="bdg sm" :class="{ on: badge.tape != null }">{{ badge.tape != null ? badge.tape : '·' }}</span>
              </div>

              <div class="edge" :class="{ down: edgeDown.glue, up: chipUp.glue }">
                <span v-if="chipUp.glue" class="chip">{{ badge.glue }}</span>
              </div>
              <div class="item" :class="['s-' + (nstate.glue || 'idle')]" @click.stop="startQuery('glue')">
                <span class="glyph sm">●</span><span class="nm">glue</span>
                <span class="price">$5</span>
                <span class="bdg sm" :class="{ on: badge.glue != null }">{{ badge.glue != null ? badge.glue : '·' }}</span>
              </div>

              <!-- optional extra leaf -->
              <transition name="slide">
                <div v-if="hasExtra" class="edge" :class="{ down: edgeDown.box, up: chipUp.box }">
                  <span v-if="chipUp.box" class="chip">{{ badge.box }}</span>
                </div>
              </transition>
              <transition name="slide">
                <div v-if="hasExtra" class="item new" :class="['s-' + (nstate.box || 'idle')]" @click.stop="startQuery('box')">
                  <span class="glyph sm">●</span><span class="nm">box</span>
                  <span class="price">$4</span>
                  <span class="bdg sm" :class="{ on: badge.box != null }">{{ badge.box != null ? badge.box : '·' }}</span>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="btns">
        <button class="b" :disabled="busy" @click="step">▸ step</button>
        <button class="b prime" :disabled="busy" @click="play">▶ play</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>

      <label class="tog" :class="{ on: hasExtra, off: busy }" @click="toggleExtra">
        <span class="knob"></span> add item → kit
      </label>

      <div class="cap" :class="{ done: rootId && nstate[rootId] === 'final' }">{{ caption }}</div>

      <div class="stack">
        <div class="slabel">call stack</div>
        <div class="sframe" v-for="(s, i) in stack" :key="i" :style="{ paddingLeft: (i * 0.7 + 0.2) + 'rem' }">
          → {{ s }}
        </div>
        <div v-if="!stack.length" class="sempty">cost({{ rootId || '…' }}) idle</div>
      </div>

      <ul class="kpts bp-dim text-sm">
        <li>One <b>cost()</b> call recurses leaf or whole subtree — no type checks</li>
        <li>Leaves return their own price; boxes sum children's chips upward</li>
        <li>Add a leaf — same interface re-flows total to {{ total }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ct { display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.4rem; font-family: "Fira Code", monospace; height: 340px; width: 100%; box-sizing: border-box; overflow: hidden; }

/* ---- stage ---- */
.stage { display: flex; align-items: center; justify-content: center; padding: .2rem; min-width: 0; min-height: 0; overflow: hidden; }

/* boxes (composite) */
.box { border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(167,139,250,.05); padding: .55rem .7rem; transition: border-color .3s, box-shadow .3s, transform .3s; cursor: pointer; }
.box.root { background: rgba(167,139,250,.06); }
.bhead { display: flex; align-items: center; gap: .4rem; }
.glyph { color: var(--bp-violet); font-size: .7rem; }
.glyph.sm { font-size: .55rem; color: var(--bp-cyan); }
.nm { font-size: .76rem; color: var(--bp-ink); }
.row { display: flex; align-items: stretch; gap: 0; margin-top: .5rem; }
.row.inner { margin-top: .45rem; gap: 0; }

/* items (leaf) */
.item { display: flex; flex-direction: column; align-items: center; gap: .15rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02); padding: .45rem .55rem; transition: border-color .28s, box-shadow .28s, transform .28s; cursor: pointer; position: relative; }
.item .price { font-size: .62rem; color: var(--bp-dim); }

/* badge (value) */
.bdg { margin-left: auto; min-width: 1.5rem; text-align: center; font-size: .72rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 6px; padding: .05rem .35rem; transition: all .3s; }
.bdg.sm { margin-left: 0; min-width: 1.2rem; font-size: .66rem; padding: .02rem .25rem; }
.bdg.on { color: var(--bp-cyan); border-color: var(--bp-cyan); background: rgba(34,211,238,.1); }

/* ---- edges (connectors) ---- */
.edge { position: relative; width: 26px; align-self: stretch; }
.edge::before { content: ''; position: absolute; left: 50%; top: 12px; bottom: 12px; width: 2px; transform: translateX(-50%); background: var(--bp-line); transition: all .3s; }
.row > .edge::before, .row.inner > .edge::before { top: 0; bottom: 0; }
.edge.down::before { background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.edge.up::before { background: var(--bp-violet); box-shadow: 0 0 10px rgba(167,139,250,.6); }
.chip { position: absolute; left: 50%; top: 50%; transform: translateX(-50%); font-size: .6rem; color: var(--bp-bg); background: var(--bp-violet); border-radius: 999px; padding: .02rem .3rem; animation: ride .3s ease forwards; z-index: 3; }
@keyframes ride { from { top: 80%; opacity: 0; } 35% { opacity: 1; } to { top: 8%; opacity: 0; } }

/* ---- per-node states ---- */
.s-active { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.s-agg { border-color: var(--bp-violet); box-shadow: 0 0 14px rgba(167,139,250,.4); }
.s-leaf { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); animation: flash .24s ease; }
.s-resolved { border-color: rgba(34,211,238,.45); }
.s-final { border-color: var(--bp-cyan); box-shadow: 0 0 22px rgba(34,211,238,.55); animation: lock .4s ease; }
.s-final > .bhead .bdg, .item.s-final .bdg { font-weight: 700; color: #fff; border-color: var(--bp-cyan); background: rgba(34,211,238,.2); }
@keyframes flash { 0% { transform: scale(1); } 50% { transform: scale(1.12); } 100% { transform: scale(1); } }
@keyframes lock { 0% { transform: scale(1); } 40% { transform: scale(1.05); } 100% { transform: scale(1); } }

.item.new { border-color: var(--bp-good); }

/* slide-in for added leaf */
.slide-enter-active { transition: all .4s ease; }
.slide-enter-from { opacity: 0; transform: translateX(-14px); }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .55rem; align-items: flex-start; min-width: 0; min-height: 0; overflow: hidden; }
.btns { display: flex; gap: .45rem; }
.b { font-family: inherit; font-size: .74rem; padding: .4rem .7rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 7px; background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.prime { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .4; cursor: not-allowed; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; color: var(--bp-dim); cursor: pointer; user-select: none; transition: color .3s; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(74,222,128,.4); }
.tog.on .knob::after { left: 16px; background: var(--bp-good); }
.tog.on { color: var(--bp-good); }
.tog.off { opacity: .4; cursor: not-allowed; }

.cap { font-size: .7rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 7px; padding: .35rem .6rem; width: 100%; box-sizing: border-box; transition: all .3s; }
.cap.done { color: var(--bp-cyan); border-color: var(--bp-cyan); background: rgba(34,211,238,.08); }

.stack { width: 100%; box-sizing: border-box; border: 1px dashed var(--bp-line); border-radius: 8px; padding: .4rem .55rem; min-height: 56px; overflow: hidden; }
.slabel { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); margin-bottom: .25rem; }
.sframe { font-size: .66rem; color: var(--bp-cyan); line-height: 1.45; }
.sempty { font-size: .64rem; color: var(--bp-dim); opacity: .6; }

.kpts { margin: .1rem 0 0; padding-left: 1.05rem; font-size: .66rem; line-height: 1.4; color: var(--bp-dim); overflow: hidden; }
.kpts b { color: var(--bp-cyan); }
</style>
