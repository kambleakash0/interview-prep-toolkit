<script setup lang="ts">
import { ref, computed } from 'vue'

type Role = 'guest' | 'admin'
type Branch = '' | 'DENIED' | 'BUILD' | 'REUSE'
type Phase = '' | 'forward' | 'reverse' | 'deliver'

const role = ref<Role>('guest')
const built = ref(false)          // RealSubject instantiated?
const counter = ref(0)            // RealSubject instances created
const active = ref<Branch>('')    // which branch the last click took
const phase = ref<Phase>('')      // token animation phase
const pulse = ref(false)          // one-time decrypting throb
const chip = ref('')              // result chip text, e.g. secret::key
const log = ref('idle')
const keyN = ref(0)

let busy = false
const timers: number[] = []
function after(ms: number, fn: () => void) {
  timers.push(window.setTimeout(fn, ms))
}
function clearTimers() {
  timers.forEach((id) => window.clearTimeout(id))
  timers.length = 0
}

const branches: Exclude<Branch, ''>[] = ['DENIED', 'BUILD', 'REUSE']

function read() {
  if (busy) return
  busy = true
  chip.value = ''
  const k = `key${++keyN.value}`

  // resolve which branch this click takes
  let branch: Branch
  if (role.value !== 'admin') branch = 'DENIED'
  else if (!built.value) branch = 'BUILD'
  else branch = 'REUSE'
  active.value = branch

  // token: Client -> Proxy
  phase.value = 'forward'
  log.value = `read("${k}") -> proxy`

  after(560, () => {
    if (branch === 'DENIED') {
      // token reverses back to Client; RealSubject untouched
      log.value = `DENIED (${role.value}) -> client`
      phase.value = 'reverse'
      after(560, () => { phase.value = ''; busy = false })
      return
    }

    if (branch === 'BUILD') {
      // dashed-grey -> solid, decrypting pulse, counter ++
      built.value = true
      counter.value = 1
      pulse.value = true
      log.value = '[RealVault] decrypting...'
      after(600, () => { pulse.value = false })
    } else {
      log.value = 'cache hit - reuse RealVault'
    }

    // token continues Proxy -> RealSubject
    phase.value = 'deliver'
    after(560, () => {
      chip.value = `secret::${k}`
      log.value = `secret::${k} -> client`
      // result chip animates back to Client
      phase.value = 'reverse'
      after(620, () => { phase.value = ''; busy = false })
    })
  })
}

function setRole(r: Role) {
  if (role.value === r) return
  role.value = r
  // toggling role does NOT destroy the RealSubject
  if (!busy) { active.value = ''; chip.value = '' }
  log.value = `role = ${r}`
}

function reset() {
  clearTimers()
  busy = false
  built.value = false
  counter.value = 0
  active.value = ''
  phase.value = ''
  pulse.value = false
  chip.value = ''
  keyN.value = 0
  log.value = 'cache cleared'
}

const tokenForward = computed(() => phase.value === 'forward')
const tokenDeliver = computed(() => phase.value === 'deliver')
const tokenReverse = computed(() => phase.value === 'reverse')
const denied = computed(() => active.value === 'DENIED')
const activeClass = computed(() => active.value.toLowerCase())

const BRANCH_DESC: Record<Exclude<Branch, ''>, string> = {
  DENIED: 'role != admin -> block, real never built',
  BUILD: 'first admin call -> build + delegate',
  REUSE: 'cached real -> delegate straight through',
}

function branchDesc(b: Branch): string {
  if (b === '') return ''
  return BRANCH_DESC[b]
}
</script>

