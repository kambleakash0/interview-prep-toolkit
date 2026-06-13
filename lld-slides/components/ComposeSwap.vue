<script setup lang="ts">
import { ref } from 'vue'

const PARTS = [
  { name: 'GasEngine',     out: 'vroom — burning fuel',  icon: '●' },
  { name: 'ElectricMotor', out: 'silent hum — battery',  icon: '◇' },
  { name: 'HybridDrive',   out: 'fuel + battery combo',  icon: '◐' },
]
const idx = ref(0)
const swapping = ref(false)
function pick(i: number) {
  if (i === idx.value) return
  swapping.value = true
  setTimeout(() => { idx.value = i; swapping.value = false }, 220)
}
</script>

<template>
  <div class="cs">
    <div class="car">
      <div class="title">Car <span class="dim">composes a part — swap at runtime</span></div>
      <div class="slot">
        <span class="bp-dim">self.engine =</span>
        <div class="part" :class="{ swapping }">
          <span class="ic">{{ PARTS[idx].icon }}</span>{{ PARTS[idx].name }}
        </div>
      </div>
      <div class="run">
        <span class="bp-dim">car.drive()</span> &rarr;
        <span class="out" :class="{ swapping }">{{ PARTS[idx].out }}</span>
      </div>
    </div>

    <div class="picker">
      <div class="lbl">drop in a different engine</div>
      <button v-for="(p, i) in PARTS" :key="p.name" class="opt" :class="{ on: i === idx }" @click="pick(i)">
        <span class="ic">{{ p.icon }}</span>{{ p.name }}
      </button>
      <div class="hint bp-dim">Car never changes — only the part it holds. That's composition.</div>
    </div>
  </div>
</template>

<style scoped>
.cs { display: grid; grid-template-columns: 1.3fr 1fr; gap: 1.6rem; align-items: center; font-family: "Fira Code", monospace; }
.car { border: 1px solid var(--bp-cyan); border-radius: 14px; padding: 1.4rem; background: linear-gradient(180deg, rgba(34,211,238,.08), transparent); box-shadow: var(--bp-glow); }
.title { font-size: 1.1rem; color: #fff; margin-bottom: 1.2rem; } .title .dim, .dim { color: var(--bp-dim); font-size: .8rem; }
.slot { display: flex; align-items: center; gap: .7rem; margin-bottom: 1.1rem; }
.part { display: flex; align-items: center; gap: .5rem; padding: .55rem .9rem; border-radius: 9px; border: 1px solid var(--bp-violet); color: var(--bp-violet); background: rgba(167,139,250,.1); font-size: .95rem; transition: all .25s; }
.part.swapping { opacity: 0; transform: translateY(-8px) scale(.9); }
.ic { font-style: normal; }
.run { font-size: 1rem; }
.run .out { color: var(--bp-good); transition: all .25s; }
.run .out.swapping { opacity: 0; }
.picker { display: flex; flex-direction: column; gap: .55rem; }
.lbl { font-size: .64rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bp-dim); margin-bottom: .2rem; }
.opt { display: flex; align-items: center; gap: .5rem; font-family: inherit; font-size: .88rem; padding: .55rem .8rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02); color: var(--bp-ink); cursor: pointer; transition: .15s; }
.opt:hover { border-color: var(--bp-violet); transform: translateX(3px); }
.opt.on { border-color: var(--bp-violet); color: var(--bp-violet); background: rgba(167,139,250,.12); }
.hint { font-size: .76rem; margin-top: .4rem; }
</style>
