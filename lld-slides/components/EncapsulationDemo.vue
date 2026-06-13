<script setup lang="ts">
import { ref } from 'vue'

const encapsulated = ref(true)
const balance = ref(120)
const flash = ref(false)
const log = ref<{ t: string; c: string }[]>([
  { t: 'account = BankAccount(balance=120)', c: 'dim' },
])

function push(t: string, c = 'ok') {
  log.value.push({ t, c })
  if (log.value.length > 5) log.value.shift()
}
function doFlash() { flash.value = true; setTimeout(() => (flash.value = false), 450) }

function deposit()  { balance.value += 100; push('account.deposit(100)  → ok', 'good'); doFlash() }
function withdraw() {
  if (balance.value >= 40) { balance.value -= 40; push('account.withdraw(40)  → ok', 'good'); doFlash() }
  else push('account.withdraw(40)  → InsufficientFunds', 'bad')
}
function getBal()   { push(`account.get_balance()  → ${balance.value}`, 'cyan') }
function peek() {
  if (encapsulated.value) push("account._balance  → AttributeError: private", 'bad')
  else push(`account._balance  → ${balance.value}   ⚠ broke encapsulation`, 'warn')
}
</script>

<template>
  <div class="enc">
    <!-- client code / outside world -->
    <div class="bp-card col">
      <div class="hd"><span class="bp-chip">client code</span></div>
      <button class="call good" @click="deposit">account.deposit(100)</button>
      <button class="call good" @click="withdraw">account.withdraw(40)</button>
      <button class="call cyan" @click="getBal">account.get_balance()</button>
      <button class="call bad"  @click="peek">account._balance <span class="bp-dim">// reach inside</span></button>

      <div class="console">
        <div v-for="(l, i) in log" :key="i" :class="['ln', l.c]">{{ l.t }}</div>
      </div>
    </div>

    <!-- the object -->
    <div :class="['bp-card', 'col', 'obj', encapsulated ? 'bp-card--cyan' : 'open']">
      <div class="hd">
        <span class="bp-mono" style="color:#fff">BankAccount</span>
        <label class="tgl">
          <input type="checkbox" v-model="encapsulated" />
          <svg class="ico" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <rect x="5" y="11" width="14" height="9" rx="2" />
            <path :d="encapsulated ? 'M8 11V8a4 4 0 0 1 8 0v3' : 'M8 11V8a4 4 0 0 1 7-2.6'" />
          </svg>
          <span>{{ encapsulated ? 'encapsulated' : 'exposed' }}</span>
        </label>
      </div>

      <div class="sect">public interface</div>
      <div class="mem pub">+ deposit(amount)</div>
      <div class="mem pub">+ withdraw(amount)</div>
      <div class="mem pub">+ get_balance()</div>

      <div class="sect">private state</div>
      <div :class="['mem', 'priv', { locked: encapsulated, hit: flash }]">
        <svg v-if="encapsulated" class="lock" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>
        − _balance = <b>{{ balance }}</b>
      </div>
      <div :class="['mem', 'priv', { locked: encapsulated }]">
        <svg v-if="encapsulated" class="lock" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>
        − _pin = ••••
      </div>
    </div>
  </div>
</template>

<style scoped>
.enc { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-family: "Fira Code", monospace; }
.col { display: flex; flex-direction: column; gap: .5rem; }
.hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: .3rem; }
.call {
  text-align: left; font-family: inherit; font-size: .82rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .5rem .7rem;
  background: rgba(255,255,255,.02); color: var(--bp-ink); transition: .15s;
}
.call:hover { transform: translateX(3px); border-color: var(--bp-cyan); }
.call.good:hover { border-color: var(--bp-good); }
.call.bad:hover  { border-color: var(--bp-bad); }
.console {
  margin-top: .4rem; border-top: 1px dashed var(--bp-line); padding-top: .5rem;
  font-size: .74rem; min-height: 6.2rem; display: flex; flex-direction: column; gap: 3px;
}
.ln.dim { color: var(--bp-dim); } .ln.good { color: var(--bp-good); }
.ln.cyan { color: var(--bp-cyan); } .ln.bad { color: var(--bp-bad); } .ln.warn { color: var(--bp-warn); }

.obj.open { border-style: dashed; }
.tgl { display: flex; align-items: center; gap: .4rem; font-size: .74rem; cursor: pointer; color: var(--bp-dim); }
.sect { font-size: .62rem; text-transform: uppercase; letter-spacing: .18em; color: var(--bp-dim); margin: .5rem 0 .2rem; }
.mem { font-size: .85rem; padding: .25rem .4rem; border-radius: 6px; transition: .3s; }
.mem.pub { color: var(--bp-good); }
.mem.priv { color: var(--bp-violet); position: relative; }
.mem.priv.locked { color: var(--bp-dim); filter: blur(2.5px); }
.mem.priv.locked .lock { filter: none; animation: breathe 2.4s ease-in-out infinite; }
.lock { position: relative; margin-right: .3rem; display: inline-block; }
.mem.hit { background: rgba(74,222,128,.15); filter: none !important; }
@keyframes breathe { 0%,100% { opacity:.55; transform: scale(1); } 50% { opacity:1; transform: scale(1.18); } }
</style>
