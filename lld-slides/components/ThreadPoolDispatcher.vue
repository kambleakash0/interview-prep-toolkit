<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

const N = 3
const RUN_MS = 700

type Chip = { id: number }
type Worker = { task: Chip | null; progress: number; running: boolean }

const queue = ref<Chip[]>([])
const workers = ref<Worker[]>(
  Array.from({ length: N }, () => ({ task: null, progress: 0, running: false }))
)
const done = ref<Chip[]>([])
const playing = ref(false)

let seq = 0
let loop: ReturnType<typeof setInterval> | null = null
const workerTimers: (ReturnType<typeof setTimeout> | null)[] = Array(N).fill(null)
const rampTimers: (ReturnType<typeof setTimeout> | null)[] = Array(N).fill(null)

const queued = computed(() => queue.value.length)
const running = computed(() => workers.value.filter(w => w.running).length)
const completed = computed(() => done.value.length)
const idleWorkers = computed(() => N - running.value)

function enqueue(count: number) {
  for (let i = 0; i < count; i++) queue.value.push({ id: ++seq })
}

// Try to feed every idle worker from the front of the queue once.
function dispatch() {
  for (let i = 0; i < N; i++) {
    const w = workers.value[i]
    if (w.running || queue.value.length === 0) continue
    const chip = queue.value.shift()!
    startWorker(i, chip)
  }
}

function startWorker(i: number, chip: Chip) {
  const w = workers.value[i]
  w.task = chip
  w.running = true
  w.progress = 0
  // guard before scheduling: a stale timer from a fast reset must never fire
  if (rampTimers[i]) { clearTimeout(rampTimers[i]!); rampTimers[i] = null }
  if (workerTimers[i]) { clearTimeout(workerTimers[i]!); workerTimers[i] = null }
  // next frame: ramp the CSS-transitioned bar to full so it visibly drains over RUN_MS
  rampTimers[i] = setTimeout(() => {
    rampTimers[i] = null
    const cur = workers.value[i]
    if (cur && cur.running) cur.progress = 100
  }, 30)
  workerTimers[i] = setTimeout(() => finishWorker(i), RUN_MS)
}

function finishWorker(i: number) {
  const w = workers.value[i]
  if (rampTimers[i]) { clearTimeout(rampTimers[i]!); rampTimers[i] = null }
  workerTimers[i] = null
  if (!w || !w.running) return
  if (w.task) done.value.push(w.task)
  w.task = null
  w.running = false
  w.progress = 0
  // a freed worker immediately tries to grab the next queued chip when playing
  if (playing.value) dispatch()
}

function step() {
  // one manual pull pass: hand the front chips to any idle workers
  dispatch()
}

function play() {
  if (playing.value) return
  playing.value = true
  dispatch()
  loop = setInterval(dispatch, 120)
}

function pause() {
  playing.value = false
  if (loop) { clearInterval(loop); loop = null }
}

function togglePlay() {
  if (playing.value) pause()
  else play()
}

function clearTimers() {
  pause()
  for (let i = 0; i < N; i++) {
    if (workerTimers[i]) { clearTimeout(workerTimers[i]!); workerTimers[i] = null }
    if (rampTimers[i]) { clearTimeout(rampTimers[i]!); rampTimers[i] = null }
  }
}

function reset() {
  clearTimers()
  seq = 0
  queue.value = []
  done.value = []
  workers.value = Array.from({ length: N }, () => ({ task: null, progress: 0, running: false }))
}

onUnmounted(clearTimers)

// queue chips shown; cap the visible row so it never overflows the column
const visibleQueue = computed(() => queue.value.slice(0, 6))
const overflow = computed(() => Math.max(0, queue.value.length - 6))
const visibleDone = computed(() => done.value.slice(-5))
const doneOverflow = computed(() => Math.max(0, done.value.length - 5))
</script>

