<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Store = 'memory' | 'sql' | 'mongo'

const STORES: Record<Store, { label: string; shape: string; kind: string; row: (id: string) => string }> = {
  memory: { label: 'InMemory', shape: 'dict', kind: '{ }', row: id => `${id}: <Order>` },
  sql:    { label: 'SQL',      shape: 'TABLE orders', kind: '▦', row: id => `| ${id} | Order |` },
  mongo:  { label: 'Mongo',    shape: 'collection orders', kind: '◇', row: id => `{ _id: ${id} }` },
}

const store = ref<Store>('memory')
const rows = ref<string[]>([])           // stored ids, e.g. ['#42']
const inserting = ref(false)             // store panel insert flash
const loaded = ref(false)                // domain shows the fetched order
const skin = ref(false)                  // store re-skin caption flash
const token = ref<'' | 'out' | 'back'>('') // wire token: out = domain→store, back = store→domain
const tokenLabel = ref('')
const domainEdits = ref(0)               // pinned badge — stays 0 forever
let busy = false
const timers: ReturnType<typeof setTimeout>[] = []

function later(fn: () => void, ms: number) { timers.push(setTimeout(fn, ms)) }
function clearAll() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearAll)

const cur = computed(() => STORES[store.value])
const has42 = computed(() => rows.value.includes('#42'))

// board coordinates (percent) — Domain → Repository → Store
const DOMAIN = { x: 13, y: 50 }
const REPO = { x: 50, y: 50 }
const STOREN = { x: 86, y: 50 }

function setStore(s: Store) {
  if (busy || store.value === s) return
  store.value = s
  skin.value = true
  later(() => { skin.value = false }, 1100)
}

function save() {
  if (busy) return
  if (has42.value) return
  busy = true
  clearAll()
  loaded.value = false
  token.value = 'out'
  tokenLabel.value = 'order#42'
  // token travels domain → store, then row appears with insert flash
  later(() => {
    token.value = ''
    rows.value = ['#42']
    inserting.value = true
    busy = false
    later(() => { inserting.value = false }, 700)
  }, 620)
}

function load() {
  if (busy) return
  if (!has42.value) return
  busy = true
  clearAll()
  loaded.value = false
  token.value = 'out'
  tokenLabel.value = 'get(42)'
  later(() => {
    // return token carries #42 back to the domain
    token.value = 'back'
    tokenLabel.value = '#42'
    later(() => {
      token.value = ''
      loaded.value = true
      busy = false
    }, 620)
  }, 620)
}

function reset() {
  clearAll()
  busy = false
  rows.value = []
  inserting.value = false
  loaded.value = false
  token.value = ''
  tokenLabel.value = ''
}
</script>

<template>
  <div class="rs">
    <div class="stage">
      <div class="board">
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <line :x1="DOMAIN.x" :y1="DOMAIN.y" :x2="REPO.x" :y2="REPO.y"
                class="wire" :class="{ hot: token }" />
          <line :x1="REPO.x" :y1="REPO.y" :x2="STOREN.x" :y2="STOREN.y"
                class="wire" :class="{ hot: token }" />
        </svg>

        <!-- traveling token along the full Domain↔Store rail -->
        <div v-if="token" class="token" :class="token">
          <span class="dot" /><span class="tl">{{ tokenLabel }}</span>
        </div>

        <!-- DOMAIN -->
        <div class="node domain" :class="{ loaded }" :style="{ left: DOMAIN.x + '%', top: DOMAIN.y + '%' }">
          <span class="nt">Domain · OrderService</span>
          <span class="call">repo.add(order)</span>
          <span class="call">repo.get(42)</span>
          <span class="loadrow" :class="{ show: loaded }">→ Order #42 loaded</span>
          <span class="pin">domain edits: {{ domainEdits }}</span>
        </div>

        <!-- REPOSITORY interface -->
        <div class="node repo" :style="{ left: REPO.x + '%', top: REPO.y + '%' }">
          <span class="iface">«interface»</span>
          <span class="rname">OrderRepository</span>
          <span class="sig">+ add() · + get()</span>
        </div>

        <!-- STORE panel -->
        <div class="node sstore" :class="[store, { flash: inserting }]" :style="{ left: STOREN.x + '%', top: STOREN.y + '%' }">
          <span class="nt">{{ cur.label }}</span>
          <span class="shape">{{ cur.shape }} <i>{{ cur.kind }}</i></span>
          <div class="rowbox">
            <transition-group name="row">
              <span v-for="id in rows" :key="id" class="row">{{ cur.row(id) }}</span>
            </transition-group>
            <span v-if="!rows.length" class="rowempty">empty</span>
          </div>
        </div>

        <transition name="cap">
          <div v-if="skin" class="caption">same interface, different backend</div>
        </transition>
      </div>
    </div>

    <div class="panel">
      <div class="lab">Store</div>
      <div class="seg">
        <button :class="{ on: store === 'memory' }" :disabled="busy" @click="setStore('memory')">InMemory</button>
        <button :class="{ on: store === 'sql' }" :disabled="busy" @click="setStore('sql')">SQL</button>
        <button :class="{ on: store === 'mongo' }" :disabled="busy" @click="setStore('mongo')">Mongo</button>
      </div>
      <div class="btns">
        <button class="b" :disabled="busy || has42" @click="save">▶ Save</button>
        <button class="b" :disabled="busy || !has42" @click="load">↩ Fetch</button>
        <button class="b ghost" @click="reset">⟲ reset</button>
      </div>
      <ul class="kpts">
        <li>Domain calls one interface — the wire never changes</li>
        <li>Swap the store: dict ▸ table ▸ collection, caller untouched</li>
        <li>Save writes #42; Fetch carries it back to the domain</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.rs { display: grid; grid-template-columns: 1.6fr 1fr; gap: 1.6rem; width: 100%; height: 340px; box-sizing: border-box; font-family: "Fira Code", monospace; color: var(--bp-ink); }
