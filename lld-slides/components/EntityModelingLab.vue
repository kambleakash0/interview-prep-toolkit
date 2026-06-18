<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   EntityModelingLab — turn a prompt into a typed graph, live.
   Stage 1: mine the blurb — sort every word-chip into the right
   bin (Entity / Attribute / Enum / Discard). Stage 2: wire the
   accepted entities into a UML relationship graph with a typed
   edge + multiplicity on each pair, then reveal the reference.
   ============================================================ */

type StageId = 1 | 2
type Bin = 'entity' | 'attr' | 'enum' | 'discard'

interface RailStage { id: StageId; label: string }
const RAIL: RailStage[] = [
  { id: 1, label: 'Mine the prompt' },
  { id: 2, label: 'Wire relationships' },
]
const stage = ref<StageId>(1)
function goto(id: StageId) {
  // only let learner advance to stage 2 once the candidate set is clean
  if (id === 2 && !mined.value) return
  stage.value = id
}

const timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) { const t = setTimeout(fn, ms); timers.push(t); return t }
onUnmounted(() => { timers.forEach(clearTimeout) })

/* ---------- STAGE 1: mine the prompt ----------
   The fixed parking-lot blurb, tokenised. Each significant word is
   a chip with a correct bin + a one-line rationale shown on a miss. */
interface Chip {
  id: string
  word: string
  bin: Bin            // correct destination
  why: string         // rationale shown when learner drops it wrong
}
const CHIPS: Chip[] = [
  { id: 'lot',   word: 'parking lot', bin: 'entity',  why: 'root aggregate with identity + behavior' },
  { id: 'lvl',   word: 'level',       bin: 'entity',  why: 'owns spots, has identity -> Entity' },
  { id: 'spot',  word: 'spot',        bin: 'entity',  why: 'identity + state -> Entity' },
  { id: 'veh',   word: 'vehicle',     bin: 'entity',  why: 'identity, parks -> Entity' },
  { id: 'num',   word: 'spot number', bin: 'attr',    why: 'plain data on Spot -> Attribute, not Entity' },
  { id: 'plate', word: 'plate',       bin: 'attr',    why: 'data on Vehicle -> Attribute' },
  { id: 'stat',  word: 'status',      bin: 'enum',    why: 'free / occupied is a fixed set -> Enum' },
  { id: 'park',  word: 'parks',       bin: 'discard', why: 'a verb -> becomes a method, not a noun' },
  { id: 'board', word: 'display board', bin: 'discard', why: 'UI / IO concern -> Discard' },
  { id: 'avail', word: 'available',   bin: 'discard', why: 'derived from status -> Discard (no new type)' },
]
const BINS: { id: Bin; label: string; hint: string }[] = [
  { id: 'entity',  label: 'Entity',    hint: 'identity + behavior' },
  { id: 'attr',    label: 'Attribute', hint: 'plain data' },
  { id: 'enum',    label: 'Enum',      hint: 'fixed value set' },
  { id: 'discard', label: 'Discard',   hint: 'verbs / UI / derived' },
]

const armed = ref<string>('')                 // chip id currently selected to place
const placedBin = reactive<Record<string, Bin>>({})  // chipId -> bin it landed in (correct only)
const badBin = ref<{ bin: Bin; chip: string } | ''>('')  // flashes a wrong-drop on a bin
const rationale = ref('')                      // one-line teaching note for the last miss

function armChip(id: string) {
  if (placedBin[id]) return
  armed.value = armed.value === id ? '' : id
}
function dropInto(bin: Bin) {
  const id = armed.value
  if (!id) return
  const chip = CHIPS.find(c => c.id === id)!
  if (chip.bin === bin) {
    placedBin[id] = bin
    armed.value = ''
    rationale.value = ''
    badBin.value = ''
  } else {
    badBin.value = { bin, chip: id }
    rationale.value = `${chip.word} -> ${chip.why}`
    later(() => { if (typeof badBin.value === 'object' && badBin.value.chip === id) badBin.value = '' }, 900)
  }
}
const unplaced = computed(() => CHIPS.filter(c => !placedBin[c.id]))
const placedCount = computed(() => CHIPS.length - unplaced.value.length)
const chipsIn = (bin: Bin) => CHIPS.filter(c => placedBin[c.id] === bin)
// the candidate set is "mined" once every chip is correctly sorted
const mined = computed(() => unplaced.value.length === 0)
// raw word-soup collapsing into a clean entity set
const ENTITY_IDS = CHIPS.filter(c => c.bin === 'entity').map(c => c.id)
function autoSort() {
  for (const c of CHIPS) placedBin[c.id] = c.bin
  armed.value = ''; rationale.value = ''; badBin.value = ''
}
function resetMine() {
  for (const k of Object.keys(placedBin)) delete placedBin[k]
  armed.value = ''; rationale.value = ''; badBin.value = ''
}