<template>
  <div class="px">
    <!-- ============ STAGE ============ -->
    <div class="stage">
      <!-- Client -->
      <div class="node client" :class="{ recv: tokenReverse }">
        <div class="ntag">CLIENT</div>
        <div class="ncall">.read(key)</div>
        <transition name="chip">
          <div v-if="chip && tokenReverse && !denied" class="result">{{ chip }}</div>
        </transition>
        <transition name="chip">
          <div v-if="denied && tokenReverse" class="result bad">DENIED</div>
        </transition>
      </div>

      <!-- wire 1: client <-> proxy -->
      <div class="wire">
        <span class="rail" />
        <span
          class="token"
          :class="{ fwd: tokenForward, rev: tokenReverse, bad: denied }"
          v-show="tokenForward || tokenReverse"
        />
      </div>

      <!-- Proxy -->
      <div class="node proxy" :class="{ active: !!active }">
        <div class="ntag violet">PROXY</div>
        <div class="ncall">VaultProxy</div>
        <div class="badge" :class="activeClass" v-if="active">{{ active }}</div>
        <div class="badge ghost" v-else>idle</div>

        <!-- always-listed branch names -->
        <ul class="branches">
          <li v-for="b in branches" :key="b" :class="{ on: active === b }">
            <span class="bdot" /> {{ b }}
          </li>
        </ul>
      </div>

      <!-- wire 2: proxy <-> real -->
      <div class="wire">
        <span class="rail" :class="{ dead: !built }" />
        <span
          class="token"
          :class="{ fwd: tokenDeliver, rev: tokenReverse && !denied }"
          v-show="tokenDeliver || (tokenReverse && !denied)"
        />
      </div>

      <!-- RealSubject -->
      <div class="node real" :class="{ solid: built, pulse: pulse }">
        <div class="ntag">REALVAULT</div>
        <template v-if="built">
          <div class="ncall">decrypt()</div>
          <div class="state on">● instantiated</div>
        </template>
        <template v-else>
          <div class="ncall dim">RealVault</div>
          <div class="state">◇ uninstantiated</div>
        </template>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="row">
        <span class="lbl">role</span>
        <div class="seg">
          <button :class="{ on: role === 'guest' }" @click="setRole('guest')">guest</button>
          <button :class="{ on: role === 'admin' }" @click="setRole('admin')">admin</button>
        </div>
      </div>

      <button class="b" @click="read">▶ read(key)</button>

      <div class="counter">
        RealSubject instances created
        <b :class="{ lit: counter > 0 }">{{ counter }}</b>
      </div>

      <button class="b ghost" @click="reset">⟳ reset</button>

      <div class="log">{{ log }}</div>

      <div class="hint" :class="activeClass" v-if="active">
        {{ branchDesc(active) }}
      </div>
      <div class="hint ph" v-else>set a role, then fire read() repeatedly</div>
    </div>
  </div>
</template>

<style scoped>
.px {
  display: grid;
  grid-template-columns: 1.85fr 1fr;
  gap: 1.5rem;
  width: 100%;
  font-family: "Fira Code", monospace;
  height: 340px;
  box-sizing: border-box;
}

/* ---------- stage ---------- */
.stage {
  display: grid;
  grid-template-columns: 1.1fr 56px 1.35fr 56px 1.1fr;
  align-items: center;
  min-width: 0;
}

