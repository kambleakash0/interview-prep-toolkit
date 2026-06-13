<script setup lang="ts">
import { ref, computed } from 'vue'

const mode = ref<'direct' | 'facade'>('direct')
const watermark = ref(false)
const subState = ref<string[]>(['idle', 'idle', 'idle'])
const facadeState = ref<'idle' | 'running' | 'done'>('idle')
const fanning = ref(false)
const flashNew = ref(false)
let busy = false
const timers: ReturnType<typeof setTimeout>[] = []

const SUBS = computed(() => watermark.value
  ? ['Encoder', 'Subtitler', 'Uploader', 'Watermark']
  : ['Encoder', 'Subtitler', 'Uploader'])
const ys = computed(() => {
  const n = SUBS.value.length
  return SUBS.value.map((_, i) => (n === 1 ? 50 : 16 + i * (68 / (n - 1))))
})
const coupling = computed(() => (mode.value === 'direct' ? SUBS.value.length : 1))

const CLIENT = { x: 12, y: 50 }
const FACADE = { x: 45, y: 50 }
const SUBX = 80

function later(fn: () => void, ms: number) { timers.push(setTimeout(fn, ms)) }
function clearAll() { timers.forEach(clearTimeout); timers.length = 0 }

function resetStates() {
  subState.value = SUBS.value.map(() => 'idle')
  facadeState.value = 'idle'
  fanning.value = false
}
function runSubs(onDone: () => void) {
  const n = SUBS.value.length
  let i = 0
  const tick = () => {
    subState.value[i] = 'running'
    later(() => {
      subState.value[i] = 'done'
      i++
      if (i < n) later(tick, 160)
      else onDone()
    }, 340)
  }
  tick()
}
function publish() {
  if (busy) return
  busy = true
  clearAll(); resetStates()
  if (mode.value === 'direct') {
    runSubs(() => { busy = false })
  } else {
    facadeState.value = 'running'
    later(() => {
      fanning.value = true
      runSubs(() => { facadeState.value = 'done'; busy = false })
    }, 520)
  }
}
function setMode(m: 'direct' | 'facade') { if (busy) return; mode.value = m; clearAll(); resetStates() }
function toggleWatermark() {
  if (busy) return
  watermark.value = !watermark.value
  clearAll(); resetStates()
  if (watermark.value) { flashNew.value = true; later(() => { flashNew.value = false }, 900) }
}
function reset() { clearAll(); busy = false; resetStates() }

const lastIdx = computed(() => SUBS.value.length - 1)
function subHot(i: number) {
  if (mode.value === 'direct') return subState.value[i] === 'running'
  return fanning.value && subState.value[i] === 'running'
}
const clientFacadeHot = computed(() => mode.value === 'facade' && facadeState.value === 'running' && !fanning.value)
</script>

<template>
  <div class="fc">
    <div class="stage">
      <div class="board">
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <template v-if="mode === 'direct'">
            <line v-for="(y, i) in ys" :key="'d' + i"
                  :x1="CLIENT.x" :y1="CLIENT.y" :x2="SUBX" :y2="y"
                  class="wire" :class="{ hot: subHot(i), flash: flashNew && i === lastIdx, red: flashNew && i === lastIdx }" />
          </template>
          <template v-else>
            <line :x1="CLIENT.x" :y1="CLIENT.y" :x2="FACADE.x" :y2="FACADE.y" class="wire" :class="{ hot: clientFacadeHot }" />
            <line v-for="(y, i) in ys" :key="'f' + i"
                  :x1="FACADE.x" :y1="FACADE.y" :x2="SUBX" :y2="y"
                  class="wire" :class="{ hot: subHot(i), flash: flashNew && i === lastIdx, green: flashNew && i === lastIdx }" />
          </template>
        </svg>

        <div class="node client" :style="{ left: CLIENT.x + '%', top: CLIENT.y + '%' }">
          <span class="nt">Client</span><span class="nm">publish()</span>
        </div>
        <div v-if="mode === 'facade'" class="node facade" :class="facadeState"
             :style="{ left: FACADE.x + '%', top: FACADE.y + '%' }">
          <span class="nt">Facade</span><span class="st">{{ facadeState }}</span>
        </div>
        <div v-for="(s, i) in SUBS" :key="s" class="node sub" :class="subState[i]"
             :style="{ left: SUBX + '%', top: ys[i] + '%' }">
          <span class="nm">{{ s }}</span><span class="st">{{ subState[i] }}</span>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="seg">
        <button :class="{ on: mode === 'direct' }" @click="setMode('direct')">Direct</button>
        <button :class="{ on: mode === 'facade' }" @click="setMode('facade')">Facade</button>
      </div>
      <div class="btns">
        <button class="b" @click="publish">▶ Publish</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>
      <label class="tog" :class="{ on: watermark }" @click="toggleWatermark"><span class="knob" /> add Watermark step</label>
      <div class="coupling" :class="mode">
        Client coupling <b>{{ coupling }}</b>
        <span class="cn">{{ mode === 'direct' ? 'one wire per subsystem' : 'one wire, period' }}</span>
      </div>
      <ul class="kpts">
        <li>Direct: client wires to every subsystem — coupling grows</li>
        <li>Facade: one entry point fans out for you — coupling = 1</li>
        <li>Add a step: every direct caller rewires; the facade hides it</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.fc { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.stage { min-width: 0; }
.board { position: relative; width: 100%; height: 300px; }
.wires { position: absolute; inset: 0; width: 100%; height: 100%; }
.wire { stroke: var(--bp-line); stroke-width: .5; transition: stroke .3s, opacity .3s; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: .9; filter: drop-shadow(0 0 3px var(--bp-cyan)); }
.wire.flash.red { stroke: var(--bp-bad); stroke-width: 1; animation: fl .9s ease; }
.wire.flash.green { stroke: var(--bp-good); stroke-width: 1; animation: fl .9s ease; }
@keyframes fl { 0%,100% { opacity: 1; } 50% { opacity: .25; } }
.node { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; gap: .1rem; padding: .4rem .65rem; border-radius: 9px; border: 1px solid var(--bp-line); background: rgba(11,19,36,.92); white-space: nowrap; transition: all .3s; }
.node .nt { font-size: .56rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }
.node .nm { font-size: .76rem; color: var(--bp-ink); }
.node .st { font-size: .56rem; color: var(--bp-dim); }
.node.client { border-color: var(--bp-violet); }
.node.facade { border-color: var(--bp-cyan); }
.node.facade.running { box-shadow: var(--bp-glow); }
.node.facade.done { border-color: var(--bp-good); }
.node.sub.running { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.node.sub.running .st { color: var(--bp-cyan); }
.node.sub.done { border-color: var(--bp-good); }
.node.sub.done .st { color: var(--bp-good); }
.panel { display: flex; flex-direction: column; gap: .7rem; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; width: fit-content; }
.seg button { font-family: inherit; font-size: .76rem; padding: .4rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.btns { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .78rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(34,211,238,.4); } .tog.on .knob::after { left: 16px; background: var(--bp-cyan); }
.tog.on { color: var(--bp-cyan); }
.coupling { font-size: .76rem; color: var(--bp-dim); padding: .45rem .65rem; border: 1px solid var(--bp-line); border-radius: 8px; }
.coupling b { font-size: 1rem; color: var(--bp-bad); margin: 0 .2rem; }
.coupling.facade b { color: var(--bp-good); }
.coupling .cn { display: block; font-size: .58rem; opacity: .8; }
.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .28rem 0; font-size: .74rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
