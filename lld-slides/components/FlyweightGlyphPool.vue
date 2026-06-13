<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Style = 'Mono/black' | 'Serif/red'

interface Slot {
  key: string
  char: string
  style: Style
  refs: number
  bump: boolean      // refcount badge just ticked
  fresh: boolean     // newly allocated -> 'allocate' pulse
}

interface Tile {
  id: number
  char: string
  style: Style
  slotKey: string
  hit: boolean
  enter: boolean     // fly-in animation
}

const KEYS = ['l', 'e', 'v', 'o', 'a', 'r']
const COLS = 10
const CELLS = 30          // grid capacity (3 rows x 10)

const style = ref<Style>('Mono/black')
const shelf = ref<Slot[]>([])
const tiles = ref<Tile[]>([])
const placed = ref(0)
const frozen = ref(false) // flashes 'flyweights created' gray on a HIT

let tid = 0
let busy = false
const dimming = ref(false)

// track pending timers so they can be cleared on unmount / reset
let timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) {
  const id = setTimeout(() => {
    timers = timers.filter((t) => t !== id)
    fn()
  }, ms)
  timers.push(id)
}
function clearTimers() {
  timers.forEach((t) => clearTimeout(t))
  timers = []
}
onUnmounted(clearTimers)

const created = computed(() => shelf.value.length)
const styleClass = computed(() => (style.value === 'Mono/black' ? 'mono' : 'serif'))

function press(char: string) {
  if (busy) return
  if (tiles.value.length >= CELLS) return
  busy = true
  const key = char + '|' + style.value
  const existing = shelf.value.find((s) => s.key === key)
  const tile: Tile = { id: ++tid, char, style: style.value, slotKey: key, hit: !!existing, enter: true }

  if (existing) {
    // HIT — reuse cached flyweight, only tiles placed increments
    existing.refs++
    existing.bump = true
    frozen.value = true
    tiles.value.push(tile)
    placed.value++
    later(() => { existing.bump = false }, 380)
    later(() => { frozen.value = false }, 520)
    later(() => { tile.enter = false; busy = false }, 460)
  } else {
    // MISS — allocate a new flyweight slot, both counters increment
    const slot: Slot = { key, char, style: style.value, refs: 1, bump: false, fresh: true }
    shelf.value.push(slot)
    tiles.value.push(tile)
    placed.value++
    later(() => { slot.fresh = false }, 620)
    later(() => { tile.enter = false; busy = false }, 460)
  }
}

function toggleStyle() {
  if (busy) return
  style.value = style.value === 'Mono/black' ? 'Serif/red' : 'Mono/black'
}

function clear() {
  if (busy) return
  // empty the grid + reset tiles placed; KEEP shelf + flyweights created
  tiles.value = []
  placed.value = 0
  dimming.value = true
  later(() => { dimming.value = false }, 480)
}

function reset() {
  if (busy) return
  clearTimers()
  shelf.value = []
  tiles.value = []
  placed.value = 0
  frozen.value = false
  dimming.value = false
  style.value = 'Mono/black'
}

function slotIndex(key: string): number {
  return shelf.value.findIndex((s) => s.key === key)
}
function tileStyleClass(t: Tile): string {
  return t.style === 'Mono/black' ? 'mono' : 'serif'
}
</script>

<template>
  <div class="fw">
    <!-- ============ STAGE ============ -->
    <div class="stage">
      <!-- counters -->
      <div class="counters">
        <div class="ctr">
          <span class="lbl">tiles placed</span>
          <b class="num">{{ placed }}</b>
        </div>
        <div class="ctr" :class="{ frozen }">
          <span class="lbl">flyweights created</span>
          <b class="num cyan">{{ created }}</b>
          <span v-if="frozen" class="nochg">no alloc</span>
        </div>
      </div>

      <div class="board">
        <!-- POOL SHELF -->
        <div class="shelf" :class="{ dim: dimming }">
          <div class="shead">POOL SHELF<span class="cap">cache[key]</span></div>
          <div class="slots">
            <transition-group name="slot">
              <div
                v-for="s in shelf"
                :key="s.key"
                class="slot"
                :class="[s.style === 'Mono/black' ? 'mono' : 'serif', { fresh: s.fresh, bump: s.bump }]"
              >
                <span class="gl">{{ s.char }}</span>
                <span class="meta">{{ s.style }}</span>
                <span class="ref" :class="{ bump: s.bump }">{{ s.refs }}</span>
                <transition name="alloc"><span v-if="s.fresh" class="alloc">allocate</span></transition>
              </div>
            </transition-group>
            <div v-if="!shelf.length" class="shelf-empty">∅ no flyweights</div>
          </div>
        </div>

        <!-- GRID -->
        <div class="grid-wrap">
          <div class="ghead">GRID<span class="cap">page render</span></div>
          <div class="grid" :style="{ gridTemplateColumns: `repeat(${COLS}, 1fr)` }">
            <transition-group name="tile">
              <div
                v-for="t in tiles"
                :key="t.id"
                class="tile"
                :class="[tileStyleClass(t), { hit: t.hit, miss: !t.hit, enter: t.enter }]"
              >
                {{ t.char }}
                <span class="slotno">#{{ slotIndex(t.slotKey) + 1 }}</span>
              </div>
            </transition-group>
            <div v-if="!tiles.length" class="grid-empty">type a key →</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="kbd">
        <button
          v-for="k in KEYS"
          :key="k"
          class="key"
          :class="styleClass"
          @click="press(k)"
        >{{ k }}</button>
      </div>

      <label class="tog" :class="{ serif: style === 'Serif/red' }" @click="toggleStyle">
        <span class="knob" />
        <span class="tlabel">style <b>{{ style }}</b></span>
      </label>

      <div class="btns">
        <button class="b" @click="clear">⟲ clear grid</button>
        <button class="b ghost" @click="reset">reset all</button>
      </div>

      <div class="legend">
        <span class="leg miss"><i /> MISS → new slot + alloc</span>
        <span class="leg hit"><i /> HIT → reuse, refs++</span>
      </div>

      <ul class="kpts bp-dim text-sm">
        <li>key = <b>char + style</b>; the factory hands back a cached instance</li>
        <li>Flip <b>style</b> — same letters now miss until that variant caches</li>
        <li>Clear the grid: tiles reset, but the pool persists and is reused</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.fw {
  display: grid;
  grid-template-columns: 1.62fr 1fr;
  gap: 1.4rem;
  height: 340px;
  font-family: "Fira Code", monospace;
}

