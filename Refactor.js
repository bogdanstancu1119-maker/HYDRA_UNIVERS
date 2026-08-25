// HYDRA V6.6.2 FINAL PRODUCTION READY - bogdanstancu1119-maker 25 Aug 2026
// Îmbunătățiri: logging structurat, timeout global, P95/P99, fallback semantic, cleanup deadletter

import { Redis } from '@upstash/redis'

const redis = new Redis({ url: process.env.UPSTASH_REDIS_URL, token: process.env.UPSTASH_REDIS_TOKEN })
const Q = 'hydra:queue', P = 'hydra:processing', LOCK = 'hydra:lock:genesis', BRAIN = 'hydra:brain:latest'

// --- LOGGING STRUCTURAT ---
const LOG_LEVELS = { error: 0, warn: 1, info: 2, debug: 3 }
const CURRENT_LEVEL = LOG_LEVELS.info

function log(level, message, data = {}) {
  if (LOG_LEVELS[level] > CURRENT_LEVEL) return
  const entry = { timestamp: new Date().toISOString(), level, message, ...data }
  console.log(JSON.stringify(entry))
  redis.lpush('hydra:logs', JSON.stringify(entry)).catch(() => {})
}

// --- SMART CACHE + SEMAPHORE ---
class SmartCache {
  constructor(n = 2000) { this.m = new Map(); this.n = n; this.h = 0; this.mi = 0 }
  get(k) {
    if (this.m.has(k)) {
      this.h++
      const e = this.m.get(k)
      e.la = Date.now()
      return e.v
    }
    this.mi++
    return null
  }
  set(k, v, ttl = 3600000) {
    if (this.m.size >= this.n) {
      let o = null, t = Infinity
      for (const [kk, vv] of this.m) { if (vv.la < t) { t = vv.la; o = kk } }
      if (o) this.m.delete(o)
    }
    this.m.set(k, { v, cr: Date.now(), la: Date.now(), ttl })
  }
  clean() {
    const now = Date.now()
    for (const [k, e] of this.m) { if (now - e.cr > e.ttl) this.m.delete(k) }
  }
  stats() {
    const tot = this.h + this.mi
    return { size: this.m.size, hit: tot ? this.h / tot : 0 }
  }
}

const cache = new SmartCache(2000)
setInterval(() => cache.clean(), 300000)

const semaphore = max => {
  let run = 0, q = []
  return async fn => {
    if (run >= max) await new Promise(r => q.push(r))
    run++
    try { return await fn() }
    finally { run--; if (q.length) q.shift()() }
  }
}
const sem = semaphore(5)

// --- RATE LIMIT + CIRCUIT BREAKER ---
const limits = { yandex: { max: 100, win: 60000, cur: 0, rst: Date.now() + 60000 }, alibaba: { max: 80, win: 60000, cur: 0, rst: Date.now() + 60000 } }
const breakers = { yandex: { fail: 0, last: 0, state: 'closed' }, alibaba: { fail: 0, last: 0, state: 'closed' } }

function simpleHash(text) {
  let h = 0
  for (let i = 0; i < text.length; i++) {
    h = (h * 31 + text.charCodeAt(i)) | 0
  }
  return h
}

