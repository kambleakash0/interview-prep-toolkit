<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

/* ============================================================
   ChessBoardPlayground — the two-layer move engine, live.
   Layer 1: each Piece.get_moves() emits geometry (Strategy).
   Layer 2: the RuleEngine simulates each candidate on a board
   copy and rejects any that leave your own king attacked.
   Click a piece: green = legal, red = reachable but ILLEGAL.
   ============================================================ */

type Color = 'w' | 'b'
type Kind = 'K' | 'Q' | 'R' | 'B' | 'N' | 'P'
interface Piece { color: Color; kind: Kind; moved: boolean }
type Cell = Piece | null
type Board = Cell[][]                 // [r][c], r=0 is the top (black home)

interface Sq { r: number; c: number }
interface Move {
  from: Sq; to: Sq
  piece: Piece
  captured: Cell
  flags: string                       // '' | 'castle' | 'enpassant' | 'double'
  capSq?: Sq                          // en-passant: captured pawn sits elsewhere
  rook?: { from: Sq; to: Sq }         // castling: the rook that rode along
  prevEp: Sq | null                   // en-passant target before this move (for revert)
  prevMoved: boolean                  // piece.moved before this move (for revert)
  prevRookMoved?: boolean
  san: string                         // algebraic-ish label for the history list
}

/* candidate destination, split exactly the way the engine splits it:
   geometry from get_moves(), then the referee verdict. */
interface Cand { r: number; c: number; legal: boolean; capture: boolean }

const KINDS: Record<Kind, string> = { K: 'K', Q: 'Q', R: 'R', B: 'B', N: 'N', P: 'P' }
const GLYPH: Record<Kind, string> = { K: '♚', Q: '♛', R: '♜', B: '♝', N: '♞', P: '♟' }

/* ---------- board factory ---------- */
function emptyBoard(): Board {
  return Array.from({ length: 8 }, () => Array<Cell>(8).fill(null))
}
function pc(color: Color, kind: Kind): Piece { return { color, kind, moved: false } }

function standardBoard(): Board {
  const b = emptyBoard()
  const back: Kind[] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
  for (let c = 0; c < 8; c++) {
    b[0][c] = pc('b', back[c])
    b[1][c] = pc('b', 'P')
    b[6][c] = pc('w', 'P')
    b[7][c] = pc('w', back[c])
  }
  return b
}
// a position one move from castling kingside (white king + rook un-moved, files clear)
function castleBoard(): Board {
  const b = emptyBoard()
  b[7][4] = pc('w', 'K'); b[7][7] = pc('w', 'R'); b[7][0] = pc('w', 'R')
  b[0][4] = pc('b', 'K'); b[0][0] = pc('b', 'R'); b[0][7] = pc('b', 'R')
  b[6][4] = pc('w', 'P'); b[6][3] = pc('w', 'P'); b[6][5] = pc('w', 'P')
  b[1][4] = pc('b', 'P')
  return b
}
// a position where a black pawn just ran two squares past a white pawn
function enPassantBoard(): { board: Board; ep: Sq | null } {
  const b = emptyBoard()
  b[7][4] = pc('w', 'K'); b[0][4] = pc('b', 'K')
  const wp = pc('w', 'P'); wp.moved = true
  b[3][4] = wp                                   // white pawn poised on the 5th rank
  const bp = pc('b', 'P'); bp.moved = true
  b[3][5] = bp                                   // black pawn that "just" double-stepped
  b[7][0] = pc('w', 'R')
  return { board: b, ep: { r: 2, c: 5 } }        // the square the white pawn may capture into
}

/* ---------- reactive game state ---------- */
const board = ref<Board>(standardBoard())
const turn = ref<Color>('w')
const sel = ref<Sq | null>(null)
const cands = ref<Cand[]>([])
const history = ref<Move[]>([])
const enPassant = ref<Sq | null>(null)          // current en-passant target square, if any
const attackMap = ref(false)
const lastFrom = ref<Sq | null>(null)
const lastTo = ref<Sq | null>(null)
const illegalFlash = ref<Sq | null>(null)
const scenario = ref<'standard' | 'castle' | 'enpassant'>('standard')

type GState = 'ACTIVE' | 'CHECK' | 'CHECKMATE' | 'STALEMATE'
const gameState = ref<GState>('ACTIVE')
const detection = ref('engine idle - click any piece to see its moves')

