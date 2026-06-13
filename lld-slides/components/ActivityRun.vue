<script setup lang="ts">
import { ref } from 'vue'

// flow: start -> login -> [valid?] -> yes: dashboard -> end
//                                   -> no:  error -> back to login
const path = ref<'none' | 'valid' | 'invalid'>('none')
const at = ref<string>('')        // currently-lit node id
let running = false

const SEQ = {
  valid:   ['start', 'login', 'check', 'dashboard', 'end'],
  invalid: ['start', 'login', 'check', 'error', 'login'],
}

function run(kind: 'valid' | 'invalid') {
  if (running) return
  running = true
  path.value = kind
  const seq = SEQ[kind]
  let i = 0
  const tick = () => {
    at.value = seq[i]
    if (i < seq.length - 1) { i++; setTimeout(tick, 620) }
    else { setTimeout(() => { at.value = ''; running = false }, 700) }
  }
  tick()
}
function reset() { running = false; path.value = 'none'; at.value = '' }
const lit = (id: string) => at.value === id
</script>

<template>
  <div class="ac">
    <div class="flow">
      <div class="node start" :class="{ on: lit('start') }">● start</div>
      <div class="edge" />
      <div class="node act" :class="{ on: lit('login') }">enter credentials</div>
      <div class="edge" />
      <div class="node dec" :class="{ on: lit('check') }">credentials valid?</div>

      <!-- branch row -->
      <div class="branch">
        <div class="arm left" :class="{ active: path === 'invalid' }">
          <span class="tag">no</span>
          <div class="node bad" :class="{ on: lit('error') }">show error</div>
          <span class="loop">⟲ back to login</span>
        </div>
        <div class="arm right" :class="{ active: path === 'valid' }">
          <span class="tag">yes</span>
          <div class="node act" :class="{ on: lit('dashboard') }">open dashboard</div>
          <div class="edge short" />
          <div class="node end" :class="{ on: lit('end') }">◉ end</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="btns">
        <button class="b ok"  @click="run('valid')">▶ valid login</button>
        <button class="b bad" @click="run('invalid')">▶ invalid login</button>
        <button class="b ghost" @click="reset">reset</button>
      </div>
      <ul class="kpts bp-dim text-sm">
        <li>Rounded nodes are <b>actions</b></li>
        <li>The diamond is a <b>decision</b></li>
        <li>Each guard label picks one outgoing edge</li>
        <li>Loops model retry / repeat</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ac { display: grid; grid-template-columns: 1.3fr 1fr; gap: 1.8rem; align-items: start; font-family: "Fira Code", monospace; }
.flow { display: flex; flex-direction: column; align-items: center; gap: 0; }
.node { padding: .5rem .9rem; border-radius: 10px; border: 1px solid var(--bp-line); background: rgba(255,255,255,.03); color: var(--bp-ink); font-size: .82rem; white-space: nowrap; transition: all .3s ease; text-align: center; }
.node.start, .node.end { border-radius: 999px; color: var(--bp-cyan); border-color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.node.dec { transform: rotate(0deg); border-color: var(--bp-blue); color: #fff; background: rgba(56,189,248,.1); }
.node.on { border-color: var(--bp-cyan); background: rgba(34,211,238,.18); box-shadow: var(--bp-glow); color: #fff; transform: scale(1.05); }
.node.bad.on { border-color: var(--bp-bad); background: rgba(251,113,133,.18); box-shadow: 0 0 14px rgba(251,113,133,.5); }
.edge { width: 0; height: 18px; border-left: 1.5px dashed var(--bp-line); }
.edge.short { height: 14px; }
.branch { display: flex; gap: 2.2rem; margin-top: .6rem; }
.arm { display: flex; flex-direction: column; align-items: center; gap: .5rem; opacity: .4; transition: opacity .3s; }
.arm.active { opacity: 1; }
.tag { font-size: .7rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 999px; padding: .05rem .5rem; }
.arm.right .tag { color: var(--bp-cyan); border-color: rgba(34,211,238,.4); }
.arm.left .tag { color: var(--bp-bad); border-color: rgba(251,113,133,.4); }
.loop { font-size: .68rem; color: var(--bp-dim); }
.panel { display: flex; flex-direction: column; gap: 1rem; }
.btns { display: flex; flex-wrap: wrap; gap: .5rem; }
.b { font-family: inherit; font-size: .8rem; padding: .5rem .8rem; border-radius: 8px; cursor: pointer; border: 1px solid var(--bp-line); background: rgba(255,255,255,.03); color: var(--bp-ink); }
.b.ok { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.b.bad { border-color: rgba(251,113,133,.5); color: var(--bp-bad); background: rgba(251,113,133,.06); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
</style>