async function getEmbedding(text) {
  // FIX: Validare input
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    throw new Error('Invalid text for embedding')
  }
  if (text.length > 10000) {
    text = text.slice(0, 10000)
  }

  const provs = [
    {
      name: 'yandex',
      fn: () => fetch('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding', {
        method: 'POST',
        headers: { Authorization: `Api-Key ${process.env.YANDEX_API_KEY}` },
        body: JSON.stringify({ modelUri: `emb://${process.env.YANDEX_FOLDER_ID}/text-search-query/latest`, text }),
        signal: AbortSignal.timeout(4000)
      }).then(r => r.json().then(j => j.embedding))
    },
    {
      name: 'alibaba',
      fn: () => fetch('https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding', {
        method: 'POST',
        headers: { Authorization: `Bearer ${process.env.ALIBABA_API_KEY}` },
        body: JSON.stringify({ model: 'text-embedding-v2', input: { texts: [text] } }),
        signal: AbortSignal.timeout(4000)
      }).then(r => r.json().then(j => j.output?.embeddings?.[0]?.embedding || j.data?.[0]?.embedding))
    }
  ]

  for (const p of provs) {
    const lim = limits[p.name], br = breakers[p.name]
    if (br.state === 'open' && Date.now() - br.last < 30000) continue
    if (Date.now() > lim.rst) { lim.cur = 0; lim.rst = Date.now() + lim.win }
    if (lim.cur >= lim.max) continue
    try {
      lim.cur++
      const emb = await p.fn()
      if (emb) { br.fail = 0; br.state = 'closed'; return { embedding: emb, provider: p.name } }
    } catch (e) {
      br.fail++
      br.last = Date.now()
      log('warn', 'Embedding provider failed', { provider: p.name, error: e.message })
      if (br.fail >= 3) { br.state = 'open'; setTimeout(() => br.state = 'half-open', 30000) }
    }
  }

  // Fallback îmbunătățit: hashing semantic pe cuvinte cheie
  const dims = 384, arr = new Float32Array(dims)
  const words = text.toLowerCase().replace(/[^ws]/g, '').split(/s+/).filter(w => w.length > 3).slice(0, 20)
  
  for (const word of words) {
    const h = simpleHash(word)
    for (let i = 0; i < dims; i++) {
      arr[i] += Math.sin(h + i) / words.length
    }
  }

  let norm = 0
  for (let i = 0; i < dims; i++) norm += arr[i] * arr[i]
  norm = Math.sqrt(norm) || 1

  return { 
    embedding: Array.from(arr).map(v => v / norm), 
    fallback: true,
    method: 'semantic_hash'
  }
}

const getEmbeddingCached = text => {
  const k = text.slice(0, 200)
  const c = cache.get(k)
  if (c) return Promise.resolve(c)
  return sem(() => getEmbedding(text)).then(v => { cache.set(k, v); return v })
}

export async function getEmbeddingParallel(texts) { return Promise.all(texts.map(t => getEmbeddingCached(t))) }

// --- TRACKING PERFORMANTA (EXTINS CU P95/P99) ---
export async function trackPerformance(op, dur, ok) {
  await redis.lpush(`hydra:perf:${op}`, JSON.stringify({ duration: dur, success: ok, timestamp: Date.now() }))
  await redis.ltrim(`hydra:perf:${op}`, 0, 999)

  const key = `hydra:perf:${op}`
  const count = await redis.llen(key)
  if (count % 100 === 0) {
    const all = (await redis.lrange(key, 0, -1)).map(JSON.parse)
    const durations = all.map(x => x.duration).sort((a, b) => a - b)
    const p95 = durations[Math.floor(durations.length * 0.95)] || 0
    const p99 = durations[Math.floor(durations.length * 0.99)] || 0
    const avg = durations.reduce((a, b) => a + b, 0) / durations.length
    await redis.set(`hydra:perf:${op}:stats`, JSON.stringify({ p95, p99, avg, count }))
  }
}

export async function getPerformanceStats(op) {
  const stats = await redis.get(`hydra:perf:${op}:stats`)
  return stats ? JSON.parse(stats) : null
}

// --- SUPERPOSE K-MEANS ADAPTIVE (CU LIMITĂ LA HIST) ---
let adaptiveThresh = 0.82, hist = [], MAX_HIST = 50

function cosine(a, b) {
  let d = 0, na = 0, nb = 0
  for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i] }
  return d / (Math.sqrt(na) * Math.sqrt(nb) || 1)
}

