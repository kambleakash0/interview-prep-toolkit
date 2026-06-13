<script setup lang="ts">
import { ref } from 'vue'
const fat = ref(true)
const CAPS = ['print', 'scan', 'fax', 'staple']
</script>

<template>
  <div class="isp">
    <div class="ctl">
      <button :class="{ on: fat }"  @click="fat = true">Fat interface</button>
      <button :class="{ on: !fat }" @click="fat = false">Segregated</button>
    </div>

    <div class="cols">
      <!-- the interface(s) -->
      <div class="side">
        <div class="lbl">interface</div>
        <div v-if="fat" class="iface bad">
          <div class="in">MultiFunctionDevice</div>
          <div class="im" v-for="c in CAPS" :key="c">+ {{ c }}()</div>
        </div>
        <div v-else class="ifaces">
          <div class="iface ok" v-for="c in CAPS" :key="c"><div class="in sm">{{ c[0].toUpperCase() + c.slice(1) }}able</div><div class="im">+ {{ c }}()</div></div>
        </div>
      </div>

      <!-- the implementer -->
      <div class="side">
        <div class="lbl">class BasicPrinter — only prints</div>
        <div class="impl">
          <div class="row ok">+ print()<span class="tag">real</span></div>
          <template v-if="fat">
            <div class="row bad" v-for="c in CAPS.slice(1)" :key="c">+ {{ c }}() &rarr; raise NotImplementedError<span class="tag bad-t">forced stub</span></div>
          </template>
          <div v-else class="clean">implements only Printable — nothing to stub</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.isp { font-family: "Fira Code", monospace; }
.ctl { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; margin-bottom: 1.4rem; }
.ctl button { font-family: inherit; font-size: .82rem; padding: .45rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.ctl button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.cols { display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.6rem; align-items: start; }
.lbl { font-size: .62rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bp-dim); margin-bottom: .5rem; }
.iface { border-radius: 10px; padding: .8rem 1rem; }
.iface.bad { border: 1px solid rgba(251,113,133,.4); background: rgba(251,113,133,.05); }
.iface.ok { border: 1px solid rgba(74,222,128,.35); background: rgba(74,222,128,.05); padding: .5rem .8rem; }
.ifaces { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
.in { color: #fff; font-size: .92rem; margin-bottom: .4rem; } .in.sm { font-size: .82rem; margin-bottom: .2rem; }
.im { color: var(--bp-dim); font-size: .82rem; }
.impl { display: flex; flex-direction: column; gap: .45rem; }
.row { font-size: .84rem; padding: .4rem .6rem; border-radius: 7px; display: flex; justify-content: space-between; align-items: center; gap: .8rem; }
.row.ok { color: var(--bp-good); background: rgba(74,222,128,.06); }
.row.bad { color: var(--bp-bad); background: rgba(251,113,133,.07); animation: fade .3s; }
.tag { font-size: .58rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 999px; padding: .1em .5em; white-space: nowrap; }
.tag.bad-t { color: var(--bp-bad); border-color: rgba(251,113,133,.4); }
.clean { color: var(--bp-good); font-size: .85rem; padding: .4rem .6rem; }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
</style>
