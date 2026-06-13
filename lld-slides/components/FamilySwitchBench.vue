<script setup lang="ts">
import { ref, computed } from 'vue'

const FAM = {
  postgres: { conn: 'PgConn',  dsn: 'postgresql://app', dialect: 'PgDialect', page: 'LIMIT 10' },
  mysql:    { conn: 'MyConn',  dsn: 'mysql://app',      dialect: 'MyDialect', page: 'LIMIT 10 OFFSET 0' },
} as const
type Fam = keyof typeof FAM

const factory = ref<Fam>('postgres')
const mixing = ref(false)
const connFam = ref<Fam>('postgres')
const dialFam = ref<Fam>('postgres')
const flipping = ref(false)

function setFactory(f: Fam) {
  if (factory.value === f) return
  flipping.value = true
  factory.value = f; connFam.value = f; dialFam.value = f
  setTimeout(() => { flipping.value = false }, 320)
}
function toggleMix() {
  mixing.value = !mixing.value
  if (!mixing.value) { connFam.value = factory.value; dialFam.value = factory.value }
}
const mismatch = computed(() => connFam.value !== dialFam.value)
</script>

<template>
  <div class="af">
    <div class="left">
      <div class="callline">run(factory) → <b>connection().dsn()</b> | <b>dialect().paginate(10)</b>
        <span class="held">caller never changes</span>
      </div>

      <div class="slots">
        <div class="slot" :class="{ flip: flipping, bad: mismatch }">
          <div class="slabel">Connection</div>
          <div class="cls">{{ FAM[connFam].conn }}</div>
          <div class="val">{{ FAM[connFam].dsn }}</div>
          <div v-if="mixing" class="pick">
            <button :class="{ on: connFam==='postgres' }" @click="connFam='postgres'">Pg</button>
            <button :class="{ on: connFam==='mysql' }" @click="connFam='mysql'">My</button>
          </div>
        </div>
        <div class="slot" :class="{ flip: flipping, bad: mismatch }">
          <div class="slabel">Dialect</div>
          <div class="cls">{{ FAM[dialFam].dialect }}</div>
          <div class="val">{{ FAM[dialFam].page }}</div>
          <div v-if="mixing" class="pick">
            <button :class="{ on: dialFam==='postgres' }" @click="dialFam='postgres'">Pg</button>
            <button :class="{ on: dialFam==='mysql' }" @click="dialFam='mysql'">My</button>
          </div>
        </div>
      </div>

      <div class="outbar" :class="{ bad: mismatch }">
        <span v-if="!mismatch">{{ FAM[connFam].dsn }} · {{ FAM[dialFam].page }}</span>
        <span v-else><s>{{ FAM[connFam].dsn }} · {{ FAM[dialFam].page }}</s> <span class="badge">mismatched family</span></span>
      </div>
    </div>

    <div class="panel">
      <div class="seg" :class="{ dim: mixing }">
        <button :class="{ on: factory==='postgres' }" :disabled="mixing" @click="setFactory('postgres')">Postgres</button>
        <button :class="{ on: factory==='mysql' }"   :disabled="mixing" @click="setFactory('mysql')">MySQL</button>
      </div>
      <label class="tog" :class="{ on: mixing }" @click="toggleMix"><span class="knob" /> allow mixing</label>
      <ul class="kpts bp-dim text-sm">
        <li>One factory yields a whole matched family</li>
        <li>Flip it — both products swap, the caller stays put</li>
        <li>Mix families by hand and the pair breaks</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.af { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.6rem; font-family: "Fira Code", monospace; }
.left { display: flex; flex-direction: column; gap: .9rem; min-width: 0; }
.callline { font-size: .74rem; color: var(--bp-dim); padding: .55rem .7rem; border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.02); position: relative; }
.callline b { color: var(--bp-ink); }
.held { display: block; font-size: .58rem; color: var(--bp-cyan); margin-top: .25rem; }
.slots { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.slot { display: flex; flex-direction: column; gap: .3rem; padding: .8rem .9rem; border: 1px solid var(--bp-line); border-radius: 11px; background: rgba(255,255,255,.03); transition: transform .32s; }
.slot.flip { animation: flip .32s ease; }
@keyframes flip { 0%{transform:rotateY(0)} 50%{transform:rotateY(90deg)} 100%{transform:rotateY(0)} }
.slot.bad { border-color: var(--bp-bad); animation: shk .3s; }
@keyframes shk { 0%,100%{transform:translateX(0)} 30%{transform:translateX(-4px)} 70%{transform:translateX(4px)} }
.slabel { font-size: .62rem; text-transform: uppercase; letter-spacing: .08em; color: var(--bp-dim); }
.cls { color: #fff; font-size: .95rem; }
.val { color: var(--bp-cyan); font-size: .74rem; }
.pick { display: flex; gap: .3rem; margin-top: .3rem; }
.pick button { font-family: inherit; font-size: .64rem; padding: .15rem .55rem; border: 1px solid var(--bp-line); color: var(--bp-dim); border-radius: 6px; background: transparent; cursor: pointer; }
.pick button.on { border-color: var(--bp-cyan); color: var(--bp-cyan); background: rgba(34,211,238,.1); }
.outbar { font-size: .78rem; color: var(--bp-good); padding: .5rem .7rem; border: 1px solid rgba(74,222,128,.3); border-radius: 9px; background: rgba(74,222,128,.05); }
.outbar.bad { color: var(--bp-bad); border-color: rgba(251,113,133,.35); background: rgba(251,113,133,.05); }
.outbar .badge { font-size: .6rem; border: 1px solid var(--bp-bad); border-radius: 999px; padding: .05rem .45rem; margin-left: .4rem; }
.panel { display: flex; flex-direction: column; gap: 1rem; align-items: flex-start; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg.dim { opacity: .4; }
.seg button { font-family: inherit; font-size: .8rem; padding: .45rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.seg button:disabled { cursor: not-allowed; }
.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .76rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(167,139,250,.4); } .tog.on .knob::after { left: 16px; background: var(--bp-violet); }
.tog.on { color: var(--bp-violet); }
</style>
