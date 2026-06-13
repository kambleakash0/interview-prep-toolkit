<script setup lang="ts">
import { ref, computed } from 'vue'

const size = ref<string | null>(null)
const crust = ref<string | null>(null)
const toppings = ref<string[]>([])
const chain = ref<string[]>(['StandardPizzaBuilder()'])
const frozen = ref(false)
const shake = ref(false)
const toast = ref(false)
const pulseRow = ref('')

function guard(): boolean {
  if (frozen.value) {
    shake.value = true; toast.value = true
    setTimeout(() => { shake.value = false }, 400)
    setTimeout(() => { toast.value = false }, 1400)
    return true
  }
  return false
}
function hit(row: string) { pulseRow.value = row; setTimeout(() => { pulseRow.value = '' }, 450) }

function setSize() { if (guard()) return; size.value = 'large'; chain.value.push(".size('large')"); hit('size') }
function setCrust() { if (guard()) return; crust.value = 'stuffed'; chain.value.push(".crust('stuffed')"); hit('crust') }
function add(t: string) { if (guard()) return; if (!toppings.value.includes(t)) toppings.value.push(t); chain.value.push(`.add('${t}')`); hit('top') }
function build() { if (frozen.value) return; chain.value.push('.build()'); frozen.value = true }
function reset() { size.value = null; crust.value = null; toppings.value = []; chain.value = ['StandardPizzaBuilder()']; frozen.value = false; toast.value = false }

const product = computed(() => {
  const tops = toppings.value.length ? toppings.value.join(', ') : 'no toppings'
  return `${size.value || 'medium'} ${crust.value || 'thin'}-crust · ${tops}`
})
</script>

<template>
  <div class="bd">
    <div class="left">
      <div class="chainstrip">
        <span v-for="(c, i) in chain" :key="i" class="seg" :class="{ build: c === '.build()' }">{{ c }}</span>
        <span class="curl" v-if="!frozen">↩ return self</span>
      </div>

      <div class="draft" :class="{ shake, frozen }">
        <div class="dh">{{ frozen ? 'Product · immutable' : 'Builder draft' }} <span v-if="frozen" class="lk">locked</span></div>
        <div class="row" :class="{ set: size, pulse: pulseRow === 'size' }"><span class="k">size</span><span class="v">{{ size || 'medium' }}</span></div>
        <div class="row" :class="{ set: crust, pulse: pulseRow === 'crust' }"><span class="k">crust</span><span class="v">{{ crust || 'thin' }}</span></div>
        <div class="row" :class="{ set: toppings.length, pulse: pulseRow === 'top' }">
          <span class="k">toppings</span>
          <span class="v chips"><span v-if="!toppings.length" class="ghost">none</span><span v-for="t in toppings" :key="t" class="chip">{{ t }}</span></span>
        </div>
      </div>
      <transition name="fade"><div v-if="toast" class="toast">product is frozen — build() already called</div></transition>
    </div>

    <div class="panel">
      <div class="btns">
        <button class="b" :disabled="frozen" @click="setSize">.size('large')</button>
        <button class="b" :disabled="frozen" @click="setCrust">.crust('stuffed')</button>
        <button class="b" :disabled="frozen" @click="add('mushroom')">.add('mushroom')</button>
        <button class="b" :disabled="frozen" @click="add('olive')">.add('olive')</button>
        <button class="b go" :disabled="frozen" @click="build">.build()</button>
        <button class="b ghost" @click="reset">reset</button>
      </div>
      <ul class="kpts bp-dim text-sm">
        <li>Each setter mutates scratch state and returns <b>self</b> — so calls chain</li>
        <li>Skip a field and it keeps its default — no nulls, any order</li>
        <li>build() freezes the result; the draft can't change after</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.bd { display: grid; grid-template-columns: 1.4fr 1fr; gap: 1.6rem; font-family: "Fira Code", monospace; }
.left { display: flex; flex-direction: column; gap: .8rem; min-width: 0; }
.chainstrip { display: flex; flex-wrap: wrap; align-items: center; gap: .15rem; font-size: .72rem; padding: .6rem .7rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02); min-height: 2.4rem; }
.seg { color: var(--bp-cyan); }
.seg.build { color: var(--bp-good); }
.curl { color: var(--bp-dim); font-size: .62rem; margin-left: .4rem; }
.draft { display: flex; flex-direction: column; gap: .4rem; padding: .8rem .9rem; border: 1px solid var(--bp-line); border-radius: 11px; background: rgba(255,255,255,.02); transition: all .35s; }
.draft.frozen { background: rgba(255,255,255,.05); border-color: rgba(74,222,128,.4); filter: grayscale(.25); }
.draft.shake { animation: sh .4s; border-color: var(--bp-bad); }
@keyframes sh { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
.dh { font-size: .7rem; color: var(--bp-dim); margin-bottom: .2rem; text-transform: uppercase; letter-spacing: .06em; }
.dh .lk { color: var(--bp-good); margin-left: .4rem; }
.row { display: flex; align-items: center; gap: 1rem; padding: .35rem .6rem; border: 1px solid transparent; border-radius: 7px; transition: all .3s; }
.row.set { background: rgba(34,211,238,.06); }
.row.pulse { border-color: var(--bp-cyan); transform: scale(1.02); }
.row .k { width: 88px; color: var(--bp-dim); font-size: .76rem; }
.row .v { color: var(--bp-ink); font-size: .82rem; }
.row.set .v { color: #fff; }
.ghost { color: var(--bp-dim); opacity: .5; }
.chips { display: inline-flex; gap: .3rem; flex-wrap: wrap; }
.chip { font-size: .68rem; padding: .12rem .5rem; border-radius: 999px; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.toast { font-size: .68rem; color: var(--bp-bad); border: 1px solid rgba(251,113,133,.4); border-radius: 8px; padding: .4rem .6rem; }
.fade-enter-active,.fade-leave-active { transition: opacity .3s; } .fade-enter-from,.fade-leave-to { opacity: 0; }
.panel { display: flex; flex-direction: column; gap: 1rem; }
.btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.b { font-family: inherit; font-size: .72rem; padding: .4rem .6rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 7px; background: rgba(255,255,255,.03); cursor: pointer; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.go { border-color: var(--bp-good); color: var(--bp-good); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .35; cursor: not-allowed; }
</style>
