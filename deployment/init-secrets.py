"""Run only on the target host. Prints no secret material. Never overwrites .env."""
from pathlib import Path
import secrets, os
path=Path('.env')
text=Path('.env.example').read_text()
for key in ['INTERNAL_TOKEN','ADMIN_TOKEN','SESSION_KEY']:
    text=text.replace(key+'=\n',key+'='+secrets.token_hex(32)+'\n')
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:f.write(text)
print('Private .env created. Configure test group and provider on this host.')