<template>
  <div class="tp">
    <div class="stage">
      <div class="board">
        <!-- percent-coordinate wires: queue -> each worker -> done -->
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <line v-for="i in N" :key="'qw' + i"
                :x1="20" :y1="50" :x2="46" :y2="18 + (i - 1) * 32"
                class="wire" :class="{ hot: workers[i - 1].running }" />
          <line v-for="i in N" :key="'wd' + i"
                :x1="74" :y1="18 + (i - 1) * 32" :x2="92" :y2="50"
                class="wire" :class="{ hot: workers[i - 1].running }" />
        </svg>

        <!-- TASK QUEUE -->
        <div class="col queue">
          <div class="ch">Task queue <span class="fifo">FIFO</span></div>
          <div class="qbody">
            <transition-group name="slide" tag="div" class="qstack">
              <div v-for="c in visibleQueue" :key="c.id" class="chip q">T{{ c.id }}</div>
            </transition-group>
            <div v-if="overflow" class="more">+{{ overflow }} waiting</div>
            <div v-if="!queue.length" class="ghost">empty</div>
          </div>
        </div>

        <!-- WORKER POOL -->
        <div v-for="i in N" :key="'w' + i" class="worker"
             :class="{ run: workers[i - 1].running }"
             :style="{ top: (18 + (i - 1) * 32) + '%' }">
          <span class="wlabel">Worker {{ i }}</span>
          <div class="slot" :class="{ busy: workers[i - 1].running }">
            <span v-if="workers[i - 1].task" class="chip w">T{{ workers[i - 1].task!.id }}</span>
            <span v-else class="idle">idle</span>
          </div>
          <div class="bar"><span class="fill" :style="{ width: workers[i - 1].progress + '%' }" /></div>
        </div>

        <!-- DONE TRAY -->
        <div class="col done">
          <div class="ch good">Done</div>
          <div class="dbody">
            <transition-group name="pop" tag="div" class="dstack">
              <div v-for="c in visibleDone" :key="c.id" class="chip d">T{{ c.id }}</div>
            </transition-group>
            <div v-if="doneOverflow" class="more">+{{ doneOverflow }} earlier</div>
            <div v-if="!done.length" class="ghost">empty</div>
          </div>
        </div>
      </div>

      <div class="counters">
        <span class="kpi">queued <b>{{ queued }}</b></span>
        <span class="kpi">running <b :class="{ cap: running === N }">{{ running }}</b><i>/{{ N }}</i></span>
        <span class="kpi">done <b class="g">{{ completed }}</b></span>
      </div>
    </div>

    <div class="panel">
      <div class="btns">
        <button class="b" @click="enqueue(1)">+ submit task</button>
        <button class="b" @click="enqueue(5)">+ submit 5</button>
      </div>
      <div class="btns">
        <button class="b play" :class="{ on: playing }" @click="togglePlay">
          {{ playing ? '▮▮ pause' : '▶ play' }}
        </button>
        <button class="b" :disabled="playing || !queued || !idleWorkers" @click="step">▸ step</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>
      <div class="conc" :class="{ full: running === N }">
        concurrency <b>{{ running }}</b> / {{ N }}
        <span class="cn">{{ running === N ? 'pool saturated — overflow waits in queue' : 'idle workers will pull next' }}</span>
      </div>
      <ul class="kpts">
        <li>Fixed crew of {{ N }} pulls from one shared queue</li>
        <li>At most {{ N }} run at once — extra tasks wait in line</li>
        <li>Threads are reused, not spawned per task</li>
        <li>Submit a burst, hit play, watch back-pressure build</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.tp { display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.stage { min-width: 0; display: flex; flex-direction: column; gap: .5rem; }
.board { position: relative; width: 100%; height: 296px; }
.wires { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.wire { stroke: var(--bp-line); stroke-width: .5; transition: stroke .3s, opacity .3s; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: .9; filter: drop-shadow(0 0 3px var(--bp-cyan)); }

/* columns */
.col { position: absolute; top: 4%; width: 18%; min-width: 86px; display: flex; flex-direction: column; gap: .35rem; }
.col.queue { left: 0; }
.col.done { right: 0; }
.ch { font-size: .58rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); display: flex; align-items: center; gap: .3rem; }
.ch.good { color: var(--bp-good); }
.fifo { font-size: .48rem; border: 1px solid var(--bp-line); border-radius: 999px; padding: .02rem .3rem; color: var(--bp-dim); }
.qbody, .dbody { border: 1px dashed var(--bp-line); border-radius: 10px; padding: .35rem; min-height: 224px; box-sizing: border-box; background: rgba(255,255,255,.02); position: relative; }
.qstack, .dstack { display: flex; flex-direction: column; gap: .3rem; }
.ghost { font-size: .6rem; color: var(--bp-dim); opacity: .5; letter-spacing: .08em; text-align: center; margin-top: .5rem; }
.more { font-size: .54rem; color: var(--bp-warn); margin-top: .25rem; text-align: center; }

/* chips */
.chip { font-size: .66rem; padding: .2rem .35rem; border-radius: 7px; border: 1px solid var(--bp-line); text-align: center; background: rgba(11,19,36,.92); transition: border-color .3s, background .3s, color .3s; }
.chip.q { color: var(--bp-ink); border-color: rgba(56,189,248,.3); }
.chip.w { color: var(--bp-cyan); border-color: var(--bp-cyan); background: rgba(34,211,238,.12); }
.chip.d { color: var(--bp-good); border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.07); }