const timers: ReturnType<typeof setTimeout>[] = []
function later(fn: () => void, ms: number) { timers.push(setTimeout(fn, ms)) }
onUnmounted(() => { timers.forEach(clearTimeout) })

/* ---------- geometry helpers ---------- */
function inb(r: number, c: number) { return r >= 0 && r < 8 && c >= 0 && c < 8 }
function at(b: Board, r: number, c: number): Cell { return b[r][c] }
function eq(a: Sq, x: Sq) { return a.r === x.r && a.c === x.c }

const RAYS: Record<'R' | 'B' | 'Q', number[][]> = {
  R: [[1, 0], [-1, 0], [0, 1], [0, -1]],
  B: [[1, 1], [1, -1], [-1, 1], [-1, -1]],
  Q: [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]],
}
const KNIGHT = [[1, 2], [2, 1], [-1, 2], [-2, 1], [1, -2], [2, -1], [-1, -2], [-2, -1]]
const KING = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

/* ---------- Piece.get_moves(): Strategy hook, raw geometry only ----------
   No check-awareness here. Sliders ray-walk until blocked; pawn is stateful
   (double step, diagonal capture, en passant). This is layer 1. */
function getMoves(b: Board, s: Sq, ep: Sq | null): Sq[] {
  const p = at(b, s.r, s.c); if (!p) return []
  const out: Sq[] = []
  if (p.kind === 'N') {
    for (const [dr, dc] of KNIGHT) {
      const r = s.r + dr, c = s.c + dc
      if (inb(r, c) && (!b[r][c] || b[r][c]!.color !== p.color)) out.push({ r, c })
    }
  } else if (p.kind === 'K') {
    for (const [dr, dc] of KING) {
      const r = s.r + dr, c = s.c + dc
      if (inb(r, c) && (!b[r][c] || b[r][c]!.color !== p.color)) out.push({ r, c })
    }
  } else if (p.kind === 'P') {
    const dir = p.color === 'w' ? -1 : 1
    const start = p.color === 'w' ? 6 : 1
    const one = s.r + dir
    if (inb(one, s.c) && !b[one][s.c]) {
      out.push({ r: one, c: s.c })
      const two = s.r + 2 * dir
      if (s.r === start && !b[two][s.c]) out.push({ r: two, c: s.c })
    }
    for (const dc of [-1, 1]) {
      const r = one, c = s.c + dc
      if (!inb(r, c)) continue
      const tgt = b[r][c]
      if (tgt && tgt.color !== p.color) out.push({ r, c })
      else if (ep && ep.r === r && ep.c === c) out.push({ r, c })   // en passant
    }
  } else {
    const dirs = RAYS[p.kind as 'R' | 'B' | 'Q']
    for (const [dr, dc] of dirs) {
      let r = s.r + dr, c = s.c + dc
      while (inb(r, c)) {
        const tgt = b[r][c]
        if (!tgt) out.push({ r, c })
        else { if (tgt.color !== p.color) out.push({ r, c }); break }
        r += dr; c += dc
      }
    }
  }
  return out
}

/* ---------- Board.is_attacked / king_sq ---------- */
function kingSq(b: Board, color: Color): Sq | null {
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
    const p = b[r][c]; if (p && p.kind === 'K' && p.color === color) return { r, c }
  }
  return null
}
// is square (tr,tc) attacked by `by`? scan every enemy piece's raw geometry.
function isAttacked(b: Board, tr: number, tc: number, by: Color): boolean {
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
    const p = b[r][c]; if (!p || p.color !== by) continue
    if (p.kind === 'P') {                       // pawns attack only the two diagonals
      const dir = by === 'w' ? -1 : 1
      if (r + dir === tr && (c - 1 === tc || c + 1 === tc)) return true
      continue
    }
    for (const m of getMoves(b, { r, c }, null)) if (m.r === tr && m.c === tc) return true
  }
  return false
}

/* ---------- apply / revert: the Move is a reversible Command ---------- */
function classifyMove(b: Board, from: Sq, to: Sq, ep: Sq | null): Partial<Move> {
  const p = at(b, from.r, from.c)!
  if (p.kind === 'K' && Math.abs(to.c - from.c) === 2) {
    const kingside = to.c > from.c
    const rookFrom = { r: from.r, c: kingside ? 7 : 0 }
    const rookTo = { r: from.r, c: kingside ? 5 : 3 }
    return { flags: 'castle', rook: { from: rookFrom, to: rookTo } }
  }
  if (p.kind === 'P' && ep && eq(to, ep)) {
    return { flags: 'enpassant', capSq: { r: from.r, c: to.c } }
  }
  if (p.kind === 'P' && Math.abs(to.r - from.r) === 2) return { flags: 'double' }
  return { flags: '' }
}

