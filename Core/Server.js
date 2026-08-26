// SERVER V6.7 AUTONOMY - Base44 + Fly.io + Vercel - bogdanstancu1119-maker 25 Aug 2026
import http from 'http'
import { runV6, healthCheck, exportMetrics, loadBrain, autoLoadSecrets } from './hydra_v6_refactor.js'

const PORT = process.env.PORT || 3000

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Content-Type', 'application/json')
  try{
    await autoLoadSecrets()
    if(req.url==='/'||req.url==='/health'){
      const health=await healthCheck()
      const brain=await loadBrain()
      res.writeHead(200)
      res.end(JSON.stringify({status:'🌊 HYDRA V6.7 AUTONOMY LIVE',health,brain:{version:brain.versionString,density:brain.density,insights:brain.insights?.length},autonomy:true,region:process.env.FLY_REGION||'gru',timestamp:Date.now()},null,2))
      return
    }
    if(req.url==='/run'){const result=await runV6();res.writeHead(200);res.end(JSON.stringify(result,null,2));return}
    if(req.url==='/metrics'){const metrics=await exportMetrics();res.writeHead(200);res.end(JSON.stringify(metrics,null,2));return}
    if(req.url==='/brain'){const brain=await loadBrain();res.writeHead(200);res.end(JSON.stringify(brain,null,2));return}
    if(req.url==='/secrets-status'){
      const secrets=await autoLoadSecrets()
      res.writeHead(200)
      res.end(JSON.stringify({autonomy:true,hasRedis:!!secrets.UPSTASH_REDIS_URL,hasYandex:!!secrets.YANDEX_API_KEY,hasAlibaba:!!secrets.ALIBABA_API_KEY,from:'redis+env'},null,2))
      return
    }
    res.writeHead(404)
    res.end(JSON.stringify({error:'not found',routes:['/','/health','/run','/metrics','/brain','/secrets-status']}))
  }catch(e){res.writeHead(500);res.end(JSON.stringify({error:e.message}))}
})

server.listen(PORT, async ()=>{
  console.log(`🌊 HYDRA V6.7 AUTONOMY pe port ${PORT}`)
  await autoLoadSecrets()
  setTimeout(async()=>{const r=await runV6();console.log('Initial run:',r.status,r.version||r.reason)},5000)
  setInterval(runV6,5*60*1000)
})