/* ---------- stage ---------- */
.stage { display: flex; flex-direction: column; gap: .55rem; min-width: 0; min-height: 0; }

.counters { display: flex; gap: .8rem; flex: 0 0 auto; }
.ctr {
  flex: 1; position: relative;
  display: flex; align-items: baseline; gap: .55rem;
  padding: .4rem .75rem;
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02);
  transition: all .3s;
}
.ctr.frozen { border-color: rgba(138,160,192,.5); background: rgba(138,160,192,.07); }
.ctr .lbl { font-size: .62rem; color: var(--bp-dim); text-transform: uppercase; letter-spacing: .07em; }
.ctr .num { font-size: 1.35rem; color: #fff; line-height: 1; margin-left: auto; transition: color .3s; }
.ctr .num.cyan { color: var(--bp-cyan); }
.ctr.frozen .num.cyan { color: var(--bp-dim); }
.ctr .nochg {
  position: absolute; top: -8px; right: 8px;
  font-size: .54rem; color: var(--bp-dim);
  border: 1px solid rgba(138,160,192,.45); border-radius: 999px;
  padding: .02rem .4rem; background: var(--bp-bg);
}

.board { display: grid; grid-template-columns: 168px 1fr; gap: .9rem; min-width: 0; flex: 1 1 auto; min-height: 0; }

/* ---------- shelf ---------- */
.shelf {
  border: 1px solid var(--bp-line); border-radius: 11px;
  padding: .5rem .55rem; background: rgba(167,139,250,.04);
  transition: opacity .3s;
  display: flex; flex-direction: column; min-height: 0;
}
.shelf.dim { opacity: .4; }
.shead { font-size: .58rem; letter-spacing: .08em; color: var(--bp-violet); display: flex; justify-content: space-between; margin-bottom: .45rem; flex: 0 0 auto; }
.shead .cap { color: var(--bp-dim); opacity: .7; }
.slots { display: flex; flex-direction: column; gap: .32rem; flex: 1 1 auto; min-height: 0; overflow: auto; }
.shelf-empty { font-size: .64rem; color: var(--bp-dim); text-align: center; padding: 1.2rem 0; }

.slot {
  position: relative;
  display: grid; grid-template-columns: 24px 1fr auto; align-items: center; gap: .4rem;
  padding: .3rem .45rem;
  border: 1px solid var(--bp-line); border-radius: 7px;
  background: rgba(255,255,255,.03);
  transition: all .35s;
  flex: 0 0 auto;
}
.slot.mono  { border-color: rgba(34,211,238,.4); }
.slot.serif { border-color: rgba(251,113,133,.45); }
.slot .gl { font-size: 1rem; text-align: center; }
.slot.mono  .gl { color: var(--bp-cyan); }
.slot.serif .gl { color: var(--bp-bad); font-family: Georgia, "Times New Roman", serif; font-style: italic; }
.slot .meta { font-size: .54rem; color: var(--bp-dim); }
.slot .ref {
  font-size: .64rem; color: var(--bp-ink);
  border: 1px solid var(--bp-line); border-radius: 999px;
  padding: .02rem .42rem; min-width: 22px; text-align: center;
  background: var(--bp-bg); transition: transform .25s, color .25s, border-color .25s;
}
.slot .ref.bump { transform: scale(1.5); color: var(--bp-cyan); border-color: var(--bp-cyan); }
.slot.bump { box-shadow: var(--bp-glow); border-color: var(--bp-cyan); }
.slot.fresh { box-shadow: 0 0 16px rgba(167,139,250,.4); }
.slot .alloc {
  position: absolute; top: -9px; left: 8px;
  font-size: .52rem; color: var(--bp-bg); background: var(--bp-violet);
  border-radius: 999px; padding: .03rem .42rem; letter-spacing: .04em;
}

/* ---------- grid ---------- */
.grid-wrap { display: flex; flex-direction: column; min-width: 0; min-height: 0; }
.ghead { font-size: .58rem; letter-spacing: .08em; color: var(--bp-cyan); display: flex; justify-content: space-between; margin-bottom: .45rem; flex: 0 0 auto; }
.ghead .cap { color: var(--bp-dim); opacity: .7; }
.grid {
  position: relative;
  display: grid; gap: 4px;
  border: 1px dashed var(--bp-line); border-radius: 11px;
  padding: 8px; flex: 1 1 auto; min-height: 0; align-content: start;
  overflow: auto;
  background:
    linear-gradient(var(--bp-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--bp-grid) 1px, transparent 1px);
  background-size: 18px 18px;
}
.grid-empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: .7rem; color: var(--bp-dim); }
.tile {
  position: relative;
  aspect-ratio: 1; min-height: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; border-radius: 5px;
  border: 1px solid var(--bp-line);
}
.tile.mono  { color: var(--bp-cyan); background: rgba(34,211,238,.1);  border-color: rgba(34,211,238,.4); }
.tile.serif { color: var(--bp-bad);  background: rgba(251,113,133,.1); border-color: rgba(251,113,133,.45);
  font-family: Georgia, "Times New Roman", serif; font-style: italic; }