function applyMove(b: Board, from: Sq, to: Sq, ep: Sq | null): Move {
  const p = at(b, from.r, from.c)!
  const meta = classifyMove(b, from, to, ep)
  const mv: Move = {
    from, to, piece: p, captured: at(b, to.r, to.c),
    flags: meta.flags || '', capSq: meta.capSq, rook: meta.rook,
    prevEp: ep, prevMoved: p.moved, san: '',
  }
  b[to.r][to.c] = p
  b[from.r][from.c] = null
  p.moved = true
  if (mv.flags === 'enpassant' && mv.capSq) {
    mv.captured = b[mv.capSq.r][mv.capSq.c]
    b[mv.capSq.r][mv.capSq.c] = null
  }
  if (mv.flags === 'castle' && mv.rook) {
    const rk = b[mv.rook.from.r][mv.rook.from.c]!
    mv.prevRookMoved = rk.moved
    b[mv.rook.to.r][mv.rook.to.c] = rk
    b[mv.rook.from.r][mv.rook.from.c] = null
    rk.moved = true
  }
  if (p.kind === 'P' && (to.r === 0 || to.r === 7)) p.kind = 'Q'   // promotion on back rank
  mv.san = toSan(mv)
  return mv
}

function revertMove(b: Board, mv: Move) {
  const p = mv.piece
  if (p.kind === 'Q' && mv.piece.kind === 'Q' && (mv.to.r === 0 || mv.to.r === 7) && wasPawn(mv))
    p.kind = 'P'
  b[mv.from.r][mv.from.c] = p
  b[mv.to.r][mv.to.c] = mv.flags === 'enpassant' ? null : mv.captured
  p.moved = mv.prevMoved
  if (mv.flags === 'enpassant' && mv.capSq) b[mv.capSq.r][mv.capSq.c] = mv.captured
  if (mv.flags === 'castle' && mv.rook) {
    const rk = b[mv.rook.to.r][mv.rook.to.c]!
    b[mv.rook.from.r][mv.rook.from.c] = rk
    b[mv.rook.to.r][mv.rook.to.c] = null
    rk.moved = mv.prevRookMoved ?? false
  }
}
// promotion detection for revert: a pawn that landed on the back rank
function wasPawn(mv: Move) {
  return (mv.to.r === 0 || mv.to.r === 7) &&
    Math.abs(mv.to.r - mv.from.r) >= 1 && Math.abs(mv.to.c - mv.from.c) <= 1 &&
    mv.from.r !== mv.to.r
}

/* ---------- RuleEngine.legal_moves(): the referee filter (layer 2) ----------
   simulate-then-check: apply on the real board, see if our king is attacked,
   revert. Pins, exposed kings, illegal castling-through-check all fall out. */
function leavesKingInCheck(b: Board, from: Sq, to: Sq, ep: Sq | null): boolean {
  const color = at(b, from.r, from.c)!.color
  // castling cannot pass through or out of check
  const meta = classifyMove(b, from, to, ep)
  if (meta.flags === 'castle') {
    const enemy: Color = color === 'w' ? 'b' : 'w'
    if (isAttacked(b, from.r, from.c, enemy)) return true
    const stepC = (from.c + to.c) / 2
    if (isAttacked(b, from.r, stepC, enemy)) return true
  }
  const mv = applyMove(b, from, to, ep)
  const ks = kingSq(b, color)
  const enemy: Color = color === 'w' ? 'b' : 'w'
  const bad = ks ? isAttacked(b, ks.r, ks.c, enemy) : false
  revertMove(b, mv)
  return bad
}

function legalDestinations(b: Board, s: Sq, ep: Sq | null): Cand[] {
  const geo = getMoves(b, s, ep)
  return geo.map(d => ({
    r: d.r, c: d.c,
    legal: !leavesKingInCheck(b, s, d, ep),
    capture: !!at(b, d.r, d.c) || (at(b, s.r, s.c)!.kind === 'P' && d.c !== s.c),
  }))
}

// does `color` have ANY legal move? drives mate vs stalemate.
function hasAnyLegalMove(b: Board, color: Color, ep: Sq | null): boolean {
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
    const p = b[r][c]; if (!p || p.color !== color) continue
    for (const d of getMoves(b, { r, c }, ep))
      if (!leavesKingInCheck(b, { r, c }, d, ep)) return true
  }
  return false
}

