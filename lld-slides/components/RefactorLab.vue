<script setup lang="ts">
import { ref, computed, reactive, onBeforeUnmount } from 'vue'

/* ============================================================
   RefactorLab — Open/Closed, live. Click "Add type" and watch
   the DIRTY process() grow another elif (complexity reddens,
   core "modified") while the CLEAN side snaps a new Strategy
   card onto the registry shelf with 0 core lines changed.
   ============================================================ */

type Mode = 'dirty' | 'clean'
const mode = ref<Mode>('dirty')          // which panel is foregrounded / scored
function setMode(m: Mode) { mode.value = m }

const timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) {
  const t = setTimeout(fn, ms); timers.push(t); return t
}
onBeforeUnmount(() => { timers.forEach(clearTimeout) })

/* ---------- the addable payment types ---------- */
interface PayType {
  id: string
  kind: string          // the literal in the if/elif
  cls: string           // the Strategy class name on the clean shelf
  call: string          // the pay() body on the clean card
}
// the three base types ship with the method; the rest are "new requirements"
const BASE: PayType[] = [
  { id: 'credit', kind: 'credit', cls: 'CreditCard',     call: 'charge(token, amount)' },
  { id: 'debit',  kind: 'debit',  cls: 'DebitCard',      call: 'debit(acct, amount)'   },
  { id: 'upi',    kind: 'upi',    cls: 'UpiHandle',      call: 'collect(vpa, amount)'  },
]
const ADDABLE: PayType[] = [
  { id: 'gift',   kind: 'gift_card', cls: 'GiftCard', call: 'redeem(code, amount)'   },
  { id: 'wallet', kind: 'wallet',    cls: 'Wallet',   call: 'spend(wallet, amount)'  },
  { id: 'crypto', kind: 'crypto',    cls: 'Crypto',   call: 'settle(chain, amount)'  },
]

// the live list of types, in order; starts with the three base ones
const types = ref<PayType[]>([...BASE])
const flashId = ref('')                  // id of the row/card just added (animates in)
const coreFlash = ref(false)             // DIRTY "modified core" badge pulse
const selAdd = ref<string>('gift')       // currently armed dropdown value
const broken = ref(false)                // "break a payment" switch

const remaining = computed(() => ADDABLE.filter(a => !types.value.some(t => t.id === a.id)))

function addType() {
  const next = ADDABLE.find(a => a.id === selAdd.value)
  if (!next || types.value.some(t => t.id === next.id)) return
  types.value.push(next)
  flashId.value = next.id
  coreFlash.value = true
  later(() => { if (flashId.value === next.id) flashId.value = '' }, 700)
  later(() => { coreFlash.value = false }, 900)
  // auto-arm the next still-missing type for fast repeat clicks
  const stillLeft = ADDABLE.filter(a => !types.value.some(t => t.id === a.id))
  selAdd.value = stillLeft[0]?.id ?? ''
}

function resetLab() {
  types.value = [...BASE]
  flashId.value = ''
  coreFlash.value = false
  broken.value = false
  selAdd.value = 'gift'
}

/* ---------- derived metrics per side ---------- */
// DIRTY: every type is a branch -> cyclomatic complexity = branches + 1,
// line-count grows ~3 lines/branch on top of the scaffold.
const dirtyBranches = computed(() => types.value.length)
const dirtyComplexity = computed(() => dirtyBranches.value + 1)   // +1 for the base path
const dirtyLines = computed(() => 4 + types.value.length * 3 + 1) // def + branches + else
const dirtyHot = computed(() => dirtyComplexity.value >= 5)       // reddens past 4

// CLEAN: Processor never changes; complexity is flat at 2 (one guard, one dispatch).
const cleanComplexity = 2
const cleanCoreLines = 0                                          // core lines edited on add

// how far the complexity meters fill (cap the visual at 8)
const dirtyFill = computed(() => Math.min(100, (dirtyComplexity.value / 8) * 100))
const cleanFill = computed(() => (cleanComplexity / 8) * 100)