/* workers */
.worker { position: absolute; left: 50%; transform: translate(-50%, -50%); width: 30%; min-width: 124px; max-width: 168px; display: flex; flex-direction: column; gap: .24rem; padding: .4rem .5rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(11,19,36,.92); box-sizing: border-box; transition: border-color .3s, box-shadow .3s; }
.worker.run { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.wlabel { font-size: .54rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }
.slot { height: 24px; display: flex; align-items: center; justify-content: center; border: 1px dashed var(--bp-line); border-radius: 7px; transition: border-color .3s, border-style .3s; }
.slot.busy { border-style: solid; border-color: var(--bp-cyan); }
.idle { font-size: .6rem; color: var(--bp-dim); opacity: .6; letter-spacing: .08em; }
.bar { height: 5px; border-radius: 999px; background: var(--bp-line); overflow: hidden; }
.fill { display: block; height: 100%; background: linear-gradient(90deg, var(--bp-cyan), var(--bp-blue)); border-radius: 999px; transition: width .7s linear; box-shadow: 0 0 6px rgba(34,211,238,.6); }

/* counters */
.counters { display: flex; gap: 1.1rem; padding: .1rem .1rem; }
.kpi { font-size: .7rem; color: var(--bp-dim); }
.kpi b { color: var(--bp-cyan); font-size: .9rem; margin-left: .25rem; }
.kpi b.g { color: var(--bp-good); }
.kpi b.cap { color: var(--bp-warn); }
.kpi i { font-style: normal; color: var(--bp-dim); font-size: .66rem; }

/* panel */
.panel { display: flex; flex-direction: column; gap: .6rem; min-width: 0; }
.btns { display: flex; gap: .5rem; flex-wrap: wrap; }
.b { font-family: inherit; font-size: .72rem; padding: .42rem .7rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); transition: all .2s; }
.b:hover:not(:disabled) { background: rgba(34,211,238,.2); }
.b.play.on { border-color: var(--bp-warn); color: var(--bp-warn); background: rgba(251,191,36,.12); box-shadow: 0 0 16px rgba(251,191,36,.3); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.conc { font-size: .72rem; color: var(--bp-dim); padding: .45rem .65rem; border: 1px solid var(--bp-line); border-radius: 8px; transition: border-color .3s; }
.conc b { font-size: 1rem; color: var(--bp-cyan); margin: 0 .2rem; }
.conc.full { border-color: rgba(251,191,36,.4); }
.conc.full b { color: var(--bp-warn); }
.conc .cn { display: block; font-size: .56rem; opacity: .85; margin-top: .15rem; }
.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .22rem 0; font-size: .68rem; line-height: 1.34; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }

/* transitions */
.slide-enter-active, .slide-leave-active { transition: all .3s ease; }
.slide-enter-from { opacity: 0; transform: translateX(-14px); }
.slide-leave-to { opacity: 0; transform: translateX(16px); }
.pop-enter-active { transition: all .3s ease; }
.pop-enter-from { opacity: 0; transform: scale(.6); }
</style>