/* ---------- STAGE 2: wire relationships ----------
   Accepted entities become boxes. Learner connects two boxes, then
   picks an edge type + a multiplicity on each end. Canvas redraws
   the UML glyph live. Many-to-many flags a link-entity note. */
interface EBox { id: string; name: string; x: number; y: number }
const EBOXES: EBox[] = [
  { id: 'lot',  name: 'ParkingLot', x: 14,  y: 14 },
  { id: 'lvl',  name: 'Level',      x: 170, y: 14 },
  { id: 'spot', name: 'Spot',       x: 326, y: 14 },
  { id: 'veh',  name: 'Vehicle',    x: 326, y: 104 },
]
type EdgeType = 'inherit' | 'compose' | 'aggregate' | 'assoc'
type Mult = '1' | '0..*' | '1..*'
const EDGE_TYPES: { id: EdgeType; label: string; glyph: string }[] = [
  { id: 'inherit',   label: 'inheritance',  glyph: 'tri' },     // hollow triangle
  { id: 'compose',   label: 'composition',  glyph: 'fdia' },    // filled diamond
  { id: 'aggregate', label: 'aggregation',  glyph: 'hdia' },    // hollow diamond
  { id: 'assoc',     label: 'association',  glyph: 'line' },    // plain line
]
const MULTS: Mult[] = ['1', '0..*', '1..*']

interface Edge {
  id: string
  from: string; to: string
  type: EdgeType
  mFrom: Mult; mTo: Mult
}
const edges = reactive<Edge[]>([])
const connectFrom = ref<string>('')   // first box clicked while wiring
const editing = ref<string>('')       // edge id whose popover is open

function clickBox(id: string) {
  if (!connectFrom.value) { connectFrom.value = id; return }
  if (connectFrom.value === id) { connectFrom.value = ''; return }
  // create a new edge with sane defaults, open its editor
  const eid = `${connectFrom.value}-${id}-${edges.length}`
  edges.push({ id: eid, from: connectFrom.value, to: id, type: 'assoc', mFrom: '1', mTo: '0..*' })
  editing.value = eid
  connectFrom.value = ''
}
function edge(id: string) { return edges.find(e => e.id === id) }
function setType(id: string, t: EdgeType) { const e = edge(id); if (e) e.type = t }
function cycleMult(id: string, end: 'from' | 'to') {
  const e = edge(id); if (!e) return
  const cur = end === 'from' ? e.mFrom : e.mTo
  const next = MULTS[(MULTS.indexOf(cur) + 1) % MULTS.length]
  if (end === 'from') e.mFrom = next; else e.mTo = next
}
function deleteEdge(id: string) {
  const i = edges.findIndex(e => e.id === id)
  if (i >= 0) edges.splice(i, 1)
  if (editing.value === id) editing.value = ''
}
function clearWiring() { edges.splice(0); connectFrom.value = ''; editing.value = ''; revealed.value = false }

const ebox = (id: string) => EBOXES.find(b => b.id === id)!
const ecx = (id: string) => ebox(id).x + 70   // box is 140 wide
const ecy = (id: string) => ebox(id).y + 26   // box is ~52 tall
const glyphOf = (t: EdgeType) => EDGE_TYPES.find(et => et.id === t)!.glyph

// a many-to-many edge needs a link entity — flag it as a teaching note
const manyToMany = computed(() =>
  edges.some(e => e.mFrom.includes('*') && e.mTo.includes('*')))

/* canonical reference model + the pattern each edge foreshadows */
interface Ref { from: string; to: string; type: EdgeType; mFrom: Mult; mTo: Mult; pattern: string }
const REFERENCE: Ref[] = [
  { from: 'lot',  to: 'lvl',  type: 'aggregate', mFrom: '1', mTo: '1..*', pattern: 'Composite (part-of tree)' },
  { from: 'lvl',  to: 'spot', type: 'compose',   mFrom: '1', mTo: '1..*', pattern: 'Composite (spots die with level)' },
  { from: 'veh',  to: 'spot', type: 'assoc',     mFrom: '1', mTo: '1',    pattern: 'State (Spot free<->occupied)' },
]
const revealed = ref(false)
function reveal() {
  edges.splice(0)
  for (let i = 0; i < REFERENCE.length; i++) {
    const r = REFERENCE[i]
    edges.push({ id: `ref-${i}`, from: r.from, to: r.to, type: r.type, mFrom: r.mFrom, mTo: r.mTo })
  }
  editing.value = ''
  connectFrom.value = ''
  revealed.value = true
}
const patternFor = (e: Edge) =>
  revealed.value ? REFERENCE.find(r => r.from === e.from && r.to === e.to)?.pattern : undefined