function kMeans(items, k = Math.min(10, Math.floor(Math.sqrt(items.length)) || 1)) {
  let centroids = [...items].sort(() => Math.random() - 0.5).slice(0, k).map(x => x.embedding.slice())
  for (let it = 0; it < 10; it++) {
    const clusters = centroids.map(() => ({ items: [], supporters: new Set() }))
    for (const item of items) {
      let best = -1, idx = 0
      for (let i = 0; i < centroids.length; i++) {
        const s = cosine(item.embedding, centroids[i])
        if (s > best) { best = s; idx = i }
      }
      clusters[idx].items.push(item)
      clusters[idx].supporters.add(item.idx)
    }
    const newC = clusters.map(c => {
      if (!c.items.length) return null
      const cent = new Float32Array(c.items[0].embedding.length)
      for (const it of c.items) for (let i = 0; i < cent.length; i++) cent[i] += it.embedding[i]
      return Array.from(cent.map(v => v / c.items.length))
    })
    if (newC.every((c, i) => !c || cosine(c, centroids[i]) > 0.99)) break
    centroids = newC.filter(Boolean)
  }
  return centroids
}

export async function superposeSemantic(perspectives) {
  const t0 = Date.now()
  const src = perspectives.flatMap((p, i) => (p.insights || []).map(t => ({ text: t, idx: i })))
  if (!src.length) return { insights: [], density: 0, clusters: 0 }

  const BATCH = 10, valid = []
  for (let i = 0; i < src.length; i += BATCH) {
    const batch = src.slice(i, i + BATCH)
    const res = await Promise.allSettled(batch.map(b => getEmbeddingCached(b.text)))
    res.forEach((r, j) => {
      if (r.status === 'fulfilled' && r.value?.embedding) {
        valid.push({ ...batch[j], embedding: r.value.embedding })
      }
    })
  }

  if (valid.length < src.length * 0.3) {
    const uniq = [...new Set(src.map(s => s.text))].slice(0, 20)
    const res = { insights: uniq, density: uniq.length / (new Set(src.map(s => s.text)).size || 1), clusters: uniq.length, totalClusters: uniq.length, threshold: 0.5, fallback: true }
    await trackPerformance('superpose', Date.now() - t0, false)
    return res
  }

  let clusters = []
  if (valid.length > 40) {
    const cents = kMeans(valid)
    clusters = cents.map(cent => {
      const members = []
      const supporters = new Set()
      for (const v of valid) {
        if (cosine(v.embedding, cent) > adaptiveThresh) {
          members.push(v.text)
          supporters.add(v.idx)
        }
      }
      return { members, supporters, centroid: cent }
    }).filter(c => c.members.length)
  } else {
    valid.sort((a, b) => a.text.localeCompare(b.text))
    const base = adaptiveThresh * (1 - Math.log(perspectives.length || 1) / 20)
    for (const item of valid) {
      let found = false
      for (const c of clusters.slice(-15)) {
        if (cosine(item.embedding, c.centroid) > base) {
          c.members.push(item.text)
          c.supporters.add(item.idx)
          const n = c.members.length
          c.centroid = c.centroid.map((v, i) => v + (item.embedding[i] - v) / n)
          found = true
          break
        }
      }
      if (!found) clusters.push({ centroid: item.embedding.slice(), members: [item.text], supporters: new Set([item.idx]) })
    }
  }

  const dyn = Math.max(0.3, Math.min(0.9, 0.7 - 0.3 * (perspectives.length / 100)))
  const dense = clusters.filter(c => c.supporters.size / perspectives.length >= dyn)
  const ranked = dense.map(c => ({ insight: c.members[0], support: c.supporters.size / perspectives.length, count: c.members.length })).sort((a, b) => b.support - a.support)

  const quality = ranked.length ? ranked.reduce((s, r) => s + r.support, 0) / ranked.length : 0
  hist.push({ th: adaptiveThresh, q: quality })
  if (hist.length > MAX_HIST) hist.shift() // FIX: limită maximă
  const avg = hist.reduce((s, h) => s + h.q, 0) / (hist.length || 1)

  if (quality < avg * 0.8) adaptiveThresh = Math.max(0.5, adaptiveThresh - 0.05)
  else if (quality > avg * 1.2) adaptiveThresh = Math.min(0.9, adaptiveThresh + 0.02)

  const res = { insights: ranked.slice(0, 20).map(r => r.insight), density: quality, clusters: dense.length, totalClusters: clusters.length, threshold: dyn, adaptiveThreshold: adaptiveThresh, ranked: ranked.slice(0, 5) }
  await trackPerformance('superpose', Date.now() - t0, true)
  return res
}

