'use strict';
const http = require('node:http');
const crypto = require('node:crypto');
const version = process.env.APP_VERSION || 'v1-blue';
const experiment = process.env.EXPERIMENT || '7';
const studentName = process.env.STUDENT_NAME || 'Virtual Lab Student';
const registration = process.env.STUDENT_ID || 'Classroom demonstration';
const counters = {requests: 0, failedLogins: 0, unauthorized: 0, validationsRejected: 0};
const escapeHtml = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const eq = (a,b) => { const aa=Buffer.from(a||''),bb=Buffer.from(b||''); return aa.length===bb.length && bb.length>0 && crypto.timingSafeEqual(aa,bb); };
const color = version.includes('green') ? '#16804a' : '#2367c5';
const page = message => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VLE ${escapeHtml(experiment)} | Synthetic Clinic</title><link rel="stylesheet" href="/style.css"></head><body><main><header>VIRTUAL LAB EXPERIMENT ${escapeHtml(experiment)}</header><h1>Synthetic Clinic</h1><p class="version">${escapeHtml(version)}</p><p>${escapeHtml(studentName)}<br>${escapeHtml(registration)}</p><p>Running in Kubernetes on AWS EC2</p><section><h2>Application status</h2><p>Healthy · Demo data only</p><p>${escapeHtml(message||'Use the forms below to test validation and authentication.')}</p></section><section><h2>Validate a synthetic appointment</h2><form action="/appointment" method="post"><label>Demo code <input name="code" maxlength="12" required placeholder="DEMO-001"></label><label>Department <select name="department"><option>General</option><option>Dental</option></select></label><button>Validate appointment</button></form></section><section><h2>Lab authentication</h2><form action="/login" method="post"><label>Username <input name="username" maxlength="40" autocomplete="username" required></label><label>Password <input name="password" type="password" maxlength="100" autocomplete="current-password" required></label><button>Sign in</button></form></section><nav><a href="/healthz">Health check</a> · <a href="/metrics">Metrics</a> · <a href="/api/records">Protected demo API</a></nav><footer>No real patient data is stored.</footer></main></body></html>`;
const server = http.createServer(async (req,res) => {
 counters.requests++;
 const path = new URL(req.url,'http://localhost').pathname;
 const headers = {'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','Permissions-Policy':'camera=(), microphone=(), geolocation=()','Cross-Origin-Resource-Policy':'same-origin','Cross-Origin-Opener-Policy':'same-origin','Content-Security-Policy':"default-src 'none'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"};
 const send=(status,body,type)=>{res.writeHead(status,{...headers,...(type?{'Content-Type':type}:{})});res.end(body);};
 if(path==='/style.css') return send(200,`body{margin:0;background:#f1f5fa;color:#203047;font:17px system-ui}main{max-width:720px;margin:28px auto;padding:24px}header{font-size:14px;letter-spacing:2px;color:${color}}h1{font-size:38px;margin-bottom:12px}.version{background:${color};color:white;padding:16px;border-radius:8px;font-size:24px;font-weight:700}section{background:white;padding:20px;margin:20px 0;border-radius:10px;box-shadow:0 2px 10px #20304710}label{display:block;margin:12px 0}input,select{display:block;padding:10px;font:inherit;max-width:100%;box-sizing:border-box}button{background:${color};color:white;border:0;border-radius:5px;padding:12px;font:inherit}footer{font-size:13px;margin-top:24px}`, 'text/css');
 if(path==='/healthz') return send(200,JSON.stringify({status:'healthy',version,experiment}),'application/json');
 if(path==='/metrics') return send(200,`# HELP vle_http_requests_total Total HTTP requests\n# TYPE vle_http_requests_total counter\nvle_http_requests_total ${counters.requests}\n# HELP vle_failed_logins_total Failed login attempts\n# TYPE vle_failed_logins_total counter\nvle_failed_logins_total ${counters.failedLogins}\n# HELP vle_unauthorized_total Unauthorized API requests\n# TYPE vle_unauthorized_total counter\nvle_unauthorized_total ${counters.unauthorized}\n# TYPE vle_validation_rejections_total counter\nvle_validation_rejections_total ${counters.validationsRejected}\n`, 'text/plain; version=0.0.4');
 if(path==='/api/records') {if(!eq(req.headers.authorization,'Bearer '+(process.env.API_TOKEN||''))||!process.env.API_TOKEN){counters.unauthorized++;return send(401,JSON.stringify({error:'Unauthorized'}),'application/json');}return send(200,JSON.stringify({records:[{code:'DEMO-001',department:'General'}]}),'application/json');}
 if(req.method==='POST' && ['/login','/appointment'].includes(path)) {
  let body='';for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>4096)return send(413,page('Request too large.'));}
  const data=new URLSearchParams(body);
  if(path==='/login'){if(data.get('username')==='lab-user'&&eq(data.get('password'),process.env.APP_PASSWORD))return send(200,page('Authentication succeeded for the synthetic lab account.'));counters.failedLogins++;return send(401,page('Invalid username or password.'));}
  if(!/^DEMO-\d{3}$/.test(data.get('code')||'')||!['General','Dental'].includes(data.get('department'))){counters.validationsRejected++;return send(400,page('Validation rejected. Use DEMO- followed by three digits and an allowed department.'));}
  return send(200,page('Synthetic appointment validated: '+data.get('code')+' / '+data.get('department')));
 }
 if(path==='/'&&req.method==='GET')return send(200,page());
 if(path==='/robots.txt')return send(200,'User-agent: *\nDisallow: /api/\n','text/plain');
 return send(404,page('Page not found.'));
});
if(require.main===module)server.listen(8080,'0.0.0.0',()=>console.log(`Experiment ${experiment} ${version} listening on 8080`));
module.exports={server,eq,escapeHtml};