// midpoint helpers for labels
const midX = (e: Edge) => (ecx(e.from) + ecx(e.to)) / 2
const midY = (e: Edge) => (ecy(e.from) + ecy(e.to)) / 2
// a point near `from` (where the glyph sits) — 22px along the edge toward `to`
function glyphPt(e: Edge) {
  const x1 = ecx(e.from), y1 = ecy(e.from), x2 = ecx(e.to), y2 = ecy(e.to)
  const dx = x2 - x1, dy = y2 - y1
  const len = Math.hypot(dx, dy) || 1
  return { x: x1 + (dx / len) * 16, y: y1 + (dy / len) * 16, ang: Math.atan2(dy, dx) * 180 / Math.PI }
}
</script>

<template>
  <div class="lab">
    <!-- ===== fixed prompt ===== -->
    <div class="prompt">
      <span class="ptag">prompt</span>
      A <b>parking lot</b> has <b>levels</b>; each level has <b>spots</b>. A <b>vehicle</b>
      <i>parks</i> in a spot; its <b>status</b> is free or occupied.
    </div>

    <!-- ===== stage rail ===== -->
    <div class="rail">
      <template v-for="(s, i) in RAIL" :key="s.id">
        <button class="rstep" :class="{ on: stage === s.id, done: stage > s.id, locked: s.id === 2 && !mined }"
                @click="goto(s.id)">
          <span class="rnum">{{ s.id }}</span>
          <span class="rlbl">{{ s.label }}</span>
          <span v-if="s.id === 2 && !mined" class="lock">sort first</span>
        </button>
        <span v-if="i < RAIL.length - 1" class="rconn" :class="{ lit: mined }" />
      </template>
      <span class="counter">{{ placedCount }}/{{ CHIPS.length }} sorted</span>
    </div>

    <!-- ===== stage body ===== -->
    <div class="stage">

      <!-- ---------- STAGE 1 ---------- -->
      <div v-if="stage === 1" class="s1">
        <div class="leftcol">
          <div class="ttl">Word soup&nbsp;<span class="cnt">{{ unplaced.length }}</span></div>
          <div class="soup">
            <button v-for="c in unplaced" :key="c.id" class="wchip"
                    :class="{ armed: armed === c.id }" @click="armChip(c.id)">
              {{ c.word }}
            </button>
            <span v-if="!unplaced.length" class="cleared">clean candidate set — nouns, data, enums sorted.</span>
          </div>
          <div class="note" :class="{ show: rationale }">
            <span v-if="rationale">{{ rationale }}</span>
            <span v-else class="dimnote">Arm a chip, drop it in a bin. Verbs and UI go to Discard.</span>
          </div>
        </div>

        <div class="bins">
          <div v-for="b in BINS" :key="b.id" class="bin"
               :class="{ armed: armed,
                         bad: typeof badBin === 'object' && badBin.bin === b.id,
                         filled: chipsIn(b.id).length }"
               @click="dropInto(b.id)">
            <div class="binhead">
              <span class="bname">{{ b.label }}</span>
              <span class="bhint">{{ b.hint }}</span>
            </div>
            <div class="binbody">
              <span v-for="c in chipsIn(b.id)" :key="c.id" class="placed">{{ c.word }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ---------- STAGE 2 ---------- -->
      <div v-else class="s2">
        <div class="canvaswrap">
          <div class="ttl">
            Relationship canvas
            <span v-if="connectFrom" class="cnt live">connecting {{ ebox(connectFrom).name }}…</span>
            <span v-else class="cnt">click two boxes to draw an edge</span>
          </div>
          <div class="canvas">
            <svg class="edges" viewBox="0 0 480 156" preserveAspectRatio="none">
              <g v-for="e in edges" :key="e.id">
                <line :x1="ecx(e.from)" :y1="ecy(e.from)" :x2="ecx(e.to)" :y2="ecy(e.to)"
                      class="eline" :class="{ ref: revealed }" />
                <!-- multiplicity labels at each end -->
                <text :x="ecx(e.from) + (ecx(e.to) > ecx(e.from) ? 12 : -12)" :y="ecy(e.from) - 6"
                      class="mlbl">{{ e.mFrom }}</text>
                <text :x="ecx(e.to) + (ecx(e.from) > ecx(e.to) ? 12 : -12)" :y="ecy(e.to) - 6"
                      class="mlbl">{{ e.mTo }}</text>
                <!-- UML glyph at the `from` end -->
                <g :transform="`translate(${glyphPt(e).x},${glyphPt(e).y}) rotate(${glyphPt(e).ang})`">
                  <polygon v-if="glyphOf(e.type) === 'tri'" points="0,-5 11,0 0,5" class="g-hollow" />
                  <polygon v-else-if="glyphOf(e.type) === 'fdia'" points="0,0 7,-5 14,0 7,5" class="g-fill" />
                  <polygon v-else-if="glyphOf(e.type) === 'hdia'" points="0,0 7,-5 14,0 7,5" class="g-hollow" />
                </g>
              </g>
            </svg>
            <button v-for="b in EBOXES" :key="b.id" class="ebox"
                    :class="{ sel: connectFrom === b.id }"
                    :style="{ left: b.x + 'px', top: b.y + 'px' }"
                    @click="clickBox(b.id)">
              {{ b.name }}
            </button>
          </div>
          <transition name="reveal">
            <div v-if="manyToMany && !revealed" class="m2m">
              many-to-many edge -> needs a link entity (add <b>Booking</b>?)
            </div>
          </transition>
        </div>

        <div class="sidecol">
          <div class="ttl">Edges <span class="cnt">{{ edges.length }}</span></div>
          <div class="edgelist">
            <div v-for="e in edges" :key="e.id" class="erow" :class="{ open: editing === e.id }">
              <div class="ehead" @click="editing = editing === e.id ? '' : e.id">
                <span class="enm">{{ ebox(e.from).name }} → {{ ebox(e.to).name }}</span>
                <button class="del" @click.stop="deleteEdge(e.id)">×</button>
              </div>
              <div v-if="patternFor(e)" class="pat">{{ patternFor(e) }}</div>
              <transition name="reveal">
                <div v-if="editing === e.id" class="editor">
                  <div class="types">
                    <button v-for="t in EDGE_TYPES" :key="t.id" class="tbtn"
                            :class="{ on: e.type === t.id }" @click="setType(e.id, t.id)">
                      {{ t.label }}
                    </button>
                  </div>
                  <div class="mults">
                    <button class="mbtn" @click="cycleMult(e.id, 'from')">{{ ebox(e.from).name.slice(0,4) }}: {{ e.mFrom }}</button>
                    <button class="mbtn" @click="cycleMult(e.id, 'to')">{{ ebox(e.to).name.slice(0,4) }}: {{ e.mTo }}</button>
                  </div>
                </div>
              </transition>
            </div>
            <span v-if="!edges.length" class="empty">no edges yet — wire two boxes.</span>
          </div>
          <button class="b reveal-btn" :class="{ done: revealed }" @click="reveal">
            {{ revealed ? 'reference model shown' : 'reveal reference model' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===== controls + footer ===== -->
    <div class="bar">
      <template v-if="stage === 1">
        <button class="b ghost" @click="resetMine">reset</button>
        <button class="b" @click="autoSort">auto-sort</button>
        <button class="b play" :disabled="!mined" @click="goto(2)">wire relationships →</button>
        <span class="foot">Mine first: nouns→entities, data→attribute, fixed sets→enum, verbs/UI→discard.</span>
      </template>
      <template v-else>
        <button class="b ghost" @click="stage = 1">← back to mining</button>
        <button class="b ghost" @click="clearWiring">clear edges</button>
        <span class="foot">Type each edge, pin multiplicity per end; the patterns are already hinted at the edges.</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.lab {
  width: 100%; height: 356px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: .55rem;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}

/* ---------- prompt ---------- */
.prompt {
  font-size: .72rem; line-height: 1.5; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-left: 3px solid var(--bp-cyan);
  border-radius: 0 8px 8px 0; background: rgba(34,211,238,.05);
  padding: .4rem .7rem; position: relative;
}
.prompt b { color: var(--bp-ink); }
.prompt i { color: var(--bp-violet); font-style: italic; }
.ptag { font-size: .5rem; text-transform: uppercase; letter-spacing: .14em;
  color: var(--bp-cyan); border: 1px solid var(--bp-line); border-radius: 999px;
  padding: .05rem .4rem; margin-right: .5rem; }

/* ---------- rail ---------- */
.rail { display: flex; align-items: center; gap: 0; }
.rstep { display: flex; align-items: center; gap: .4rem; font-family: inherit; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02);
  color: var(--bp-dim); padding: .28rem .55rem; transition: all .25s; }
.rstep:hover:not(.locked) { border-color: var(--bp-cyan); color: var(--bp-ink); }
.rstep.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.rstep.done { color: var(--bp-good); border-color: rgba(74,222,128,.35); }
.rstep.locked { opacity: .55; cursor: not-allowed; }
.rnum { font-size: .6rem; border: 1px solid currentColor; border-radius: 5px; padding: 0 .3rem; opacity: .8; }
.rlbl { font-size: .72rem; }
.lock { font-size: .52rem; color: var(--bp-warn); border: 1px solid rgba(251,191,36,.4);
  border-radius: 4px; padding: 0 .3rem; }
.rconn { flex: 0 0 28px; height: 2px; background: var(--bp-line); margin: 0 .3rem; transition: background .3s; }
.rconn.lit { background: linear-gradient(90deg, var(--bp-good), var(--bp-line)); }
.counter { margin-left: auto; font-size: .6rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 999px; padding: .15rem .6rem; }

/* ---------- stage ---------- */
.stage { flex: 1; min-height: 0; border: 1px solid var(--bp-line); border-radius: 12px;
  background: rgba(255,255,255,.015); padding: .7rem .8rem; overflow: hidden; }
.ttl { font-size: .62rem; text-transform: uppercase; letter-spacing: .12em; color: var(--bp-cyan);
  display: flex; align-items: center; gap: .35rem; }
.cnt { font-size: .54rem; color: var(--bp-bg); background: var(--bp-cyan);
  border-radius: 999px; padding: .04rem .4rem; }
.cnt.live { background: var(--bp-violet); }

/* ---------- stage 1 ---------- */
.s1 { display: grid; grid-template-columns: 1fr 1.25fr; gap: 1rem; height: 100%; }
.leftcol { display: flex; flex-direction: column; gap: .5rem; min-width: 0; }
.soup { flex: 1; display: flex; flex-wrap: wrap; gap: .4rem; align-content: flex-start;
  border: 1px dashed var(--bp-line); border-radius: 10px; padding: .55rem; }
.wchip { font-family: inherit; font-size: .66rem; cursor: pointer; color: var(--bp-ink);
  border: 1px solid var(--bp-line); border-radius: 7px; padding: .26rem .5rem;
  background: rgba(255,255,255,.03); transition: all .18s; }
.wchip:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.wchip.armed { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.16);
  box-shadow: var(--bp-glow); transform: translateY(-1px); }
.cleared { font-size: .62rem; color: var(--bp-good); }
.note { font-size: .6rem; min-height: 1.5rem; padding: .35rem .5rem; border-radius: 7px;
  border: 1px solid transparent; transition: all .2s; }
.note.show { color: var(--bp-bad); border-color: rgba(251,113,133,.4); background: rgba(251,113,133,.08); }
.dimnote { color: var(--bp-dim); }

.bins { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: .55rem; height: 100%; min-height: 0; }
.bin { border: 1px dashed var(--bp-line); border-radius: 10px; padding: .4rem .5rem;
  background: rgba(255,255,255,.02); cursor: default; transition: all .2s;
  display: flex; flex-direction: column; gap: .3rem; min-height: 0; overflow: hidden; }
.bin.armed { cursor: pointer; border-color: var(--bp-cyan); }
.bin.armed:hover { border-style: solid; background: rgba(34,211,238,.06); }
.bin.filled { border-style: solid; }
.bin.bad { border-color: var(--bp-bad); background: rgba(251,113,133,.1); animation: shake .4s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-4px)} 75%{transform:translateX(4px)} }
.binhead { display: flex; align-items: baseline; gap: .4rem; }
.bname { font-size: .64rem; color: var(--bp-ink); }
.bhint { font-size: .5rem; color: var(--bp-dim); }
.binbody { display: flex; flex-wrap: wrap; gap: .3rem; align-content: flex-start; overflow: hidden; }
.placed { font-size: .58rem; color: var(--bp-good); border: 1px solid rgba(74,222,128,.4);
  background: rgba(74,222,128,.1); border-radius: 6px; padding: .12rem .4rem; }