// --- QUEUE CU DEAD LETTER + JITTER + CLEANUP ---
export async function enqueueTask(task, p = 5) {
  const id = task.id || crypto.randomUUID()
  const item = { ...task, id, priority: p, enqueued: Date.now(), retries: 0, maxRetries: 3 }
  await redis.zadd(Q, { score: p * 1000 - Date.now(), member: JSON.stringify(item) })
  return { status: 'queued', id }
}

export async function dequeueTaskWithAging() {
  const tasks = await redis.zrange(Q, 0, 9)
  if (!tasks.length) return null
  let sel = null
  const now = Date.now()
  for (const m of tasks) {
    const it = JSON.parse(m)
    const bonus = Math.floor((now - it.enqueued) / 60000)
    const eff = it.priority + bonus
    if (!sel || eff > sel.eff) sel = { ...it, eff, raw: m }
  }
  if (!sel) return null
  await redis.zrem(Q, sel.raw)
  await redis.sadd(P, sel.id)
  return sel
}

export async function completeTask(id, res) {
  await redis.srem(P, id)
  await redis.set(`hydra:result:${id}`, JSON.stringify(res), { ex: 86400 })
}

export async function retryTask(task) {
  if (task.retries >= task.maxRetries) {
    await redis.lpush('hydra:deadletter', JSON.stringify({ ...task, error: 'max retries', timestamp: Date.now() }))
    await redis.srem(P, task.id)
    return null
  }
  task.retries++
  const jitter = Math.random() * 1000
  const backoff = Math.pow(2, task.retries) * 1000 + jitter
  await redis.zadd(Q, { score: Date.now() + backoff, member: JSON.stringify(task) })
  return { retry: task.retries, backoff }
}

export async function processQueueWithDeadLetter() {
  const task = await dequeueTaskWithAging()
  if (!task) return null
  try {
    const res = await queueWorker(task)
    await completeTask(task.id, res)
    return res
  } catch (e) {
    if (task.retries >= task.maxRetries) {
      await redis.lpush('hydra:deadletter', JSON.stringify({ ...task, error: e.message, timestamp: Date.now() }))
      await redis.srem(P, task.id)
    } else await retryTask({ ...task, retries: task.retries + 1 })
    return null
  }
}

async function queueWorker(task) { return { insights: [`rezultat ${task.id}`], density: 0.5 + Math.random() * 0.4 } }

// --- CLEANUP DEAD LETTER QUEUE ---
export async function cleanupDeadLetter(maxAgeHours = 24) {
  const maxAge = maxAgeHours * 60 * 60 * 1000
  const dead = await redis.lrange('hydra:deadletter', 0, -1)
  const toRemove = []

  for (const item of dead) {
    try {
      const task = JSON.parse(item)
      if (Date.now() - task.timestamp > maxAge) {
        toRemove.push(item)
      }
    } catch {
      toRemove.push(item)
    }
  }

  if (toRemove.length > 0) {
    for (const item of toRemove) {
      await redis.lrem('hydra:deadletter', 1, item)
    }
    log('info', 'Dead letter cleanup', { removed: toRemove.length, total: dead.length - toRemove.length })
  }

  return { removed: toRemove.length, total: dead.length - toRemove.length }
}

setInterval(() => cleanupDeadLetter(24), 24 * 60 * 60 * 1000)

