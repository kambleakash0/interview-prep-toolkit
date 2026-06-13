<script setup lang="ts">
import { ref, computed } from 'vue'

/* ── fixed expression tree: Add(Num 3, Add(Num 4, Num 5)) ───────────── */
type NodeT = {
  id: string
  kind: 'Num' | 'Add'
  value?: number
  left?: string
  right?: string
}
const NODES: Record<string, NodeT> = {
  n1: { id: 'n1', kind: 'Add', left: 'n2', right: 'n3' },
  n2: { id: 'n2', kind: 'Num', value: 3 },
  n3: { id: 'n3', kind: 'Add', left: 'n4', right: 'n5' },
  n4: { id: 'n4', kind: 'Num', value: 4 },
  n5: { id: 'n5', kind: 'Num', value: 5 },
}

type Visitor = 'Eval' | 'Print'
const visitor = ref<Visitor>('Eval')
const selected = ref<string>('n1')

/* ── the two operations (what each visit method actually returns) ────── */
function evalNode(id: string): number {
  const n = NODES[id]
  return n.kind === 'Num' ? n.value! : evalNode(n.left!) + evalNode(n.right!)
}
function printNode(id: string): string {
  const n = NODES[id]
  return n.kind === 'Num' ? String(n.value!) : `(${printNode(n.left!)} + ${printNode(n.right!)})`
}
function result(id: string): string {
  return visitor.value === 'Eval' ? String(evalNode(id)) : printNode(id)
}

/* ── frame = one explicit state in the double-dispatch walk ──────────── */
type Phase = 'ELEMENT_SELECTED' | 'VISIT_RESOLVED' | 'RESULT_RETURNED'
type Edge = 'left' | 'right' | 'root'
type Frame = {
  node: string
  phase: Phase
  row: 'num' | 'add'          // which visitor row resolves
  depth: number
  ret?: string                // value returned (RESULT_RETURNED only)
  edge?: Edge                 // which incoming edge to label on return
}

function buildFrames(id: string, depth: number, edge: Edge, out: Frame[]) {
  const n = NODES[id]
  const row: 'num' | 'add' = n.kind === 'Num' ? 'num' : 'add'
  out.push({ node: id, phase: 'ELEMENT_SELECTED', row, depth, edge })
  out.push({ node: id, phase: 'VISIT_RESOLVED', row, depth, edge })
  if (n.kind === 'Add') {
    buildFrames(n.left!, depth + 1, 'left', out)
    buildFrames(n.right!, depth + 1, 'right', out)
  }
  out.push({ node: id, phase: 'RESULT_RETURNED', row, depth, edge, ret: result(id) })
}

const frames = ref<Frame[]>([])
const fi = ref<number>(-1)   // -1 == IDLE

function rebuild() {
  const out: Frame[] = []
  buildFrames(selected.value, 0, 'root', out)
  frames.value = out
}
rebuild()

const cur = computed<Frame | null>(() => (fi.value >= 0 ? frames.value[fi.value] : null))
const idle = computed(() => fi.value < 0)
const done = computed(() => fi.value >= frames.value.length - 1 && fi.value >= 0)

/* ── call stack: frames pushed on ELEMENT_SELECTED, popped on RETURN ─── */
const stack = computed(() => {
  const s: { node: string; row: string }[] = []
  for (let i = 0; i <= fi.value; i++) {
    const f = frames.value[i]
    if (f.phase === 'ELEMENT_SELECTED') s.push({ node: f.node, row: f.row })
    else if (f.phase === 'RESULT_RETURNED') s.pop()
  }
  return s
})

/* ── returned-value labels collected on each edge so far ─────────────── */
const edgeRet = computed(() => {
  const m: Record<string, string> = {}
  for (let i = 0; i <= fi.value; i++) {
    const f = frames.value[i]
    if (f.phase === 'RESULT_RETURNED' && f.ret !== undefined) m[f.node] = f.ret
  }
  return m
})

/* the accept(v) label currently in flight */
const flying = computed(() =>
  cur.value && cur.value.phase === 'ELEMENT_SELECTED' ? cur.value.node : '')
