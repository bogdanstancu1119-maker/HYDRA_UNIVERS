// HYDRA SOLVER V5.1 - rezolva probleme reale, nu teorie
import { HydraGovernor } from './hydra_governor.js'
import { HydraGenesis } from './genesis.js'

class HydraRealSolver {
  constructor() {
    this.gov = new HydraGovernor()
    this.genesis = new HydraGenesis(this.gov)
    this.cache = new Map()
  }

  // INTRARE: problema reala in limbaj natural
  async solve(problema) {
    // 1. Rupe problema in 20 sub-probleme din 20 unghiuri
    const subProblems = await this.gov.execute({
      type: 'research',
      payload: {
        prompt: `Rupe problema in 20 taskuri concrete executabile: "${problema}"`
      }
    })

    // 2. Distribuie pe toate capetele - paralel 10
    const pLimit = (await import('p-limit')).default(10)
    const results = await Promise.all(
      subProblems.tasks.map(task => 
        pLimit(() => this.gov.execute({
          type: task.heavy ? 'agent_creator' : 'edge_router',
          payload: task
        }))
      )
    )

    // 3. Suprapune - pastreaza doar ce apare in 70%
    const dens = this.superpose(results)
    
    // 4. Daca nu e suficient de dens, cere Genesis sa creeze agenti noi
    if (dens.density < 0.8) {
      await this.genesis.spawnAgentsOnAll(problema)
      return this.solve(problema) // recursiv cu mai multe capete
    }

    return dens
  }

  superpose(results) {
    const freq = {}
    results.flat().forEach(r => {
      const key = JSON.stringify(r.solution)
      freq[key] = (freq[key] || 0) + 1
    })
    const best = Object.entries(freq)
      .filter(([_,c]) => c >= results.length * 0.7)
      .sort((a,b) => b[1]-a[1])[0]
    
    return best ? JSON.parse(best[0]) : { density: 0, solution: null }
  }

  // EXEMPLE REALE - apelezi direct:
  async exemple() {
    // 1. Scraping + analiza
    // await solver.solve("Ia toate preturile de pe emag la telefoane si fa-mi cel mai ieftin top 10")
    
    // 2. Cercetare + sinteza
    // await solver.solve("Cauta toate metodele noi de deploy serverless aparute in ultima saptamana si fa-mi un rank")

    // 3. Automatizare
    // await solver.solve("Creaza-mi 5 landing page-uri diferite pentru hydrapsie.vercel.app si deployeaza-le pe Vercel/Fly")

    // 4. Bani reali
    // await solver.solve("Gaseste-mi 3 produse sub 10$ pe AliExpress care se vand cu 50$+ pe Amazon")
  }
}

// USAGE - 1 linie:
const solver = new HydraRealSolver()
const rezultat = await solver.solve("PROBLEMA TA REALA AICI")
console.log(rezultat)