/* ---------- "break a payment" trace ---------- */
// DIRTY throws deep in the nest; CLEAN rejects at the guard on entry.
const dirtyStack = computed(() => [
  'process(kind, amount)',
  `if/elif ... (${dirtyBranches.value} branches)`,
  'matched branch -> charge(...)',
  'gateway.call() raises',
])
const cleanStack = ['Processor.run(amount)', 'guard: amount <= 0 -> reject']

/* the chips back to Deck 3 */
const PATTERN_CHIPS = ['Strategy', 'State', 'Factory']
</script>

<template>
  <div class="rl">
    <!-- ===== top bar: mode toggle + add control + break switch ===== -->
    <div class="bar">
      <div class="modeseg">
        <button class="seg" :class="{ on: mode === 'dirty', dirty: true }" @click="setMode('dirty')">DIRTY</button>
        <button class="seg" :class="{ on: mode === 'clean', clean: true }" @click="setMode('clean')">CLEAN</button>
      </div>

      <div class="addbox">
        <span class="albl">Add type</span>
        <select v-model="selAdd" class="dd" :disabled="!remaining.length">
          <option v-for="a in remaining" :key="a.id" :value="a.id">{{ a.cls }}</option>
          <option v-if="!remaining.length" value="">— all added —</option>
        </select>
        <button class="addbtn" :disabled="!remaining.length" @click="addType">+ Add</button>
        <button class="resetbtn" @click="resetLab">&#9851; reset</button>
      </div>

      <label class="tog trap" :class="{ on: broken }" @click="broken = !broken">
        <span class="knob" /> Break a payment
      </label>
    </div>

    <!-- ===== two synced panels ===== -->
    <div class="stage">

      <!-- ---------- DIRTY ---------- -->
      <div class="panel dirty" :class="{ fg: mode === 'dirty' }">
        <div class="phead">
          <span class="ptag bad">DIRTY · one tested method</span>
          <span class="badge" :class="{ flash: coreFlash }">modified core</span>
        </div>

        <div class="codebox">
          <div class="cline def"><span class="kw">def</span> process(kind, amount):</div>
          <transition-group name="row">
            <div v-for="(t, i) in types" :key="t.id" class="cline branch"
                 :class="{ added: flashId === t.id }">
              <span class="kw">{{ i === 0 ? 'if' : 'elif' }}</span>
              kind == <span class="str">"{{ t.kind }}"</span>:
              <span class="dim">{{ t.call.split('(')[0] }}(...)</span>
            </div>
          </transition-group>
          <div class="cline branch else"><span class="kw">else</span>: <span class="err">raise ValueError(kind)</span></div>

          <!-- broken: red pointer deep in the nest -->
          <transition name="reveal">
            <div v-if="broken" class="throwline deep">
              <span class="ptr">&#9654;</span> raises at depth {{ types.length }} — caller can't tell which branch
            </div>
          </transition>
        </div>

        <div class="metrics">
          <div class="meter">
            <span class="mlbl">cyclomatic</span>
            <div class="track"><div class="fill" :class="{ hot: dirtyHot }" :style="{ width: dirtyFill + '%' }" /></div>
            <span class="mval" :class="{ hot: dirtyHot }">{{ dirtyComplexity }}</span>
          </div>
          <div class="stat"><span>lines</span><b>{{ dirtyLines }}</b></div>
          <div class="stat"><span>files touched</span><b>1</b></div>
        </div>
      </div>

      <!-- ---------- CLEAN ---------- -->
      <div class="panel clean" :class="{ fg: mode === 'clean' }">
        <div class="phead">
          <span class="ptag good">CLEAN · seam + registry</span>
          <span class="badge zero">{{ cleanCoreLines }} core lines changed</span>
        </div>

        <div class="cleanbody">
          <div class="processor">
            <div class="pname">Processor</div>
            <div class="pbody"><span class="kw">def</span> run(a):</div>
            <div class="pbody guard"><span class="kw">if</span> a &lt;= 0: raise InvalidAmount</div>
            <div class="pbody"><span class="dim">return</span> method.pay(a)</div>
            <span class="pnote">untouched on every add</span>
          </div>

          <div class="shelf">
            <span class="shlbl">registry shelf · PaymentMethod[]</span>
            <div class="cards">
              <transition-group name="snap">
                <div v-for="t in types" :key="t.id" class="scard"
                     :class="{ added: flashId === t.id }">
                  <div class="scname">{{ t.cls }}</div>
                  <div class="scpay">pay(): <span class="dim">{{ t.call }}</span></div>
                </div>
              </transition-group>
            </div>
          </div>
        </div>

        <div class="metrics">
          <div class="meter">
            <span class="mlbl">cyclomatic</span>
            <div class="track"><div class="fill good" :style="{ width: cleanFill + '%' }" /></div>
            <span class="mval gd">{{ cleanComplexity }}</span>
          </div>
          <div class="stat"><span>classes</span><b>{{ types.length }}</b></div>
          <div class="stat"><span>files touched</span><b>+1</b></div>

          <!-- broken: rejected at the guard on entry -->
          <transition name="reveal">
            <div v-if="broken" class="throwline guardline">
              <span class="ptr gd">&#9654;</span> rejected at guard, flat happy path
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- ===== bottom scoreboard / lesson ===== -->
    <div class="footer">
      <span class="lesson"><b>Open/Closed:</b> new behavior = a new class, not an edited method.</span>
      <span class="pchips">
        <span v-for="c in PATTERN_CHIPS" :key="c" class="pchip">{{ c }}</span>
      </span>
      <span class="tail">
        DIRTY: <b class="bad">+{{ types.length - 3 }}</b> branches edited in &nbsp;·&nbsp;
        CLEAN: <b class="good">+{{ types.length - 3 }}</b> cards, core <b class="good">0</b>
      </span>
    </div>
  </div>
