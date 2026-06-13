<script setup lang="ts">
import { ref, computed } from 'vue'

// A simple interface (3 calls) over complex hidden machinery.
const ACTIONS: Record<string, { call: string; steps: string[] }> = {
  start: { call: 'car.start()', steps: ['turn ignition key', 'engage starter motor', 'inject fuel', 'fire spark plugs', 'engine idles'] },
  drive: { call: 'car.drive()', steps: ['release clutch', 'select gear ratio', 'open throttle', 'transmit torque', 'wheels turn'] },
  brake: { call: 'car.brake()', steps: ['press pedal', 'pressurize brake fluid', 'clamp the calipers', 'apply friction', 'car slows'] },
}

const revealed = ref(false)
const current = ref<string | null>(null)
const lit = ref(0)

const steps = computed(() => (current.value ? ACTIONS[current.value].steps : []))

function run(key: string) {
  current.value = key
  lit.value = 0
  const n = ACTIONS[key].steps.length
  for (let i = 1; i <= n; i++) setTimeout(() => (lit.value = i), 260 * i)
}
</script>

<template>
  <div class="abs">
    <!-- simple interface -->
    <div class="bp-card col">
      <div class="hd"><span class="bp-chip">public interface</span><span class="bp-dim xs">what you call</span></div>
      <button v-for="(a, k) in ACTIONS" :key="k" :class="['call', { on: current === k }]" @click="run(k)">
        {{ a.call }}
      </button>
      <div class="hint bp-dim">Three methods. That's all a driver needs to know.</div>
    </div>

    <div class="arrow">
      <div class="bp-mono xs bp-dim">calls</div>
      <svg width="46" height="20" viewBox="0 0 46 20"><path d="M2,10 H40 M34,4 L42,10 L34,16" fill="none" stroke="var(--bp-cyan)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </div>

    <!-- hidden implementation -->
    <div :class="['bp-card', 'col', 'impl', revealed ? 'bp-card--cyan' : '']">
      <div class="hd">
        <span class="bp-mono" style="color:#fff">under the hood</span>
        <label class="tgl">
          <input type="checkbox" v-model="revealed" />
          <span>{{ revealed ? 'implementation shown' : 'reveal implementation' }}</span>
        </label>
      </div>

      <div class="steps" :class="{ hidden: !revealed }">
        <template v-if="steps.length">
          <div v-for="(s, i) in steps" :key="s" :class="['step', { lit: i < lit }]">
            <span class="dot" /> {{ s }}
          </div>
        </template>
        <div v-else class="bp-dim sm">press a method to run it…</div>
      </div>

      <div v-if="!revealed" class="veil">
        <div class="veil-txt bp-mono">complexity abstracted away</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.abs { display: grid; grid-template-columns: 1fr auto 1.25fr; gap: 1rem; align-items: stretch; font-family: "Fira Code", monospace; }
.col { display: flex; flex-direction: column; gap: .55rem; position: relative; }
.hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: .2rem; }
.xs { font-size: .62rem; } .sm { font-size: .85rem; }
.call {
  text-align: left; font-family: inherit; font-size: .92rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .6rem .8rem;
  background: rgba(255,255,255,.02); color: var(--bp-ink); transition: .15s;
}
.call:hover { transform: translateX(3px); border-color: var(--bp-cyan); }
.call.on { border-color: var(--bp-cyan); color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.hint { font-size: .72rem; margin-top: auto; }

.arrow { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .3rem; }

.impl { overflow: hidden; }
.tgl { display: flex; align-items: center; gap: .4rem; font-size: .72rem; cursor: pointer; color: var(--bp-dim); }
.steps { display: flex; flex-direction: column; gap: .5rem; padding-top: .3rem; transition: filter .4s, opacity .4s; }
.steps.hidden { filter: blur(6px); opacity: .35; pointer-events: none; }
.step { display: flex; align-items: center; gap: .6rem; font-size: .88rem; color: var(--bp-dim); transition: all .3s; }
.step .dot { width: 9px; height: 9px; border-radius: 999px; border: 1.5px solid var(--bp-dim); flex: none; transition: all .3s; }
.step.lit { color: #fff; }
.step.lit .dot { background: var(--bp-cyan); border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.veil { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; pointer-events: none; }
.veil-txt {
  font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; color: var(--bp-cyan);
  border: 1px solid var(--bp-line); border-radius: 999px; padding: .35em 1em; background: rgba(11,19,36,.6);
}
</style>
