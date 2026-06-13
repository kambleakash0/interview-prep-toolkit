<script setup lang="ts">
import { ref } from 'vue'

const MSGS = ['job started', 'summing 0..4', 'job done -> 10']
const mode = ref<'real' | 'null'>('real')
const step = ref(0)            // calls made (0..3)
const console_ = ref<string[]>([])
const flying = ref(false)
const pulse = ref(false)
let busy = false
let timer: ReturnType<typeof setInterval> | null = null
const pending: ReturnType<typeof setTimeout>[] = []

function later(fn: () => void, ms: number) { pending.push(setTimeout(fn, ms)) }

function fire() {
  if (busy || step.value >= MSGS.length) return false
  busy = true
  const msg = MSGS[step.value]
  flying.value = true
  later(() => {                       // token reaches the slot
    flying.value = false
    pulse.value = true
    if (mode.value === 'real') console_.value.push(`[LOG] ${msg}`)
    later(() => { pulse.value = false }, 260)
    step.value++
    busy = false
  }, 600)
  return true
}

function play() {
  reset()
  timer = setInterval(() => {
    if (!fire() && step.value >= MSGS.length) { if (timer) clearInterval(timer); timer = null }
  }, 900)
}
function reset() {
  if (timer) { clearInterval(timer); timer = null }
  pending.forEach(clearTimeout); pending.length = 0
  busy = false; step.value = 0; console_.value = []; flying.value = false; pulse.value = false
}
function setMode(m: 'real' | 'null') { mode.value = m }   // keeps step index
</script>

<template>
  <div class="no">
    <div class="stage">
      <div class="flow">
        <!-- frozen client -->
        <div class="client">
          <div class="tag">CLIENT</div>
          <code>logger.log(msg)</code>
          <div class="frozen">never edited</div>
        </div>

        <!-- arrow + travelling token -->
        <div class="arrow">
          <span class="line" />
          <span class="head" />
          <span v-if="flying" class="token" :class="mode" />
        </div>

        <!-- swappable dependency slot -->
        <div class="slot" :class="[mode, { pulse }]">
          <div class="tag">{{ mode === 'real' ? 'ConsoleLogger' : 'NullLogger' }}</div>
          <code>{{ mode === 'real' ? 'print(f"[LOG] {msg}")' : 'pass' }}</code>
          <div class="body">{{ mode === 'real' ? 'visible side effect' : 'no-op' }}</div>
        </div>
      </div>

      <!-- output console -->
      <div class="console">
        <div class="ctitle">Output console</div>
        <div class="lines">
          <div v-for="(l, i) in console_" :key="i" class="logline">{{ l }}</div>
          <div v-if="!console_.length" class="empty">(empty)</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="seg">
        <button :class="{ on: mode === 'real' }" @click="setMode('real')">REAL</button>
        <button :class="{ on: mode === 'null' }" @click="setMode('null')">NULL</button>
      </div>
      <div class="btns">
        <button class="b" @click="fire">▸ step</button>
        <button class="b alt" @click="play">▶ play</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>
      <div class="badges">
        <span class="badge zero">null checks written: <b>0</b></span>
        <span class="badge">calls made: <b>{{ step }}</b></span>
      </div>
      <ul class="kpts">
        <li>Same call site for both objects — never an <code>if x is None</code></li>
        <li>REAL logs; NULL quietly does nothing</li>
        <li>Absence of behavior is still a behavior</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.no { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; align-content: start; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.stage { display: flex; flex-direction: column; gap: .8rem; min-width: 0; }
.flow { display: grid; grid-template-columns: 1fr 70px 1fr; align-items: center; }
.client, .slot { display: flex; flex-direction: column; gap: .25rem; padding: .7rem .85rem; border: 1px solid var(--bp-line); border-radius: 11px; background: rgba(255,255,255,.02); transition: all .3s; }
.tag { font-size: .58rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }
.client code, .slot code { font-size: .74rem; color: var(--bp-ink); }
.frozen { font-size: .58rem; color: var(--bp-dim); }
.body { font-size: .58rem; color: var(--bp-dim); }
.slot.real { border-color: rgba(34,211,238,.45); }
.slot.null { border-color: var(--bp-line); opacity: .92; }
.slot.real code { color: var(--bp-cyan); }
.slot.null code { color: var(--bp-dim); }
.slot.pulse.real { box-shadow: var(--bp-glow); transform: scale(1.04); }
.slot.pulse.null { box-shadow: 0 0 12px rgba(138,160,192,.25); transform: scale(1.02); }
.arrow { position: relative; height: 2px; }
.line { position: absolute; top: 50%; left: 0; right: 6px; height: 1.5px; background: var(--bp-line); }
.head { position: absolute; top: 50%; right: 0; transform: translateY(-50%); width: 0; height: 0; border: 5px solid transparent; border-left-color: var(--bp-line); }
.token { position: absolute; top: 50%; width: 9px; height: 9px; border-radius: 999px; transform: translateY(-50%); animation: glide .6s ease forwards; }
.token.real { background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.token.null { background: var(--bp-dim); animation: glidefade .6s ease forwards; }
@keyframes glide { from { left: 0; } to { left: calc(100% - 9px); } }
@keyframes glidefade { 0% { left: 0; opacity: 1; } 80% { opacity: 1; } 100% { left: calc(100% - 9px); opacity: 0; } }
.console { border: 1px solid var(--bp-line); border-radius: 10px; background: var(--bp-bg); padding: .55rem .7rem; height: 132px; display: flex; flex-direction: column; gap: .3rem; }
.ctitle { font-size: .58rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }
.lines { flex: 1; overflow: auto; display: flex; flex-direction: column; gap: .15rem; }
.logline { font-size: .72rem; color: var(--bp-good); }
.empty { font-size: .7rem; color: var(--bp-dim); opacity: .5; }
.panel { display: flex; flex-direction: column; gap: .8rem; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; width: fit-content; }
.seg button { font-family: inherit; font-size: .76rem; padding: .4rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.btns { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .78rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); cursor: pointer; }
.b.alt { color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
.badges { display: flex; flex-wrap: wrap; gap: .5rem; }
.badge { font-size: .66rem; padding: .2rem .55rem; border: 1px solid var(--bp-line); border-radius: 999px; color: var(--bp-dim); }
.badge b { color: var(--bp-ink); }
.badge.zero { border-color: rgba(74,222,128,.3); color: var(--bp-good); }
.badge.zero b { color: var(--bp-good); }
.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .3rem 0; font-size: .76rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
.kpts code { font-size: .7rem; color: var(--bp-ink); }
</style>
