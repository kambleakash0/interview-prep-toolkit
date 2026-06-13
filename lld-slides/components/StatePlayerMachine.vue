<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

type StateName = 'Locked' | 'Playing' | 'Paused'

// nodes stacked top-to-bottom: Locked, Playing, Paused
const NODES: StateName[] = ['Locked', 'Playing', 'Paused']
const ROW_Y: Record<StateName, number> = { Locked: 0, Playing: 1, Paused: 2 }

const active = ref<StateName>('Locked')
const pill = ref('')          // transient handler message
const flash = ref(false)      // Locked rejection flash
const log = ref<string[]>([])
const logBox = ref<HTMLElement | null>(null)

let busy = false
let pillTimer: ReturnType<typeof setTimeout> | null = null
let flashTimer: ReturnType<typeof setTimeout> | null = null

// arrow tip vertical offset (px) — 3 rows, gap-matched to .node layout.
// The rail is vertically centered, so the centre aligns with the middle
// node (Playing, row 1). Centre the offset around that row so the arrow
// lands on the active node instead of one row above it.
const NODE_STEP = 72
const arrowY = computed(() => (ROW_Y[active.value] - 1) * NODE_STEP)

function append(line: string) {
  log.value.push(line)
  nextTick(() => { if (logBox.value) logBox.value.scrollTop = logBox.value.scrollHeight })
}

function showPill(text: string, ms = 600) {
  if (pillTimer) clearTimeout(pillTimer)
  pill.value = text
  pillTimer = setTimeout(() => { pill.value = ''; pillTimer = null }, ms)
}

function unlock() {
  if (busy) return
  if (active.value !== 'Locked') return     // only meaningful from Locked
  busy = true
  active.value = 'Paused'                    // arrow slides Locked -> Paused
  append('context.state = Paused')
  setTimeout(() => { busy = false }, 420)
}

function push() {
  if (busy) return
  const cur = active.value

  if (cur === 'Locked') {
    // reject: flash outline twice, transient pill, arrow stays
    busy = true
    if (flashTimer) clearTimeout(flashTimer)
    flash.value = false
    nextTick(() => { flash.value = true })
    showPill('press play first', 600)
    append('Locked.push -> stay Locked')
    flashTimer = setTimeout(() => { flash.value = false; flashTimer = null }, 620)
    setTimeout(() => { busy = false }, 640)
    return
  }

  if (cur === 'Paused') {
    busy = true
    showPill('Resuming', 600)
    active.value = 'Playing'                  // arrow Paused -> Playing
    append('Paused.push -> Playing')
    setTimeout(() => { busy = false }, 420)
    return
  }

  // Playing
  busy = true
  showPill('Pausing', 600)
  active.value = 'Paused'                      // arrow Playing -> Paused
  append('Playing.push -> Paused')
  setTimeout(() => { busy = false }, 420)
}

function reset() {
  if (pillTimer) { clearTimeout(pillTimer); pillTimer = null }
  if (flashTimer) { clearTimeout(flashTimer); flashTimer = null }
  busy = false
  active.value = 'Locked'
  pill.value = ''
  flash.value = false
  log.value = []
}

const HANDLER: Record<StateName, string> = {
  Locked: 'print("press play first")',
  Playing: 'print("Pausing"); state = Paused()',
  Paused: 'print("Resuming"); state = Playing()',
}
</script>

