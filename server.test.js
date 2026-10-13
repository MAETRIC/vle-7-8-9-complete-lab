const {test}=require('node:test');
const assert=require('node:assert/strict');
const {server,eq,escapeHtml}=require('./server');
test('escape untrusted content',()=>assert.equal(escapeHtml('<script>'), '&lt;script&gt;'));
test('empty and incorrect secrets rejected',()=>{assert.equal(eq('',''),false);assert.equal(eq('wrong','secret'),false);assert.equal(eq('valid','valid'),true);});
test('application rejects invalid inputs and unauthorized API access', async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const base='http://127.0.0.1:'+server.address().port;
 try{
  assert.equal((await fetch(base+'/healthz')).status,200);
  assert.equal((await fetch(base+'/api/records')).status,401);
  assert.equal((await fetch(base+'/appointment',{method:'POST',body:'code=%3Cscript%3E&department=General'})).status,400);
  assert.equal((await fetch(base+'/appointment',{method:'POST',body:'code=DEMO-001&department=General'})).status,200);
  assert.equal((await fetch(base+'/login',{method:'POST',body:'username=x&password=bad'})).status,401);
 }finally{await new Promise(r=>server.close(r));}
});
