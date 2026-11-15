"""Private host CLI: python deployment/admin.py pause|resume|disconnect|qr.
QR is saved to a mode-600 local file, never stdout. View only in a private UI.
"""
import getpass,os,sys,urllib.request
from pathlib import Path
config=dict(line.split('=',1) for line in Path('.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
action=sys.argv[1]
if action not in ['pause','resume','disconnect','qr','enroll','enrollment','pair']:raise SystemExit('Unknown action')
if action=='pair' and not sys.stdin.isatty():raise SystemExit('Use a private interactive terminal')
body=getpass.getpass('Test account number, including country code, digits only: ').encode() if action=='pair' else None
request=urllib.request.Request('http://127.0.0.1:8080/'+action,data=body,method='GET' if action in ['qr','enrollment'] else 'POST',headers={'Authorization':'Bearer '+config['ADMIN_TOKEN']})
with urllib.request.urlopen(request,timeout=10) as response:data=response.read()
if action=='qr':
    fd=os.open('/tmp/belong-link.png',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data)
    print('QR saved privately at /tmp/belong-link.png; remove immediately after linking.')
elif action=='pair':getpass.getpass('WhatsApp linking code: '+data.decode()+' (press Enter to finish) ')
else:print(data.decode())
