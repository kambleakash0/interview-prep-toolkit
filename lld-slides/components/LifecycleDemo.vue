<script setup lang="ts">
import { ref, computed } from 'vue'

// mode: 'composition' (parts owned, die with whole) | 'aggregation' (parts independent)
const mode = ref<'composition' | 'aggregation'>('composition')
const alive = ref(true)
const parts = ref([
  { id: 1, name: 'Kitchen', gone: false, freed: false },
  { id: 2, name: 'Bedroom', gone: false, freed: false },
  { id: 3, name: 'Bathroom', gone: false, freed: false },
])

const isComp = computed(() => mode.value === 'composition')
const diamond = computed(() => (isComp.value ? '◆' : '◇'))
const caption = computed(() =>
  isComp.value
    ? 'House ◆──> Room  ·  parts are OWNED — they die with the whole'
    : 'Team ◇──> Player  ·  parts are SHARED — they outlive the whole',
)

function setMode(m: 'composition' | 'aggregation') { mode.value = m; reset() }

function demolish() {
  alive.value = false
  parts.value.forEach((p, i) => {
    setTimeout(() => {
      if (isComp.value) p.gone = true     // destroyed with the whole
      else p.freed = true                  // released, keeps living
    }, 120 * i)
  })
}
function reset() {
  alive.value = true
  parts.value.forEach(p => { p.gone = false; p.freed = false })
}
</script>

<template>
  <div class="life">
    <div class="controls">
      <div class="seg">
        <button :class="{ on: isComp }"  @click="setMode('composition')">◆ Composition</button>
        <button :class="{ on: !isComp }" @click="setMode('aggregation')">◇ Aggregation</button>
      </div>
      <button class="danger" :disabled="!alive" @click="demolish">
        {{ isComp ? 'Destroy House' : 'Disband Team' }}
      </button>
      <button class="ghost" @click="reset">↻ reset</button>
    </div>

    <div class="stage">
      <!-- the whole -->
      <div :class="['whole', { dead: !alive }]">
        <span class="lbl">{{ isComp ? 'House' : 'Team' }}</span>
        <span class="dia">{{ diamond }}</span>
      </div>

      <div class="link" />

      <!-- the parts -->
      <div class="parts">
        <div
          v-for="p in parts" :key="p.id"
          :class="['part', { breathe: alive, gone: p.gone, freed: p.freed }]"
        >
          {{ isComp ? p.name : (p.name === 'Kitchen' ? 'Alice' : p.name === 'Bedroom' ? 'Bob' : 'Carol') }}
          <span v-if="p.freed" class="tag">still alive ✓</span>
        </div>
      </div>
    </div>

    <p class="cap bp-mono" :class="isComp ? 'c' : 'a'">{{ caption }}</p>
  </div>
</template>

<style scoped>
.life { font-family: "Fira Code", monospace; }
.controls { display: flex; gap: .8rem; align-items: center; margin-bottom: 1.4rem; }
.seg { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; }
.seg button { font-family: inherit; font-size: .8rem; padding: .45rem .9rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.seg button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.danger { font-family: inherit; font-size: .8rem; padding: .45rem .9rem; border: 1px solid var(--bp-bad); color: var(--bp-bad); border-radius: 8px; background: rgba(251,113,133,.06); cursor: pointer; }
.danger:disabled { opacity: .35; cursor: default; }
.ghost { font-family: inherit; font-size: .8rem; padding: .45rem .8rem; border: 1px solid var(--bp-line); color: var(--bp-dim); border-radius: 8px; background: transparent; cursor: pointer; }

.stage { display: flex; align-items: center; gap: 0; height: 190px; }
.whole {
  width: 130px; height: 120px; border-radius: 12px; flex: none;
  border: 2px solid var(--bp-cyan); box-shadow: var(--bp-glow);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .3rem;
  background: linear-gradient(180deg, rgba(34,211,238,.1), transparent);
  transition: all .5s ease;
}
.whole .lbl { color: #fff; font-size: .95rem; }
.whole .dia { color: var(--bp-cyan); font-size: 1.4rem; }
.whole.dead { opacity: 0; transform: scale(.6) rotate(-6deg); filter: blur(3px); }
.link { width: 70px; height: 2px; background: linear-gradient(90deg, var(--bp-cyan), var(--bp-line)); }

.parts { display: flex; flex-direction: column; gap: .6rem; }
.part {
  min-width: 150px; padding: .5rem .8rem; border-radius: 9px;
  border: 1px solid var(--bp-violet); color: var(--bp-ink);
  background: rgba(167,139,250,.08); transition: all .55s ease;
  display: flex; justify-content: space-between; align-items: center; gap: .6rem;
}
.part.breathe { animation: breathe 2.8s ease-in-out infinite; }
.part.gone  { opacity: 0; transform: translateY(40px) scale(.7); filter: blur(4px); }     /* composition: destroyed */
.part.freed { transform: translateX(60px); border-color: var(--bp-good); color: var(--bp-good); box-shadow: 0 0 18px rgba(74,222,128,.3); } /* aggregation: survives */
.tag { font-size: .6rem; color: var(--bp-good); }
@keyframes breathe { 0%,100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-3px) scale(1.02); } }

.cap { margin-top: 1.1rem; font-size: .82rem; padding: .5rem .8rem; border-radius: 8px; border: 1px solid var(--bp-line); }
.cap.c { color: var(--bp-cyan); } .cap.a { color: var(--bp-good); }
</style>