/* which row of the active card is lit right now */
const litRow = computed<'num' | 'add' | ''>(() =>
  cur.value && (cur.value.phase === 'VISIT_RESOLVED' || cur.value.phase === 'ELEMENT_SELECTED')
    ? cur.value.row : '')

/* ── per-node css classes for the tree buttons ──────────────────────── */
function nodeCls(id: string) {
  return {
    sel: selected.value === id,
    activeframe: cur.value !== null && cur.value.node === id,
    pulse: cur.value !== null && cur.value.node === id && cur.value.phase === 'ELEMENT_SELECTED',
    returned: edgeRet.value[id] !== undefined,
  }
}

/* ── controls (guarded so repeat clicks never double-fire) ──────────── */
let timer: ReturnType<typeof setInterval> | null = null
const playing = ref(false)

function stopPlay() {
  if (timer) { clearInterval(timer); timer = null }
  playing.value = false
}
function step() {
  if (fi.value < frames.value.length - 1) fi.value++
  else stopPlay()
}
function play() {
  if (playing.value) { stopPlay(); return }
  if (done.value) reset()
  playing.value = true
  timer = setInterval(() => {
    if (fi.value >= frames.value.length - 1) { stopPlay(); return }
    fi.value++
  }, 720)
}
function reset() { stopPlay(); fi.value = -1 }

function pick(id: string) {
  reset()
  selected.value = id
  rebuild()
}
function setVisitor(v: Visitor) {
  if (v === visitor.value) return
  const keepAt = fi.value
  visitor.value = v
  rebuild()                          // same node + same steps, other operation
  fi.value = Math.min(keepAt, frames.value.length - 1)
}

/* ── render helpers ─────────────────────────────────────────────────── */
const nodeLabel = (id: string) => {
  const n = NODES[id]
  return n.kind === 'Num' ? `Num ${n.value}` : 'Add'
}
const phaseLabel = computed(() => {
  if (idle.value) return 'IDLE'
  return cur.value!.phase
})
const ROWBODY: Record<Visitor, { num: string; add: string }> = {
  Eval: { num: 'return n.value', add: 'return L.accept(self) + R.accept(self)' },
  Print: { num: 'return str(n.value)', add: 'return f"({L} + {R})"' },
}
const finalShown = computed(() => done.value ? result(selected.value) : '')
</script>

