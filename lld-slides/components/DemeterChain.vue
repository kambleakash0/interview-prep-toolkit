<script setup lang="ts">
import { ref } from 'vue'
const good = ref(false)   // false = train-wreck, true = delegation
</script>

<template>
  <div class="dem">
    <div class="seg">
      <button :class="{ on: !good }" @click="good = false">Train wreck</button>
      <button :class="{ on: good }"  @click="good = true">Delegation</button>
    </div>

    <!-- bad: reach through strangers -->
    <div v-if="!good" class="lane bad">
      <code class="call">order<span class="reach">.get_customer()</span><span class="reach">.get_address()</span><span class="reach">.get_city()</span></code>
      <div class="hops">
        <div class="obj friend">order</div>
        <div class="arrow flow">→</div>
        <div class="obj stranger">Customer</div>
        <div class="arrow flow">→</div>
        <div class="obj stranger">Address</div>
        <div class="arrow flow">→</div>
        <div class="obj stranger">City</div>
      </div>
      <div class="note bad-t">reaches through 3 strangers — break any one and this shatters</div>
    </div>

    <!-- good: one friend -->
    <div v-else class="lane ok">
      <code class="call">order<span class="keep">.ship_to_city()</span></code>
      <div class="hops">
        <div class="obj friend">order</div>
        <div class="arrow flow ok-a">→</div>
        <div class="obj result">"Berlin"</div>
      </div>
      <div class="note ok-t">talks to one friend; Order delegates internally — callers stay decoupled</div>
    </div>
  </div>
</template>

<style scoped>
.dem { font-family: "Fira Code", monospace; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; margin-bottom: 1.6rem; }
.seg button { font-family: inherit; font-size: .82rem; padding: .45rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.lane { animation: fade .4s ease; }
@keyframes fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; } }
.call { display: block; font-size: 1.25rem; margin-bottom: 1.6rem; color: var(--bp-ink); }
.reach { color: var(--bp-bad); }
.keep { color: var(--bp-good); }
.hops { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.2rem; }
.obj { padding: .6rem 1rem; border-radius: 9px; border: 1px solid var(--bp-line); font-size: .95rem; }
.obj.friend { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.obj.stranger { border-color: var(--bp-bad); color: var(--bp-bad); background: rgba(251,113,133,.06); }
.obj.result { border-color: var(--bp-good); color: var(--bp-good); background: rgba(74,222,128,.06); }
.arrow { font-size: 1.4rem; color: var(--bp-dim); }
.arrow.flow { animation: slide 1.2s ease-in-out infinite; }
.arrow.ok-a { color: var(--bp-good); animation: none; }
@keyframes slide { 0%,100% { transform: translateX(0); opacity: .5; } 50% { transform: translateX(4px); opacity: 1; } }
.note { font-size: .85rem; padding: .5rem .8rem; border-radius: 8px; border: 1px solid var(--bp-line); }
.note.bad-t { color: var(--bp-bad); } .note.ok-t { color: var(--bp-good); }
</style>
