<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

type Wiring = 'new' | 'injected'
type Prov = 'smtp' | 'fake' | 'null'

const PROVIDERS: Record<Prov, { cls: string; tag: string }> = {
  smtp: { cls: 'SmtpMailer', tag: 'real' },
  fake: { cls: 'FakeMailer', tag: 'test' },
  null: { cls: 'NullMailer', tag: 'noop' },
}
const ORDER: Prov[] = ['smtp', 'fake', 'null']

const wiring = ref<Wiring>('new')
const plugged = ref<Prov>('smtp')   // which provider sits in the slot
const out = ref('')                 // run output line
const outKind = ref<'real' | 'iso' | 'noop'>('real')
const firing = ref(false)
const litWire = ref<Prov | ''>('')
const codeChanges = ref(0)          // pinned: stays 0 forever

// reactive so the run button disables mid-animation
const busy = ref(false)

const timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) { timers.push(setTimeout(fn, ms)) }
function clearAll() { timers.forEach(clearTimeout); timers.length = 0 }
onUnmounted(clearAll)

// vertical positions of the three provider chips on the board (percent)
const PY: Record<Prov, number> = { smtp: 22, fake: 50, null: 78 }
const PX = 18          // provider chip x
const SLOT = { x: 68, y: 50 }  // dependency slot x/y

const slotLabel = computed(() =>
  wiring.value === 'new' ? 'SmtpMailer()' : PROVIDERS[plugged.value].cls + '()'
)
const welded = computed(() => wiring.value === 'new')

function setWiring(w: Wiring) {
  if (busy.value || wiring.value === w) return
  clearAll()
  wiring.value = w
  out.value = ''
  litWire.value = ''
  if (w === 'new') plugged.value = 'smtp'
}

function plug(p: Prov) {
  if (busy.value || wiring.value !== 'injected') return
  clearAll()
  plugged.value = p
  out.value = ''
  litWire.value = p
}

function run() {
  if (busy.value) return
  busy.value = true
  firing.value = true
  out.value = ''
  // new-inside always resolves to a welded SmtpMailer; injected uses the plug
  const eff: Prov = wiring.value === 'new' ? 'smtp' : plugged.value
  if (wiring.value === 'injected') litWire.value = eff
  later(() => {
    if (eff === 'smtp') { out.value = 'SMTP -> a@b.com'; outKind.value = 'real' }
    else if (eff === 'fake') { out.value = 'captured: [a@b.com] (no real email)'; outKind.value = 'iso' }
    else { out.value = 'discarded (no-op sink)'; outKind.value = 'noop' }
    firing.value = false
    busy.value = false
  }, 620)
}

function reset() {
  clearAll()
  busy.value = false
  firing.value = false
  wiring.value = 'new'
  plugged.value = 'smtp'
  out.value = ''
  litWire.value = ''
}

const provActive = (p: Prov) => wiring.value === 'injected'
const isPlugged = (p: Prov) => wiring.value === 'injected' && plugged.value === p
</script>