/* ---------- stage 2 ---------- */
.s2 { display: grid; grid-template-columns: 1.35fr 1fr; gap: 1rem; height: 100%; }
.canvaswrap { display: flex; flex-direction: column; gap: .45rem; min-width: 0; }
.canvas { position: relative; width: 100%; max-width: 480px; height: 156px; align-self: center; }
.edges { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.eline { stroke: var(--bp-cyan); stroke-width: 1.6; opacity: .9; }
.eline.ref { stroke: var(--bp-good); }
.mlbl { fill: var(--bp-dim); font-size: 8px; font-family: "Fira Code", monospace; text-anchor: middle; }
.g-fill { fill: var(--bp-violet); stroke: var(--bp-violet); }
.g-hollow { fill: var(--bp-bg); stroke: var(--bp-violet); stroke-width: 1.4; }
.ebox { position: absolute; width: 140px; height: 52px; box-sizing: border-box;
  border: 1px solid var(--bp-line); border-radius: 8px; background: var(--bp-bg-2);
  color: var(--bp-ink); font-family: inherit; font-size: .68rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all .2s; }
.ebox:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.ebox.sel { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); }
.m2m { font-size: .58rem; color: var(--bp-warn); border: 1px solid rgba(251,191,36,.4);
  background: rgba(251,191,36,.08); border-radius: 7px; padding: .3rem .55rem; }