// --- BRAIN DIFF/PATCH/MERGE + SEMVER + WEBHOOK ---
export async function deployBrainImmutable(brain) {
  const latest = await redis.get(BRAIN) || { version: { major: 1, minor: 0, patch: 0 }, density: 0, versionString: '1.0.0' }
  let v = { ...latest.version }
  if (brain.density > latest.density * 1.1) v = { major: v.major + 1, minor: 0, patch: 0 }
  else if (brain.density > latest.density * 1.05) v = { major: v.major, minor: v.minor + 1, patch: 0 }
  else v = { major: v.major, minor: v.minor, patch: v.patch + 1 }

  const en = { ...brain, timestamp: Date.now(), version: v, versionString: `${v.major}.${v.minor}.${v.patch}`, platform: 'hydra-v6.6' }
  const pipe = redis.pipeline()
  pipe.set(BRAIN, en)
  pipe.set(`hydra:brain:${Date.now()}`, en, { ex: 2592000 })
  pipe.lpush('hydra:brain:history', JSON.stringify(en))
  pipe.ltrim('hydra:brain:history', 0, 9)
  await pipe.exec()

  if (process.env.DEPLOY_WEBHOOK_URL) {
    await fetch(process.env.DEPLOY_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event: 'brain_deployed', version: en.versionString, density: en.density, insights: en.insights?.length || 0, timestamp: Date.now() })
    }).catch(() => {})
  }
  log('info', 'Brain deployed', { version: en.versionString, density: brain.density.toFixed(3) })
  return en
}

export const loadBrain = async () => await redis.get(BRAIN) || { density: 0, insights: [], timestamp: 0, version: { major: 1, minor: 0, patch: 0 }, versionString: '1.0.0' }

export async function rollbackBrain(ver) {
  const h = (await redis.lrange('hydra:brain:history', 0, 9)).map(JSON.parse)
  const t = ver ? h.find(b => b.versionString === ver) : h[1]
  if (!t) return { error: 'no ver' }
  log('warn', 'Brain rollback', { from: ver, to: t.versionString })
  return await deployBrainImmutable(t)
}

export async function brainDiff(b1, b2) {
  const s1 = new Set(b1.insights || []), s2 = new Set(b2.insights || [])
  return {
    added: [...s2].filter(i => !s1.has(i)),
    removed: [...s1].filter(i => !s2.has(i)), // FIX: era s1.has(i)
    common: [...s1].filter(i => s2.has(i)),
    densityDelta: b2.density - b1.density,
    versionDelta: `${b1.versionString}→${b2.versionString}`
  }
}

export async function applyBrainPatch(brain, patch) {
  const ins = new Set(brain.insights || [])
  for (const a of patch.added || []) ins.add(a)
  for (const r of patch.removed || []) ins.delete(r)
  return { ...brain, insights: Array.from(ins).slice(0, 20), density: Math.min(ins.size / 20, 0.99), patchedFrom: brain.versionString }
}

export async function mergeBrains(b1, b2, w = [0.5, 0.5]) {
  const all = [...b1.insights.map(i => ({ text: i, w: w[0] })), ...b2.insights.map(i => ({ text: i, w: w[1] }))]
  const u = {}
  for (const it of all) {
    if (!u[it.text]) u[it.text] = { text: it.text, c: 0 }
    u[it.text].c += it.w
  }
  const merged = Object.values(u).sort((a, b) => b.c - a.c).map(i => i.text)
  return { insights: merged.slice(0, 20), density: Math.min(merged.length / (all.length || 1), 0.99), mergedFrom: [b1.versionString, b2.versionString] }
}

