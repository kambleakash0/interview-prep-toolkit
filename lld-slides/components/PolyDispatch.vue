<script setup lang="ts">
import { ref } from 'vue'

type Shape = { key: string; name: string; formula: string; calc: () => number; icon: string }
const shapes: Shape[] = [
  { key: 'circle',   name: 'Circle(r=3)',     formula: 'π · r²',      calc: () => +(Math.PI * 9).toFixed(2),  icon: '●' },
  { key: 'square',   name: 'Square(s=4)',     formula: 's²',          calc: () => 16,                          icon: '■' },
  { key: 'triangle', name: 'Triangle(b=6,h=4)', formula: '½ · b · h', calc: () => 12,                          icon: '▲' },
]
const selected = ref(0)
const firing = ref(false)
const landed = ref<number | null>(null)
const result = ref<string>('')

function call() {
  firing.value = true
  landed.value = null
  result.value = ''
  const i = selected.value
  setTimeout(() => {
    landed.value = i
    result.value = `${shapes[i].formula} = ${shapes[i].calc()}`
    firing.value = false
    setTimeout(() => (landed.value = null), 1400)
  }, 650)
}
</script>

<template>
  <div class="poly">
    <!-- call site -->
    <div class="callsite">
      <div class="bp-chip">runtime</div>
      <div class="picker">
        <span class="bp-dim">shape =</span>
        <button
          v-for="(s, i) in shapes" :key="s.key"
          :class="['pick', { on: selected === i }]"
          @click="selected = i; landed = null; result = ''"
        >{{ s.icon }} {{ s.name.split('(')[0] }}</button>
      </div>
      <button class="invoke" :disabled="firing" @click="call">▸ shape.area()</button>
      <div class="bus">
        <span :class="['token', { fly: firing }]">area()</span>
      </div>
    </div>

    <!-- dispatch targets -->
    <div class="targets">
      <div
        v-for="(s, i) in shapes" :key="s.key"
        :class="['target', { dim: selected !== i, hot: landed === i }]"
      >
        <div class="ttl"><span class="ic">{{ s.icon }}</span> {{ s.name }}</div>
        <div class="impl">def area(self):</div>
        <div class="impl ind">return {{ s.formula }}</div>
        <div v-if="landed === i" class="ret">→ {{ result }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.poly { font-family: "Fira Code", monospace; display: grid; grid-template-columns: 1fr 1.4fr; gap: 1.4rem; align-items: center; }
.callsite { display: flex; flex-direction: column; gap: .7rem; }
.picker { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; font-size: .8rem; }
.pick { font-family: inherit; font-size: .76rem; padding: .3rem .6rem; border: 1px solid var(--bp-line); border-radius: 7px; background: transparent; color: var(--bp-dim); cursor: pointer; }
.pick.on { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.1); }
.invoke { font-family: inherit; font-size: .9rem; padding: .55rem .9rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 9px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.invoke:disabled { opacity: .5; }
.bus { height: 26px; position: relative; }
.token { position: absolute; left: 0; font-size: .72rem; color: var(--bp-cyan); border: 1px solid var(--bp-cyan); border-radius: 999px; padding: .1rem .5rem; opacity: 0; }
.token.fly { animation: fly .65s ease-in forwards; }
@keyframes fly { 0% { left: 0; opacity: 1; } 100% { left: 100%; opacity: 0; } }

.targets { display: flex; flex-direction: column; gap: .55rem; }
.target { border: 1px solid var(--bp-line); border-radius: 10px; padding: .55rem .8rem; transition: all .35s ease; background: rgba(255,255,255,.02); }
.target.dim { opacity: .4; }
.target.hot { opacity: 1; border-color: var(--bp-cyan); box-shadow: var(--bp-glow); transform: scale(1.03); background: rgba(34,211,238,.08); }
.ttl { color: #fff; font-size: .85rem; margin-bottom: .25rem; }
.ic { color: var(--bp-cyan); margin-right: .3rem; }
.impl { color: var(--bp-dim); font-size: .76rem; }
.impl.ind { padding-left: 1.1rem; color: var(--bp-violet); }
.ret { margin-top: .3rem; color: var(--bp-good); font-size: .82rem; }
</style>