<template>
  <div class="di">
    <!-- ============ STAGE ============ -->
    <div class="stage">
      <div class="board">
        <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
          <!-- one wire per provider; only the plugged one is solid/lit -->
          <line
            v-for="p in ORDER" :key="'w' + p"
            :x1="PX + 9" :y1="PY[p]" :x2="SLOT.x - 9" :y2="SLOT.y"
            class="wire"
            :class="{
              live: wiring === 'injected' && isPlugged(p),
              hot: wiring === 'injected' && litWire === p && firing,
            }"
          />
        </svg>

        <!-- provider chips (outside the Service) -->
        <div
          v-for="p in ORDER" :key="p"
          class="node prov"
          :class="{ active: provActive(p), on: isPlugged(p), [PROVIDERS[p].tag]: true }"
          :style="{ left: PX + '%', top: PY[p] + '%' }"
          @click="plug(p)"
        >
          <span class="nt">{{ PROVIDERS[p].tag }}</span>
          <span class="nm">{{ PROVIDERS[p].cls }}</span>
          <span v-if="isPlugged(p)" class="pin">● wired</span>
        </div>

        <!-- the Service box, holding the dependency slot -->
        <div class="node svc" :style="{ left: SLOT.x + '%', top: SLOT.y + '%' }">
          <span class="svc-h">class Signup</span>
          <div
            class="slot"
            :class="{ welded, filled: !welded, fire: firing, [outKind]: !welded && !!out }"
          >
            <span class="sk">mailer =</span>
            <span class="sv">{{ slotLabel }}</span>
            <span class="lock" :class="{ open: !welded }">{{ welded ? '◆' : '◇' }}</span>
          </div>
          <span class="svc-c">register("a@b.com")</span>
        </div>

        <!-- hard-to-test tag pinned to the slot in new-inside mode -->
        <transition name="pop">
          <div v-if="welded" class="badtag">hard to test</div>
        </transition>
      </div>

      <!-- output console -->
      <div class="console" :class="{ on: !!out, [outKind]: !!out }">
        <span class="ca">▸</span>
        <span v-if="out" class="cl">{{ out }}</span>
        <span v-else class="cd">run register() to see what the mailer does</span>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="lbl">Wiring</div>
      <div class="seg">
        <button :class="{ on: wiring === 'new' }" @click="setWiring('new')">new inside</button>
        <button :class="{ on: wiring === 'injected' }" @click="setWiring('injected')">injected</button>
      </div>

      <div class="hint" :class="{ warn: welded }">
        <template v-if="welded">dependency welded in — providers locked</template>
        <template v-else>pick a provider chip to plug the slot</template>
      </div>

      <div class="btns">
        <button class="b" :disabled="busy" @click="run">▶ register()</button>
        <button class="b ghost" @click="reset">⟳ reset</button>
      </div>

      <div class="counter">
        Service code changed: <b>{{ codeChanges }}</b>
        <span class="cn">the class is never edited — only the wiring</span>
      </div>

      <ul class="kpts">
        <li>Built inside: the collaborator is welded; no seam to test</li>
        <li>Injected: the same slot accepts real, fake, or null</li>
        <li>Fake captures the call — proves isolation, sends nothing</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.di {
  display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.4rem;
  width: 100%; height: 340px; box-sizing: border-box;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}
.stage { min-width: 0; display: flex; flex-direction: column; gap: .7rem; }
.board { position: relative; width: 100%; height: 248px; }
.wires { position: absolute; inset: 0; width: 100%; height: 100%; }
.wire { stroke: var(--bp-line); stroke-width: .4; stroke-dasharray: 2 2; transition: stroke .3s, opacity .3s; }
.wire.live { stroke: var(--bp-cyan); stroke-width: .8; stroke-dasharray: none; opacity: .9; }
.wire.hot { stroke: var(--bp-cyan); stroke-width: 1.1; filter: drop-shadow(0 0 3px var(--bp-cyan)); animation: pulse .6s ease; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .35; } }

.node {
  position: absolute; transform: translate(-50%, -50%);
  display: flex; flex-direction: column; gap: .12rem;
  padding: .42rem .6rem; border-radius: 9px;
  border: 1px solid var(--bp-line); background: rgba(11,19,36,.94);
  white-space: nowrap; transition: border-color .3s, box-shadow .3s, background .3s, opacity .3s;
}
.node .nt { font-size: .54rem; text-transform: uppercase; letter-spacing: .07em; color: var(--bp-dim); }
.node .nm { font-size: .72rem; color: var(--bp-ink); }

/* provider chips */
.prov { width: 96px; cursor: not-allowed; opacity: .42; }
.prov.active { opacity: 1; cursor: pointer; }
.prov.active:hover { border-color: var(--bp-cyan); }
.prov.active.real .nt { color: var(--bp-cyan); }
.prov.active.test .nt { color: var(--bp-good); }
.prov.active.noop .nt { color: var(--bp-warn); }
.prov.on { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); background: rgba(34,211,238,.08); }
.prov .pin { font-size: .54rem; color: var(--bp-cyan); margin-top: .05rem; }

