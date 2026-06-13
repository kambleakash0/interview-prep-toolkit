<script setup lang="ts">
import { ref, computed } from 'vue'

const ACTORS = [
  { id: 'User', x: 14 },
  { id: 'Service', x: 50 },
  { id: 'Database', x: 86 },
]
const MSGS = [
  { from: 14, to: 50, y: 60,  label: 'request()',  ret: false },
  { from: 50, to: 86, y: 120, label: 'query()',    ret: false },
  { from: 86, to: 50, y: 180, label: 'rows',       ret: true },
  { from: 50, to: 14, y: 240, label: 'response',   ret: true },
]
const step = ref(0)
let timer: any = null

function play() {
  reset()
  timer = setInterval(() => {
    if (step.value >= MSGS.length) { clearInterval(timer); return }
    step.value++
  }, 750)
}
function reset() { clearInterval(timer); step.value = 0 }
const active = computed(() => step.value - 1)
</script>

<template>
  <div class="sq">
    <div class="diagram">
      <!-- actors + lifelines -->
      <div v-for="a in ACTORS" :key="a.id" class="actor" :style="{ left: a.x + '%' }">{{ a.id }}</div>
      <div v-for="a in ACTORS" :key="a.id + 'l'" class="life" :style="{ left: a.x + '%' }" />

      <!-- messages -->
      <template v-for="(m, i) in MSGS" :key="i">
        <div v-show="i < step" class="msg" :class="{ ret: m.ret, live: i === active }"
             :style="{ top: m.y + 'px', left: Math.min(m.from, m.to) + '%', width: Math.abs(m.to - m.from) + '%' }">
          <span class="lbl" :class="{ right: m.to < m.from }">{{ m.label }}</span>
          <div class="line"><span class="head" :class="m.to > m.from ? 'r' : 'l'" /></div>
          <span v-if="i === active" class="token" :class="m.to > m.from ? 'go-r' : 'go-l'" />
        </div>
      </template>
    </div>

    <div class="panel">
      <div class="btns">
        <button class="b" @click="step < MSGS.length ? step++ : null">▸ step</button>
        <button class="b alt" @click="play">▶ play</button>
        <button class="b ghost" @click="reset">reset</button>
      </div>
      <div class="prog">message {{ step }} / {{ MSGS.length }}</div>
      <ul class="kpts bp-dim text-sm">
        <li>Actors initiate; participants respond</li>
        <li>Time flows top to bottom</li>
        <li>Dashed arrows are returns</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.sq { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; font-family: "Fira Code", monospace; }
.diagram { position: relative; height: 300px; }
.actor { position: absolute; top: 0; transform: translateX(-50%); padding: .45rem .9rem; border: 1px solid var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.1); color: #fff; font-size: .85rem; white-space: nowrap; }
.life { position: absolute; top: 38px; bottom: 0; width: 0; border-left: 1px dashed var(--bp-line); }
.msg { position: absolute; height: 0; }
.msg .line { position: relative; height: 0; border-top: 1.5px solid var(--bp-blue); }
.msg.ret .line { border-top-style: dashed; }
.msg.live .line { border-top-color: var(--bp-cyan); box-shadow: 0 0 8px rgba(34,211,238,.5); }
.head { position: absolute; top: -4px; width: 0; height: 0; border: 5px solid transparent; }
.head.r { right: -1px; border-left-color: var(--bp-blue); }
.head.l { left: -1px; border-right-color: var(--bp-blue); }
.lbl { position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: .72rem; color: var(--bp-ink); white-space: nowrap; }
.token { position: absolute; top: -4px; width: 8px; height: 8px; border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.token.go-r { animation: tr .6s ease forwards; } .token.go-l { animation: tl .6s ease forwards; }
@keyframes tr { from { left: 0; } to { left: 100%; } }
@keyframes tl { from { left: 100%; } to { left: 0; } }
.panel { display: flex; flex-direction: column; gap: .8rem; }
.btns { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .82rem; padding: .5rem .8rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); cursor: pointer; }
.b.alt { color: #fff; } .b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
.prog { font-size: .76rem; color: var(--bp-dim); }
</style>
