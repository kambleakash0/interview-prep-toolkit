<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Node = 'view' | 'controller' | 'model'
type Hop = '' | 'input' | 'command' | 'notify'

const count = ref(0)
const active = ref<Node | ''>('')      // which node is currently pulsing
const hop = ref<Hop>('')               // which wire is currently lit
const showFlow = ref(true)
const busy = ref(false)
const autoLeft = ref(0)
const HOP_MS = 450
const timers: ReturnType<typeof setTimeout>[] = []

function later(fn: () => void, ms: number) { timers.push(setTimeout(fn, ms)) }
function clearAll() { timers.forEach(clearTimeout); timers.length = 0 }

// triangle layout on the 0..100 board — arrows form a one-way cycle
const POS: Record<Node, { x: number; y: number }> = {
  view: { x: 22, y: 30 },
  controller: { x: 78, y: 30 },
  model: { x: 50, y: 80 },
}

// one round-trip: View -> Controller -> Model -> View
function step() {
  if (busy.value) return
  busy.value = true
  active.value = 'view'
  hop.value = 'input'                       // View emits input token to Controller
  later(() => {
    active.value = 'controller'             // Controller.on_click -> handle
    hop.value = 'command'
    later(() => {
      active.value = 'model'                // Model mutate: count++
      count.value++
      hop.value = 'notify'
      later(() => {
        active.value = 'view'               // Model notifies View -> render
        hop.value = ''
        later(() => {
          active.value = ''
          busy.value = false
          if (autoLeft.value > 0) { autoLeft.value--; later(step, 240) }
        }, HOP_MS)
      }, HOP_MS)
    }, HOP_MS)
  }, HOP_MS)
}

function play() {
  if (busy.value || autoLeft.value > 0) return
  autoLeft.value = 2                         // this call + 2 queued = three round-trips
  step()
}

function reset() {
  clearAll()
  busy.value = false
  autoLeft.value = 0
  count.value = 0
  active.value = ''
  hop.value = ''
}

onUnmounted(clearAll)

const phaseLabel = computed(() => {
  if (hop.value === 'input') return 'View -> Controller : input'
  if (hop.value === 'command') return 'Controller -> Model : count++'
  if (hop.value === 'notify') return 'Model -> View : notify'
  if (active.value === 'view' && busy.value) return 'View : render(count)'
  return busy.value ? 'round-trip...' : 'idle'
})
const running = computed(() => busy.value || autoLeft.value > 0)
</script>

