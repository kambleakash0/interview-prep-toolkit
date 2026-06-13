<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

const CAP = 5

interface Slot { id: number; leaving: boolean }

const buffer = ref<Slot[]>([])
const produced = ref(0)
const consumed = ref(0)
let nextId = 1

const prodBlocked = ref(false)
const consBlocked = ref(false)
const prodAuto = ref(false)
const consAuto = ref(false)
const wireP = ref(false)   // producer -> buffer wire hot
const wireC = ref(false)   // buffer -> consumer wire hot

let prodTimer: ReturnType<typeof setInterval> | null = null
let consTimer: ReturnType<typeof setInterval> | null = null
const flashes: ReturnType<typeof setTimeout>[] = []

function flash(fn: () => void, ms: number) { flashes.push(setTimeout(fn, ms)) }
function clearFlashes() { flashes.forEach(clearTimeout); flashes.length = 0 }

const count = computed(() => buffer.value.filter(s => !s.leaving).length)
const isFull = computed(() => count.value >= CAP)
const isEmpty = computed(() => count.value === 0)

// Fixed slot lanes so items never overlap; indexes 0..CAP-1, left -> right.
// Leaving cells are kept in their lane until the slide-out transition finishes,
// so the FIFO drain animates instead of snapping.
const slotView = computed(() => {
  const out: (Slot | null)[] = []
  let li = 0
  for (let i = 0; i < CAP; i++) out.push(buffer.value[li++] ?? null)
  return out
})

function produce() {
  if (isFull.value) {
    prodBlocked.value = true
    flash(() => { prodBlocked.value = false }, 700)
    return
  }
  prodBlocked.value = false
  buffer.value.push({ id: nextId++, leaving: false })
  produced.value++
  wireP.value = true
  flash(() => { wireP.value = false }, 360)
}

function consume() {
  const front = buffer.value.find(s => !s.leaving)
  if (!front) {
    consBlocked.value = true
    flash(() => { consBlocked.value = false }, 700)
    return
  }
  consBlocked.value = false
  front.leaving = true
  consumed.value++
  wireC.value = true
  flash(() => { wireC.value = false }, 360)
  // remove after slide-out transition completes
  flash(() => { buffer.value = buffer.value.filter(s => s !== front) }, 320)
}

function toggleProdAuto() {
  prodAuto.value = !prodAuto.value
  if (prodAuto.value) {
    if (prodTimer) clearInterval(prodTimer)
    prodTimer = setInterval(produce, 620)   // producer faster
  } else if (prodTimer) {
    clearInterval(prodTimer); prodTimer = null
    prodBlocked.value = false
  }
}

function toggleConsAuto() {
  consAuto.value = !consAuto.value
  if (consAuto.value) {
    if (consTimer) clearInterval(consTimer)
    consTimer = setInterval(consume, 1000)  // consumer slower -> buffer fills
  } else if (consTimer) {
    clearInterval(consTimer); consTimer = null
    consBlocked.value = false
  }
}

function stopAuto() {
  if (prodTimer) { clearInterval(prodTimer); prodTimer = null }
  if (consTimer) { clearInterval(consTimer); consTimer = null }
  prodAuto.value = false
  consAuto.value = false
}

function reset() {
  stopAuto()
  clearFlashes()
  buffer.value = []
  produced.value = 0
  consumed.value = 0
  nextId = 1
  prodBlocked.value = false
  consBlocked.value = false
  wireP.value = false
  wireC.value = false
}

onUnmounted(() => { stopAuto(); clearFlashes() })

// stage geometry (percent coords on the board)
const PROD = { x: 14, y: 50 }
const BUF = { x: 50, y: 50 }
const CONS = { x: 86, y: 50 }
</script>

