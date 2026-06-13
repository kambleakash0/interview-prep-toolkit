<script setup lang="ts">
import { ref } from 'vue'

const PALETTE = ['#22d3ee', '#a78bfa', '#38bdf8', '#fbbf24', '#4ade80']
const NAMES = ['a', 'b', 'c', 'd', 'e']
type Obj = { id: number; name: string; color: string; speed: number }
const objs = ref<Obj[]>([])
let n = 0

function spawn() {
  if (objs.value.length >= 5) return
  const i = objs.value.length
  objs.value.push({ id: n++, name: NAMES[i], color: PALETTE[i], speed: 0 })
}
function accel(o: Obj) { o.speed += 10 }
function reset() { objs.value = [] }
</script>

<template>
  <div class="os">
    <div class="blueprint">
      <span class="tag">blueprint</span>
      <code>class Car</code>
    </div>

    <div class="arrow">instantiate ▾</div>

    <div class="objs">
      <div v-for="o in objs" :key="o.id" class="obj" :style="{ borderColor: o.color }">
        <span class="dot" :style="{ background: o.color }" />
        <span class="oname">{{ o.name }} = Car("{{ o.color === '#22d3ee' ? 'cyan' : o.color === '#a78bfa' ? 'violet' : o.color === '#38bdf8' ? 'blue' : o.color === '#fbbf24' ? 'amber' : 'green' }}")</span>
        <span class="spd">speed&nbsp;{{ o.speed }}</span>
        <button class="mini" :style="{ color: o.color, borderColor: o.color }" @click="accel(o)">accelerate()</button>
      </div>
      <div v-if="!objs.length" class="empty bp-dim">no objects yet — build one from the blueprint</div>
    </div>

    <div class="ctl">
      <button class="b" @click="spawn">+ new Car()</button>
      <button class="b ghost" @click="reset">reset</button>
    </div>
    <div class="cap bp-dim bp-mono">one class &rarr; many objects, each with its own state</div>
  </div>
</template>

<style scoped>
.os { font-family: "Fira Code", monospace; display: flex; flex-direction: column; gap: .5rem; }
.blueprint { display: flex; align-items: center; gap: .6rem; padding: .5rem .8rem; border: 1px dashed var(--bp-cyan); border-radius: 10px; background: rgba(34,211,238,.06); width: fit-content; }
.blueprint .tag { font-size: .6rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-cyan); }
.blueprint code { color: #fff; font-size: .9rem; }
.arrow { font-size: .68rem; color: var(--bp-dim); padding-left: .4rem; }
.objs { display: flex; flex-direction: column; gap: .4rem; min-height: 96px; }
.obj { display: flex; align-items: center; gap: .5rem; padding: .35rem .6rem; border: 1px solid; border-radius: 8px; background: rgba(255,255,255,.03); font-size: .72rem; }
.dot { width: 9px; height: 9px; border-radius: 999px; flex: none; }
.oname { color: var(--bp-ink); }
.spd { margin-left: auto; color: var(--bp-dim); }
.mini { font-family: inherit; font-size: .62rem; padding: .12rem .45rem; border: 1px solid; border-radius: 6px; background: transparent; cursor: pointer; }
.empty { font-size: .72rem; display: flex; align-items: center; height: 96px; }
.ctl { display: flex; gap: .5rem; margin-top: .2rem; }
.b { font-family: inherit; font-size: .78rem; padding: .4rem .8rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); cursor: pointer; }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
.cap { font-size: .7rem; margin-top: .2rem; }
</style>