/* ---------- GameState detection ---------- */
function recomputeState() {
  const b = board.value
  const mover = turn.value
  const ks = kingSq(b, mover)
  const enemy: Color = mover === 'w' ? 'b' : 'w'
  const inCheck = ks ? isAttacked(b, ks.r, ks.c, enemy) : false
  const canMove = hasAnyLegalMove(b, mover, enPassant.value)
  if (inCheck && !canMove) {
    gameState.value = 'CHECKMATE'
    detection.value = `king attacked + 0 legal moves -> CHECKMATE (${mover === 'w' ? 'black' : 'white'} wins)`
  } else if (!inCheck && !canMove) {
    gameState.value = 'STALEMATE'
    detection.value = 'king safe + 0 legal moves -> STALEMATE (draw)'
  } else if (inCheck) {
    gameState.value = 'CHECK'
    detection.value = `is_attacked(king_sq(${mover})) = true -> CHECK, must respond`
  } else {
    gameState.value = 'ACTIVE'
    detection.value = `${mover === 'w' ? 'white' : 'black'} to move - ${countLegal(b, mover)} legal moves`
  }
}
function countLegal(b: Board, color: Color): number {
  let n = 0
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
    const p = b[r][c]; if (!p || p.color !== color) continue
    for (const d of getMoves(b, { r, c }, enPassant.value))
      if (!leavesKingInCheck(b, { r, c }, d, enPassant.value)) n++
  }
  return n
}

/* ---------- interaction ---------- */
const over = computed(() => gameState.value === 'CHECKMATE' || gameState.value === 'STALEMATE')

function onCell(r: number, c: number) {
  if (over.value) return
  const p = at(board.value, r, c)

  // clicking a highlighted destination => commit the move
  if (sel.value) {
    const cand = cands.value.find(x => x.r === r && x.c === c)
    if (cand) {
      if (!cand.legal) { flashIllegal(r, c); return }
      commit(sel.value, { r, c })
      return
    }
  }

  // otherwise (re)select one of your own pieces and emit its Strategy moves
  if (p && p.color === turn.value) {
    sel.value = { r, c }
    cands.value = legalDestinations(board.value, { r, c }, enPassant.value)
    const legal = cands.value.filter(x => x.legal).length
    const blocked = cands.value.length - legal
    detection.value = blocked
      ? `${KINDS[p.kind]}.get_moves() -> ${cands.value.length} geometric, referee kept ${legal}, cut ${blocked} (would leave king in check)`
      : `${KINDS[p.kind]}.get_moves() -> ${cands.value.length} moves, all survive the referee`
    return
  }

  // click on empty / enemy with nothing selected -> clear
  sel.value = null
  cands.value = []
  recomputeState()
}

function flashIllegal(r: number, c: number) {
  illegalFlash.value = { r, c }
  detection.value = 'referee rejected: simulate-then-check shows your own king attacked'
  later(() => { illegalFlash.value = null }, 650)
}

function commit(from: Sq, to: Sq) {
  const mv = applyMove(board.value, from, to, enPassant.value)
  history.value.push(mv)
  enPassant.value = mv.flags === 'double' ? { r: (from.r + to.r) / 2, c: from.c } : null
  lastFrom.value = from
  lastTo.value = to
  sel.value = null
  cands.value = []
  turn.value = turn.value === 'w' ? 'b' : 'w'
  // force reactivity for the in-place board mutation
  board.value = board.value.map(row => row.slice())
  recomputeState()
}

function undo() {
  const mv = history.value.pop()
  if (!mv) return
  revertMove(board.value, mv)
  enPassant.value = mv.prevEp
  turn.value = turn.value === 'w' ? 'b' : 'w'
  const prev = history.value[history.value.length - 1]
  lastFrom.value = prev ? prev.from : null
  lastTo.value = prev ? prev.to : null
  sel.value = null
  cands.value = []
  board.value = board.value.map(row => row.slice())
  recomputeState()
}

