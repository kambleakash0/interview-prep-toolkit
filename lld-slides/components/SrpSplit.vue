<script setup lang="ts">
import { ref } from 'vue'
const split = ref(false)
const FOCUSED = [
  { cls: 'OrderProcessor', m: 'process_order()' },
  { cls: 'PaymentService', m: 'charge_card()' },
  { cls: 'EmailService', m: 'send_email()' },
  { cls: 'Logger', m: 'write_log()' },
  { cls: 'InventoryService', m: 'update_stock()' },
]
</script>

<template>
  <div class="srp">
    <div class="ctl">
      <button :class="{ on: !split }" @click="split = false">God class</button>
      <button :class="{ on: split }"  @click="split = true">Apply SRP</button>
    </div>

    <div v-if="!split" class="god">
      <div class="hd">class <b>OrderService</b><span class="badge bad">5 reasons to change</span></div>
      <div class="m" v-for="f in FOCUSED" :key="f.m">+ {{ f.m }}</div>
      <div class="warn">one class doing five jobs — every change risks the others</div>
    </div>

    <div v-else class="grid">
      <div class="card" v-for="(f, i) in FOCUSED" :key="f.cls" :style="{ animationDelay: 80 * i + 'ms' }">
        <div class="cn">{{ f.cls }}</div>
        <div class="cm">+ {{ f.m }}</div>
        <span class="badge ok">1 reason</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.srp { font-family: "Fira Code", monospace; }
.ctl { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; margin-bottom: 1.5rem; }
.ctl button { font-family: inherit; font-size: .82rem; padding: .45rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.ctl button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.god { border: 1px solid var(--bp-bad); border-radius: 12px; padding: 1.2rem 1.4rem; background: rgba(251,113,133,.05); max-width: 30rem; animation: fade .35s; }
.hd { font-size: 1.1rem; color: var(--bp-ink); margin-bottom: .8rem; } .hd b { color: #fff; }
.m { color: var(--bp-dim); font-size: .9rem; margin: .2rem 0; }
.warn { margin-top: .9rem; color: var(--bp-bad); font-size: .8rem; }
.badge { font-size: .6rem; padding: .15em .6em; border-radius: 999px; margin-left: .7rem; letter-spacing: .08em; }
.badge.bad { color: var(--bp-bad); border: 1px solid rgba(251,113,133,.4); }
.badge.ok { color: var(--bp-good); border: 1px solid rgba(74,222,128,.4); margin-left: 0; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; }
.card { border: 1px solid rgba(74,222,128,.3); border-radius: 11px; padding: .8rem 1rem; background: rgba(74,222,128,.05); animation: rise .45s ease both; }
.cn { color: #fff; font-size: .92rem; } .cm { color: var(--bp-dim); font-size: .8rem; margin: .35rem 0 .6rem; }
@keyframes rise { from { opacity: 0; transform: translateY(14px) scale(.95); } to { opacity: 1; transform: none; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
</style>
