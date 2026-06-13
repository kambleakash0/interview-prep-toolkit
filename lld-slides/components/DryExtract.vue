<script setup lang="ts">
import { ref } from 'vue'
const extracted = ref(false)
const USERS = ['AuthService', 'PaymentService', 'SignupService']
</script>

<template>
  <div class="dry">
    <div class="ctl">
      <button :class="{ on: !extracted }" @click="extracted = false">Duplicated</button>
      <button :class="{ on: extracted }"  @click="extracted = true">Apply DRY</button>
    </div>

    <!-- duplicated: same logic copy-pasted in 3 places -->
    <div v-if="!extracted" class="grid3">
      <div class="copy" v-for="u in USERS" :key="u">
        <div class="cn">{{ u }}</div>
        <pre class="snip">if "@" in email \nand "." in email:
    ...</pre>
        <span class="tag bad">copy #{{ USERS.indexOf(u) + 1 }}</span>
      </div>
    </div>

    <!-- extracted: one source of truth -->
    <div v-else class="extracted">
      <div class="src">
        <div class="cn">EmailValidator <span class="tag ok">single source of truth</span></div>
        <pre class="snip">def is_valid(email):
    return "@" in email and "." in email</pre>
      </div>
      <div class="users">
        <div class="u" v-for="(u, i) in USERS" :key="u" :style="{ animationDelay: 90 * i + 'ms' }">{{ u }} <span class="arr">&rarr; uses it</span></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dry { font-family: "Fira Code", monospace; }
.ctl { display: inline-flex; border: 1px solid var(--bp-line); border-radius: 8px; overflow: hidden; margin-bottom: 1.4rem; }
.ctl button { font-family: inherit; font-size: .82rem; padding: .45rem 1rem; background: transparent; color: var(--bp-dim); cursor: pointer; }
.ctl button.on { background: rgba(34,211,238,.14); color: var(--bp-cyan); }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; }
.copy { border: 1px solid rgba(251,113,133,.35); border-radius: 10px; padding: .8rem; background: rgba(251,113,133,.05); }
.cn { color: #fff; font-size: .9rem; margin-bottom: .5rem; }
.snip { font-size: .76rem; color: var(--bp-dim); margin: 0; white-space: pre-wrap; line-height: 1.45; }
.tag { font-size: .58rem; padding: .12em .55em; border-radius: 999px; }
.tag.bad { color: var(--bp-bad); border: 1px solid rgba(251,113,133,.4); display: inline-block; margin-top: .5rem; }
.tag.ok { color: var(--bp-good); border: 1px solid rgba(74,222,128,.4); margin-left: .5rem; }
.extracted { display: grid; grid-template-columns: 1.4fr 1fr; gap: 1.4rem; align-items: center; animation: fade .35s; }
.src { border: 1px solid var(--bp-cyan); border-radius: 11px; padding: 1rem 1.2rem; background: rgba(34,211,238,.07); box-shadow: var(--bp-glow); }
.users { display: flex; flex-direction: column; gap: .5rem; }
.u { padding: .5rem .8rem; border: 1px solid rgba(74,222,128,.3); border-radius: 8px; background: rgba(74,222,128,.05); font-size: .85rem; color: var(--bp-ink); animation: rise .4s ease both; }
.u .arr { color: var(--bp-good); font-size: .75rem; }
@keyframes rise { from { opacity: 0; transform: translateX(12px); } to { opacity: 1; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
</style>