function loadScenario(which: 'standard' | 'castle' | 'enpassant') {
  scenario.value = which
  if (which === 'castle') { board.value = castleBoard(); enPassant.value = null }
  else if (which === 'enpassant') {
    const r = enPassantBoard(); board.value = r.board; enPassant.value = r.ep
  } else { board.value = standardBoard(); enPassant.value = null }
  turn.value = 'w'
  history.value = []
  sel.value = null
  cands.value = []
  lastFrom.value = null
  lastTo.value = null
  attackMap.value = false
  recomputeState()
  if (which === 'castle') detection.value = 'castle setup: click the white King, kingside is legal (flags + path clear + no check)'
  else if (which === 'enpassant') detection.value = 'en-passant setup: click the white Pawn on e5, the diagonal capture is enabled by the previous Move'
}

/* ---------- attack-map overlay ---------- */
const enemyAttacks = computed<boolean[][]>(() => {
  const grid = Array.from({ length: 8 }, () => Array<boolean>(8).fill(false))
  if (!attackMap.value) return grid
  const enemy: Color = turn.value === 'w' ? 'b' : 'w'
  for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++)
    grid[r][c] = isAttacked(board.value, r, c, enemy)
  return grid
})

const checkedKing = computed<Sq | null>(() => {
  if (gameState.value !== 'CHECK' && gameState.value !== 'CHECKMATE') return null
  return kingSq(board.value, turn.value)
})

/* ---------- SAN-ish labels for the history list ---------- */
function toSan(mv: Move): string {
  if (mv.flags === 'castle') return mv.to.c > mv.from.c ? 'O-O' : 'O-O-O'
  const file = 'abcdefgh'[mv.to.c]
  const rank = String(8 - mv.to.r)
  const k = mv.piece.kind === 'P' ? '' : KINDS[mv.piece.kind]
  const x = mv.captured || mv.flags === 'enpassant'
    ? (mv.piece.kind === 'P' ? 'abcdefgh'[mv.from.c] + 'x' : 'x') : ''
  const ep = mv.flags === 'enpassant' ? ' e.p.' : ''
  return `${k}${x}${file}${rank}${ep}`
}
const historyRows = computed(() => {
  const rows: { n: number; w: string; b: string }[] = []
  for (let i = 0; i < history.value.length; i += 2) {
    rows.push({
      n: i / 2 + 1,
      w: history.value[i]?.san ?? '',
      b: history.value[i + 1]?.san ?? '',
    })
  }
  return rows
})

const SCENS = [
  { id: 'standard', label: 'New game' },
  { id: 'castle', label: 'Castling' },
  { id: 'enpassant', label: 'En passant' },
] as const

function isSel(r: number, c: number) { return sel.value && eq(sel.value, { r, c }) }
function candAt(r: number, c: number) { return cands.value.find(x => x.r === r && x.c === c) }

recomputeState()
</script>

