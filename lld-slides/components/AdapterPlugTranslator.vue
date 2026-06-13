<script setup lang="ts">
import { ref, computed } from 'vue'

const inserted = ref(false)        // adapter REMOVED (false) / INSERTED (true)
const phase = ref<'idle' | 'out' | 'mismatch' | 'back' | 'ret'>('idle')
const socketHot = ref(false)       // adaptee turns green once reached
const crossed = ref(false)         // pulse has passed the adapter block (label cross-fade)
const retCrossed = ref(false)      // return pulse has passed the adapter block
const busy = ref(false)
const timers: ReturnType<typeof setTimeout>[] = []

function clearTimers() {
  timers.forEach(clearTimeout)
  timers.length = 0
}
function later(fn: () => void, ms: number) {
  timers.push(setTimeout(fn, ms))
}

function toggle() {
  if (busy.value) return
  reset()
  inserted.value = !inserted.value
}

function send() {
  if (busy.value) return
  busy.value = true
  socketHot.value = false
  crossed.value = false
  retCrossed.value = false

  if (!inserted.value) {
    // STATE REMOVED: pulse travels to the gap, stalls, snaps back, mismatch flashes
    phase.value = 'out'
    later(() => { phase.value = 'mismatch' }, 520)
    later(() => { phase.value = 'back' }, 560)
    later(() => { phase.value = 'idle'; busy.value = false }, 1320)
  } else {
    // STATE INSERTED: forward request() -> specificRequest(), socket greens, return temp converts
    phase.value = 'out'
    later(() => { crossed.value = true }, 520)         // cross-fade label mid-flight
    later(() => { socketHot.value = true }, 980)       // reach socket -> green
    later(() => { phase.value = 'ret' }, 1180)         // launch return pulse
    later(() => { retCrossed.value = true }, 1700)     // 98.6 F -> 37.0 C mid-flight
    later(() => { phase.value = 'idle'; busy.value = false }, 2200)
  }
}

function reset() {
  clearTimers()
  busy.value = false
  phase.value = 'idle'
  socketHot.value = false
  crossed.value = false
  retCrossed.value = false
}

const fwdLabel = computed(() => (crossed.value ? 'specificRequest()' : 'request()'))
const retLabel = computed(() => (retCrossed.value ? '37.0 C' : '98.6 F'))
const statusText = computed(() => {
  if (phase.value === 'mismatch' || (phase.value === 'back' && !inserted.value)) return 'shape mismatch — call rejected'
  if (!inserted.value) return 'Target API does not fit Adaptee'
  if (phase.value === 'idle') return inserted.value ? 'adapter bridges Target → Adaptee' : ''
  if (phase.value === 'ret') return 'translating 98.6 F → 37.0 C'
  return 'request() → specificRequest()'
})
</script>

<template>
  <div class="ad">
    <!-- ================= STAGE ================= -->
    <div class="stage">
      <div class="track">
        <!-- Client plug (Target) -->
        <div class="node plug" :class="{ active: phase === 'out' || phase === 'idle' }">
          <div class="tag">CLIENT · Target</div>
          <div class="api">read_celsius()</div>
          <div class="port plugport"><span class="prong" /><span class="prong" /></div>
        </div>

        <!-- center gap / rail -->
        <div class="gap">
          <div class="rail"><span class="rail-line" /></div>

          <!-- Adapter block, slides in when INSERTED -->
          <div class="adapter" :class="{ in: inserted, lit: inserted && (crossed || retCrossed || phase === 'out' || phase === 'ret') }">
            <div class="atag">ADAPTER</div>
            <div class="aconv">F → C</div>
          </div>

          <!-- forward pulse -->
          <span
            v-if="phase === 'out' || phase === 'back'"
            class="pulse fwd"
            :class="[phase, { lit: inserted }]"
          >{{ inserted ? fwdLabel : 'request()' }}</span>

          <!-- return pulse -->
          <span v-if="phase === 'ret'" class="pulse ret">{{ retLabel }}</span>

          <!-- mismatch badge -->
          <transition name="shk">
            <div v-if="phase === 'mismatch'" class="mismatch">✕ shape mismatch</div>
          </transition>
        </div>

        <!-- Adaptee socket -->
        <div class="node socket" :class="{ hot: socketHot, cold: !inserted }">
          <div class="port sockport" :class="{ hot: socketHot }"><span class="hole" /><span class="hole" /></div>
          <div class="tag">ADAPTEE</div>
          <div class="api">get_fahrenheit()</div>
        </div>
      </div>

      <!-- edits counter: hard-coded zero in both states -->
      <div class="ledger">
        <span class="led">Client edits <b>0</b></span>
        <span class="sep">·</span>
        <span class="led">Adaptee edits <b>0</b></span>
        <span class="hint">no source modified</span>
      </div>

      <div class="status" :class="phase">{{ statusText || ' ' }}</div>
    </div>

    <!-- ================= CONTROLS ================= -->
    <div class="panel">
      <label class="tog" :class="{ on: inserted }" @click="toggle">
        <span class="knob" />
        Adapter {{ inserted ? 'INSERTED' : 'REMOVED' }}
      </label>

      <div class="btns">
        <button class="b" @click="send">▶ Send</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>

      <ul class="kpts">
        <li>REMOVED: the plug's shape can't reach the foreign socket</li>
        <li>INSERTED: the adapter translates request → specificRequest</li>
        <li>Reply flips 98.6 F → 37.0 C — client & adaptee untouched</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ad {
  display: grid;
  grid-template-columns: 1.55fr 1fr;
  gap: 1.6rem;
  width: 100%;
  height: 340px;
  box-sizing: border-box;
  align-content: start;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- stage ---------- */
.stage { display: flex; flex-direction: column; gap: .7rem; min-width: 0; }
.track { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 0; height: 168px; }

.node { display: flex; flex-direction: column; gap: .35rem; padding: .7rem .85rem; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.02); transition: all .35s; position: relative; }
.node.active { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.tag { font-size: .58rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-dim); }
.api { font-size: .76rem; color: var(--bp-ink); }

