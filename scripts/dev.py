"""Start a local FC5K server with a persistent, private development password."""
import os
from pathlib import Path
import runpy
import secrets

root = Path(__file__).resolve().parents[1]
if not os.environ.get('FC5K_HOST_PASSWORD'):
    password_file = root / 'data/private/host-password.txt'
    password_file.parent.mkdir(parents=True, exist_ok=True)
    if not password_file.exists():
        with open(password_file, 'x') as handle:
            os.chmod(password_file, 0o600)
            handle.write(secrets.token_urlsafe(24) + '\n')
    os.environ['FC5K_HOST_PASSWORD'] = password_file.read_text().strip()
    print('Local host password is saved in ' + str(password_file), flush=True)
runpy.run_path(str(root / 'server/app.py'), run_name='__main__')
