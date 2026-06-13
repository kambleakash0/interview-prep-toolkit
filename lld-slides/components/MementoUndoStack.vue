<script setup lang="ts">
import { ref, computed } from 'vue'

interface Card { id: number; label: string; text: string; settling: boolean }

const TOKENS = ['lvl', 'hp', 'gold', 'map', 'key', 'orb', 'gem', 'rune']
let tok = 0
let mintN = 0

const text = ref('start')
const dirty = ref(false)
const pulse = ref(false)       // one-shot mutation pulse
const flash = ref(false)       // restore flash
const peek = ref(false)        // Peek toggle
const flying = ref<null | { label: string }>(null)  // card flying left on undo

const stack = ref<Card[]>([])
let busy = false

const empty = computed(() => stack.value.length === 0)

function onceBorder(target: 'pulse' | 'flash') {
  if (target === 'pulse') { pulse.value = false; requestPulse(() => pulse.value = true, () => pulse.value = false) }
  else { flash.value = false; requestPulse(() => flash.value = true, () => flash.value = false) }
}
function requestPulse(on: () => void, off: () => void) {
  on()
  setTimeout(off, 460)
}

function type() {
  if (busy) return
  const t = TOKENS[tok % TOKENS.length]; tok++
  text.value = (text.value + ' ' + t).trim()
  dirty.value = true
  onceBorder('pulse')
}

function save() {
  if (busy) return
  busy = true
  mintN++
  const card: Card = { id: mintN, label: `snapshot #${mintN} (sealed)`, text: text.value, settling: true }
  // card slides up from originator and lands on top with a settle bounce
  stack.value.unshift(card)
  dirty.value = false
  setTimeout(() => { card.settling = false; busy = false }, 420)
}

function undo() {
  if (busy || empty.value) return
  busy = true
  const top = stack.value[0]
  flying.value = { label: top.label }
  // remove from stack as the card flies leftward into the originator
  stack.value.shift()
  setTimeout(() => {
    // editor snaps to the frozen value; border flashes
    text.value = top.text
    dirty.value = false
    flying.value = null
    onceBorder('flash')
    busy = false
  }, 280)
}

const cursorChars = computed(() => text.value.length)
</script>

<template>
  <div class="mm">
    <!-- ============ STAGE ============ -->
    <div class="stage">
      <!-- Originator -->
      <div class="orig" :class="{ pulse, flash }">
        <div class="ohead">
          <span class="otitle">Originator</span>
          <span class="udot" :class="{ on: dirty }">● unsaved</span>
        </div>

        <div class="editor">
          <span class="caret-label">editor ▸</span>
          <span class="line">
            <span class="txt">{{ text }}</span><span class="cursor" />
          </span>
        </div>

        <div class="ostate">
          value = <b>"{{ text }}"</b><span class="len">len {{ cursorChars }}</span>
        </div>

        <!-- card flying left back into originator on undo -->
        <div v-if="flying" class="fly">
          <span class="lockico">◆</span>{{ flying.label }} ↩
        </div>
      </div>

      <!-- rail -->
      <div class="rail">
        <span class="arrow up">save ↑</span>
        <span class="arrow dn">↩ undo</span>
      </div>

      <!-- Caretaker -->
      <div class="care">
        <div class="chead">Caretaker</div>
        <div class="pile" :class="{ vacant: empty }">
          <transition-group name="card" tag="div" class="pile-inner">
            <div
              v-for="(c, i) in stack"
              :key="c.id"
              class="snap"
              :class="{ settle: c.settling, top: i === 0, peekable: peek }"
            >
              <span class="seal">◆</span>
              <span class="slabel">{{ c.label }}</span>
              <!-- Peek: opaque overlay, contents never shown -->
              <div v-if="peek" class="opaque">
                <span class="padlock">⊘</span>
                <span class="otext">opaque — contents hidden</span>
              </div>
            </div>
          </transition-group>
          <div v-if="empty" class="vacancy">empty stack</div>
        </div>
        <div class="cnote">Caretaker: stores, never inspects</div>
      </div>
    </div>

    <!-- ============ CONTROLS ============ -->
    <div class="panel">
      <div class="btns">
        <button class="b" @click="type">▸ Type</button>
        <button class="b cyan" @click="save">■ Save</button>
        <button class="b" :disabled="empty" @click="undo">↩ Undo</button>
        <label class="tog" :class="{ on: peek }" @click="peek = !peek">
          <span class="knob" /> Peek {{ peek ? 'ON' : 'OFF' }}
        </label>
      </div>

      <div class="hint" :class="{ warn: empty }">
        <template v-if="empty">nothing to undo — stack is empty</template>
        <template v-else-if="peek">Peek tries to open a card — and fails. Snapshots are sealed.</template>
        <template v-else-if="dirty">unsaved edits — Save to seal a snapshot</template>
        <template v-else>Type to mutate ▸ Save to snapshot ▸ Undo to rewind</template>
      </div>

      <ul class="kpts bp-dim text-sm">
        <li>Originator packs its private state into a sealed Memento</li>
        <li>Caretaker stacks opaque cards — pops the top to rewind</li>
        <li>Peek proves the snapshot is a black box: no contents leak</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.mm {
  display: grid; grid-template-columns: 1.55fr 1fr; gap: 1.5rem;
  font-family: "Fira Code", monospace;
  width: 100%; height: 340px; box-sizing: border-box;
}