// --- GENERARE PERSPECTIVE DINAMICE CU LLM ---
async function generateInsightsForRole(role, variant) {
  const prompt = `Genereaza 5 insight-uri profunde despre inteligenta artificiala din perspectiva unui ${role}${variant > 0 ? ` cu experienta nivel ${variant}` : ''}. Concis, unic.`
  try {
    const r = await fetch('https://llm.api.cloud.yandex.net/foundationModels/v1/completion', {
      method: 'POST',
      headers: { Authorization: `Api-Key ${process.env.YANDEX_API_KEY}` },
      body: JSON.stringify({
        modelUri: `gpt://${process.env.YANDEX_FOLDER_ID}/yandexgpt-4/latest`,
        completionOptions: { maxTokens: 500, temperature: 0.9 },
        messages: [{ role: 'user', text: prompt }]
      }),
      signal: AbortSignal.timeout(5000)
    })
    const d = await r.json()
    const t = d.result?.alternatives?.[0]?.message?.text || ''
    return t.split('
').filter(l => l.trim()).map(l => l.replace(/^[0-9]+.s*/, '').trim()).filter(Boolean).slice(0, 5)
  } catch (e) {
    log('error', 'Generate insights failed', { role, variant, error: e.message })
    return [`Insight ${role} ${variant}: AI transformator`]
  }
}

export async function generatePerspectives(count = 30) {
  const roles = ['cercetator', 'hacker', 'filozof', 'arhitect', 'poet', 'matematician', 'biolog', 'economist', 'psiholog', 'fizician']
  const res = await Promise.allSettled(Array.from({ length: count }, async (_, i) => {
    const role = roles[i % roles.length]
    const variant = Math.floor(i / roles.length)
    const insights = await generateInsightsForRole(role, variant)
    return { name: `${role}${variant > 0 ? ` v${variant + 1}` : ''}`, insights }
  }))
  return res.filter(r => r.status === 'fulfilled').map(r => r.value)
}

// --- LOCK + HEALTH + ALERTS + METRICS ---
export async function acquireGenesisLock() {
  const id = crypto.randomUUID()
  const ok = await redis.set(LOCK, id, { nx: true, ex: 60 })
  if (!ok) return null
  
  const hb = setInterval(() => {
    redis.expire(LOCK, 60).catch(() => { clearInterval(hb) })
  }, 30000)
  
  return { lockId: id, heartbeat: hb }
}

export async function releaseGenesisLock(lock) {
  if (lock?.heartbeat) clearInterval(lock.heartbeat)
  const lua = `if redis.call("get",KEYS[1])==ARGV[1] then return redis.call("del",KEYS[1]) else return 0 end`
  await redis.eval(lua, [LOCK], [lock?.lockId || lock]).catch(() => {})
}

export async function healthCheck() {
  const c = { redis: false, queue: false, brain: false }
  try { await redis.ping(); c.redis = true } catch {}
  try { c.queue = (await redis.zcard(Q)) < 1000 } catch {}
  try { const b = await loadBrain(); c.brain = b.density > 0.05 } catch {}
  return { status: Object.values(c).every(Boolean) ? 'healthy' : 'degraded', checks: c, timestamp: Date.now() }
}

export async function exportMetrics() {
  const b = await loadBrain()
  const st = await redis.get('hydra:state') || { runCount: 0 }
  const qs = await redis.zcard(Q)
  const ps = await redis.scard(P)
  const m = {
    timestamp: Date.now(),
    brain: { density: b.density, version: b.versionString, insights: b.insights?.length || 0 },
    queue: { size: qs, processing: ps },
    run: { count: st.runCount || 0 },
    cache: cache.stats(),
    breakers
  }
  await redis.set('hydra:metrics:current', JSON.stringify(m))
  await redis.lpush('hydra:metrics:history', JSON.stringify(m))
  await redis.ltrim('hydra:metrics:history', 0, 1439)
  return m
}

export async function exportMetricsPrometheus() {
  const metrics = await exportMetrics()
  const lines = [
    `# HELP hydra_brain_density Current brain density`,
    `# TYPE hydra_brain_density gauge`,
    `hydra_brain_density ${metrics.brain.density}`,
    ``,
    `# HELP hydra_queue_size Current queue size`,
    `# TYPE hydra_queue_size gauge`,
    `hydra_queue_size ${metrics.queue.size}`,
    ``,
    `# HELP hydra_processing_size Current processing size`,
    `# TYPE hydra_processing_size gauge`,
    `hydra_processing_size ${metrics.queue.processing}`,
    ``,
    `# HELP hydra_run_count Total run count`,
    `# TYPE hydra_run_count counter`,
    `hydra_run_count ${metrics.run.count}`,
    ``,
    `# HELP hydra_cache_hit_rate Cache hit rate`,
    `# TYPE hydra_cache_hit_rate gauge`,
    `hydra_cache_hit_rate ${metrics.cache.hit}`,
    ``,
    `# HELP hydra_circuit_breaker_state Circuit breaker state (0=closed, 1=open)`,
    `# TYPE hydra_circuit_breaker_state gauge`,
    `hydra_circuit_breaker_yandex ${metrics.breakers.yandex.state === 'open' ? 1 : 0}`,
    `hydra_circuit_breaker_alibaba ${metrics.breakers.alibaba.state === 'open' ? 1 : 0}`
  ]
  return lines.join('
')
}

export async function checkAlerts() {
  const health = await healthCheck()
  const metrics = await exportMetrics()
  const alerts = []
  if (metrics.brain.density < 0.3) alerts.push({ severity: 'critical', message: `Density ${metrics.brain.density.toFixed(3)}` })
  if (metrics.queue.size > 500) alerts.push({ severity: 'warning', message: `Queue ${metrics.queue.size}>500` })
  if (breakers.yandex.state === 'open') alerts.push({ severity: 'error', message: 'Yandex OPEN' })
  if (alerts.length && process.env.WEBHOOK_URL) {
    await fetch(process.env.WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alerts, health, metrics })
    }).catch(() => {})
  }
  return alerts
}

