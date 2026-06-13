<script setup lang="ts">
import { ref } from 'vue'
const inverted = ref(false)
</script>

<template>
  <div class="dip">
    <div class="stage">
      <div class="box high">OrderService <span class="lv">high-level policy</span></div>

      <!-- direct dependency -->
      <template v-if="!inverted">
        <div class="conn down bad"><span class="a">&darr;</span><span class="t">depends on a concrete detail</span></div>
        <div class="box low bad-b">MySQLDatabase <span class="lv">low-level detail</span></div>
      </template>

      <!-- inverted: both depend on the abstraction -->
      <template v-else>
        <div class="conn down ok"><span class="a">&darr;</span></div>
        <div class="box abs">&laquo;interface&raquo; Database <span class="lv">abstraction</span></div>
        <div class="conn up ok"><span class="a">&uarr;</span><span class="t">implements</span></div>
        <div class="box low ok-b">MySQLDatabase <span class="lv">low-level detail</span></div>
      </template>
    </div>

    <div class="panel">
      <button class="invert" @click="inverted = !inverted">{{ inverted ? '↺ revert' : '⤵ invert dependency' }}</button>
      <div class="explain" :class="inverted ? 'ok' : 'bad'">
        <b v-if="!inverted">Tightly coupled.</b><b v-else>Decoupled.</b>
        {{ inverted
          ? 'Both the policy and the detail depend on the Database abstraction — swap MySQL for Postgres freely.'
          : 'OrderService points straight at MySQL — changing the database ripples upward.' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.dip { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.8rem; align-items: center; font-family: "Fira Code", monospace; }
.stage { display: flex; flex-direction: column; align-items: center; gap: .5rem; min-height: 300px; justify-content: center; }
.box { padding: .7rem 1.1rem; border-radius: 10px; border: 1px solid var(--bp-line); text-align: center; transition: all .4s; animation: fade .4s; }
.box .lv { display: block; font-size: .62rem; color: var(--bp-dim); margin-top: .2rem; }
.box.high { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.08); }
.box.abs { border-color: var(--bp-violet); color: var(--bp-violet); background: rgba(167,139,250,.1); box-shadow: 0 0 18px rgba(167,139,250,.25); }
.box.bad-b { border-color: rgba(251,113,133,.5); color: var(--bp-bad); }
.box.ok-b { border-color: rgba(74,222,128,.45); color: var(--bp-good); }
.conn { display: flex; flex-direction: column; align-items: center; }
.conn .a { font-size: 1.5rem; line-height: 1; }
.conn .t { font-size: .64rem; color: var(--bp-dim); }
.conn.bad .a { color: var(--bp-bad); } .conn.ok .a { color: var(--bp-good); }
.panel { display: flex; flex-direction: column; gap: 1rem; }
.invert { font-family: inherit; font-size: .9rem; padding: .6rem 1rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 9px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); width: fit-content; }
.explain { font-size: .9rem; line-height: 1.5; padding: .8rem 1rem; border-radius: 9px; border: 1px solid var(--bp-line); color: var(--bp-dim); }
.explain b { color: #fff; }
.explain.ok { border-color: rgba(74,222,128,.3); } .explain.bad { border-color: rgba(251,113,133,.3); }
@keyframes fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; } }
</style>