<template>
  <div class="vz">
    <!-- ── STAGE ──────────────────────────────────────────────────── -->
    <div class="stage">
      <!-- expression tree -->
      <div class="tree">
        <div class="tlabel">expression tree</div>

        <!-- root -->
        <div class="row r0">
          <button class="node add" :class="nodeCls('n1')" @click="pick('n1')">
            <span class="nk">Add</span>
            <span v-if="edgeRet['n1']" class="ret">→ {{ edgeRet['n1'] }}</span>
          </button>
        </div>

        <!-- level 1 -->
        <div class="row r1">
          <button class="node num" :class="nodeCls('n2')" @click="pick('n2')">
            <span class="nk">Num 3</span>
            <span v-if="edgeRet['n2']" class="ret">→ {{ edgeRet['n2'] }}</span>
          </button>
          <button class="node add" :class="nodeCls('n3')" @click="pick('n3')">
            <span class="nk">Add</span>
            <span v-if="edgeRet['n3']" class="ret">→ {{ edgeRet['n3'] }}</span>
          </button>
        </div>

        <!-- level 2 -->
        <div class="row r2">
          <button class="node num" :class="nodeCls('n4')" @click="pick('n4')">
            <span class="nk">Num 4</span>
            <span v-if="edgeRet['n4']" class="ret">→ {{ edgeRet['n4'] }}</span>
          </button>
          <button class="node num" :class="nodeCls('n5')" @click="pick('n5')">
            <span class="nk">Num 5</span>
            <span v-if="edgeRet['n5']" class="ret">→ {{ edgeRet['n5'] }}</span>
          </button>
        </div>

        <!-- in-flight accept(v) label -->
        <transition name="slide">
          <div v-if="flying" class="accept">{{ nodeLabel(flying) }}.accept({{ visitor.toLowerCase() }})</div>
        </transition>
      </div>

      <!-- call stack -->
      <div class="callstack">
        <div class="tlabel">call stack</div>
        <transition-group name="frm" tag="div" class="frames">
          <div v-for="(f, i) in stack" :key="f.node + '-' + i" class="frame" :class="{ top: i === stack.length - 1 }">
            <span class="fn">{{ nodeLabel(f.node) }}</span>
            <span class="fr">.accept</span>
          </div>
        </transition-group>
        <div v-if="!stack.length" class="empty">—</div>
      </div>

      <!-- visitor cards -->
      <div class="visitors">
        <div class="tlabel">visitor</div>
        <div v-for="v in (['Eval','Print'] as const)" :key="v"
             class="vcard" :class="{ active: visitor === v, dim: visitor !== v }">
          <div class="vhd">
            <span class="vdot" /> {{ v }}(Visitor)
          </div>
          <div class="vrow" :class="{ lit: visitor === v && litRow === 'num' }">
            <code>num(n)</code><span class="body">{{ ROWBODY[v].num }}</span>
          </div>
          <div class="vrow" :class="{ lit: visitor === v && litRow === 'add' }">
            <code>add(n)</code><span class="body">{{ ROWBODY[v].add }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── CONTROLS ───────────────────────────────────────────────── -->
    <div class="panel">
      <div class="seg">
        <button :class="{ on: visitor === 'Eval' }" @click="setVisitor('Eval')">EVAL</button>
        <button :class="{ on: visitor === 'Print' }" @click="setVisitor('Print')">PRINT</button>
      </div>

      <div class="btns">
        <button class="b" @click="step" :disabled="done">▸ step</button>
        <button class="b" :class="{ live: playing }" @click="play">{{ playing ? '■ pause' : '▶ play' }}</button>
        <button class="b ghost" @click="reset">⟳ reset</button>
      </div>

      <div class="status">
        <span class="phase" :class="phaseLabel.toLowerCase()">{{ phaseLabel }}</span>
        <span class="sel">selected: <b>{{ nodeLabel(selected) }}</b></span>
      </div>

      <div class="resbar" :class="{ on: done }">
        <span class="rl">root →</span>
        <code class="rv">{{ done ? finalShown : '…' }}</code>
      </div>

      <ul class="kpts bp-dim text-sm">
        <li>accept() lets the <b>node</b> pick the visit method — that is double dispatch</li>
        <li>The method run depends on <b>both</b> the node type and the active visitor</li>
        <li>Flip EVAL / PRINT: same node, same walk, a different method fires</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.vz {
  display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.4rem;
  font-family: "Fira Code", monospace;
  width: 100%; height: 340px; box-sizing: border-box; overflow: hidden;
}

/* stage */
.stage { display: grid; grid-template-columns: 1.3fr 0.7fr 1.25fr; gap: .8rem; align-items: start; position: relative; min-height: 0; overflow: hidden; }
.tlabel { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); margin-bottom: .5rem; }

/* tree */
.tree { position: relative; display: flex; flex-direction: column; gap: .85rem; }
.row { display: flex; gap: .8rem; }
.r0 { justify-content: center; }
.r1 { justify-content: space-around; }
.r2 { justify-content: space-around; padding-left: 48%; }

.node {
  position: relative; font-family: inherit; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: .1rem;
  min-width: 56px; padding: .32rem .5rem;
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.03); color: var(--bp-ink);
  transition: all .3s;
}
.node .nk { font-size: .72rem; }
.node.num { color: var(--bp-blue); }
.node.add { color: var(--bp-violet); }
.node:hover { border-color: var(--bp-cyan); }
.node.sel { border-color: var(--bp-cyan); box-shadow: 0 0 0 1px rgba(34,211,238,.35); }
.node.pulse { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); animation: ring .8s ease; }
.node.activeframe { border-color: var(--bp-cyan); background: rgba(34,211,238,.1); }
.node.returned { border-color: var(--bp-good); }
@keyframes ring { 0% { box-shadow: 0 0 0 0 rgba(34,211,238,.5); } 100% { box-shadow: 0 0 0 8px rgba(34,211,238,0); } }
.ret { font-size: .56rem; color: var(--bp-good); white-space: nowrap; }