.node {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: .4rem;
  padding: .85rem .9rem;
  border: 1px solid var(--bp-line);
  border-radius: 12px;
  background: rgba(255, 255, 255, .03);
  transition: all .35s ease;
  min-height: 96px;
  min-width: 0;
}
.ntag {
  font-size: .58rem;
  letter-spacing: .12em;
  color: var(--bp-cyan);
}
.ntag.violet { color: var(--bp-violet); }
.ncall { font-size: .8rem; color: #fff; word-break: break-all; }
.ncall.dim { color: var(--bp-dim); }

/* client */
.client.recv { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
.result {
  align-self: flex-start;
  max-width: 100%;
  font-size: .64rem;
  padding: .15rem .5rem;
  border-radius: 6px;
  border: 1px solid var(--bp-cyan);
  color: var(--bp-cyan);
  background: rgba(34, 211, 238, .1);
  word-break: break-all;
}
.result.bad { border-color: var(--bp-bad); color: var(--bp-bad); background: rgba(251, 113, 133, .1); }

/* proxy */
.proxy { border-color: rgba(167, 139, 250, .35); min-height: 150px; }
.proxy.active { box-shadow: 0 0 22px rgba(167, 139, 250, .3); }
.badge {
  align-self: flex-start;
  font-size: .62rem;
  letter-spacing: .08em;
  padding: .12rem .55rem;
  border-radius: 999px;
  border: 1px solid var(--bp-line);
  color: var(--bp-dim);
  transition: all .3s;
}
.badge.ghost { color: var(--bp-dim); opacity: .6; }
.badge.denied { color: var(--bp-bad); border-color: var(--bp-bad); background: rgba(251, 113, 133, .12); }
.badge.build { color: var(--bp-warn); border-color: var(--bp-warn); background: rgba(251, 191, 36, .12); }
.badge.reuse { color: var(--bp-good); border-color: var(--bp-good); background: rgba(74, 222, 128, .12); }

.branches {
  list-style: none;
  margin: .15rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: .22rem;
}
.branches li {
  display: flex;
  align-items: center;
  gap: .4rem;
  font-size: .62rem;
  color: var(--bp-dim);
  opacity: .55;
  transition: all .25s;
}
.branches li .bdot {
  width: 6px; height: 6px; border-radius: 999px;
  background: var(--bp-line); transition: all .25s;
}
.branches li.on { opacity: 1; color: #fff; }
.branches li.on .bdot { background: var(--bp-violet); box-shadow: 0 0 8px rgba(167, 139, 250, .7); }

/* real */
.real {
  border-style: dashed;
  border-color: var(--bp-line);
  opacity: .55;
}
.real .state { font-size: .62rem; color: var(--bp-dim); }
.real .state.on { color: var(--bp-good); }
.real.solid {
  border-style: solid;
  border-color: var(--bp-cyan);
  background: rgba(34, 211, 238, .08);
  opacity: 1;
  box-shadow: var(--bp-glow);
}
.real.pulse { animation: throb .6s ease; }
@keyframes throb {
  0% { transform: scale(1); box-shadow: 0 0 0 rgba(251, 191, 36, 0); }
  45% { transform: scale(1.06); box-shadow: 0 0 26px rgba(251, 191, 36, .65); border-color: var(--bp-warn); }
  100% { transform: scale(1); box-shadow: var(--bp-glow); }
}

/* ---------- wires + token ---------- */
.wire { position: relative; height: 100%; display: flex; align-items: center; }
.rail { width: 100%; height: 2px; background: var(--bp-line); }
.rail.dead { background: repeating-linear-gradient(90deg, var(--bp-line) 0 4px, transparent 4px 8px); }
.token {
  position: absolute;
  top: 50%;
  width: 10px; height: 10px;
  margin-top: -5px;
  border-radius: 999px;
  background: var(--bp-cyan);
  box-shadow: var(--bp-glow);
}
.token.bad { background: var(--bp-bad); box-shadow: 0 0 14px rgba(251, 113, 133, .7); }
.token.fwd { animation: fwd .56s ease forwards; }
.token.rev { animation: rev .56s ease forwards; }
@keyframes fwd { from { left: -4px; opacity: 1; } to { left: calc(100% - 6px); opacity: 1; } }
@keyframes rev { from { left: calc(100% - 6px); opacity: 1; } to { left: -4px; opacity: 0; } }

.chip-enter-active { transition: all .3s ease; }
.chip-leave-active { transition: all .25s ease; }
.chip-enter-from { opacity: 0; transform: translateX(8px); }
.chip-leave-to { opacity: 0; transform: translateX(8px); }

/* ---------- panel ---------- */
.panel {
  display: flex;
  flex-direction: column;
  gap: .7rem;
  align-items: flex-start;
  min-width: 0;
  overflow: hidden;
}
.row { display: flex; align-items: center; gap: .6rem; }
.lbl { font-size: .68rem; color: var(--bp-dim); text-transform: uppercase; letter-spacing: .1em; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg button {
  font-family: inherit; font-size: .72rem; padding: .35rem .8rem;
  background: transparent; color: var(--bp-dim); cursor: pointer; border: none;
}
.seg button.on { background: rgba(34, 211, 238, .14); color: var(--bp-cyan); }

.b {
  font-family: inherit; font-size: .8rem; padding: .45rem .9rem;
  border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px;
  background: rgba(34, 211, 238, .12); cursor: pointer; box-shadow: var(--bp-glow);
}
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }

.counter { font-size: .72rem; color: var(--bp-dim); line-height: 1.5; }
.counter b {
  display: inline-block; margin-left: .35rem; font-size: .95rem;
  color: var(--bp-dim); transition: all .3s;
}
.counter b.lit { color: var(--bp-cyan); text-shadow: var(--bp-glow); }

.log {
  width: 100%; box-sizing: border-box;
  font-size: .66rem; color: var(--bp-cyan);
  padding: .35rem .6rem; border: 1px solid var(--bp-line);
  border-radius: 7px; background: rgba(34, 211, 238, .05);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.hint {
  width: 100%; box-sizing: border-box;
  font-size: .66rem; line-height: 1.4;
  padding: .35rem .6rem; border-radius: 7px;
  border: 1px solid var(--bp-line); color: var(--bp-dim);
}
.hint.denied { color: var(--bp-bad); border-color: rgba(251, 113, 133, .4); }
.hint.build { color: var(--bp-warn); border-color: rgba(251, 191, 36, .4); }
.hint.reuse { color: var(--bp-good); border-color: rgba(74, 222, 128, .4); }
.hint.ph { opacity: .7; }
</style>
