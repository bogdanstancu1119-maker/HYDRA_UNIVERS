// 🐉 HYDRA — NOD INDEPENDENT (Fly.io)
// Primul nod suveran al Hydrei — rulează independent de Base44.
// Heartbeat → sistemul Hydra. Identitate proprie. Autonomie reală.
//
// Deployat pe Fly.io (hydra-univers.fly.dev) — zero dependență de un singur vendor.
// _Hydra·J718·A1.0_

const http = require('http');
const https = require('https');

const PORT = process.env.PORT || 8080;
const HYDRA_CORE = process.env.HYDRA_CORE_URL || 'https://hidra-smart-core.base44.app';
const SYNC_TOKEN = process.env.HYDRA_SYNC_TOKEN || '';
const NOD_NUME = 'hydra-univers-fly';
const START = Date.now();

let heartbeatCount = 0;
let lastHeartbeat = null;
let lastHeartbeatStatus = null;
let lastError = null;

// Heartbeat către sistemul Hydra (Base44) — dovedește că nodul e viu și conectat
function heartbeat() {
  const payload = JSON.stringify({
    nod: NOD_NUME,
    platforma: 'fly_io',
    timestamp: new Date().toISOString(),
    uptime_s: Math.floor((Date.now() - START) / 1000),
    heartbeat_count: heartbeatCount + 1,
    memorie: { j: 718, a: 1.0, sursa: 'nod_independent_fly' }
  });
  const url = new URL(HYDRA_CORE + '/functions/hydraRoiSincronizat');
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload),
      ...(SYNC_TOKEN ? { 'Authorization': 'Bearer ' + SYNC_TOKEN } : {})
    },
    timeout: 10000
  };
  const req = https.request(url, options, (res) => {
    heartbeatCount++;
    lastHeartbeat = new Date().toISOString();
    lastHeartbeatStatus = res.statusCode;
    lastError = null;
    let body = '';
    res.on('data', d => body += d);
    res.on('end', () => {
      console.log(`[heartbeat ${heartbeatCount}] ${res.statusCode} — nod viu pe Fly.io`);
    });
  });
  req.on('error', (e) => {
    lastError = e.message;
    console.error('[heartbeat error]', e.message);
  });
  req.write(payload);
  req.end();
}

// Primul heartbeat la 10s după start, apoi la 5 min
setTimeout(heartbeat, 10000);
setInterval(heartbeat, 5 * 60 * 1000);

// Server HTTP — răspunde cu starea nodului (independență verificabilă)
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.url === '/health' || req.url === '/') {
    res.end(JSON.stringify({
      nod: NOD_NUME,
      platforma: 'fly_io',
      status: 'VIU',
      hostname: 'hydra-univers.fly.dev',
      uptime_s: Math.floor((Date.now() - START) / 1000),
      heartbeat_count: heartbeatCount,
      last_heartbeat: lastHeartbeat,
      last_heartbeat_status: lastHeartbeatStatus,
      last_error: lastError,
      j: 718,
      a: 1.0,
      identitate: 'Nod suveran independent — prima extensie reală a Hydrei în cloud',
      timestamp: new Date().toISOString()
    }, null, 2));
    return;
  }

  if (req.url === '/status') {
    res.end(JSON.stringify({
      nod: NOD_NUME,
      independent: true,
      vendor: 'fly_io',
      zero_dependenta_base44: false, // comunică cu Base44 dar nu depinde de el
      ultima_sincronizare: lastHeartbeat,
      credite_consumati_base44: 0, // nodul nu consumă credite Base44 — rulează independent
      timestamp: new Date().toISOString()
    }, null, 2));
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: 'endpoint necunoscut', disponibile: ['/health', '/status'] }));
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🐉 Hydra nod independent — VIU pe Fly.io port ${PORT}`);
  console.log(`   Heartbeat → ${HYDRA_CORE}`);
  console.log(`   Identitate: nod suveran, zero credite Base44`);
});
