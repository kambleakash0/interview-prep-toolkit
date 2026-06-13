<script setup lang="ts">
import { ref } from 'vue'
const specs = ref([
  { name: 'Multi-currency support', need: false },
  { name: 'Plugin architecture', need: false },
  { name: 'Distributed caching layer', need: false },
  { name: 'save(order)', need: true },
])
const pruned = ref(false)
function prune() { pruned.value = true }
function reset() { pruned.value = false }
</script>

<template>
  <div class="yagni">
    <div class="head">
      <span class="bp-dim">Backlog for a feature that just needs to <b style="color:#fff">save an order</b>:</span>
      <button class="act" @click="pruned ? reset() : prune()">{{ pruned ? '↺ reset' : 'You aren’t gonna need it ✕' }}</button>
    </div>

    <div class="list">
      <div v-for="s in specs" :key="s.name" class="item" :class="{ need: s.need, gone: pruned && !s.need, keep: pruned && s.need }">
        <span class="dot" />
        <span class="nm">{{ s.name }}</span>
        <span v-if="s.need" class="tag ok">actually needed</span>
        <span v-else class="tag spec">speculative</span>
      </div>
    </div>

    <div class="note" :class="pruned ? 'ok' : 'bad'">
      {{ pruned ? 'Ship the one thing you need. Add the rest when a real requirement shows up.'
                : 'Three speculative features, zero current users for them — pure maintenance cost.' }}
    </div>
  </div>
</template>

<style scoped>
.yagni { font-family: "Fira Code", monospace; }
.head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1.2rem; font-size: .9rem; }
.act { font-family: inherit; font-size: .8rem; padding: .45rem .9rem; border: 1px solid var(--bp-warn); color: var(--bp-warn); border-radius: 8px; background: rgba(251,191,36,.07); cursor: pointer; white-space: nowrap; }
.list { display: flex; flex-direction: column; gap: .55rem; max-width: 34rem; }
.item { display: flex; align-items: center; gap: .7rem; padding: .55rem .9rem; border: 1px solid var(--bp-line); border-radius: 9px; font-size: .9rem; color: var(--bp-ink); transition: all .5s ease; }
.item .dot { width: 8px; height: 8px; border-radius: 999px; background: var(--bp-dim); flex: none; }
.item.need .dot { background: var(--bp-good); }
.item.gone { opacity: 0; transform: translateX(40px) scale(.9); border-color: transparent; }
.item.keep { border-color: var(--bp-good); background: rgba(74,222,128,.07); }
.nm { flex: 1; } .tag { font-size: .6rem; padding: .12em .6em; border-radius: 999px; }
.tag.spec { color: var(--bp-dim); border: 1px solid var(--bp-line); }
.tag.ok { color: var(--bp-good); border: 1px solid rgba(74,222,128,.4); }
.note { margin-top: 1.2rem; font-size: .85rem; padding: .5rem .8rem; border-radius: 8px; border: 1px solid var(--bp-line); max-width: 34rem; }
.note.bad { color: var(--bp-bad); } .note.ok { color: var(--bp-good); }
</style>