.m2m b { color: var(--bp-warn); }

.sidecol { display: flex; flex-direction: column; gap: .45rem; min-width: 0; min-height: 0; }
.edgelist { flex: 1; display: flex; flex-direction: column; gap: .4rem; overflow-y: auto; min-height: 0; padding-right: 2px; }
.edgelist::-webkit-scrollbar { width: 5px; }
.edgelist::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.erow { border: 1px solid var(--bp-line); border-radius: 8px; background: rgba(255,255,255,.02);
  padding: .32rem .45rem; transition: all .2s; }
.erow.open { border-color: var(--bp-cyan); }
.ehead { display: flex; align-items: center; gap: .4rem; cursor: pointer; }
.enm { font-size: .6rem; color: var(--bp-ink); flex: 1; }
.del { font-family: inherit; font-size: .78rem; line-height: 1; color: var(--bp-dim);
  border: none; background: transparent; cursor: pointer; padding: 0 .2rem; }
.del:hover { color: var(--bp-bad); }
.pat { font-size: .54rem; color: var(--bp-violet); margin-top: .2rem; }
.editor { margin-top: .4rem; display: flex; flex-direction: column; gap: .35rem; }
.types { display: grid; grid-template-columns: 1fr 1fr; gap: .28rem; }
.tbtn { font-family: inherit; font-size: .54rem; cursor: pointer; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 6px; padding: .2rem .3rem;
  background: rgba(255,255,255,.02); transition: all .18s; }
