import { HydraSmartRouter } from './router.js';
import fs from 'fs';

const router = new HydraSmartRouter([...]);

async function runBatch() {
  const queue = JSON.parse(fs.readFileSync('./state/queue.json','utf8') || '[]').slice(0,50); // max 50 taskuri / rulare
  
  for (const task of queue) {
    try {
      await router.execute(task);
    } catch (e) {
      // Nu crapa workflow-ul, salvează eroarea ca învățare
      fs.appendFileSync('./state/errors.json', JSON.stringify({task, error:e.message, at:Date.now()})+'\n');
      console.warn(`Soft fail: ${task.id} -> ${e.message}`);
    }
  }
  
  // Curăță coada
  fs.writeFileSync('./state/queue.json','[]');
  process.exit(0); // mereu 0 = 0 mailuri de la GitHub
}

runBatch();