<template>
  <div class="sm">
    <!-- STAGE -->
    <div class="stage">
      <!-- Context box -->
      <div class="ctx">
        <div class="ct">Context</div>
        <div class="ctx-name">Player</div>
        <div class="ctx-field">
          <span class="dim">.state</span>
          <span class="bind">{{ active }}</span>
        </div>
        <div class="ctx-call">push() <span class="dim">→</span> state.push()</div>
        <span class="anchor" />
      </div>

      <!-- delegation rail + moving arrow -->
      <div class="rail">
        <span class="line" />
        <span class="arrow" :style="{ transform: `translateY(${arrowY}px)` }">
          <span class="shaft" /><span class="head">▶</span>
          <transition name="pill">
            <span v-if="pill" class="pill" :class="{ reject: active === 'Locked' }">{{ pill }}</span>
          </transition>
        </span>
      </div>

      <!-- state nodes -->
      <div class="nodes">
        <div
          v-for="n in NODES"
          :key="n"
          class="node"
          :class="{ on: active === n, shake: active === n && n === 'Locked' && flash }"
        >
          <span class="dot" />
          <div class="nbody">
            <span class="nname">{{ n }}</span>
            <span class="nhandler">push(): {{ HANDLER[n] }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- PANEL -->
    <div class="panel">
      <div class="btns">
        <button class="b push" @click="push">▶ Push</button>
        <button class="b unlock" :disabled="active !== 'Locked'" @click="unlock">◇ Unlock</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>

      <div class="logwrap">
        <div class="logtitle">delegated calls</div>
        <div ref="logBox" class="log">
          <div v-if="!log.length" class="logempty">— same Push, different state —</div>
          <div v-for="(l, i) in log" :key="i" class="logline">
            <span class="lk">›</span> {{ l }}
          </div>
        </div>
      </div>

      <ul class="kpts bp-dim text-sm">
        <li>One Push button — the bound state object decides what it does</li>
        <li>States swap the context to the next state themselves</li>
        <li>Identical input, moving arrow: behavior follows the wiring</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.sm { display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.5rem; font-family: "Fira Code", monospace; height: 340px; }

/* ---- stage ---- */
.stage { display: grid; grid-template-columns: auto 70px 1fr; align-items: center; }

/* context box */
.ctx { position: relative; display: flex; flex-direction: column; gap: .35rem; padding: .8rem .9rem; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.03); min-width: 168px; }
.ct { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.ctx-name { font-size: 1rem; color: #fff; }
.ctx-field { font-size: .76rem; display: flex; gap: .35rem; align-items: baseline; }
.ctx-field .bind { color: var(--bp-cyan); border: 1px solid var(--bp-cyan); border-radius: 6px; padding: .02rem .4rem; background: rgba(34,211,238,.1); transition: all .25s; }
.ctx-call { font-size: .6rem; color: var(--bp-dim); margin-top: .15rem; }
.dim { color: var(--bp-dim); }
.anchor { position: absolute; right: -5px; top: 50%; width: 9px; height: 9px; border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow); transform: translateY(-50%); }

/* delegation rail */
.rail { position: relative; height: 100%; }
.line { position: absolute; left: 0; top: 50%; width: 100%; height: 1px; background: var(--bp-line); transform: translateY(-50%); }
.arrow { position: absolute; left: 0; top: 50%; width: 100%; display: flex; align-items: center; margin-top: -1px; transition: transform .42s cubic-bezier(.5,.05,.2,1); }
.shaft { flex: 1; height: 2px; background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.head { color: var(--bp-cyan); font-size: .85rem; margin-left: -2px; text-shadow: var(--bp-glow); }
.pill { position: absolute; left: 50%; top: -20px; transform: translateX(-50%); white-space: nowrap; font-size: .6rem; color: var(--bp-bg); background: var(--bp-cyan); border-radius: 999px; padding: .12rem .55rem; box-shadow: var(--bp-glow); }
.pill.reject { background: var(--bp-warn); color: var(--bp-bg); box-shadow: 0 0 14px rgba(251,191,36,.5); }
.pill-enter-active, .pill-leave-active { transition: all .25s; }
.pill-enter-from, .pill-leave-to { opacity: 0; transform: translate(-50%, -6px); }

/* state nodes */
.nodes { display: flex; flex-direction: column; gap: 24px; }
.node { display: flex; align-items: center; gap: .55rem; height: 48px; padding: 0 .8rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.02); opacity: .42; transition: all .3s; }
.node.on { opacity: 1; border-color: var(--bp-cyan); background: rgba(34,211,238,.1); box-shadow: var(--bp-glow); }
.node .dot { width: 9px; height: 9px; border-radius: 999px; background: var(--bp-line); flex: none; transition: all .3s; }
.node.on .dot { background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.nbody { display: flex; flex-direction: column; line-height: 1.2; overflow: hidden; }
.nname { font-size: .82rem; color: var(--bp-ink); }
.node.on .nname { color: #fff; }
.nhandler { font-size: .56rem; color: var(--bp-dim); white-space: nowrap; }
.node.shake { animation: shake .3s ease 2; border-color: var(--bp-warn); box-shadow: 0 0 16px rgba(251,191,36,.5); }
@keyframes shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-4px); } 75% { transform: translateX(4px); } }

/* ---- panel ---- */
.panel { display: flex; flex-direction: column; gap: .7rem; align-items: stretch; }
.btns { display: flex; flex-wrap: wrap; gap: .5rem; }
.b { font-family: inherit; font-size: .78rem; padding: .42rem .8rem; border-radius: 8px; cursor: pointer; transition: all .2s; }
.b.push { border: 1px solid var(--bp-cyan); color: #fff; background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); }
.b.unlock { border: 1px solid var(--bp-violet); color: var(--bp-violet); background: rgba(167,139,250,.1); }
.b.unlock:disabled { opacity: .32; cursor: not-allowed; }
.b.ghost { border: 1px solid var(--bp-line); color: var(--bp-dim); background: transparent; }
.b.ghost:hover { border-color: var(--bp-cyan); color: var(--bp-cyan); }

.logwrap { display: flex; flex-direction: column; gap: .3rem; }
.logtitle { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.log { height: 92px; overflow-y: auto; border: 1px solid var(--bp-line); border-radius: 8px; background: rgba(7,11,20,.6); padding: .4rem .55rem; font-size: .64rem; line-height: 1.55; }
.log::-webkit-scrollbar { width: 5px; }
.log::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.logempty { color: var(--bp-dim); opacity: .6; }
.logline { color: var(--bp-ink); white-space: nowrap; }
.lk { color: var(--bp-cyan); }

.kpts { margin: 0; }
</style>