<template>
  <div class="pc">
    <div class="stage">
      <div class="board">
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <line :x1="PROD.x" :y1="PROD.y" :x2="32" :y2="BUF.y" class="wire" :class="{ hot: wireP, blocked: prodBlocked }" />
          <line :x1="68" :y1="BUF.y" :x2="CONS.x" :y2="CONS.y" class="wire" :class="{ hot: wireC, blocked: consBlocked }" />
        </svg>

        <!-- Producer -->
        <div class="node prod" :class="{ blocked: prodBlocked, live: prodAuto }" :style="{ left: PROD.x + '%', top: PROD.y + '%' }">
          <span class="nt">Producer</span>
          <span class="nm">put()</span>
          <transition name="pop">
            <span v-if="prodBlocked" class="badge bad">BLOCKED <i>(full)</i></span>
          </transition>
        </div>

        <!-- Bounded buffer -->
        <div class="buffer" :class="{ full: isFull }" :style="{ left: BUF.x + '%', top: BUF.y + '%' }">
          <div class="blabel">bounded buffer · FIFO</div>
          <div class="slots">
            <div v-for="(s, i) in slotView" :key="i" class="slot" :class="{ filled: !!s && !s.leaving }">
              <transition name="cell">
                <span v-if="s" :key="s.id" class="cell" :class="{ out: s.leaving }">{{ s.id }}</span>
              </transition>
            </div>
          </div>
          <div class="cap">{{ count }}<span class="capd">/{{ CAP }}</span></div>
          <span class="arrow in">▸</span>
          <span class="arrow out">▸</span>
        </div>

        <!-- Consumer -->
        <div class="node cons" :class="{ blocked: consBlocked, live: consAuto }" :style="{ left: CONS.x + '%', top: CONS.y + '%' }">
          <span class="nt">Consumer</span>
          <span class="nm">get()</span>
          <transition name="pop">
            <span v-if="consBlocked" class="badge warn">BLOCKED <i>(empty)</i></span>
          </transition>
        </div>
      </div>

      <div class="readouts">
        <span class="ro">buffer <b :class="{ bad: isFull }">{{ count }}/{{ CAP }}</b></span>
        <span class="ro">produced <b class="cy">{{ produced }}</b></span>
        <span class="ro">consumed <b class="gd">{{ consumed }}</b></span>
        <span class="ro pressure" v-if="isFull">← back-pressure</span>
        <span class="ro drain" v-else-if="isEmpty">empty → consumer waits</span>
      </div>
    </div>

    <div class="panel">
      <div class="grp">
        <div class="gt">Producer</div>
        <button class="b cy" :disabled="prodAuto" @click="produce">▶ produce</button>
        <label class="tog" :class="{ on: prodAuto }" @click="toggleProdAuto"><span class="knob" /> auto (fast)</label>
      </div>
      <div class="grp cons">
        <div class="gt">Consumer</div>
        <button class="b gd" :disabled="consAuto" @click="consume">▶ consume</button>
        <label class="tog gd" :class="{ on: consAuto }" @click="toggleConsAuto"><span class="knob" /> auto (slow)</label>
      </div>
      <button class="b ghost" @click="reset">⟲ reset</button>
      <ul class="kpts">
        <li>Produce into a full buffer blocks — nothing is added</li>
        <li>Consume an empty buffer blocks — back-pressure works both ways</li>
        <li>Auto: producer outruns consumer, the buffer fills</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.pc { display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.pc *, .pc *::before, .pc *::after { box-sizing: border-box; }
.stage { min-width: 0; display: flex; flex-direction: column; gap: .55rem; }
.board { position: relative; width: 100%; height: 252px; }
.wires { position: absolute; inset: 0; width: 100%; height: 100%; }
.wire { stroke: var(--bp-line); stroke-width: .5; transition: stroke .3s, opacity .3s; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: 1; filter: drop-shadow(0 0 3px var(--bp-cyan)); }
.wire.blocked { stroke: var(--bp-bad); stroke-width: 1; animation: dash .7s ease; }
@keyframes dash { 0%,100% { opacity: 1; } 50% { opacity: .2; } }

.node { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; gap: .12rem; padding: .55rem .7rem; min-width: 86px; border-radius: 10px; border: 1px solid var(--bp-line); background: rgba(11,19,36,.94); transition: border-color .3s, box-shadow .3s; }
.node .nt { font-size: .56rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-dim); }
.node .nm { font-size: .82rem; color: var(--bp-ink); }
.node.prod { border-color: var(--bp-cyan); }
.node.cons { border-color: var(--bp-good); }
.node.live { box-shadow: var(--bp-glow); }
.node.cons.live { box-shadow: 0 0 22px rgba(74,222,128,.4); }
.node.blocked { border-color: var(--bp-bad); box-shadow: 0 0 18px rgba(251,113,133,.45); animation: shk .35s; }
@keyframes shk { 0%,100%{transform:translate(-50%,-50%)} 30%{transform:translate(calc(-50% - 3px),-50%)} 70%{transform:translate(calc(-50% + 3px),-50%)} }
.badge { position: absolute; bottom: -15px; font-size: .54rem; letter-spacing: .04em; padding: .12rem .45rem; border-radius: 999px; white-space: nowrap; animation: pulse 1s ease-in-out infinite; }
.badge i { font-style: normal; opacity: .85; }
.badge.bad { color: var(--bp-bg); background: var(--bp-bad); }
.badge.warn { color: var(--bp-bg); background: var(--bp-warn); }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .55; transform: scale(.94); } }