<template>
  <div class="cb">
    <!-- ============ LEFT: board ============ -->
    <div class="boardcol">
      <div class="banner" :class="gameState.toLowerCase()">
        <span class="gstate">{{ gameState }}</span>
        <span class="bturn">turn:&nbsp;<b :class="turn">{{ turn === 'w' ? 'White' : 'Black' }}</b></span>
        <span class="bep" v-if="enPassant">e.p. target: {{ 'abcdefgh'[enPassant.c] }}{{ 8 - enPassant.r }}</span>
      </div>

      <div class="grid" :class="{ mapon: attackMap }">
        <template v-for="(row, r) in board" :key="r">
          <button
            v-for="(cell, c) in row"
            :key="r + '-' + c"
            class="sq"
            :class="{
              dark: (r + c) % 2 === 1,
              sel: isSel(r, c),
              legal: candAt(r, c) && candAt(r, c)!.legal,
              illegalmove: candAt(r, c) && !candAt(r, c)!.legal,
              capture: candAt(r, c) && candAt(r, c)!.capture,
              lastf: lastFrom && lastFrom.r === r && lastFrom.c === c,
              lastt: lastTo && lastTo.r === r && lastTo.c === c,
              flash: illegalFlash && illegalFlash.r === r && illegalFlash.c === c,
              checked: checkedKing && checkedKing.r === r && checkedKing.c === c,
              attacked: attackMap && enemyAttacks[r][c],
            }"
            @click="onCell(r, c)"
          >
            <span v-if="cell" class="pc" :class="cell.color">{{ GLYPH[cell.kind] }}</span>
            <span v-if="candAt(r, c) && candAt(r, c)!.legal && !cell" class="dot" />
            <span v-if="candAt(r, c) && candAt(r, c)!.legal && cell" class="ring" />
            <span v-if="candAt(r, c) && !candAt(r, c)!.legal" class="cross">x</span>
          </button>
        </template>
      </div>

      <div class="legend">
        <span class="lg legal">legal move</span>
        <span class="lg illegal">would expose king</span>
        <span class="lg atk" :class="{ off: !attackMap }">enemy attack</span>
      </div>
    </div>

    <!-- ============ RIGHT: control rail ============ -->
    <div class="railcol">
      <div class="rtag">two-layer move engine</div>

      <!-- live detection: which rule fired -->
      <div class="detect" :class="gameState.toLowerCase()">
        <span class="dk">&gt;</span>
        <span class="dtext">{{ detection }}</span>
      </div>

      <!-- layer split: Strategy output vs referee verdict -->
      <div class="split">
        <div class="splitcell s-strat">
          <span class="sl">Piece.get_moves()</span>
          <span class="sn">{{ cands.length || '-' }}</span>
          <span class="sc">geometry</span>
        </div>
        <span class="arrow">-&gt;</span>
        <div class="splitcell s-ref">
          <span class="sl">RuleEngine filter</span>
          <span class="sn good">{{ cands.filter(x => x.legal).length || (cands.length ? 0 : '-') }}</span>
          <span class="sc">legal</span>
        </div>
        <div class="splitcell s-cut" v-if="cands.length">
          <span class="sl">rejected</span>
          <span class="sn bad">{{ cands.filter(x => !x.legal).length }}</span>
          <span class="sc">king exposed</span>
        </div>
      </div>

      <!-- scenario stages: the stateful special moves -->
      <div class="scens">
        <button
          v-for="s in SCENS"
          :key="s.id"
          class="scn"
          :class="{ on: scenario === s.id }"
          @click="loadScenario(s.id)"
        >{{ s.label }}</button>
      </div>

      <!-- attack-map toggle + undo -->
      <div class="ctrls">
        <button class="tog" :class="{ on: attackMap }" @click="attackMap = !attackMap">
          <span class="knob" /> Attack map
        </button>
        <button class="undo" :disabled="!history.length" @click="undo">&#9100; Undo Move</button>
      </div>

      <!-- move history = the Command log -->
      <div class="histwrap">
        <div class="histhead">
          <span>Move history</span>
          <span class="hcount">{{ history.length }} Move{{ history.length === 1 ? '' : 's' }}</span>
        </div>
        <div class="hist">
          <div v-for="row in historyRows" :key="row.n" class="hrow">
            <span class="hn">{{ row.n }}.</span>
            <span class="hw">{{ row.w }}</span>
            <span class="hb">{{ row.b }}</span>
          </div>
          <div v-if="!history.length" class="hempty">each Move is a reversible Command - Undo pops one</div>
        </div>
      </div>

      <div class="railhint">
        Green/red split = the SAME candidate list, with vs without the referee filter.
      </div>
    </div>
  </div>
</template>

<style scoped>
.cb {
  display: grid;
  grid-template-columns: 1fr 1.18fr;
  gap: 1.3rem;
  width: 100%;
  height: 366px;
  box-sizing: border-box;
  font-family: "Fira Code", monospace;
  color: var(--bp-ink);
}

/* ---------- board column ---------- */
.boardcol { display: flex; flex-direction: column; gap: .5rem; min-width: 0; }

.banner {
  display: flex; align-items: center; gap: .7rem;
  border: 1px solid var(--bp-line); border-radius: 9px;
  padding: .3rem .6rem; transition: all .35s;
}
.banner.active { border-color: var(--bp-line); }
.banner.check { border-color: rgba(251,191,36,.55); background: rgba(251,191,36,.08); box-shadow: 0 0 16px rgba(251,191,36,.25); animation: pulseb .5s ease; }
.banner.checkmate { border-color: rgba(251,113,133,.6); background: rgba(251,113,133,.1); box-shadow: 0 0 18px rgba(251,113,133,.35); animation: pulseb .5s ease; }
.banner.stalemate { border-color: rgba(138,160,192,.5); background: rgba(138,160,192,.08); }
@keyframes pulseb { 0% { transform: scale(1); } 45% { transform: scale(1.015); } 100% { transform: scale(1); } }
.gstate { font-size: .68rem; letter-spacing: .1em; color: var(--bp-cyan); font-weight: 700; }
.banner.check .gstate { color: var(--bp-warn); }
.banner.checkmate .gstate { color: var(--bp-bad); }
.banner.stalemate .gstate { color: var(--bp-dim); }
.bturn { font-size: .62rem; color: var(--bp-dim); margin-left: auto; }
.bturn b.w { color: var(--bp-cyan); }
.bturn b.b { color: var(--bp-violet); }
.bep { font-size: .54rem; color: var(--bp-good); border: 1px solid rgba(74,222,128,.35); border-radius: 999px; padding: .05rem .4rem; }

.grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  grid-template-rows: repeat(8, 1fr);
  width: 100%;
  aspect-ratio: 1 / 1;
  max-height: 268px;
  max-width: 268px;
  border: 1px solid var(--bp-line);
  border-radius: 8px;
  overflow: hidden;
}
.sq {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  border: 0; padding: 0; margin: 0;
  background: rgba(11,19,36,.55);
  cursor: pointer; font-family: inherit;
  transition: background .2s, box-shadow .2s;
}
.sq.dark { background: rgba(56,189,248,.05); }
.sq:hover { background: rgba(34,211,238,.12); }
.sq .pc { font-size: 1.42rem; line-height: 1; user-select: none; }
.sq .pc.w { color: #eef6ff; text-shadow: 0 0 6px rgba(34,211,238,.55), 0 1px 1px #000; }
.sq .pc.b { color: #9db4d6; text-shadow: 0 0 7px rgba(167,139,250,.55), 0 1px 1px #000; }

.sq.lastf { box-shadow: inset 0 0 0 2px rgba(56,189,248,.35); }
.sq.lastt { box-shadow: inset 0 0 0 2px rgba(34,211,238,.6); }
.sq.sel { box-shadow: inset 0 0 0 2px var(--bp-cyan); background: rgba(34,211,238,.16); }

/* legal destination marker */
.dot { width: 12px; height: 12px; border-radius: 999px; background: var(--bp-good); box-shadow: 0 0 10px rgba(74,222,128,.7); }
.ring { position: absolute; inset: 3px; border: 2px solid var(--bp-good); border-radius: 999px; box-shadow: 0 0 10px rgba(74,222,128,.55); }
.sq.legal:hover { background: rgba(74,222,128,.18); }

/* illegal (geometrically reachable but rejected by the referee) */
.sq.illegalmove .cross { color: var(--bp-bad); font-size: 1rem; font-weight: 700; opacity: .8; }
.sq.illegalmove { background: rgba(251,113,133,.12); }
.sq.illegalmove:hover { background: rgba(251,113,133,.2); }
.sq.flash { animation: shakef .5s; background: rgba(251,113,133,.32); }
@keyframes shakef { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-3px)} 60%{transform:translateX(3px)} }

/* attack-map heat overlay */
.sq.attacked::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at center, rgba(251,113,133,.32), rgba(251,113,133,.1));
  pointer-events: none;
}
/* king in check */
.sq.checked { box-shadow: inset 0 0 0 3px var(--bp-bad); background: rgba(251,113,133,.22); animation: pulsek .7s infinite alternate; }
@keyframes pulsek { from { box-shadow: inset 0 0 0 3px rgba(251,113,133,.6); } to { box-shadow: inset 0 0 0 3px rgba(251,113,133,1); } }

.legend { display: flex; gap: .8rem; margin-top: .1rem; }
.lg { font-size: .52rem; color: var(--bp-dim); display: inline-flex; align-items: center; gap: .28rem; }
.lg::before { content: ''; width: 8px; height: 8px; border-radius: 999px; }
.lg.legal::before { background: var(--bp-good); }
.lg.illegal::before { background: var(--bp-bad); }
.lg.atk::before { background: rgba(251,113,133,.5); }
.lg.atk.off { opacity: .4; }

/* ---------- rail column ---------- */
.railcol { display: flex; flex-direction: column; gap: .5rem; min-width: 0; }
.rtag { font-size: .58rem; letter-spacing: .08em; text-transform: uppercase; color: var(--bp-cyan); }

.detect {
  display: flex; gap: .4rem; align-items: baseline;
  border: 1px solid var(--bp-line); border-radius: 8px;
  background: rgba(7,11,20,.6); padding: .42rem .55rem;
  min-height: 2.4rem; transition: all .3s;
}
.detect.check { border-color: rgba(251,191,36,.45); }
.detect.checkmate { border-color: rgba(251,113,133,.5); }
.dk { color: var(--bp-cyan); flex: none; }
.dtext { font-size: .6rem; line-height: 1.45; color: var(--bp-ink); }
.detect.check .dtext { color: var(--bp-warn); }
.detect.checkmate .dtext { color: var(--bp-bad); }