.tbtn:hover { border-color: var(--bp-violet); color: var(--bp-ink); }
.tbtn.on { border-color: var(--bp-violet); color: #fff; background: rgba(167,139,250,.16); }
.mults { display: flex; gap: .3rem; }
.mbtn { flex: 1; font-family: inherit; font-size: .54rem; cursor: pointer; color: var(--bp-cyan);
  border: 1px solid var(--bp-line); border-radius: 6px; padding: .2rem .3rem;
  background: rgba(34,211,238,.06); transition: all .18s; }
.mbtn:hover { border-color: var(--bp-cyan); }
.empty { font-size: .6rem; color: var(--bp-dim); }

/* ---------- shared controls ---------- */
.bar { display: flex; align-items: center; gap: .5rem; }
.b { font-family: inherit; font-size: .66rem; padding: .35rem .6rem; cursor: pointer;
  border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px;
  background: rgba(255,255,255,.03); transition: all .2s; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.play { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.reveal-btn { margin-top: auto; border-color: rgba(167,139,250,.4); color: var(--bp-violet);
  background: rgba(167,139,250,.08); }
.reveal-btn:hover { border-color: var(--bp-violet); color: #fff; }
.reveal-btn.done { border-color: var(--bp-good); color: var(--bp-good); background: rgba(74,222,128,.08); }
.foot { margin-left: auto; font-size: .58rem; color: var(--bp-dim); letter-spacing: .03em; }

/* ---------- transitions ---------- */
.reveal-enter-active { transition: all .3s ease; }
.reveal-enter-from { opacity: 0; transform: translateY(-4px); }
.reveal-leave-active { transition: all .2s ease; }
.reveal-leave-to { opacity: 0; }
</style>
