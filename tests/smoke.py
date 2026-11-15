"""Actual process/HTTP smoke; no live WhatsApp or provider calls."""
import os,subprocess,tempfile,time,json,secrets,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as state:
    env={**os.environ,'INTERNAL_TOKEN':secrets.token_hex(32),'ADMIN_TOKEN':secrets.token_hex(32),'SESSION_KEY':secrets.token_hex(32),'SESSION_DB':state+'/state.sqlite','CONNECT_WHATSAPP':'false','LLM_PROVIDER':'disabled','PORT':'18080','TEST_GROUP_IDS':'test@g.us'}
    ps=[subprocess.Popen(['python','-m','uvicorn','backend.app:app','--port','18000','--no-access-log'],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),subprocess.Popen(['node','src.js'],cwd=root/'whatsapp-gateway',env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)]
    def req(port,path,token=None,data=None):
        headers={}
        if token:headers['Authorization']='Bearer '+token
        if data is not None:headers['Content-Type']='application/json'
        r=urllib.request.Request(f'http://127.0.0.1:{port}'+path,headers=headers,data=json.dumps(data).encode() if data is not None else None)
        with urllib.request.urlopen(r,timeout=2) as response:return response.read()
    try:
        for port in [18000,18080]:
            for _ in range(60):
                try:req(port,'/healthz');break
                except (OSError,urllib.error.URLError):time.sleep(.1)
            else:raise RuntimeError('process failed to start')
        assert json.loads(req(18080,'/healthz'))['paused'] is True
        try:req(18080,'/resume',data={});raise AssertionError('missing auth accepted')
        except urllib.error.HTTPError as e:assert e.code==401
        assert req(18080,'/resume',env['ADMIN_TOKEN'],{})==b'resumed'
        assert req(18080,'/pause',env['ADMIN_TOKEN'],{})==b'paused'
        assert 'code' in json.loads(req(18080,'/enroll',env['ADMIN_TOKEN'],{}))
        text=json.loads(req(18000,'/respond',env['INTERNAL_TOKEN'],{'text':'ليش نحب اعداءنا'}))['answer']
        assert '5:44' in text
        assert req(18080,'/disconnect',env['ADMIN_TOKEN'],{})==b'disconnected'
        print('PASS: actual backend/gateway HTTP health, authentication, pause/resume, enrollment, curated reply, disconnect. No external integration attempted.')
    finally:
        for p in ps:p.terminate()
        for p in ps:
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait()
