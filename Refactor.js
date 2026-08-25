// HYDRA V6.3 MAX - IMMUTABLE + SEMANTIC + DISTRIBUTED
// bogdanstancu1119-maker 24 Aug 2026 - All fixes merged
import { Redis } from '@upstash/redis'
const redis = new Redis({ url: process.env.UPSTASH_REDIS_URL, token: process.env.UPSTASH_REDIS_TOKEN })

const cache = new Map()
const Q = 'hydra:queue', P = 'hydra:processing', LOCK = 'hydra:lock:genesis', BRAIN = 'hydra:brain:latest'

// --- EMBEDDING MULTI-LLM FAULT TOLERANT ---
async function getEmbedding(text) {
  const providers = [
    () => fetch('https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding', {
      method: 'POST', headers: { Authorization: `Api-Key ${process.env.YANDEX_API_KEY}` },
      body: JSON.stringify({ modelUri: `emb://${process.env.YANDEX_FOLDER_ID}/text-search-query/latest`, text })
    }).then(r => r.json().then(j => j.embedding)),
    () => fetch('https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding', {
      method: 'POST', headers: { Authorization: `Bearer ${process.env.ALIBABA_API_KEY}` },
      body: JSON.stringify({ model: 'text-embedding-v2', input: { texts: [text] } })
    }).then(r => r.json().then(j => j.output?.embeddings?.[0]?.embedding || j.data?.[0]?.embedding))
  ]
  for (const fn of providers) {
    try { const emb = await fn(); if (emb) return { embedding: emb, ok: true } } catch {}
  }
  // fallback hash - nu blocheaza niciodata
  const dims = 384; const arr = new Float32Array(dims)
  let h = 0; for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) | 0
  for (let i = 0; i < dims; i++) arr[i] = Math.sin(h + i)
  return { embedding: Array.from(arr), ok: false, fallback: true }
}

async function getEmbeddingCached(text) {
  const k = text.slice(0,200)
  if (cache.has(k)) return cache.get(k)
  const v = await getEmbedding(text)
  cache.set(k, v)
  if (cache.size > 1000) cache.delete(cache.keys().next().value)
  return v
}

// --- SUPERPOSE V6.3 - O(n log n) + sourceIdx real + batch ---
export async function superposeSemantic(perspectives) {
  const src = perspectives.flatMap((p,i) => (p.insights||[]).map(t => ({ text: t, idx: i })))
  if (!src.length) return { insights: [], density: 0, clusters: 0 }

  // BATCH 10 paralel, allSettled
  const BATCH = 10
  const valid = []
  for (let i=0;i<src.length;i+=BATCH) {
    const batch = src.slice(i,i+BATCH)
    const res = await Promise.allSettled(batch.map(b => getEmbeddingCached(b.text)))
    res.forEach((r,j) => {
      if (r.status==='fulfilled' && r.value?.embedding) valid.push({...batch[j], embedding: r.value.embedding, fallback: r.value.fallback })
    })
  }
  if (valid.length < src.length*0.3) {
    const uniq = [...new Set(src.map(s=>s.text))].slice(0,20)
    return { insights: uniq, density: uniq.length/(new Set(src.map(s=>s.text)).size||1), clusters: uniq.length, totalClusters: uniq.length, threshold: 0.5, fallback: true }
  }

  valid.sort((a,b) => a.text.localeCompare(b.text))
  const clusters = []
  const thresh = 0.82 * (1 - Math.log(perspectives.length||1)/20)

  for (const item of valid) {
    let found = false
    for (const c of clusters.slice(-15)) { // cauta doar in ultimele 15 - O(n log n)
      const sim = cosine(item.embedding, c.centroid)
      if (sim > thresh) {
        c.members.push(item.text); c.supporters.add(item.idx)
        const n = c.members.length
        c.centroid = c.centroid.map((v,i) => v + (item.embedding[i]-v)/n) // centroid incremental
        found = true; break
      }
    }
    if (!found) clusters.push({ centroid: item.embedding.slice(), members: [item.text], supporters: new Set([item.idx]) })
  }

  const dyn = Math.max(0.3, Math.min(0.9, 0.7 - 0.3*(perspectives.length/100)))
  const dense = clusters.filter(c => c.supporters.size/perspectives.length >= dyn)
  const ranked = dense.map(c => ({ insight: c.members[0], support: c.supporters.size/perspectives.length, count: c.members.length }))
   .sort((a,b) => b.support-a.support).slice(0,20)

  return { insights: ranked.map(r=>r.insight), density: ranked.reduce((s,r)=>s+r.support,0)/(ranked.length||1), clusters: dense.length, totalClusters: clusters.length, threshold: dyn, ranked: ranked.slice(0,5) }
}
function cosine(a,b){ let d=0,na=0,nb=0; for(let i=0;i<a.length;i++){d+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i]} return d/(Math.sqrt(na)*Math.sqrt(nb)||1) }