/* accept(v) flying label */
.accept {
  position: absolute; top: 4px; right: -6px;
  font-size: .56rem; color: var(--bp-cyan);
  border: 1px solid var(--bp-cyan); border-radius: 999px;
  padding: .08rem .45rem; background: var(--bp-bg);
  box-shadow: var(--bp-glow);
}
.slide-enter-active { transition: all .4s ease; }
.slide-enter-from { opacity: 0; transform: translateX(-14px); }

/* call stack */
.callstack { border-left: 1px solid var(--bp-line); padding-left: .7rem; min-height: 150px; }
.frames { display: flex; flex-direction: column-reverse; gap: .3rem; }
.frame {
  display: flex; align-items: baseline; gap: .15rem;
  font-size: .62rem; padding: .22rem .4rem;
  border: 1px solid var(--bp-line); border-radius: 6px;
  background: rgba(255,255,255,.02); color: var(--bp-dim);
  transition: all .3s;
}
.frame.top { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.frame .fn { color: inherit; }
.frame .fr { color: var(--bp-dim); font-size: .56rem; }
.frm-enter-active, .frm-leave-active { transition: all .3s ease; }
.frm-enter-from { opacity: 0; transform: translateX(-10px); }
.frm-leave-to { opacity: 0; transform: translateX(10px); }
.callstack .empty { color: var(--bp-dim); font-size: .7rem; opacity: .5; }

/* visitor cards */
.visitors { display: flex; flex-direction: column; gap: .55rem; }
.vcard {
  border: 1px solid var(--bp-line); border-radius: 10px;
  padding: .5rem .55rem; background: rgba(255,255,255,.02);
  transition: all .35s;
}
.vcard.active { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); background: rgba(34,211,238,.05); }
.vcard.dim { opacity: .4; }
.vhd { display: flex; align-items: center; gap: .35rem; font-size: .68rem; color: #fff; margin-bottom: .35rem; }
.vdot { width: 8px; height: 8px; border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.vcard.dim .vdot { background: var(--bp-line); box-shadow: none; }
.vrow {
  display: flex; flex-direction: column; gap: .05rem;
  padding: .25rem .4rem; border-radius: 6px;
  border: 1px solid transparent; margin-top: .15rem;
  transition: all .25s;
}
.vrow code { font-size: .64rem; color: var(--bp-cyan); }
.vrow .body { font-size: .54rem; color: var(--bp-dim); }
.vrow.lit { border-color: var(--bp-cyan); background: rgba(34,211,238,.12); animation: flash .5s ease; }
.vrow.lit .body { color: var(--bp-ink); }
@keyframes flash { 0% { background: rgba(34,211,238,.4); } 100% { background: rgba(34,211,238,.12); } }

/* panel */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: flex-start; min-height: 0; overflow: hidden; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg button { font-family: inherit; font-size: .72rem; padding: .38rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; border: none; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.b { font-family: inherit; font-size: .74rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b.live { background: rgba(251,191,36,.16); border-color: var(--bp-warn); color: var(--bp-warn); box-shadow: 0 0 18px rgba(251,191,36,.3); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.b:disabled { opacity: .35; cursor: not-allowed; box-shadow: none; }

.status { display: flex; align-items: center; gap: .6rem; font-size: .68rem; }
.phase {
  font-size: .58rem; letter-spacing: .06em; padding: .16rem .5rem;
  border-radius: 999px; border: 1px solid var(--bp-line); color: var(--bp-dim);
}
.phase.element_selected { color: var(--bp-cyan); border-color: var(--bp-cyan); }
.phase.visit_resolved { color: var(--bp-violet); border-color: rgba(167,139,250,.5); }
.phase.result_returned { color: var(--bp-good); border-color: rgba(74,222,128,.5); }
.sel { color: var(--bp-dim); } .sel b { color: var(--bp-ink); }

.resbar {
  display: flex; align-items: center; gap: .5rem; width: 100%;
  padding: .4rem .7rem; border: 1px dashed var(--bp-line); border-radius: 8px;
  box-sizing: border-box;
  transition: all .35s;
}
.resbar.on { border-style: solid; border-color: var(--bp-good); background: rgba(74,222,128,.07); }
.rl { font-size: .64rem; color: var(--bp-dim); }
.rv { font-size: .76rem; color: var(--bp-good); }

.kpts { margin-top: .1rem; }
.kpts b { color: var(--bp-cyan); }
</style>
