<script setup lang="ts">
import { ref } from 'vue'

const linked = ref(false)
const courseAlive = ref(true)

function enroll() { if (courseAlive.value) linked.value = true }
function dropCourse() { courseAlive.value = false; linked.value = false }
function reset() { courseAlive.value = true; linked.value = false }
</script>

<template>
  <div class="al">
    <div class="stage">
      <div class="node course" :class="{ gone: !courseAlive }">
        Course
        <span class="field">students[]</span>
      </div>

      <div class="wires">
        <div class="wire top" :class="{ on: linked }"><span class="cap">has &rarr;</span></div>
        <div class="wire bot" :class="{ on: linked }"><span class="cap">&larr; course</span></div>
      </div>

      <div class="node student">
        Student
        <span class="field">course</span>
      </div>
    </div>

    <div class="ctl">
      <button class="b" :disabled="!courseAlive" @click="enroll">course.enroll(student)</button>
      <button class="b bad" :disabled="!courseAlive" @click="dropCourse">del course</button>
      <button class="b ghost" @click="reset">reset</button>
    </div>
    <div class="msg" :class="{ warn: !courseAlive }">
      {{ !courseAlive
        ? 'Course deleted — the Student still exists. Neither owns the other.'
        : linked
          ? 'Both sides reference each other — an association, not ownership.'
          : 'Two independent objects. Link them with enroll().' }}
    </div>
  </div>
</template>

<style scoped>
.al { font-family: "Fira Code", monospace; display: flex; flex-direction: column; gap: 1rem; }
.stage { display: grid; grid-template-columns: 1fr 1.2fr 1fr; align-items: center; }
.node { display: flex; flex-direction: column; align-items: center; gap: .3rem; padding: .8rem .6rem; border: 1px solid var(--bp-line); border-radius: 10px; background: rgba(255,255,255,.03); color: #fff; font-size: .9rem; transition: all .4s ease; }
.node .field { font-size: .62rem; color: var(--bp-dim); }
.node.course { border-color: rgba(34,211,238,.4); }
.node.student { border-color: rgba(167,139,250,.4); }
.node.gone { opacity: .12; transform: scale(.9); filter: grayscale(1); }
.wires { display: flex; flex-direction: column; gap: 1rem; position: relative; }
.wire { position: relative; height: 0; border-top: 1.5px dashed var(--bp-line); transition: border-color .4s; }
.wire.on.top { border-top-color: var(--bp-cyan); border-top-style: solid; }
.wire.on.bot { border-top-color: var(--bp-violet); border-top-style: solid; }
.wire .cap { position: absolute; top: -1.1rem; left: 50%; transform: translateX(-50%); font-size: .64rem; color: var(--bp-dim); white-space: nowrap; }
.wire.on.top .cap { color: var(--bp-cyan); }
.wire.on.bot .cap { color: var(--bp-violet); top: .2rem; }
.ctl { display: flex; flex-wrap: wrap; gap: .5rem; }
.b { font-family: inherit; font-size: .76rem; padding: .4rem .8rem; border: 1px solid var(--bp-cyan); color: var(--bp-cyan); border-radius: 8px; background: rgba(34,211,238,.08); cursor: pointer; }
.b.bad { border-color: rgba(251,113,133,.5); color: var(--bp-bad); background: rgba(251,113,133,.06); }
.b.ghost { border-color: var(--bp-line); color: var(--bp-dim); background: transparent; }
.b:disabled { opacity: .35; cursor: not-allowed; }
.msg { font-size: .78rem; color: var(--bp-dim); line-height: 1.5; padding: .55rem .7rem; border: 1px solid var(--bp-line); border-radius: 8px; }
.msg.warn { color: var(--bp-warn); border-color: rgba(251,191,36,.3); }
</style>