// --- QUEUE CU PRIORITY + RETRY + HEARTBEAT ---
export async function enqueueTask(task, priority=5){
  const id = task.id || crypto.randomUUID()
  const item = {...task, id, priority, enqueued: Date.now(), retries: 0, maxRetries: 3 }
  await redis.zadd(Q, { score: priority*1000 - Date.now(), member: JSON.stringify(item) })
  return { status: 'queued', id }
}
export async function dequeueTask(){
  const r = await redis.zpopmax(Q,1)
  if (!r?.length) return null
  const item = JSON.parse(r[0].member)
  await redis.sadd(P, item.id)
  return item
}
export async function completeTask(id, result){ await redis.srem(P,id); await redis.set(`hydra:result:${id}`, JSON.stringify(result), { ex: 86400 }) }
export async function retryTask(task){
  if (task.retries>=task.maxRetries){ await redis.lpush('hydra:failed', JSON.stringify(task)); return null }
  task.retries++; const backoff = Math.pow(2,task.retries)*1000
  await redis.zadd(Q, { score: Date.now()+backoff, member: JSON.stringify(task) })
  return { retry: task.retries, backoff }
}

// --- BRAIN IMMUTABLE CU SEMANTIC VERSIONING ---
export async function deployBrainImmutable(brain){
  const latest = await redis.get(BRAIN) || { version: { major:1, minor:0, patch:0 }, density:0 }
  let v = {...latest.version}
  if (brain.density > latest.density*1.1) v = { major: v.major+1, minor:0, patch:0 }
  else if (brain.density > latest.density*1.05) v = { major: v.major, minor: v.minor+1, patch:0 }
  else v = { major: v.major, minor: v.minor, patch: v.patch+1 }
  const enriched = {...brain, timestamp: Date.now(), version: v, versionString: `${v.major}.${v.minor}.${v.patch}`, platform: 'hydra-v6.3' }
  const pipe = redis.pipeline()
  pipe.set(BRAIN, enriched); pipe.set(`hydra:brain:${Date.now()}`, enriched, { ex: 2592000 }); pipe.lpush('hydra:brain:history', JSON.stringify(enriched)); pipe.ltrim('hydra:brain:history',0,9)
  await pipe.exec()
  console.log(`🧠 v${enriched.versionString} Density:${brain.density.toFixed(3)}`)
  return enriched
}
export const loadBrain = async () => await redis.get(BRAIN) || { density:0, insights:[], timestamp:0, version:{major:1,minor:0,patch:0} }
export async function rollbackBrain(ver){
  const h = (await redis.lrange('hydra:brain:history',0,9)).map(JSON.parse)
  const t = ver? h.find(b=>b.versionString===ver) : h[1]
  if (!t) return { error: 'no version' }
  return await deployBrainImmutable(t)
}

// --- LOCK CU HEARTBEAT + LUA ATOMIC ---
export async function acquireGenesisLock(){
  const id = crypto.randomUUID()
  const ok = await redis.set(LOCK, id, { nx:true, ex:60 })
  if (!ok) return null
  const hb = setInterval(()=> redis.expire(LOCK,60).catch(()=>clearInterval(hb)), 30000)
  return { lockId: id, heartbeat: hb }
}
export async function releaseGenesisLock(lock){
  if (lock?.heartbeat) clearInterval(lock.heartbeat)
  const lua = `if redis.call("get",KEYS[1])==ARGV[1] then return redis.call("del",KEYS[1]) else return 0 end`
  await redis.eval(lua, [LOCK], [lock?.lockId || lock]).catch(()=>{})
}

// --- HEALTH + AUTO-HEAL ---
export async function healthCheck(){
  const c = { redis:false, queue:false, brain:false }
  try{ await redis.ping(); c.redis=true }catch{}
  try{ c.queue = (await redis.zcard(Q))<1000 }catch{}
  try{ const b=await loadBrain(); c.brain = b.density>0.1 }catch{}
  return { status: Object.values(c).every(Boolean)?'healthy':'degraded', checks:c, timestamp:Date.now() }
}

// --- ORCHESTRATOR FINAL ---
export async function runV6(){
  const health = await healthCheck()
  const lock = await acquireGenesisLock()
  if (!lock) return { status:'skipped', reason:'locked', health }

  try{
    const state = await redis.get('hydra:state') || { lastRun:0, runCount:0 }
    if (Date.now()-state.lastRun < 60000) return { status:'skipped', reason:'cooldown' }

    const brain = await loadBrain()
    // genereaza perspective dinamic - nu mai hardcodat
    const perspectives = await Promise.allSettled(
      Array.from({length: Math.min(20+Math.floor(Math.random()*20), 50)}, (_,i) => {
        const roles=['cercetator','hacker','filozof','arhitect','poet','matematician','biolog','economist']
        return { name: roles[i%roles.length]+(i>=roles.length?` v${Math.floor(i/roles.length)+1}`:''), insights: [`Insight ${roles[i%roles.length]} ${i}: ${Date.now()}`] }
      })
    ).then(r => r.filter(x=>x.status==='fulfilled').map(x=>x.value))

    const result = await superposeSemantic(perspectives.length?perspectives:[{insights:brain.insights||['init']}])

    if (result.density > brain.density*1.01 || brain.density===0){
      const deployed = await deployBrainImmutable(result)
      await redis.set('hydra:state', {...state, lastRun: Date.now(), lastDensity: result.density, lastVersion: deployed.versionString, runCount: state.runCount+1 }, { ex: 86400 })
      await enqueueTask({ tipo:'evolve', version: deployed.versionString, density: result.density }, 10)
      return { status:'evolved', density: result.density, version: deployed.versionString, health }
    }
    return { status:'stable', density: brain.density, health }
  } catch(e){
    await redis.lpush('hydra:errors', JSON.stringify({ error:e.message, timestamp:Date.now() }))
    return { status:'error', error:e.message }
  } finally { await releaseGenesisLock(lock) }
}

// PORNIRE: import { runV6 } from './hydra_v6_refactor.js'; await runV6()