.tile.hit { box-shadow: 0 0 12px rgba(34,211,238,.45); }
.tile .slotno { position: absolute; bottom: 0; right: 1px; font-size: .42rem; color: var(--bp-dim); font-family: "Fira Code", monospace; font-style: normal; }

/* fly-in: tiles enter scaled/lifted, settle into the grid cell */
.tile-enter-from { opacity: 0; transform: translateY(-22px) scale(1.6); }
.tile-enter-active { transition: all .42s cubic-bezier(.2,.9,.3,1.2); }
.tile-leave-active { transition: all .25s; position: absolute; }
.tile-leave-to { opacity: 0; transform: scale(.6); }

/* shelf slot grow-in */
.slot-enter-from { opacity: 0; transform: translateY(10px) scale(.7); }
.slot-enter-active { transition: all .4s cubic-bezier(.2,.9,.3,1.2); }

.alloc-enter-from, .alloc-leave-to { opacity: 0; transform: translateY(4px); }
.alloc-enter-active, .alloc-leave-active { transition: all .25s; }

/* ---------- controls ---------- */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: flex-start; min-height: 0; overflow: auto; }
.kbd { display: flex; flex-wrap: wrap; gap: .4rem; }
.key {
  font-family: inherit; font-size: 1rem; width: 38px; height: 38px;
  border-radius: 8px; cursor: pointer; transition: all .15s;
}
.key.mono  { border: 1px solid var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.key.serif { border: 1px solid var(--bp-bad); color: var(--bp-bad); background: rgba(251,113,133,.08);
  font-family: Georgia, "Times New Roman", serif; font-style: italic; }
.key:hover { box-shadow: var(--bp-glow); transform: translateY(-1px); }
.key:active { transform: translateY(1px) scale(.95); }

.tog { display: inline-flex; align-items: center; gap: .55rem; cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: rgba(34,211,238,.4); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-cyan); transition: all .3s; }
.tog.serif .knob { background: rgba(251,113,133,.4); }
.tog.serif .knob::after { left: 16px; background: var(--bp-bad); }
.tog .tlabel { font-size: .74rem; color: var(--bp-dim); }
.tog .tlabel b { color: var(--bp-cyan); }
.tog.serif .tlabel b { color: var(--bp-bad); }

.btns { display: flex; gap: .45rem; }
.b { font-family: inherit; font-size: .74rem; padding: .42rem .7rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 7px; background: rgba(255,255,255,.03); cursor: pointer; }
.b:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.ghost { color: var(--bp-dim); }
.b.ghost:hover { border-color: var(--bp-bad); color: var(--bp-bad); }

.legend { display: flex; flex-direction: column; gap: .25rem; }
.leg { display: inline-flex; align-items: center; gap: .45rem; font-size: .66rem; color: var(--bp-dim); }
.leg i { width: 9px; height: 9px; border-radius: 3px; display: inline-block; }
.leg.miss i { background: var(--bp-violet); }
.leg.hit i { background: var(--bp-cyan); box-shadow: 0 0 8px rgba(34,211,238,.6); }

.kpts { margin-top: .15rem; }
.kpts b { color: var(--bp-cyan); }

.slots::-webkit-scrollbar { width: 5px; }
.slots::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
</style>