/* the Service box */
.svc {
  width: 172px; gap: .35rem; padding: .55rem .7rem;
  border-color: var(--bp-violet);
}
.svc-h { font-size: .64rem; color: var(--bp-violet); letter-spacing: .03em; }
.svc-c { font-size: .58rem; color: var(--bp-dim); }

.slot {
  position: relative; display: flex; align-items: center; gap: .35rem;
  padding: .34rem .5rem; border-radius: 7px;
  border: 1px dashed var(--bp-line); background: rgba(255,255,255,.02);
  transition: border-color .3s, background .3s, box-shadow .3s;
}
.slot .sk { font-size: .58rem; color: var(--bp-dim); }
.slot .sv { font-size: .68rem; color: #fff; }
.slot.welded { border-style: solid; border-color: var(--bp-bad); background: rgba(251,113,133,.07); }
.slot.filled { border-style: solid; border-color: var(--bp-cyan); background: rgba(34,211,238,.08); }
.slot.fire { box-shadow: var(--bp-glow); }
.slot.real { border-color: var(--bp-cyan); }
.slot.iso  { border-color: var(--bp-good); background: rgba(74,222,128,.08); }
.slot.noop { border-color: var(--bp-warn); background: rgba(251,191,36,.07); }
.slot .lock { font-size: .66rem; color: var(--bp-bad); margin-left: auto; transition: color .3s; }
.slot .lock.open { color: var(--bp-cyan); }

.badtag {
  position: absolute; left: 68%; top: 50%;
  transform: translate(-50%, 34px);
  font-size: .56rem; color: var(--bp-bad);
  border: 1px solid var(--bp-bad); border-radius: 999px;
  padding: .1rem .5rem; background: var(--bp-bg); white-space: nowrap;
}
.pop-enter-active, .pop-leave-active { transition: opacity .25s, transform .25s; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translate(-50%, 26px); }

.console {
  display: flex; align-items: center; gap: .5rem;
  min-height: 34px; padding: .4rem .7rem;
  border: 1px solid var(--bp-line); border-radius: 9px;
  background: rgba(255,255,255,.02);
  transition: border-color .3s, background .3s;
}
.console .ca { color: var(--bp-dim); font-size: .72rem; flex: none; }
.console .cl { font-size: .74rem; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.console .cd { font-size: .68rem; color: var(--bp-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.console.on.real { border-color: var(--bp-cyan); }
.console.on.real .cl { color: var(--bp-cyan); }
.console.on.iso  { border-color: var(--bp-good); }
.console.on.iso  .cl { color: var(--bp-good); }
.console.on.noop { border-color: var(--bp-warn); }
.console.on.noop .cl { color: var(--bp-warn); }

/* panel */
.panel { display: flex; flex-direction: column; gap: .55rem; min-width: 0; }
.lbl { font-size: .58rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-dim); }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; width: fit-content; }
.seg button { font-family: inherit; font-size: .76rem; padding: .4rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; border: none; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.hint { font-size: .64rem; color: var(--bp-dim); }
.hint.warn { color: var(--bp-bad); }
.btns { display: flex; gap: .5rem; }
.b { font-family: inherit; font-size: .78rem; padding: .42rem .8rem; border: 1px solid var(--bp-cyan); color: #fff; border-radius: 8px; background: rgba(34,211,238,.12); cursor: pointer; box-shadow: var(--bp-glow); }
.b:disabled { opacity: .5; cursor: not-allowed; box-shadow: none; }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; box-shadow: none; }
.counter { font-size: .72rem; color: var(--bp-dim); padding: .45rem .65rem; border: 1px solid var(--bp-line); border-radius: 8px; }
.counter b { font-size: 1rem; color: var(--bp-good); margin: 0 .25rem; }
.counter .cn { display: block; font-size: .56rem; opacity: .8; margin-top: .1rem; }
.kpts { list-style: none; padding: 0; margin: 0; }
.kpts li { position: relative; padding-left: 1.1rem; margin: .24rem 0; font-size: .68rem; line-height: 1.35; color: var(--bp-dim); }
.kpts li::before { content: '\25B8'; position: absolute; left: 0; color: var(--bp-cyan); }
</style>
