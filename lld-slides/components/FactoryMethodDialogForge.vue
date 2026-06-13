<script setup lang="ts">
import { ref } from 'vue'

type Creator = { name: string; product: string; output: string }
const base: Creator[] = [
  { name: 'WebDialog',     product: 'HtmlButton',   output: '<button>Click</button>' },
  { name: 'DesktopDialog', product: 'NativeButton', output: '[ Click ]' },
]
const creators = ref<Creator[]>([...base])
const added = ref(false)
const active = ref(-1)
const phase = ref<'idle' | 'run' | 'done'>('idle')
let busy = false

function pick(i: number) {
  if (busy) return
  busy = true
  active.value = i; phase.value = 'run'
  setTimeout(() => { phase.value = 'done'; busy = false }, 850)
}
function addMobile() {
  if (added.value) return
  added.value = true
  creators.value.push({ name: 'MobileDialog', product: 'ToastButton', output: 'toast("Click")' })
}
function reset() { creators.value = [...base]; added.value = false; active.value = -1; phase.value = 'idle' }
const cur = () => creators.value[active.value]
</script>

<template>
  <div class="fm">
    <div class="left">
      <!-- creator tiles -->
      <div class="tiles">
        <button v-for="(c, i) in creators" :key="c.name" class="tile" :class="{ on: active === i, fresh: c.name === 'MobileDialog' }" @click="pick(i)">
          {{ c.name }}<span class="ov">create_button()</span>
        </button>
        <button v-if="!added" class="tile add" @click="addMobile">+ MobileDialog</button>
      </div>

      <!-- the render() pipeline (never changes) -->
      <div class="pipe">
        <div class="box" :class="{ lit: phase !== 'idle' }">render()</div>
        <div class="link"><span class="tok" :class="{ go: phase === 'run' }" /></div>
        <div class="box mid" :class="{ lit: phase !== 'idle' }">create_button()<span class="hook">factory method</span></div>
        <div class="link" /><div class="box" :class="{ lit: phase === 'done' }">show output</div>
      </div>

      <!-- product lane -->
      <div class="prods">
        <div v-for="(c, i) in creators" :key="c.product" class="prod" :class="{ on: phase === 'done' && active === i }">{{ c.product }}</div>
      </div>

      <div class="out" :class="{ live: phase === 'done' }">
        <span v-if="phase === 'done'">{{ cur().name }} → {{ cur().output }}</span>
        <span v-else class="bp-dim">pick a Creator to run render()</span>
      </div>
    </div>

    <div class="panel">
      <button class="b ghost" @click="reset">reset</button>
      <transition name="fade"><div v-if="added" class="ocp">New dialog = new subclass. No existing class was edited — Open/Closed.</div></transition>
      <ul class="kpts bp-dim text-sm">
        <li>One render() workflow, fixed for every dialog</li>
        <li>The subclass you pick decides which Product is forged</li>
        <li>Add a dialog by subclassing — never by editing render()</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.fm { display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.6rem; font-family: "Fira Code", monospace; }
.left { display: flex; flex-direction: column; gap: 1rem; min-width: 0; }
.tiles { display: flex; flex-wrap: wrap; gap: .5rem; }
.tile { font-family: inherit; display: flex; flex-direction: column; align-items: flex-start; gap: .15rem; font-size: .8rem; padding: .45rem .75rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 9px; background: rgba(255,255,255,.03); cursor: pointer; transition: all .25s; }
.tile .ov { font-size: .58rem; color: var(--bp-dim); }
.tile.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.tile.add { border-style: dashed; color: var(--bp-dim); justify-content: center; }
.tile.fresh { animation: slidein .5s ease; }
@keyframes slidein { from { opacity: 0; transform: translateX(24px); } to { opacity: 1; transform: translateX(0); } }
.pipe { display: grid; grid-template-columns: 1fr 40px 1.3fr 40px 1fr; align-items: center; }
.box { text-align: center; font-size: .72rem; padding: .5rem .4rem; border: 1px solid var(--bp-line); border-radius: 9px; color: var(--bp-dim); background: rgba(255,255,255,.02); transition: all .3s; position: relative; }
.box.lit { border-color: var(--bp-cyan); color: #fff; }
.box.mid .hook { display: block; font-size: .55rem; color: var(--bp-violet); }
.link { position: relative; height: 2px; background: var(--bp-line); }
.tok { position: absolute; top: -3px; left: 0; width: 8px; height: 8px; border-radius: 999px; background: var(--bp-cyan); opacity: 0; box-shadow: var(--bp-glow); }
.tok.go { animation: tok .8s ease forwards; }
@keyframes tok { 0%{left:0;opacity:1} 100%{left:100%;opacity:1} }
.prods { display: flex; gap: .6rem; justify-content: center; }
.prod { font-size: .72rem; padding: .35rem .7rem; border: 1px solid var(--bp-line); border-radius: 8px; color: var(--bp-dim); transition: all .3s; }
.prod.on { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); transform: scale(1.08); box-shadow: var(--bp-glow); }
.out { font-size: .8rem; color: var(--bp-cyan); padding: .5rem .7rem; border: 1px solid var(--bp-line); border-radius: 9px; min-height: 1.2rem; }
.out.live { border-color: rgba(34,211,238,.3); background: rgba(34,211,238,.05); }
.panel { display: flex; flex-direction: column; gap: .9rem; align-items: flex-start; }
.b { font-family: inherit; font-size: .8rem; padding: .45rem .85rem; border-radius: 8px; cursor: pointer; border: 1px solid var(--bp-line); color: var(--bp-dim); background: transparent; }
.ocp { font-size: .68rem; color: var(--bp-violet); border: 1px solid rgba(167,139,250,.35); border-radius: 8px; padding: .4rem .6rem; }
.fade-enter-active { transition: opacity .4s; } .fade-enter-from { opacity: 0; }
</style>
