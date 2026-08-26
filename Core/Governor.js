// HYDRA GOVERNOR V6.6 FINAL - EVOLUTION GATE - bogdanstancu1119-maker 24 Aug 2026
// Decide dacă Hydra are voie să evolueze. Fără el, Hydra se autodistruge.

export type Platform = {
  id: string
  name: string
  type: 'edge' | 'cloud' | 'agent' | 'db' | 'queue' | 'custom'
  capacity: number
  costPerUnit: number
  latencyMs: number
  reliability: number
  availability: number
  maturity: number
  score?: number
}

export type Agent = {
  id: string
  name: string
  category: string
  autonomy: number
  impact: number
  risk: number
  reliability: number
  psie: number
  enabled: boolean
}

export type EvolutionProposal = {
  id: string
  kind: 'platform' | 'agent' | 'workflow' | 'policy' | 'memory'
  description: string
  targetId?: string
  expectedGain: number
  expectedCost: number
  expectedRisk: number
  psieDelta: number
  evidence: number
}

export type SystemState = {
  version: string
  psie: number
  stability: number
  coherence: number
  load: number
  entropy: number
  trust: number
  enabledModules: string[]
  platforms: Platform[]
  agents: Agent[]
  history: Array<{ ts: number; action: string; data: any }>
}

export type Decision = {
  allow: boolean
  reason: string
  score: number
  psieScore: number
  mathScore: number
  riskScore: number
  nextVersion?: string
}

const clamp = (v: number, min = 0, max = 1) => Math.max(min, Math.min(max, v))
function normalize(x: number, min: number, max: number) {
  if (max === min) return 0
  return clamp((x - min) / (max - min))
}

function mathScore(p: EvolutionProposal, s: SystemState) {
  const gain = normalize(p.expectedGain, 0, 100)
  const cost = 1 - normalize(p.expectedCost, 0, 100)
  const risk = 1 - normalize(p.expectedRisk, 0, 100)
  const evidence = normalize(p.evidence, 0, 100)
  const coherence = s.coherence
  return clamp(0.30 * gain + 0.20 * cost + 0.25 * risk + 0.15 * evidence + 0.10 * coherence)
}

function psieScore(p: EvolutionProposal, s: SystemState) {
  const continuity = clamp(1 - Math.abs(p.psieDelta - 0.5))
  const alignment = clamp(s.psie)
  const stability = clamp(s.stability)
  const trust = clamp(s.trust)
  const entropyPenalty = 1 - clamp(s.entropy)
  return clamp(0.30 * alignment + 0.20 * continuity + 0.20 * stability + 0.20 * trust + 0.10 * entropyPenalty)
}

export function evolutionGate(p: EvolutionProposal, s: SystemState): Decision {
  const m = mathScore(p, s)
  const ps = psieScore(p, s)
  const risk = clamp(normalize(p.expectedRisk, 0, 100))
  const combined = clamp(0.45 * m + 0.35 * ps + 0.20 * (1 - risk))

  if (s.coherence < 0.55) return { allow: false, reason: 'coherence too low', score: combined, psieScore: ps, mathScore: m, riskScore: risk }
  if (s.psie < 0.60) return { allow: false, reason: 'PSIE too low', score: combined, psieScore: ps, mathScore: m, riskScore: risk }
  if (risk > 0.65) return { allow: false, reason: 'risk too high', score: combined, psieScore: ps, mathScore: m, riskScore: risk }
  if (combined < 0.72) return { allow: false, reason: 'below activation threshold', score: combined, psieScore: ps, mathScore: m, riskScore: risk }

  return { allow: true, reason: 'approved', score: combined, psieScore: ps, mathScore: m, riskScore: risk, nextVersion: bumpVersion(s.version, p.kind) }
}

function bumpVersion(version: string, kind: EvolutionProposal['kind']) {
  const parts = version.split('.').map(Number)
  const [maj, min, pat] = [parts[0] || 1, parts[1] || 0, parts[2] || 0]
  if (kind === 'platform' || kind === 'policy') return `${maj + 1}.0.0`
  if (kind === 'agent') return `${maj}.${min + 1}.0`
  return `${maj}.${min}.${pat + 1}`
}

export function evaluatePlatform(pl: Platform) {
  return clamp(0.25 * pl.availability + 0.25 * pl.reliability + 0.20 * pl.maturity + 0.15 * (1 - normalize(pl.latencyMs, 0, 2000)) + 0.15 * (1 - normalize(pl.costPerUnit, 0, 100)))
}
export function rankPlatforms(platforms: Platform[]) {
  return [...platforms].map(p => ({...p, score: evaluatePlatform(p) })).sort((a, b) => (b.score || 0) - (a.score || 0))
}
export function registerPlatform(state: SystemState, platform: Platform): SystemState {
  if (state.platforms.some(p => p.id === platform.id)) return state
  return {...state, platforms: [...state.platforms, platform], history: [...state.history, { ts: Date.now(), action: 'platform_registered', data: platform }] }
}
export function registerAgent(state: SystemState, agent: Agent): SystemState {
  if (state.agents.some(a => a.id === agent.id)) return state
  return {...state, agents: [...state.agents, {...agent, enabled: false }], history: [...state.history, { ts: Date.now(), action: 'agent_registered', data: agent }] }
}
export function activateAgent(state: SystemState, agentId: string): SystemState {
  return {...state, agents: state.agents.map(a => a.id === agentId? {...a, enabled: true } : a), history: [...state.history, { ts: Date.now(), action: 'agent_activated', data: { agentId } }] }
}
export function canEvolve(state: SystemState, proposal: EvolutionProposal) { return evolutionGate(proposal, state) }
export function applyEvolution(state: SystemState, proposal: EvolutionProposal): { state: SystemState; decision: Decision } {
  const decision = canEvolve(state, proposal)
  if (!decision.allow) return { state, decision }
  const nextState: SystemState = {
   ...state, version: decision.nextVersion || state.version,
    psie: clamp(state.psie + proposal.psieDelta * 0.1),
    stability: clamp(state.stability + 0.02), coherence: clamp(state.coherence + 0.03),
    entropy: clamp(state.entropy - 0.02), trust: clamp(state.trust + 0.01),
    history: [...state.history, { ts: Date.now(), action: 'evolution_applied', data: proposal }]
  }
  return { state: nextState, decision }
}
export function rollbackEvolution(state: SystemState, snapshot: SystemState): SystemState {
  return {...snapshot, history: [...state.history, { ts: Date.now(), action: 'rollback', data: { from: state.version, to: snapshot.version } }] }
}

// INTEGRARE CU V6.6 - adauga asta in hydra_v6_refactor.js runV6():
// import { evolutionGate } from './hydra_governor.js'
// const proposal = { id: crypto.randomUUID(), kind: 'memory', description: `evolve density ${brain.density}→${result.density}`, expectedGain: result.density*100, expectedCost: 5, expectedRisk: result.fallback?80:10, psieDelta: result.density-brain.density, evidence: result.clusters*10 }
// const decision = evolutionGate(proposal, { version: brain.versionString, psie: brain.density, stability: 0.8, coherence: 0.85, load: 0.3, entropy: 0.2, trust: 0.9, enabledModules:[], platforms:[], agents:[], history:[] })
// if (!decision.allow) return { status: 'blocked_by_governor', reason: decision.reason, decision }
