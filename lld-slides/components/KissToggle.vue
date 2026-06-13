<script setup lang="ts">
import { ref } from 'vue'
const simple = ref(false)
const TOWER = ['Operation (interface)', 'Addition', 'Subtraction', 'Multiplication', 'OperationFactory', 'Calculator executor']
</script>

<template>
  <div class="kiss">
    <div class="ctl">
      <button :class="{ on: !simple }" @click="simple = false">Over-engineered</button>
      <button :class="{ on: simple }"  @click="simple = true">Keep it simple</button>
    </div>

    <div v-if="!simple" class="tower">
      <div class="t" v-for="(c, i) in TOWER" :key="c" :style="{ animationDelay: 50 * i + 'ms' }">{{ c }}</div>
      <div class="note bad">6 classes to add two numbers — every change touches the whole tower</div>
    </div>

    <div v-else class="simple">
      <pre class="code">def calc(op, a, b):
    return {"+" : a + b, "-" : a - b, "*" : a * b}[op]</pre>
      <div class="note ok">one function, obvious, testable — add cases only when you truly need them</div>
    </div>
  </div>
</template>

<style scoped>
.kiss { font-family: "Fira Code", monospace; }
.ctl { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; margin-bottom: 1.5rem; }
.ctl button { font-family: inherit; font-size: .82rem; padding: .45rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.ctl button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.tower { display: flex; flex-direction: column; gap: .4rem; max-width: 26rem; }
.t { padding: .5rem .9rem; border: 1px solid rgba(251,113,133,.35); border-radius: 8px; background: rgba(251,113,133,.05); color: var(--bp-ink); font-size: .85rem; animation: rise .4s ease both; }
.simple { animation: fade .4s; }
.code { font-size: 1rem; color: var(--bp-ink); background: rgba(34,211,238,.05); border: 1px solid var(--bp-cyan); border-radius: 10px; padding: 1.1rem; box-shadow: var(--bp-glow); white-space: pre-wrap; }
.note { margin-top: 1.1rem; font-size: .85rem; padding: .5rem .8rem; border-radius: 8px; border: 1px solid var(--bp-line); max-width: 34rem; }
.note.bad { color: var(--bp-bad); } .note.ok { color: var(--bp-good); }
@keyframes rise { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
</style>
