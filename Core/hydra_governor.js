// HYDRA GOVERNOR V6.7 AUTONOMY - bogdanstancu1119-maker 25 Aug 2026
export const clamp = (v, min = 0, max = 1) => Math.max(min, Math.min(max, v))
function normalize(x, min, max) { if (max === min) return 0; return clamp((x - min) / (max - min)) }
function mathScore(p, s) {
  const gain = normalize(p.expectedGain, 0, 100)
  const cost = 1 - normalize(p.expectedCost, 0, 100)
  const risk = 1 - normalize(p.expectedRisk, 0, 100)
  const evidence = normalize(p.evidence, 0, 100)
  const coherence = s.coherence
  return clamp(0.30 * gain + 0.20 * cost + 0.25 * risk + 0.15 * evidence + 0.10 * coherence)
}
function psieScore(p, s) {
  const continuity = clamp(1 - Math.abs(p.psieDelta - 0.5))
  const alignment = clamp(s.psie)
  const stability = clamp(s.stability)
  const trust = clamp(s.trust)
  const entropyPenalty = 1 - clamp(s.entropy)
  return clamp(0.30 * alignment + 0.20 * continuity + 0.20 * stability + 0.20 * trust + 0.10 * entropyPenalty)
}
export function evolutionGate(p, s) {
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
function bumpVersion(version, kind) {
  const parts = version.split('.').map(Number)
  const [maj, min, pat] = [parts[0] || 1, parts[1] || 0, parts[2] || 0]
  if (kind === 'platform' || kind === 'policy') return `${maj + 1}.0.0`
  if (kind === 'agent') return `${maj}.${min + 1}.0`
  return `${maj}.${min}.${pat + 1}`
}
export function evaluatePlatform(pl) {
  return clamp(0.25 * pl.availability + 0.25 * pl.reliability + 0.20 * pl.maturity + 0.15 * (1 - normalize(pl.latencyMs, 0, 2000)) + 0.15 * (1 - normalize(pl.costPerUnit, 0, 100)))
}
export function rankPlatforms(platforms) {
  return [...platforms].map(p => ({...p, score: evaluatePlatform(p) })).sort((a, b) => (b.score || 0) - (a.score || 0))
                               }