<template>
  <div class="mvc">
    <div class="stage">
      <div class="board">
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <marker id="mvc-arrow" viewBox="0 0 10 10" refX="8" refY="5"
                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M0,1 L9,5 L0,9 Z" />
            </marker>
          </defs>
          <!-- View -> Controller : input -->
          <line class="wire" :class="{ on: showFlow, hot: hop === 'input' }"
                :x1="POS.view.x" :y1="POS.view.y" :x2="POS.controller.x" :y2="POS.controller.y"
                :marker-end="showFlow ? 'url(#mvc-arrow)' : undefined" />
          <!-- Controller -> Model : command -->
          <line class="wire" :class="{ on: showFlow, hot: hop === 'command' }"
                :x1="POS.controller.x" :y1="POS.controller.y" :x2="POS.model.x" :y2="POS.model.y"
                :marker-end="showFlow ? 'url(#mvc-arrow)' : undefined" />
          <!-- Model -> View : notify -->
          <line class="wire" :class="{ on: showFlow, hot: hop === 'notify' }"
                :x1="POS.model.x" :y1="POS.model.y" :x2="POS.view.x" :y2="POS.view.y"
                :marker-end="showFlow ? 'url(#mvc-arrow)' : undefined" />
        </svg>

        <!-- wire labels (only when flow shown) -->
        <template v-if="showFlow">
          <span class="wlabel" :class="{ hot: hop === 'input' }" :style="{ left: '50%', top: '24%' }">input</span>
          <span class="wlabel" :class="{ hot: hop === 'command' }" :style="{ left: '69%', top: '57%' }">command</span>
          <span class="wlabel" :class="{ hot: hop === 'notify' }" :style="{ left: '31%', top: '57%' }">notify</span>
        </template>

        <div class="node view" :class="{ active: active === 'view' }"
             :style="{ left: POS.view.x + '%', top: POS.view.y + '%' }">
          <span class="nt">View</span>
          <span class="big">count = {{ count }}</span>
          <button class="plus" :disabled="running" @click="step">+1</button>
          <span class="st" :class="{ lit: active === 'view' && busy }">render()</span>
        </div>

        <div class="node controller" :class="{ active: active === 'controller' }"
             :style="{ left: POS.controller.x + '%', top: POS.controller.y + '%' }">
          <span class="nt">Controller</span>
          <span class="mid">on_click()</span>
          <span class="st" :class="{ lit: active === 'controller' }">handle</span>
        </div>

        <div class="node model" :class="{ active: active === 'model' }"
             :style="{ left: POS.model.x + '%', top: POS.model.y + '%' }">
          <span class="nt">Model</span>
          <span class="mid">count = {{ count }}</span>
          <span class="st" :class="{ lit: active === 'model' }">mutate: count++</span>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="btns">
        <button class="b" :disabled="running" @click="step">▸ Step (+1)</button>
        <button class="b ghost" :disabled="running" @click="play">▶ Play x3</button>
      </div>
      <button class="b ghost reset" @click="reset">↻ reset</button>
      <label class="tog" :class="{ on: showFlow }" @click="showFlow = !showFlow">
        <span class="knob" /> show data flow
      </label>

      <div class="phase">
        <span class="plabel">phase</span>
        <span class="pval" :class="{ live: busy }">{{ phaseLabel }}</span>
      </div>

      <ul class="kpts">
        <li>Input flows one way: Controller → Model → View</li>
        <li>Model mutates and notifies; View only renders</li>
        <li>Each part owns one job — never reaches into the others</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.mvc { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.stage { min-width: 0; display: flex; }
.board { position: relative; width: 100%; height: 100%; padding: 8px 64px; box-sizing: border-box; }

.wires { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.wire { stroke: var(--bp-line); stroke-width: .4; fill: none; opacity: .35; transition: stroke .3s, opacity .3s, stroke-width .3s; }
.wire.on { opacity: 1; stroke: var(--bp-line); stroke-width: .55; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: 1; opacity: 1; filter: drop-shadow(0 0 3px var(--bp-cyan)); animation: pulseDash 1s linear; }
.wires :deep(#mvc-arrow path) { fill: var(--bp-line); transition: fill .3s; }
@keyframes pulseDash { 0% { opacity: .4; } 50% { opacity: 1; } 100% { opacity: .4; } }

.wlabel { position: absolute; transform: translate(-50%, -50%); font-size: .56rem; letter-spacing: .08em; color: var(--bp-dim); background: var(--bp-bg); padding: 0 .25rem; border-radius: 4px; transition: color .3s; pointer-events: none; white-space: nowrap; }
.wlabel.hot { color: var(--bp-cyan); }

.node { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; gap: .18rem; padding: .5rem .7rem; min-width: 116px; border-radius: 10px; border: 1px solid var(--bp-line); background: rgba(11,19,36,.94); white-space: nowrap; transition: border-color .3s, box-shadow .3s, transform .3s; }
.node .nt { font-size: .56rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.node .big { font-size: .92rem; color: #fff; }
.node .mid { font-size: .76rem; color: var(--bp-ink); }
.node .st { font-size: .56rem; color: var(--bp-dim); transition: color .3s; }
.node .st.lit { color: var(--bp-cyan); }

.node.view { border-color: var(--bp-cyan); }
.node.controller { border-color: var(--bp-violet); }
.node.model { border-color: var(--bp-blue); }
.node.active { box-shadow: var(--bp-glow); transform: translate(-50%, -50%) scale(1.06); }
.node.view.active { border-color: var(--bp-cyan); }
.node.controller.active { border-color: var(--bp-violet); box-shadow: 0 0 22px rgba(167,139,250,.45); }
.node.model.active { border-color: var(--bp-blue); }

.plus { font-family: inherit; font-size: .72rem; margin: .12rem 0; padding: .18rem .7rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 7px; background: rgba(34,211,238,.1); cursor: pointer; transition: background .2s, opacity .2s; }
.plus:disabled { opacity: .45; cursor: not-allowed; }
.plus:not(:disabled):hover { background: rgba(34,211,238,.2); }

.panel { display: flex; flex-direction: column; gap: .7rem; min-width: 0; }
.btns { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .78rem; padding: .44rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); transition: opacity .2s; }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.b.reset { width: fit-content; }
.b:disabled { opacity: .45; cursor: not-allowed; box-shadow: none; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; color: var(--bp-dim); cursor: pointer; user-select: none; width: fit-content; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: left .3s, background .3s; }
.tog.on .knob { background: rgba(34,211,238,.4); }
.tog.on .knob::after { left: 16px; background: var(--bp-cyan); }
.tog.on { color: var(--bp-cyan); }

.phase { display: flex; flex-direction: column; gap: .15rem; padding: .45rem .65rem; border: 1px solid var(--bp-line); border-radius: 8px; background: rgba(255,255,255,.02); }
.plabel { font-size: .54rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.pval { font-size: .74rem; color: var(--bp-ink); transition: color .3s; }
.pval.live { color: var(--bp-cyan); }

.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .28rem 0; font-size: .72rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