</template>

<style scoped>
.rl {
  width: 100%; height: 360px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: .6rem;
  font-family: "Fira Code", monospace; color: var(--bp-ink);
}

/* ---------- top bar ---------- */
.bar { display: flex; align-items: center; gap: .9rem; flex-wrap: wrap; }
.modeseg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 9px; overflow: hidden; }
.seg { font-family: inherit; font-size: .64rem; letter-spacing: .08em; cursor: pointer;
  border: none; background: rgba(255,255,255,.02); color: var(--bp-dim); padding: .34rem .7rem; transition: all .2s; }
.seg.dirty.on { color: #fff; background: rgba(251,113,133,.16); box-shadow: inset 0 0 0 1px var(--bp-bad); }
.seg.clean.on { color: #fff; background: rgba(74,222,128,.14); box-shadow: inset 0 0 0 1px var(--bp-good); }
.seg:hover:not(.on) { color: var(--bp-ink); }

.addbox { display: inline-flex; align-items: center; gap: .4rem; }
.albl { font-size: .6rem; text-transform: uppercase; letter-spacing: .1em; color: var(--bp-cyan); }
.dd { font-family: inherit; font-size: .64rem; color: var(--bp-ink); cursor: pointer;
  background: var(--bp-bg-2); border: 1px solid var(--bp-line); border-radius: 7px; padding: .3rem .45rem; }
.dd:disabled { opacity: .5; cursor: not-allowed; }
.addbtn { font-family: inherit; font-size: .66rem; cursor: pointer; color: #fff;
  border: 1px solid var(--bp-cyan); border-radius: 7px; padding: .32rem .6rem;
  background: rgba(34,211,238,.14); box-shadow: var(--bp-glow); transition: all .2s; }
.addbtn:hover:not(:disabled) { background: rgba(34,211,238,.24); }
.addbtn:disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.resetbtn { font-family: inherit; font-size: .62rem; cursor: pointer; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 7px; padding: .32rem .55rem; background: transparent; transition: all .2s; }
.resetbtn:hover { color: var(--bp-cyan); border-color: var(--bp-cyan); }

/* ---------- stage / panels ---------- */
.stage { flex: 1; min-height: 0; display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }
.panel { border: 1px solid var(--bp-line); border-radius: 12px; padding: .6rem .7rem;
  display: flex; flex-direction: column; gap: .5rem; min-width: 0; min-height: 0;
  background: rgba(255,255,255,.015); transition: box-shadow .25s, border-color .25s, opacity .25s; }
.panel.dirty.fg { border-color: rgba(251,113,133,.5); box-shadow: 0 0 22px rgba(251,113,133,.22); }
.panel.clean.fg { border-color: rgba(74,222,128,.5); box-shadow: 0 0 22px rgba(74,222,128,.22); }
.panel:not(.fg) { opacity: .82; }

.phead { display: flex; align-items: center; justify-content: space-between; gap: .4rem; }
.ptag { font-size: .56rem; text-transform: uppercase; letter-spacing: .08em; }
.ptag.bad { color: var(--bp-bad); }
.ptag.good { color: var(--bp-good); }
.badge { font-size: .52rem; color: var(--bp-dim); border: 1px solid var(--bp-line);
  border-radius: 999px; padding: .08rem .45rem; transition: all .2s; }
.badge.flash { color: #fff; border-color: var(--bp-bad); background: rgba(251,113,133,.2);
  box-shadow: 0 0 14px rgba(251,113,133,.5); animation: bpulse .5s ease; }
.badge.zero { color: var(--bp-good); border-color: rgba(74,222,128,.4); background: rgba(74,222,128,.08); }
@keyframes bpulse { 0%{transform:scale(1)} 45%{transform:scale(1.12)} 100%{transform:scale(1)} }

/* DIRTY code box */
.codebox { flex: 1; min-height: 0; overflow-y: auto; border: 1px solid var(--bp-line);
  border-radius: 9px; background: rgba(7,11,20,.6); padding: .4rem .5rem;
  font-size: .6rem; line-height: 1.55; }
.codebox::-webkit-scrollbar { width: 5px; }
.codebox::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.cline { white-space: nowrap; color: var(--bp-ink); }
.cline.def { color: var(--bp-cyan); margin-bottom: .1rem; }
.cline.branch { padding-left: 1rem; }
.cline.branch.else { padding-left: 1rem; color: var(--bp-dim); }
.cline.added { animation: rowin .55s ease; }
.kw { color: var(--bp-violet); }
.str { color: var(--bp-good); }
.err { color: var(--bp-bad); }
.dim { color: var(--bp-dim); }
@keyframes rowin { 0%{ background: rgba(251,113,133,.25); } 100%{ background: transparent; } }

.throwline { margin-top: .35rem; font-size: .56rem; padding: .25rem .4rem; border-radius: 6px; }
.throwline.deep { color: var(--bp-bad); border: 1px solid rgba(251,113,133,.4); background: rgba(251,113,133,.1); }
.throwline.guardline { color: var(--bp-good); border: 1px solid rgba(74,222,128,.4); background: rgba(74,222,128,.08); }
.ptr { color: var(--bp-bad); margin-right: .25rem; }
.ptr.gd { color: var(--bp-good); }

/* CLEAN body */
.cleanbody { flex: 1; min-height: 0; display: grid; grid-template-columns: 1fr 1.2fr; gap: .5rem; }
.processor { border: 1px solid var(--bp-line); border-radius: 9px; padding: .4rem .5rem;
  background: rgba(56,189,248,.04); display: flex; flex-direction: column; gap: .12rem; font-size: .56rem; }
.pname { font-size: .62rem; color: var(--bp-cyan); margin-bottom: .15rem; }
.pbody { color: var(--bp-dim); white-space: nowrap; }
.pbody.guard { color: var(--bp-ink); }
.pnote { margin-top: auto; font-size: .5rem; color: var(--bp-dim); opacity: .8; font-style: italic; }

.shelf { border: 1px dashed var(--bp-line); border-radius: 9px; padding: .4rem; display: flex; flex-direction: column; gap: .3rem; min-height: 0; }
.shlbl { font-size: .5rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-good); }
.cards { display: flex; flex-direction: column; gap: .28rem; overflow-y: auto; min-height: 0; }
.cards::-webkit-scrollbar { width: 5px; }
.cards::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.scard { border: 1px solid rgba(167,139,250,.4); border-radius: 7px; padding: .22rem .4rem;
  background: rgba(167,139,250,.08); }
.scard.added { animation: snapin .55s ease; }
.scname { font-size: .58rem; color: var(--bp-violet); }
.scpay { font-size: .5rem; color: var(--bp-ink); white-space: nowrap; }
@keyframes snapin { 0%{ transform: translateX(24px) scale(.85); opacity: 0; box-shadow: 0 0 18px rgba(74,222,128,.6); }
  100%{ transform: translateX(0) scale(1); opacity: 1; } }

/* metrics row */
.metrics { display: flex; align-items: center; gap: .7rem; flex-wrap: wrap; }
.meter { display: flex; align-items: center; gap: .4rem; }
.mlbl { font-size: .5rem; text-transform: uppercase; letter-spacing: .06em; color: var(--bp-dim); }
.track { width: 64px; height: 6px; border-radius: 999px; background: var(--bp-line); overflow: hidden; }
.fill { height: 100%; border-radius: 999px; background: var(--bp-cyan); transition: width .35s ease, background .3s; }
.fill.hot { background: var(--bp-bad); }
.fill.good { background: var(--bp-good); }
.mval { font-size: .68rem; color: var(--bp-ink); }
.mval.hot { color: var(--bp-bad); }
.mval.gd { color: var(--bp-good); }
.stat { font-size: .54rem; color: var(--bp-dim); display: inline-flex; align-items: baseline; gap: .25rem; }
.stat b { font-size: .66rem; color: var(--bp-ink); }

/* ---------- toggle ---------- */
.tog { display: inline-flex; align-items: center; gap: .45rem; font-size: .64rem; color: var(--bp-dim);
  cursor: pointer; user-select: none; margin-left: auto; }
.tog .knob { width: 30px; height: 16px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: 0 0 auto; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.trap.on .knob { background: rgba(251,113,133,.4); }
.tog.trap.on .knob::after { left: 16px; background: var(--bp-bad); }
.tog.trap.on { color: var(--bp-bad); }

/* ---------- footer ---------- */
.footer { display: flex; align-items: center; gap: .8rem; flex-wrap: wrap;
  border-top: 1px solid var(--bp-line); padding-top: .4rem; font-size: .58rem; color: var(--bp-dim); }
.lesson b { color: var(--bp-cyan); }
.pchips { display: inline-flex; gap: .3rem; }
.pchip { font-size: .52rem; color: var(--bp-violet); border: 1px solid rgba(167,139,250,.4);
  background: rgba(167,139,250,.08); border-radius: 999px; padding: .06rem .4rem; }
.tail { margin-left: auto; }
.tail .bad { color: var(--bp-bad); }
.tail .good { color: var(--bp-good); }

/* ---------- transitions ---------- */
.reveal-enter-active { transition: all .3s ease; }
.reveal-enter-from { opacity: 0; transform: translateY(-4px); }
.row-enter-active, .snap-enter-active { transition: all .4s ease; }
.row-enter-from { opacity: 0; transform: translateY(-6px); }
.snap-enter-from { opacity: 0; transform: translateX(20px) scale(.85); }
</style>