/* ports */
.port { display: flex; gap: 5px; }
.plugport { justify-content: flex-end; }
.prong { width: 5px; height: 16px; border-radius: 2px; background: var(--bp-cyan); box-shadow: 0 0 6px rgba(34,211,238,.5); }
.sockport { justify-content: flex-start; }
.hole { width: 7px; height: 16px; border-radius: 3px; border: 2px solid var(--bp-dim); background: var(--bp-bg); transition: all .35s; }
.sockport.hot .hole { border-color: var(--bp-good); box-shadow: 0 0 8px rgba(74,222,128,.5); }

.socket { align-items: flex-start; }
.socket.cold { opacity: .85; }
.socket.hot { border-color: var(--bp-good); box-shadow: 0 0 20px rgba(74,222,128,.4); }
.socket.hot .api { color: var(--bp-good); }

/* ---------- center gap ---------- */
.gap { position: relative; height: 80px; display: flex; align-items: center; justify-content: center; }
.rail { position: absolute; left: 0; right: 0; top: 50%; height: 2px; }
.rail-line { display: block; height: 2px; width: 100%; background: repeating-linear-gradient(90deg, var(--bp-line) 0 8px, transparent 8px 16px); }

/* adapter block */
.adapter { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; gap: .1rem; padding: .4rem .7rem; border: 1px solid var(--bp-violet); border-radius: 9px; background: rgba(167,139,250,.1); opacity: 0; transform: scale(.4) translateY(6px); transition: all .45s cubic-bezier(.34,1.56,.64,1); pointer-events: none; }
.adapter.in { opacity: 1; transform: scale(1) translateY(0); }
.adapter.lit { border-color: var(--bp-cyan); box-shadow: 0 0 16px rgba(34,211,238,.4); }
.atag { font-size: .54rem; letter-spacing: .12em; color: var(--bp-violet); }
.aconv { font-size: .72rem; color: #fff; }

/* pulses */
.pulse { position: absolute; z-index: 3; top: 50%; padding: .12rem .5rem; border-radius: 999px; font-size: .6rem; white-space: nowrap; transform: translate(-50%, -50%); }
.pulse.fwd { left: 0; color: var(--bp-bg); background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.pulse.fwd.out { animation: fwd-stall .52s ease forwards; }
.pulse.fwd.lit.out { animation: fwd-cross 1.18s ease forwards; }
.pulse.fwd.back { animation: snapback .76s ease forwards; }
.pulse.ret { right: 0; color: var(--bp-bg); background: var(--bp-good); box-shadow: 0 0 14px rgba(74,222,128,.5); animation: ret-cross 1.02s ease forwards; }

@keyframes fwd-stall { 0% { left: 0; opacity: 0; } 15% { opacity: 1; } 100% { left: 50%; opacity: 1; } }
@keyframes fwd-cross { 0% { left: 0; opacity: 0; } 12% { opacity: 1; } 100% { left: 100%; opacity: 1; } }
@keyframes snapback { 0% { left: 50%; } 70% { left: 0; opacity: 1; } 100% { left: 0; opacity: 0; } }
@keyframes ret-cross { 0% { right: 0; opacity: 0; } 12% { opacity: 1; } 100% { right: 100%; opacity: 1; } }

/* mismatch badge */
.mismatch { position: absolute; z-index: 4; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: .6rem; color: var(--bp-bad); border: 1px solid var(--bp-bad); border-radius: 999px; padding: .15rem .55rem; background: var(--bp-bg); box-shadow: 0 0 14px rgba(251,113,133,.5); }
.shk-enter-active { animation: shake .6s; }
@keyframes shake { 0%, 100% { transform: translate(-50%, -50%); } 20% { transform: translate(-58%, -50%); } 40% { transform: translate(-42%, -50%); } 60% { transform: translate(-56%, -50%); } 80% { transform: translate(-44%, -50%); } }

/* ---------- ledger ---------- */
.ledger { display: flex; align-items: center; gap: .55rem; font-size: .66rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 8px; padding: .35rem .7rem; align-self: flex-start; }
.led b { color: var(--bp-good); margin-left: .25rem; }
.sep { opacity: .4; }
.hint { margin-left: .4rem; font-size: .58rem; letter-spacing: .04em; color: var(--bp-good); opacity: .8; }

/* status line */
.status { font-size: .68rem; min-height: 1rem; color: var(--bp-cyan); transition: color .3s; }
.status.mismatch, .status.back { color: var(--bp-bad); }
.status.ret { color: var(--bp-good); }

/* ---------- panel ---------- */
.panel { display: flex; flex-direction: column; gap: .75rem; align-items: flex-start; min-width: 0; }
.tog { display: inline-flex; align-items: center; gap: .55rem; font-size: .78rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 32px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(167,139,250,.4); }
.tog.on .knob::after { left: 18px; background: var(--bp-violet); }
.tog.on { color: var(--bp-violet); }

.btns { display: flex; gap: .6rem; }
.b { font-family: inherit; font-size: .8rem; padding: .45rem .85rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }

.kpts { list-style: none; padding: 0; margin: .3rem 0 0; }
.kpts li { position: relative; padding-left: 1.05rem; margin: .32rem 0; font-size: .68rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