/* ---- stage ---- */
.stage { display: grid; grid-template-columns: 1fr 64px 0.92fr; align-items: stretch; gap: 0; min-height: 0; }

/* ---- Originator ---- */
.orig {
  position: relative; display: flex; flex-direction: column; gap: .55rem;
  padding: .85rem .9rem; border: 1px solid var(--bp-line); border-radius: 12px;
  background: rgba(255,255,255,.03); transition: border-color .3s, box-shadow .3s;
  overflow: hidden; min-height: 0;
}
.orig.pulse { animation: pulseB .46s ease; }
.orig.flash { border-color: var(--bp-good); box-shadow: 0 0 18px rgba(74,222,128,.45); }
@keyframes pulseB {
  0% { border-color: var(--bp-line); box-shadow: none; }
  40% { border-color: var(--bp-cyan); box-shadow: var(--bp-glow); }
  100% { border-color: var(--bp-line); box-shadow: none; }
}
.ohead { display: flex; justify-content: space-between; align-items: center; }
.otitle { font-size: .62rem; text-transform: uppercase; letter-spacing: .09em; color: var(--bp-dim); }
.udot { font-size: .58rem; color: var(--bp-line); transition: color .3s; }
.udot.on { color: var(--bp-warn); }

.editor {
  display: flex; flex-direction: column; gap: .25rem;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .5rem .6rem;
  background: var(--bp-bg); min-height: 0; overflow: hidden;
}
.caret-label { font-size: .56rem; color: var(--bp-dim); letter-spacing: .05em; }
.line { display: inline-flex; align-items: center; font-size: .8rem; color: #fff; min-height: 1.2em; flex-wrap: wrap; }
.txt { color: var(--bp-ink); word-break: break-all; }
.cursor { width: 7px; height: 1em; margin-left: 2px; background: var(--bp-cyan); display: inline-block; animation: blink 1s steps(1) infinite; box-shadow: var(--bp-glow); }
@keyframes blink { 0%,50% { opacity: 1; } 51%,100% { opacity: 0; } }

.ostate { font-size: .68rem; color: var(--bp-dim); display: flex; align-items: baseline; gap: .5rem; }
.ostate b { color: var(--bp-cyan); font-weight: 600; word-break: break-all; }
.len { font-size: .56rem; color: var(--bp-dim); border: 1px solid var(--bp-line); border-radius: 5px; padding: 0 .35rem; flex: none; }

/* flying card returning to originator */
.fly {
  position: absolute; bottom: 10px; right: 10px;
  font-size: .58rem; color: var(--bp-violet);
  border: 1px solid var(--bp-violet); border-radius: 7px; padding: .25rem .5rem;
  background: var(--bp-bg); display: inline-flex; align-items: center; gap: .35rem;
  animation: flyIn .28s ease forwards;
}
.fly .lockico { color: var(--bp-violet); }
@keyframes flyIn {
  from { transform: translateX(120px) scale(.9); opacity: 0; }
  60% { opacity: 1; }
  to { transform: translateX(0) scale(1); opacity: .95; }
}

/* ---- rail between panels ---- */
.rail { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1.4rem; }
.rail::before { content: ''; position: absolute; top: 12%; bottom: 12%; width: 2px; background: var(--bp-line); }
.arrow { font-size: .54rem; color: var(--bp-dim); background: var(--bp-bg); padding: .15rem .25rem; z-index: 1; }
.arrow.up { color: var(--bp-cyan); }
.arrow.dn { color: var(--bp-violet); }

/* ---- Caretaker ---- */
.care { display: flex; flex-direction: column; gap: .4rem; min-height: 0; }
.chead { font-size: .62rem; text-transform: uppercase; letter-spacing: .09em; color: var(--bp-dim); }
.pile {
  position: relative; flex: 1; min-height: 0;
  border: 1px dashed var(--bp-line); border-radius: 12px; padding: .5rem;
  background: rgba(255,255,255,.015); overflow: hidden;
}
.pile.vacant { border-color: var(--bp-line); }
.pile-inner { display: flex; flex-direction: column; gap: .4rem; }

.snap {
  position: relative; display: flex; align-items: center; gap: .5rem;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .42rem .55rem;
  background: linear-gradient(180deg, rgba(167,139,250,.10), rgba(167,139,250,.03));
  font-size: .68rem; color: var(--bp-ink); overflow: hidden;
}
.snap.top { border-color: rgba(167,139,250,.5); box-shadow: 0 0 12px rgba(167,139,250,.25); }
.snap.settle { animation: settle .42s cubic-bezier(.3,1.5,.5,1); }
@keyframes settle {
  0% { transform: translateY(-30px) scale(.94); opacity: 0; }
  60% { transform: translateY(4px) scale(1.02); opacity: 1; }
  100% { transform: translateY(0) scale(1); }
}
.seal { color: var(--bp-violet); font-size: .7rem; }
.slabel { letter-spacing: .02em; }

/* Peek mode: hover shakes + opaque overlay that refuses to reveal contents */
.snap.peekable:hover { animation: shake .35s; }
@keyframes shake {
  0%,100% { transform: translateX(0); }
  25% { transform: translateX(-3px); }
  50% { transform: translateX(3px); }
  75% { transform: translateX(-2px); }
}
.opaque {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: .4rem;
  background: rgba(7,11,20,.86); backdrop-filter: blur(1.5px);
  font-size: .56rem; color: var(--bp-bad); border-radius: 8px;
}
.padlock { font-size: .8rem; }
.otext { text-decoration: line-through; text-decoration-color: var(--bp-bad); }

.vacancy {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: .72rem; letter-spacing: .08em; color: var(--bp-dim); opacity: .6;
}
.cnote { font-size: .56rem; color: var(--bp-dim); opacity: .7; letter-spacing: .03em; }

/* card add/remove transitions for the stack */
.card-enter-active { transition: none; }
.card-leave-active { transition: all .26s ease; position: absolute; left: .5rem; right: .5rem; }
.card-leave-to { transform: translateX(-120px) scale(.9); opacity: 0; }
.card-move { transition: transform .26s ease; }

/* ---- controls ---- */
.panel { display: flex; flex-direction: column; gap: .8rem; align-items: flex-start; min-height: 0; overflow: hidden; }
.btns { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; }
.b {
  font-family: inherit; font-size: .76rem; padding: .42rem .8rem;
  border: 1px solid var(--bp-line); color: var(--bp-ink); border-radius: 8px;
  background: rgba(255,255,255,.03); cursor: pointer; transition: all .2s;
}
.b:hover:not(:disabled) { border-color: var(--bp-cyan); color: var(--bp-cyan); }
.b.cyan { border-color: var(--bp-cyan); color: #fff; background: rgba(34,211,238,.12); box-shadow: var(--bp-glow); }
.b:disabled { opacity: .32; cursor: not-allowed; }

.tog { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; color: var(--bp-dim); cursor: pointer; user-select: none; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: none; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on .knob { background: rgba(167,139,250,.4); }
.tog.on .knob::after { left: 16px; background: var(--bp-violet); }
.tog.on { color: var(--bp-violet); }

.hint {
  font-size: .7rem; padding: .4rem .7rem; border-radius: 7px;
  border: 1px solid var(--bp-line); color: var(--bp-dim);
  background: rgba(255,255,255,.02); min-height: 1.1rem;
}
.hint.warn { color: var(--bp-warn); border-color: rgba(251,191,36,.35); }

.kpts { margin-top: .15rem; }
</style>