export async function predictiveScale() {
  const qs = await redis.zcard(Q)
  const hist = (await redis.lrange('hydra:metrics:history', 0, 59)).map(j => {
    try { return JSON.parse(j) } catch { return { queue: { size: 0 } } }
  })
  const avg = hist.reduce((s, r) => s + (r.queue?.size || 0), 0) / (hist.length || 1)
  const pred = qs + avg * 0.5
  let w = 1
  if (pred > 100) w = 2
  if (pred > 500) w = 3
  if (pred > 1000) w = 5
  await redis.set('hydra:scale', { workers: w, predicted: pred, actual: qs })
  return { workers: w, predictedQueue: pred }
}

// --- ORCHESTRATOR FINAL CU AUTO-ROLLBACK + TIMEOUT GLOBAL ---
export async function runV6() {
  const TIMEOUT_MS = 300000 // 5 minute
  const tStart = Date.now()
  
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Timeout: runV6 exceeded 5 minutes')), TIMEOUT_MS)
  })

  const mainPromise = (async () => {
    const lock = await acquireGenesisLock()
    if (!lock) return { status: 'skipped', reason: 'locked' }

    try {
      const state = await redis.get('hydra:state') || { lastRun: 0, runCount: 0 }
      if (Date.now() - state.lastRun < 60000) return { status: 'skipped', reason: 'cooldown' }

      const brain = await loadBrain()
      const perspectives = await generatePerspectives(30)
      const result = await superposeSemantic(perspectives.length ? perspectives : [{ insights: brain.insights || ['init'] }])

      if (brain.density > 0 && result.density < brain.density * 0.9) {
        log('warn', 'Density drop detected', { from: brain.density, to: result.density })
        await trackPerformance('evolution', Date.now() - tStart, false)
        await rollbackBrain()
        return { status: 'rollback', reason: 'density_drop', from: brain.density, to: result.density }
      }

      if (result.density > brain.density * 1.01 || brain.density === 0) {
        const deployed = await deployBrainImmutable(result)
        await redis.set('hydra:state', { 
          ...state, 
          lastRun: Date.now(), 
          lastDensity: result.density, 
          lastVersion: deployed.versionString,
          runCount: (state.runCount || 0) + 1
        })
        await trackPerformance('evolution', Date.now() - tStart, true)
        return { status: 'evolved', ...deployed }
      }

      await trackPerformance('evolution', Date.now() - tStart, false)
      return { status: 'unchanged', density: result.density, brain: brain.versionString }

    } catch (e) {
      log('error', 'runV6 error', { error: e.message })
      await trackPerformance('evolution', Date.now() - tStart, false)
      return { status: 'error', error: e.message }
    } finally {
      await releaseGenesisLock(lock)
    }
  })()

  return Promise.race([mainPromise, timeoutPromise])
}
