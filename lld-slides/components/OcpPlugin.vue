<script setup lang="ts">
import { ref } from 'vue'

const shipped = ref([
  { name: 'CreditCard', icon: '▢' },
  { name: 'UPI', icon: '◇' },
])
const available = ref([
  { name: 'PayPal', icon: '◉' },
  { name: 'Crypto', icon: '◈' },
  { name: 'ApplePay', icon: '◆' },
])
const edits = ref(0)

function plug(i: number) {
  const [s] = available.value.splice(i, 1)
  shipped.value.push({ ...s, fresh: true } as any)
  setTimeout(() => { (shipped.value.at(-1) as any).fresh = false }, 700)
}
</script>

<template>
  <div class="ocp">
    <div class="context bp-card">
      <div class="bp-chip">closed for modification</div>
      <pre class="ctx">class PaymentProcessor:
    def pay(self, <span class="hl">method</span>, amount):
        <span class="hl">method</span>.pay(amount)   <span class="dim"># never changes</span></pre>
      <div class="edits">existing code edited: <b :class="{ zero: edits === 0 }">{{ edits }} lines</b></div>
    </div>

    <div class="rows">
      <div class="lbl">PaymentMethod implementations</div>
      <div class="grid">
        <div v-for="s in shipped" :key="s.name" class="chip live" :class="{ fresh: (s as any).fresh }">
          <span class="ic">{{ s.icon }}</span>{{ s.name }} <span class="ok">shipped</span>
        </div>
      </div>

      <div class="lbl mt">open for extension — plug one in</div>
      <div class="grid">
        <button v-for="(a, i) in available" :key="a.name" class="chip add" @click="plug(i)">
          <span class="ic">{{ a.icon }}</span>+ {{ a.name }}
        </button>
        <div v-if="!available.length" class="dim sm">all plugged in — zero existing code touched</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ocp { display: grid; grid-template-columns: 1fr 1.1fr; gap: 1.4rem; align-items: start; font-family: "Fira Code", monospace; }
.context { display: flex; flex-direction: column; gap: .7rem; }
.ctx { font-size: .82rem; color: var(--bp-ink); margin: 0; line-height: 1.5; white-space: pre-wrap; }
.ctx .hl { color: var(--bp-cyan); } .ctx .dim, .dim { color: var(--bp-dim); }
.edits { font-size: .82rem; color: var(--bp-dim); } .edits b { color: var(--bp-bad); } .edits b.zero { color: var(--bp-good); }
.rows { display: flex; flex-direction: column; gap: .5rem; }
.lbl { font-size: .64rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bp-dim); } .lbl.mt { margin-top: .7rem; }
.grid { display: flex; flex-wrap: wrap; gap: .5rem; }
.chip { display: flex; align-items: center; gap: .45rem; font-family: inherit; font-size: .84rem; padding: .5rem .8rem; border-radius: 9px; border: 1px solid var(--bp-line); }
.chip .ic { color: var(--bp-cyan); }
.chip.live { background: rgba(74,222,128,.06); border-color: rgba(74,222,128,.3); color: var(--bp-ink); }
.chip.live .ok { font-size: .62rem; color: var(--bp-good); margin-left: .2rem; }
.chip.fresh { animation: pop .6s ease; }
@keyframes pop { 0% { transform: translateY(-8px) scale(.9); opacity: 0; box-shadow: var(--bp-glow); } 100% { transform: none; opacity: 1; } }
.chip.add { cursor: pointer; color: var(--bp-cyan); background: rgba(34,211,238,.06); border-color: rgba(34,211,238,.3); transition: .15s; }
.chip.add:hover { background: rgba(34,211,238,.16); transform: translateY(-2px); }
.sm { font-size: .82rem; }
</style>