.buffer { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; gap: .35rem; padding: .6rem .7rem .9rem; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.03); transition: border-color .3s, box-shadow .3s; }
.buffer.full { border-color: var(--bp-bad); box-shadow: 0 0 18px rgba(251,113,133,.3); }
.blabel { font-size: .54rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-dim); }
.slots { display: flex; gap: .3rem; }
.slot { position: relative; width: 30px; height: 36px; border: 1px dashed var(--bp-line); border-radius: 7px; display: flex; align-items: center; justify-content: center; overflow: hidden; transition: border-color .3s, background .3s; }
.slot.filled { border-style: solid; border-color: var(--bp-cyan); background: rgba(34,211,238,.12); }
.cell { font-size: .82rem; color: var(--bp-cyan); font-weight: 600; }
.cell.out { color: var(--bp-good); }
.cap { font-size: .72rem; color: var(--bp-dim); }
.cap .capd { opacity: .6; }
.buffer.full .cap { color: var(--bp-bad); }
.arrow { position: absolute; top: 50%; transform: translateY(-50%); font-size: .8rem; color: var(--bp-dim); }
.arrow.in { left: -15px; color: var(--bp-cyan); }
.arrow.out { right: -15px; color: var(--bp-good); }

.cell-enter-active { transition: transform .3s cubic-bezier(.3,1.3,.5,1), opacity .3s; }
.cell-enter-from { transform: translateX(-22px) scale(.5); opacity: 0; }
.cell-leave-active { transition: transform .3s ease, opacity .3s; position: absolute; }
.cell-leave-to { transform: translateX(22px) scale(.5); opacity: 0; }

.readouts { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; padding: .5rem .7rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02); }
.ro { font-size: .72rem; color: var(--bp-dim); }
.ro b { font-size: .9rem; margin-left: .3rem; }
.ro b.cy { color: var(--bp-cyan); } .ro b.gd { color: var(--bp-good); }
.ro b.bad { color: var(--bp-bad); }
.pressure { color: var(--bp-bad); font-size: .64rem; letter-spacing: .04em; animation: pulse 1.1s ease-in-out infinite; }
.drain { color: var(--bp-dim); font-size: .64rem; letter-spacing: .04em; }

.panel { display: flex; flex-direction: column; gap: .6rem; min-width: 0; }
.grp { display: flex; align-items: center; gap: .55rem; flex-wrap: wrap; padding: .45rem .6rem; border: 1px solid var(--bp-line); border-radius: 9px; }
.grp .gt { font-size: .56rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-cyan); width: 100%; }
.grp.cons .gt { color: var(--bp-good); }
.b { font-family: inherit; font-size: .76rem; padding: .4rem .75rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px; background: rgba(255,255,255,.03); cursor: pointer; transition: border-color .2s, color .2s, background .2s; }
.b.cy { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.cy:hover:not(:disabled) { background: rgba(34,211,238,.2); }
.b.gd { border-color: var(--bp-good); color: var(--bp-good); background: rgba(74,222,128,.12); box-shadow: 0 0 18px rgba(74,222,128,.3); }
.b.gd:hover:not(:disabled) { background: rgba(74,222,128,.2); }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; width: fit-content; }
.b.ghost:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.tog { display: inline-flex; align-items: center; gap: .45rem; font-size: .7rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: left .3s, background .3s; }
.tog.on .knob { background: rgba(34,211,238,.4); } .tog.on .knob::after { left: 16px; background: var(--bp-cyan); }
.tog.on { color: var(--bp-cyan); }
.tog.gd.on .knob { background: rgba(74,222,128,.4); } .tog.gd.on .knob::after { background: var(--bp-good); }
.tog.gd.on { color: var(--bp-good); }
.pop-enter-active { transition: opacity .2s, transform .2s; } .pop-enter-from { opacity: 0; transform: translateY(-4px) scale(.8); }
.pop-leave-active { transition: opacity .15s; } .pop-leave-to { opacity: 0; }
.kpts { list-style: none; padding: 0; margin: .1rem 0 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .26rem 0; font-size: .7rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