.stage { min-width: 0; }
.board { position: relative; width: 100%; height: 320px; }

.wires { position: absolute; inset: 0; width: 100%; height: 100%; }
.wire { stroke: var(--bp-line); stroke-width: .5; transition: stroke .3s, filter .3s; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: .9; filter: drop-shadow(0 0 3px var(--bp-cyan)); }

/* token travels along the rail between domain (13%) and store (86%) */
.token { position: absolute; top: 50%; transform: translate(-50%, -50%); display: flex; align-items: center; gap: .35rem; z-index: 4; pointer-events: none; }
.token .dot { width: 9px; height: 9px; border-radius: 999px; background: var(--bp-cyan); box-shadow: var(--bp-glow); }
.token .tl { font-size: .56rem; color: var(--bp-cyan); background: var(--bp-bg); border: 1px solid var(--bp-cyan); border-radius: 999px; padding: .04rem .4rem; }
.token.out { animation: travelOut .62s ease forwards; }
.token.back { animation: travelBack .62s ease forwards; }
.token.back .dot, .token.back .tl { color: var(--bp-good); border-color: var(--bp-good); background: var(--bp-bg); }
.token.back .dot { background: var(--bp-good); box-shadow: 0 0 16px rgba(74,222,128,.5); }
@keyframes travelOut { from { left: 13%; } to { left: 86%; } }
@keyframes travelBack { from { left: 86%; } to { left: 13%; } }

.node { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; gap: .15rem; padding: .55rem .7rem; border-radius: 10px; border: 1px solid var(--bp-line); background: rgba(11,19,36,.94); white-space: nowrap; transition: border-color .3s, box-shadow .3s; }
.node .nt { font-size: .56rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }

/* DOMAIN — fixed, never re-renders its calls */
.node.domain { border-color: var(--bp-violet); z-index: 3; }
.node.domain.loaded { box-shadow: 0 0 20px rgba(74,222,128,.32); }
.call { font-size: .74rem; color: var(--bp-ink); }
.call::before { content: '▸ '; color: var(--bp-violet); }
.loadrow { font-size: .62rem; color: var(--bp-good); max-height: 0; opacity: 0; overflow: hidden; transition: max-height .3s, opacity .3s, margin .3s; }
.loadrow.show { max-height: 1.2rem; opacity: 1; margin-top: .1rem; }
.pin { margin-top: .25rem; font-size: .54rem; color: var(--bp-warn); border: 1px solid var(--bp-warn); border-radius: 999px; padding: .04rem .45rem; align-self: flex-start; }

/* REPOSITORY interface */
.node.repo { border-color: var(--bp-cyan); align-items: center; z-index: 3; }
.iface { font-size: .54rem; color: var(--bp-dim); font-style: italic; }
.rname { font-size: .78rem; color: var(--bp-cyan); }
.sig { font-size: .56rem; color: var(--bp-dim); }

/* STORE panel — re-skins per backend */
.node.sstore { min-width: 130px; z-index: 3; transition: border-color .35s, box-shadow .35s; }
.node.sstore.memory { border-color: var(--bp-cyan); }
.node.sstore.sql { border-color: var(--bp-blue); }
.node.sstore.mongo { border-color: var(--bp-good); }
.node.sstore.flash { box-shadow: var(--bp-glow); }
.shape { font-size: .68rem; color: var(--bp-ink); }
.shape i { font-style: normal; color: var(--bp-dim); margin-left: .2rem; }
.rowbox { margin-top: .3rem; display: flex; flex-direction: column; gap: .15rem; min-height: 1.1rem; }
.row { font-size: .64rem; color: var(--bp-cyan); }
.node.sstore.sql .row { color: var(--bp-blue); }
.node.sstore.mongo .row { color: var(--bp-good); }
.rowempty { font-size: .58rem; color: var(--bp-dim); letter-spacing: .08em; }
.row-enter-active { transition: opacity .3s, transform .3s; }
.row-enter-from { opacity: 0; transform: translateX(-8px); }

.caption { position: absolute; left: 50%; bottom: 6px; transform: translateX(-50%); font-size: .6rem; color: var(--bp-cyan); border: 1px solid var(--bp-line); border-radius: 999px; padding: .1rem .6rem; background: rgba(34,211,238,.08); white-space: nowrap; z-index: 5; }
.cap-enter-active, .cap-leave-active { transition: opacity .4s, transform .4s; }
.cap-enter-from, .cap-leave-to { opacity: 0; transform: translate(-50%, 6px); }

.panel { display: flex; flex-direction: column; gap: .7rem; }
.lab { font-size: .56rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); margin-bottom: -.3rem; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; width: fit-content; }
.seg button { font-family: inherit; font-size: .72rem; padding: .4rem .85rem; background: transparent; color: var(--bp-dim); cursor: pointer; border: 0; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.seg button:disabled { cursor: not-allowed; opacity: .55; }
.btns { display: flex; gap: .5rem; flex-wrap: wrap; }
.b { font-family: inherit; font-size: .76rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.b:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.kpts { list-style: none; padding: 0; margin: .2rem 0 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .3rem 0; font-size: .72rem; line-height: 1.4; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
