<script setup lang="ts">
import { ref, computed } from 'vue'

const STATES = ['PLACED', 'CONFIRMED', 'SHIPPED', 'DELIVERED']
const i = ref(0)
const current = computed(() => STATES[i.value])
function next() { i.value = (i.value + 1) % STATES.length }
function reset() { i.value = 0 }
</script>

<template>
  <div class="ec">
    <div class="track">
      <template v-for="(s, k) in STATES" :key="s">
        <div class="state" :class="{ on: k === i, done: k < i }">{{ s }}</div>
        <div v-if="k < STATES.length - 1" class="link" :class="{ done: k < i }">→</div>
      </template>
    </div>

    <div class="now">
      <span class="bp-dim">status =</span>
      <span class="pill">OrderStatus.{{ current }}</span>
    </div>

    <div class="ctl">
      <button class="b" @click="next">status = next()</button>
      <button class="b ghost" @click="reset">reset</button>
    </div>

    <div class="bad-row">
      <span class="x">×</span>
      <code>status = "SHPPED"</code>
      <span class="bp-dim">— typo can't compile: only the four names exist</span>
    </div>
  </div>
</template>

<style scoped>
.ec { font-family: "Fira Code", monospace; display: flex; flex-direction: column; gap: 1.1rem; }
.track { display: flex; align-items: center; flex-wrap: wrap; gap: .4rem; }
.state { padding: .4rem .7rem; border: 1px solid var(--bp-line); border-radius: 8px; font-size: .72rem; color: var(--bp-dim); transition: all .3s ease; }
.state.done { color: var(--bp-ink); border-color: rgba(56,189,248,.3); }
.state.on { color: #fff; border-color: var(--bp-cyan); background: rgba(34,211,238,.16); box-shadow: var(--bp-glow); transform: scale(1.06); }
.link { color: var(--bp-line); font-size: .9rem; transition: color .3s; }
.link.done { color: var(--bp-blue); }
.now { display: flex; align-items: center; gap: .6rem; font-size: .9rem; }
.pill { color: var(--bp-cyan); border: 1px solid var(--bp-cyan); border-radius: 999px; padding: .25rem .8rem; background: rgba(34,211,238,.1); }
.ctl { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .82rem; padding: .45rem .9rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); cursor: pointer; }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
.bad-row { display: flex; align-items: center; gap: .5rem; font-size: .72rem; padding: .5rem .7rem; border: 1px solid rgba(251,113,133,.3); border-radius: 8px; }
.bad-row .x { color: var(--bp-bad); font-weight: 700; }
.bad-row code { color: var(--bp-bad); text-decoration: line-through; }
</style>
