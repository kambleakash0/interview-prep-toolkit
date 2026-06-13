<script setup lang="ts">
import { ref, computed } from 'vue'

const tplTags = ref<string[]>(['vip', 'beta'])
const tplWidth = 100
const mode = ref<'shallow' | 'deep'>('shallow')

const clone = ref<null | { width: number; tags: string[] }>(null)
const state = ref<'empty' | 'linked' | 'isolated' | 'corrupted'>('empty')
let extra = 0

function doClone() {
  if (mode.value === 'shallow') {
    clone.value = { width: tplWidth, tags: tplTags.value }   // SHARED reference
    state.value = 'linked'
  } else {
    clone.value = { width: tplWidth, tags: [...tplTags.value] } // deep copy
    state.value = 'isolated'
  }
}
function step(d: number) { if (clone.value) clone.value.width += d }   // scalar: never affects template
function addTag() {
  if (!clone.value) return
  const t = `tag${++extra}`
  clone.value.tags.push(t)
  if (mode.value === 'shallow') {
    // shared list: the template sees it too
    if (clone.value.tags !== tplTags.value) tplTags.value.push(t)
    state.value = 'corrupted'
  }
}
function reset() { tplTags.value = ['vip', 'beta']; clone.value = null; state.value = 'empty'; extra = 0 }

const linked = computed(() => state.value === 'linked' || state.value === 'corrupted')
const LABEL = { empty: 'no clone yet', linked: 'shallow — tags shared', isolated: 'deep — tags independent', corrupted: 'shared reference mutated!' }
</script>

<template>
  <div class="pt">
    <div class="stage">
      <!-- template -->
      <div class="card tpl">
        <div class="ct">Template</div>
        <div class="scalar"><span>width</span><b>{{ tplWidth }}</b></div>
        <div class="scalar"><span>color</span><i class="sw" /></div>
        <div class="nested" :class="{ shared: linked }">
          <div class="nlabel">tags[]</div>
          <span v-for="t in tplTags" :key="t" class="chip">{{ t }}</span>
        </div>
      </div>

      <div class="bridge" :class="{ on: linked }">
        <span class="line" /><span class="cap">{{ linked ? 'shared list' : '' }}</span>
      </div>

      <!-- clone -->
      <div class="card clone" :class="{ empty: !clone, corrupt: state==='corrupted' }">
        <template v-if="clone">
          <div class="ct">clone</div>
          <div class="scalar"><span>width</span><b class="cyan">{{ clone.width }}</b></div>
          <div class="scalar"><span>color</span><i class="sw" /></div>
          <div class="nested" :class="{ shared: linked, iso: state==='isolated' }">
            <div class="nlabel">tags[]</div>
            <span v-for="t in clone.tags" :key="t" class="chip">{{ t }}</span>
          </div>
        </template>
        <div v-else class="slotempty">clone slot</div>
      </div>
    </div>

    <div class="panel">
      <div class="seg">
        <button :class="{ on: mode==='shallow' }" @click="mode='shallow'; reset()">SHALLOW</button>
        <button :class="{ on: mode==='deep' }" @click="mode='deep'; reset()">DEEP</button>
      </div>
      <div class="btns">
        <button class="b" :disabled="!!clone" @click="doClone">clone()</button>
        <button class="b" :disabled="!clone" @click="step(10)">width +10</button>
        <button class="b" :disabled="!clone" @click="addTag">clone.tags.add()</button>
        <button class="b ghost" @click="reset">reset</button>
      </div>
      <div class="legend" :class="state">{{ LABEL[state] }}</div>
      <ul class="kpts bp-dim text-sm">
        <li>Scalars (width, color) are always copied outright</li>
        <li>Shallow copies only the <b>reference</b> to nested tags</li>
        <li>Add a tag on a shallow clone — it bleeds into the template</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.pt { display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.4rem; font-family: "Fira Code", monospace; }
.stage { display: grid; grid-template-columns: 1fr 70px 1fr; align-items: center; }
.card { display: flex; flex-direction: column; gap: .45rem; padding: .8rem .9rem; border: 1px solid var(--bp-line); border-radius: 12px; background: rgba(255,255,255,.03); transition: all .35s; }
.clone.empty { border-style: dashed; opacity: .5; align-items: center; justify-content: center; min-height: 150px; }
.clone.corrupt { border-color: var(--bp-bad); box-shadow: 0 0 16px rgba(251,113,133,.4); }
.ct { font-size: .62rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-dim); }
.scalar { display: flex; justify-content: space-between; align-items: center; font-size: .78rem; color: var(--bp-dim); }
.scalar b { color: #fff; } .scalar b.cyan { color: var(--bp-cyan); }
.sw { width: 14px; height: 14px; border-radius: 4px; background: var(--bp-cyan); display: inline-block; }
.nested { border: 1px solid var(--bp-line); border-radius: 8px; padding: .4rem .5rem; display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; transition: all .35s; }
.nested.shared { border-color: var(--bp-warn); background: rgba(251,191,36,.06); }
.nested.iso { border-color: var(--bp-good); background: rgba(74,222,128,.05); }
.nlabel { font-size: .6rem; color: var(--bp-dim); width: 100%; }
.chip { font-size: .66rem; padding: .1rem .45rem; border-radius: 999px; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.slotempty { font-size: .72rem; color: var(--bp-dim); }
.bridge { position: relative; height: 100%; display: flex; align-items: center; justify-content: center; }
.bridge .line { width: 100%; height: 2px; background: var(--bp-line); transition: all .3s; }
.bridge.on .line { background: var(--bp-warn); box-shadow: 0 0 8px rgba(251,191,36,.5); }
.bridge .cap { position: absolute; top: 30%; font-size: .56rem; color: var(--bp-warn); white-space: nowrap; }
.panel { display: flex; flex-direction: column; gap: .8rem; align-items: flex-start; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg button { font-family: inherit; font-size: .74rem; padding: .4rem .9rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.btns { display: flex; flex-wrap: wrap; gap: .45rem; }
.b { font-family: inherit; font-size: .72rem; padding: .4rem .65rem; border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 7px; background: rgba(255,255,255,.03); cursor: pointer; }
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.ghost { color: var(--bp-dim); }
.b:disabled { opacity: .35; cursor: not-allowed; }
.legend { font-size: .72rem; padding: .35rem .65rem; border-radius: 7px; border: 1px solid var(--bp-line); color: var(--bp-dim); }
.legend.linked { color: var(--bp-warn); border-color: rgba(251,191,36,.35); }
.legend.isolated { color: var(--bp-good); border-color: rgba(74,222,128,.35); }
.legend.corrupted { color: var(--bp-bad); border-color: rgba(251,113,133,.4); }
</style>
