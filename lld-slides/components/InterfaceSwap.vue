<script setup lang="ts">
import { ref } from 'vue'

const IMPLS = [
  { name: 'Stripe',   out: 'charge_stripe(amt)',   c: '#22d3ee' },
  { name: 'Razorpay', out: 'razorpay.capture(amt)', c: '#a78bfa' },
  { name: 'PayPal',   out: 'paypal.checkout(amt)',  c: '#38bdf8' },
]
const active = ref(0)
const log = ref('')
function plug(i: number) { active.value = i; log.value = '' }
function pay() {
  const im = IMPLS[active.value]
  log.value = `${im.name}.pay(99) → ${im.out}`
}
</script>

<template>
  <div class="is">
    <!-- the consumer, unchanged -->
    <div class="checkout">
      <span class="lbl">Checkout</span>
      <div class="slot" :style="{ borderColor: IMPLS[active].c }">
        gateway: <b :style="{ color: IMPLS[active].c }">«{{ IMPLS[active].name }}»</b>
      </div>
      <span class="bp-dim note">never edited — it only knows the contract</span>
    </div>

    <div class="arrow">PaymentGateway ▾</div>

    <div class="impls">
      <button v-for="(im, i) in IMPLS" :key="im.name" class="chip"
              :class="{ on: i === active }"
              :style="i === active ? { borderColor: im.c, color: im.c } : {}"
              @click="plug(i)">{{ im.name }}</button>
    </div>

    <div class="ctl">
      <button class="b" @click="pay">checkout.process(99)</button>
    </div>
    <div class="log" :class="{ live: log }">{{ log || 'plug a gateway, then run checkout' }}</div>
  </div>
</template>

<style scoped>
.is { font-family: "Fira Code", monospace; display: flex; flex-direction: column; gap: .7rem; }
.checkout { display: flex; flex-direction: column; gap: .4rem; padding: .7rem .9rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.03); }
.checkout .lbl { color: #fff; font-size: .9rem; }
.slot { padding: .35rem .7rem; border: 1px dashed; border-radius: 8px; font-size: .76rem; color: var(--bp-ink); width: fit-content; transition: border-color .3s; }
.note { font-size: .66rem; }
.arrow { font-size: .68rem; color: var(--bp-dim); padding-left: .4rem; }
.impls { display: flex; gap: .5rem; }
.chip { font-family: inherit; font-size: .78rem; padding: .4rem .9rem; border: 1px solid var(--bp-line); color: var(--bp-dim); border-radius: 8px; background: transparent; cursor: pointer; transition: all .25s; }
.chip.on { background: rgba(34,211,238,.08); transform: translateY(-1px); }
.ctl { margin-top: .2rem; }
.b { font-family: inherit; font-size: .82rem; padding: .45rem .9rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.log { font-size: .76rem; color: var(--bp-dim); padding: .55rem .7rem; border: 1px solid var(--bp-line); border-radius: 8px; min-height: 1.2rem; }
.log.live { color: var(--bp-cyan); border-color: rgba(34,211,238,.3); }
</style>
