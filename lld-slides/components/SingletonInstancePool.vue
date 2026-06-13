<script setup lang="ts">
import { ref } from 'vue'

const built = ref(0)
const created = ref(false)
const badge = ref('')      // 'new' | 'reused'
const fly = ref('')        // 'A' | 'B' | 'AB' — which lane(s) fired
const lockOn = ref(true)
const waiting = ref(false)
const race = ref(false)
let busy = false

function flash(b: string) {
  badge.value = b
  setTimeout(() => { if (badge.value === b) badge.value = '' }, 750)
}
function arrow(l: string) { fly.value = l; setTimeout(() => { fly.value = '' }, 600) }

function get(lane: 'A' | 'B') {
  if (busy) return
  arrow(lane)
  if (!created.value) { created.value = true; built.value = 1; flash('new') }
  else flash('reused')
}

function doRace() {
  if (busy) return
  busy = true
  reset()
  arrow('AB')
  if (lockOn.value) {
    created.value = true; built.value = 1; flash('new')
    waiting.value = true
    setTimeout(() => { waiting.value = false; flash('reused'); busy = false }, 950)
  } else {
    created.value = true; built.value = 2; race.value = true
    setTimeout(() => { busy = false }, 350)
  }
}

function reset() { built.value = 0; created.value = false; badge.value = ''; waiting.value = false; race.value = false }
</script>

<template>
  <div class="sg">
    <div class="stage">
      <div class="lanes">
        <div class="lane" :class="{ fire: fly === 'A' || fly === 'AB' }">
          <span class="who">Client A</span>
          <button class="call" @click="get('A')">get_instance()</button>
        </div>
        <div class="lane" :class="{ fire: fly === 'B' || fly === 'AB', wait: waiting }">
          <span class="who">Client B</span>
          <button class="call" @click="get('B')">get_instance()</button>
          <span v-if="waiting" class="spin">waiting…</span>
        </div>
      </div>

      <div class="rail"><span class="dot" :class="{ go: fly }" /></div>

      <div class="mid">
        <div class="counter">objects built: <b :class="{ bad: built > 1 }">{{ built }}</b></div>
        <div class="slot" :class="{ on: created, race }">
          <template v-if="created">
            <span class="id">#42</span>
            <span class="vals">values={}</span>
          </template>
          <span v-else class="empty">EMPTY</span>
          <span v-if="lockOn && busy && waiting" class="lock">lock held</span>
          <transition name="pop"><span v-if="badge" class="tag" :class="badge">{{ badge }}</span></transition>
        </div>
        <div v-if="race" class="warn">DATA RACE — two objects built</div>
      </div>
    </div>

    <div class="panel">
      <button class="b" @click="doRace">▶ race A + B</button>
      <label class="tog" :class="{ on: lockOn }" @click="lockOn = !lockOn">
        <span class="knob" /> lock {{ lockOn ? 'ON' : 'OFF' }}
      </label>
      <button class="b ghost" @click="reset">reset</button>
      <ul class="kpts bp-dim text-sm">
        <li>First call builds; the rest reuse the same object</li>
        <li>Lock + re-check stops two threads racing to build two</li>
        <li>Turn the lock off, then race — watch the count hit 2</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.sg { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; font-family: "Fira Code", monospace; }
.stage { display: grid; grid-template-columns: auto 60px 1fr; align-items: center; gap: 0; }
.lanes { display: flex; flex-direction: column; gap: 1.4rem; }
.lane { display: flex; flex-direction: column; gap: .4rem; padding: .7rem .8rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.02); transition: all .3s; position: relative; }
.lane.fire { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.lane.wait { opacity: .6; }
.who { color: var(--bp-ink); font-size: .82rem; }
.call { font-family: inherit; font-size: .7rem; padding: .35rem .5rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 7px; background: rgba(34,211,238,.08); cursor: pointer; }
.spin { font-size: .62rem; color: var(--bp-warn); }
.rail { position: relative; height: 2px; background: var(--bp-line); align-self: center; }
.dot { position: absolute; top: -3px; left: 0; width: 8px; height: 8px; border-radius: 999px; background: var(--bp-cyan); opacity: 0; box-shadow: var(--bp-glow); }
.dot.go { animation: travel .6s ease forwards; }
@keyframes travel { from { left: 0; opacity: 1; } to { left: 100%; opacity: 0; } }
.mid { display: flex; flex-direction: column; align-items: center; gap: .5rem; }
.counter { font-size: .74rem; color: var(--bp-dim); }
.counter b { color: var(--bp-cyan); } .counter b.bad { color: var(--bp-bad); }
.slot { position: relative; width: 150px; height: 90px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .2rem; border: 1px dashed var(--bp-line); border-radius: 12px; color: var(--bp-dim); transition: all .3s; }
.slot.on { border-style: solid; border-color: var(--bp-cyan); background: rgba(34,211,238,.1); color: #fff; box-shadow: var(--bp-glow); }
.slot.race { border-color: var(--bp-bad); box-shadow: 0 0 18px rgba(251,113,133,.5); }
.id { font-size: 1.05rem; color: var(--bp-cyan); } .vals { font-size: .68rem; color: var(--bp-dim); }
.empty { font-size: .8rem; letter-spacing: .1em; }
.lock { position: absolute; top: -10px; font-size: .58rem; color: var(--bp-warn); border: 1px solid var(--bp-warn); border-radius: 999px; padding: .05rem .4rem; background: var(--bp-bg); }
.tag { position: absolute; bottom: -12px; right: -8px; font-size: .58rem; padding: .1rem .45rem; border-radius: 999px; }
.tag.new { color: var(--bp-bg); background: var(--bp-cyan); }
.tag.reused { color: var(--bp-cyan); border: 1px solid var(--bp-cyan); background: var(--bp-bg); }
.warn { font-size: .66rem; color: var(--bp-bad); }
.pop-enter-active { transition: all .25s; } .pop-enter-from { opacity: 0; transform: scale(.6); }
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: flex-start; }
.b { font-family: inherit; font-size: .8rem; padding: .45rem .85rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .76rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(34,211,238,.4); } .tog.on .knob::after { left: 16px; background: var(--bp-cyan); }
.tog.on { color: var(--bp-cyan); }
.kpts { margin-top: .3rem; }
</style>
