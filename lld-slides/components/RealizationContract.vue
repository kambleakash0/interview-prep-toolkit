<script setup lang="ts">
import { ref } from 'vue'

const IMPLS = [
  { name: 'Bird',     out: 'flaps wings', c: '#22d3ee' },
  { name: 'Airplane', out: 'engines roar', c: '#a78bfa' },
]
const fired = ref<number | null>(null)
function call(i: number) { fired.value = i }
</script>

<template>
  <div class="rc">
    <div class="contract">
      <span class="kw">«interface»</span>
      <b>Flyable</b>
      <span class="m">+ fly()</span>
    </div>

    <div class="links">
      <div class="link" :class="{ on: fired === 0 }"><span>▲</span></div>
      <div class="link" :class="{ on: fired === 1 }"><span>▲</span></div>
    </div>

    <div class="impls">
      <button v-for="(im, i) in IMPLS" :key="im.name" class="impl"
              :class="{ on: fired === i }"
              :style="fired === i ? { borderColor: im.c } : {}"
              @click="call(i)">
        <span class="nm" :style="fired === i ? { color: im.c } : {}">{{ im.name }}</span>
        <span class="ret" :class="{ show: fired === i }">fly() → "{{ im.out }}"</span>
      </button>
    </div>

    <div class="cap bp-dim bp-mono">a Bird and a Plane share nothing — except the contract</div>
  </div>
</template>

<style scoped>
.rc { font-family: "Fira Code", monospace; display: flex; flex-direction: column; gap: .55rem; align-items: center; }
.contract { display: flex; flex-direction: column; align-items: center; gap: .15rem; padding: .6rem 1.4rem; border: 1px solid var(--bp-cyan); border-radius: 10px; background: rgba(34,211,238,.08); box-shadow: var(--bp-glow); }
.contract .kw { font-size: .6rem; color: var(--bp-cyan); text-transform: uppercase; letter-spacing: .08em; }
.contract b { color: #fff; font-size: 1rem; }
.contract .m { font-size: .68rem; color: var(--bp-dim); }
.links { display: flex; gap: 7rem; }
.link { color: var(--bp-line); font-size: .9rem; line-height: 1; transition: color .3s; }
.link span { display: inline-block; border-bottom: 1.5px dashed currentColor; padding-bottom: .35rem; }
.link.on { color: var(--bp-cyan); }
.impls { display: flex; gap: 1.5rem; }
.impl { font-family: inherit; display: flex; flex-direction: column; align-items: center; gap: .25rem; padding: .55rem .9rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.03); cursor: pointer; transition: all .25s; min-width: 140px; }
.impl.on { background: rgba(255,255,255,.05); transform: translateY(-2px); }
.impl .nm { color: var(--bp-ink); font-size: .9rem; }
.impl .ret { font-size: .66rem; color: var(--bp-dim); opacity: 0; height: 0; transition: opacity .3s; }
.impl .ret.show { opacity: 1; height: auto; }
.cap { font-size: .7rem; margin-top: .3rem; }
</style>
