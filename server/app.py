"""FC5K: static public site and private invitation/RSVP API. SQLite locally; Postgres in production."""
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DB = Path(os.environ.get('FC5K_DB', ROOT / 'data/private/rsvp.sqlite3'))
PASSWORD = os.environ.get('FC5K_HOST_PASSWORD', '')
ORIGIN = os.environ.get('FC5K_ORIGIN', 'http://127.0.0.1:8766').rstrip('/')
DATABASE_URL = os.environ.get("DATABASE_URL")


class PostgresConnection:
    def __init__(self, db):
        self.db = db

    def execute(self, query, values=()):
        return self.db.execute(query.replace('?', '%s'), values)


@contextmanager
def connect():
    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=10) as db:
            yield PostgresConnection(db)
    else:
        db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()


def initialize():
    if not DATABASE_URL:
        DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS invites (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, token_hash TEXT UNIQUE NOT NULL,
            max_guests INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
            party_size INTEGER NOT NULL DEFAULT 0, activity TEXT NOT NULL DEFAULT 'run',
            notes TEXT NOT NULL DEFAULT '', updated_at INTEGER, created_at INTEGER NOT NULL)''')
        db.execute('CREATE TABLE IF NOT EXISTS host_sessions (token_hash TEXT PRIMARY KEY, expires_at INTEGER NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS rate_limits (bucket TEXT PRIMARY KEY, attempts INTEGER NOT NULL, expires_at INTEGER NOT NULL)')



def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Invite tokens and submitted data must never enter access logs.
        pass

    def send(self, code, value, cookie=None):
        data = json.dumps(value).encode()
        self.send_response(code)
        self.headers_common()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(data)

    def headers_common(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')

    def authorized(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
            sid = cookie['fc5k_host'].value
        except (KeyError, ValueError):
            return False
        with connect() as db:
            row = db.execute('SELECT expires_at FROM host_sessions WHERE token_hash=?', (digest(sid),)).fetchone()
        return bool(row and row['expires_at'] > time.time())

    def rate_limited(self, kind, limit, window):
        # Vercel overwrites this header at its trusted edge. Never trust it locally.
        ip = self.headers.get('x-vercel-forwarded-for', self.client_address[0]) if os.environ.get('VERCEL') else self.client_address[0]
        bucket = digest(kind + ':' + ip)
        now = int(time.time())
        with connect() as db:
            db.execute('DELETE FROM rate_limits WHERE expires_at < ?', (now,))
            row = db.execute('''INSERT INTO rate_limits (bucket, attempts, expires_at) VALUES (?,1,?)
                ON CONFLICT(bucket) DO UPDATE SET attempts=rate_limits.attempts+1 RETURNING attempts''', (bucket, now + window)).fetchone()
        return row['attempts'] > limit

    def body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length < 1 or length > 8192:
            raise ValueError('Invalid request size.')
        data = json.loads(self.rfile.read(length))
        if not isinstance(data, dict):
            raise ValueError('Expected an object.')
        return data

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/host/invites':
            if not self.authorized():
                return self.send(401, {'error': 'Sign in to continue.'})
            with connect() as db:
                rows = db.execute('SELECT id,name,max_guests,status,party_size,activity,notes,updated_at FROM invites ORDER BY created_at DESC, name').fetchall()
            return self.send(200, {'invites': [dict(row) for row in rows]})
        # Explicit allowlist: never serve source, databases, or the old private archive.
        files = {'/': 'index.html', '/index.html': 'index.html', '/history.html': 'history.html',
                 '/rsvp': 'rsvp.html', '/rsvp.html': 'rsvp.html', '/host': 'host.html',
                 '/style.css': 'style.css', '/logo.svg': 'logo.svg',
                 '/assets/rsvp.js': 'assets/rsvp.js', '/assets/host.js': 'assets/host.js',
                 '/trails': 'trails.html', '/trails.html': 'trails.html',
                 '/assets/trails.js': 'assets/trails.js', '/data/trail-review.json': 'data/trail-review.json',
                 '/data/course.json': 'data/course.json', '/event.ics': 'event.ics'}
        filename = files.get(path)
        if not filename and path.startswith('/photos/public/'):
            candidate = (ROOT / path.lstrip('/')).resolve()
            if candidate.is_relative_to(ROOT / 'photos/public') and candidate.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
                filename = str(candidate)
        if not filename or not (ROOT / filename).is_file():
            return self.send(404, {'error': 'Page not found.'})
        data = (ROOT / filename).read_bytes()
        import mimetypes
        self.send_response(200)
        self.headers_common()
        self.send_header('Content-Type', mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.headers.get('Origin') != ORIGIN:
            return self.send(403, {'error': 'Request origin is not allowed.'})
        try:
            data = self.body()
            self.post(urlparse(self.path).path, data)
        except (ValueError, TypeError, KeyError, UnicodeDecodeError):
            self.send(400, {'error': 'Please check the fields and try again.'})

    def post(self, path, data):
        if path == '/api/host/login':
            if self.rate_limited('login', 10, 900):
                return self.send(429, {'error': 'Too many attempts. Try again in 15 minutes.'})
            if len(PASSWORD) < 16 or not isinstance(data.get('password'), str) or not hmac.compare_digest(data['password'].encode(), PASSWORD.encode()):
                return self.send(401, {'error': 'That password did not match.'})
            sid = secrets.token_urlsafe(32)
            with connect() as db:
                db.execute('DELETE FROM host_sessions WHERE expires_at < ?', (int(time.time()),))
                db.execute('INSERT INTO host_sessions (token_hash,expires_at) VALUES (?,?)', (digest(sid), int(time.time()) + 43200))
            secure = '; Secure' if ORIGIN.startswith('https://') else ''
            return self.send(200, {'ok': True}, 'fc5k_host=' + sid + '; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200' + secure)
        if path.startswith('/api/host/'):
            if not self.authorized():
                return self.send(401, {'error': 'Sign in to continue.'})
            if path == '/api/host/logout':
                cookie = SimpleCookie(self.headers.get('Cookie', ''))
                with connect() as db:
                    db.execute('DELETE FROM host_sessions WHERE token_hash=?', (digest(cookie['fc5k_host'].value),))
                return self.send(200, {'ok': True}, 'fc5k_host=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
            if path == '/api/host/invites':
                name = data.get('name', '')
                if not isinstance(name, str):
                    raise ValueError()
                name = name.strip()
                maximum = data.get('max_guests')
                if not name or len(name) > 120 or type(maximum) is not int or not 1 <= maximum <= 20:
                    raise ValueError()
                token = secrets.token_urlsafe(32)
                invite_id = secrets.token_hex(12)
                with connect() as db:
                    db.execute('INSERT INTO invites (id,name,token_hash,max_guests,created_at) VALUES (?,?,?,?,?)', (invite_id, name, digest(token), maximum, int(time.time())))
                return self.send(201, {'url': ORIGIN + '/rsvp#' + token, 'name': name})
            if path == '/api/host/rotate':
                token = secrets.token_urlsafe(32)
                with connect() as db:
                    changed = db.execute('UPDATE invites SET token_hash=? WHERE id=?', (digest(token), data.get('id'))).rowcount
                if not changed:
                    return self.send(404, {'error': 'Invitation not found.'})
                return self.send(200, {'url': ORIGIN + '/rsvp#' + token})
        if path == '/api/public/rsvp':
            if self.rate_limited('signup', 20, 3600):
                return self.send(429, {'error': 'Too many signups. Please try again later.'})
            name = data.get('name', '')
            if not isinstance(name, str):
                raise ValueError()
            name = name.strip()
            status, size, activity, notes = (data.get(k) for k in ('status', 'party_size', 'activity', 'notes'))
            if not name or len(name) > 120 or status not in ('yes', 'maybe', 'no') or activity not in ('run', 'walk', 'party') or type(size) is not int or not isinstance(notes, str) or len(notes) > 1000:
                raise ValueError()
            if (status == 'no' and size != 0) or (status != 'no' and not 1 <= size <= 20):
                raise ValueError()
            token = secrets.token_urlsafe(32)
            now = int(time.time())
            with connect() as db:
                db.execute('INSERT INTO invites (id,name,token_hash,max_guests,status,party_size,activity,notes,updated_at,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)', (secrets.token_hex(12), name, digest(token), 20, status, size, activity, notes.strip(), now, now))
            return self.send(201, {'token': token, 'url': ORIGIN + '/rsvp#' + token})
        if path in ('/api/invite', '/api/rsvp'):
            token = data.get('token')
            if not isinstance(token, str) or len(token) > 100:
                raise ValueError()
            with connect() as db:
                row = db.execute('SELECT * FROM invites WHERE token_hash=?', (digest(token),)).fetchone()
                if not row:
                    return self.send(404, {'error': 'This invitation is invalid or has been replaced. Ask your host for a new link.'})
                if path == '/api/rsvp':
                    status, size, activity, notes = (data.get(k) for k in ('status', 'party_size', 'activity', 'notes'))
                    if status not in ('yes', 'maybe', 'no') or activity not in ('run', 'walk', 'party') or type(size) is not int or not isinstance(notes, str) or len(notes) > 1000:
                        raise ValueError()
                    if (status == 'no' and size != 0) or (status != 'no' and not 1 <= size <= row['max_guests']):
                        raise ValueError()
                    db.execute('UPDATE invites SET status=?,party_size=?,activity=?,notes=?,updated_at=? WHERE id=?', (status, size, activity, notes.strip(), int(time.time()), row['id']))
                    return self.send(200, {'ok': True})
                return self.send(200, {k: row[k] for k in ('name', 'max_guests', 'status', 'party_size', 'activity', 'notes')})
        self.send(404, {'error': 'Not found.'})


if __name__ == '__main__':
    if len(PASSWORD) < 16:
        raise SystemExit('Set FC5K_HOST_PASSWORD to a password of at least 16 characters.')
    initialize()
    port = int(os.environ.get('PORT', '8766'))
    print('FC5K running at ' + ORIGIN, flush=True)
    ThreadingHTTPServer((os.environ.get('BIND', '127.0.0.1'), port), Handler).serve_forever()
