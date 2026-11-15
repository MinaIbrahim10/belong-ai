"""Private host CLI: python deployment/admin.py pause|resume|disconnect|qr.
QR is saved to a mode-600 local file, never stdout. View only in a private UI.
"""
import os,sys,urllib.request
from pathlib import Path
config=dict(line.split('=',1) for line in Path('.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
action=sys.argv[1]
if action not in ['pause','resume','disconnect','qr','enroll','enrollment']:raise SystemExit('Unknown action')
request=urllib.request.Request('http://127.0.0.1:8080/'+action,method='GET' if action in ['qr','enrollment'] else 'POST',headers={'Authorization':'Bearer '+config['ADMIN_TOKEN']})
with urllib.request.urlopen(request,timeout=10) as response:data=response.read()
if action=='qr':
    fd=os.open('/tmp/belong-link.png',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data)
    print('QR saved privately at /tmp/belong-link.png; remove immediately after linking.')
else:print(data.decode())