/* layer split */
.split {
  display: flex; align-items: stretch; gap: .4rem;
}
.splitcell {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: .05rem;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .35rem .3rem;
  background: rgba(255,255,255,.02);
}
.s-strat { border-color: rgba(56,189,248,.35); }
.s-ref { border-color: rgba(74,222,128,.35); background: rgba(74,222,128,.05); }
.s-cut { border-color: rgba(251,113,133,.35); background: rgba(251,113,133,.05); }
.sl { font-size: .5rem; color: var(--bp-dim); text-align: center; }
.sn { font-size: 1.05rem; color: var(--bp-blue); font-weight: 700; line-height: 1; }
.sn.good { color: var(--bp-good); }
.sn.bad { color: var(--bp-bad); }
.sc { font-size: .48rem; color: var(--bp-dim); }
.arrow { align-self: center; color: var(--bp-dim); font-size: .7rem; }

/* scenario buttons */
.scens { display: flex; gap: .4rem; }
.scn {
  flex: 1; font-family: inherit; font-size: .62rem; cursor: pointer;
  border: 1px solid var(--bp-line); border-radius: 8px; padding: .34rem .3rem;
  background: rgba(255,255,255,.02); color: var(--bp-dim); transition: all .2s;
}
.scn:hover { border-color: var(--bp-cyan); color: var(--bp-ink); }
.scn.on { border-color: var(--bp-violet); color: #fff; background: rgba(167,139,250,.14); box-shadow: 0 0 14px rgba(167,139,250,.3); }

/* attack toggle + undo */
.ctrls { display: flex; gap: .5rem; align-items: center; }
.tog {
  display: inline-flex; align-items: center; gap: .5rem;
  font-family: inherit; font-size: .64rem; color: var(--bp-dim);
  border: 1px solid var(--bp-line); border-radius: 8px;
  padding: .32rem .55rem; background: transparent; cursor: pointer; transition: all .25s;
}
.tog .knob { width: 28px; height: 15px; border-radius: 999px; background: var(--bp-line); position: relative; transition: background .3s; flex: none; }
.tog .knob::after { content: ''; position: absolute; top: 2px; left: 2px; width: 11px; height: 11px; border-radius: 999px; background: var(--bp-dim); transition: all .3s; }
.tog.on { color: var(--bp-bad); border-color: rgba(251,113,133,.5); }
.tog.on .knob { background: rgba(251,113,133,.4); }
.tog.on .knob::after { left: 15px; background: var(--bp-bad); }
.undo {
  margin-left: auto; font-family: inherit; font-size: .64rem; color: var(--bp-ink);
  border: 1px solid var(--bp-cyan); border-radius: 8px;
  padding: .32rem .6rem; background: rgba(34,211,238,.1);
  cursor: pointer; transition: all .2s;
}
.undo:hover:not(:disabled) { background: rgba(34,211,238,.2); }
.undo:disabled { opacity: .35; cursor: not-allowed; border-color: var(--bp-line); background: transparent; }

/* history */
.histwrap {
  flex: 1; min-height: 0; display: flex; flex-direction: column;
  border: 1px solid var(--bp-line); border-radius: 9px; background: rgba(255,255,255,.015);
  overflow: hidden;
}
.histhead {
  display: flex; justify-content: space-between; align-items: center;
  font-size: .54rem; text-transform: uppercase; letter-spacing: .08em;
  color: var(--bp-dim); padding: .35rem .55rem; border-bottom: 1px solid var(--bp-line);
}
.hcount { color: var(--bp-cyan); }
.hist { flex: 1; overflow-y: auto; padding: .25rem .4rem; min-height: 0; }
.hist::-webkit-scrollbar { width: 5px; }
.hist::-webkit-scrollbar-thumb { background: var(--bp-line); border-radius: 3px; }
.hrow { display: grid; grid-template-columns: 1.6rem 1fr 1fr; gap: .3rem; font-size: .6rem; padding: .08rem 0; }
.hn { color: var(--bp-dim); }
.hw { color: var(--bp-cyan); }
.hb { color: var(--bp-violet); }
.hempty { font-size: .56rem; color: var(--bp-dim); opacity: .75; padding: .3rem .15rem; line-height: 1.4; }

.railhint { font-size: .55rem; color: var(--bp-dim); line-height: 1.4; }
</style>
