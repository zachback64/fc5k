import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

spec = importlib.util.spec_from_file_location('app', Path(__file__).resolve().parents[1] / 'server/app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class RSVPTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        app.DB = Path(cls.temp.name) / 'test.sqlite3'
        app.PASSWORD = 'a-long-test-password'
        app.initialize()
        cls.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.port = cls.server.server_address[1]
        app.ORIGIN = f'http://127.0.0.1:{cls.port}'
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp.cleanup()

    def setUp(self):
        with app.connect() as db:
            db.execute('DELETE FROM rate_limits')

    def request(self, path, data=None, cookie=None, origin=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.port)
        headers = {'Origin': origin or app.ORIGIN, 'Content-Type': 'application/json'}
        if cookie:
            headers['Cookie'] = cookie
        conn.request('GET' if data is None else 'POST', path, body=None if data is None else json.dumps(data), headers=headers)
        response = conn.getresponse()
        body = response.read()
        result = (response.status, json.loads(body) if response.getheader('Content-Type') == 'application/json' else body, response.getheader('Set-Cookie'))
        conn.close()
        return result

    def login(self):
        code, _, cookie = self.request('/api/host/login', {'password': app.PASSWORD})
        self.assertEqual(code, 200)
        return cookie.split(';')[0]

    def test_invitation_lifecycle(self):
        cookie = self.login()
        code, result, _ = self.request('/api/host/invites', {'name': 'Test household', 'max_guests': 3}, cookie)
        self.assertEqual(code, 201)
        token = result['url'].split('#')[1]
        self.assertEqual(self.request('/api/invite', {'token': token})[1]['status'], 'pending')
        payload = {'token': token, 'status': 'yes', 'party_size': 3, 'activity': 'walk', 'notes': 'Vegetarian'}
        self.assertEqual(self.request('/api/rsvp', dict(payload, party_size=4))[0], 400)
        self.assertEqual(self.request('/api/rsvp', payload)[0], 200)
        self.assertEqual(self.request('/api/rsvp', dict(payload, status='no', party_size=0))[0], 200)
        rows = self.request('/api/host/invites', cookie=cookie)[1]['invites']
        row = next(i for i in rows if i['name'] == 'Test household')
        self.assertEqual(row['status'], 'no')
        self.assertNotIn('token_hash', row)
        code, replacement, _ = self.request('/api/host/rotate', {'id': row['id']}, cookie)
        self.assertEqual(code, 200)
        self.assertEqual(self.request('/api/invite', {'token': token})[0], 404)
        self.assertEqual(self.request('/api/invite', {'token': replacement['url'].split('#')[1]})[1]['notes'], 'Vegetarian')
        self.assertEqual(self.request('/api/host/logout', {}, cookie)[0], 200)
        self.assertEqual(self.request('/api/host/invites', cookie=cookie)[0], 401)

    def test_public_rsvp_and_update(self):
        payload = {'name': 'Public visitor', 'status': 'yes', 'party_size': 2, 'activity': 'party', 'notes': ''}
        code, result, _ = self.request('/api/public/rsvp', payload)
        self.assertEqual(code, 201)
        self.assertEqual(self.request('/api/invite', {'token': result['token']})[1]['party_size'], 2)
        payload.update(token=result['token'], status='maybe', party_size=1)
        self.assertEqual(self.request('/api/rsvp', payload)[0], 200)
        self.assertEqual(self.request('/api/invite', {'token': result['token']})[1]['status'], 'maybe')
        with app.connect() as db:
            self.assertEqual(db.execute('SELECT status FROM invites WHERE token_hash=?', (app.digest(result['token']),)).fetchone()['status'], 'maybe')

    def test_privacy_and_auth(self):
        for path in ('/data/private/rsvp.sqlite3', '/admin/', '/server/app.py', '/.git/config', '/photos/public/../../data/private/rsvp.sqlite3'):
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request('/api/host/invites')[0], 401)
        self.assertEqual(self.request('/api/host/invites', {'name': 'Stranger', 'max_guests': 1})[0], 401)
        self.assertEqual(self.request('/api/host/login', {'password': 'wrong'})[0], 401)
        self.assertEqual(self.request('/api/host/login', {'password': app.PASSWORD}, origin='https://untrusted.example')[0], 403)
        self.assertEqual(self.request('/api/invite', {'token': 'guess'})[0], 404)

    def test_invalid_inputs(self):
        payload = {'name': 'Test', 'status': 'yes', 'party_size': 1, 'activity': 'run', 'notes': ''}
        for patch in ({'name': ''}, {'name': 123}, {'party_size': 0}, {'party_size': 21}, {'party_size': True}, {'status': 'pending'}, {'notes': 'x' * 1001}, {'activity': 'invalid'}):
            self.assertEqual(self.request('/api/public/rsvp', dict(payload, **patch))[0], 400)

    def test_session_persistence_and_expiry(self):
        cookie = self.login()
        token = cookie.split('=', 1)[1]
        with app.connect() as db:
            saved = db.execute('SELECT token_hash FROM host_sessions WHERE token_hash=?', (app.digest(token),)).fetchone()
            self.assertEqual(saved['token_hash'], app.digest(token))
            self.assertNotEqual(saved['token_hash'], token)
            db.execute('UPDATE host_sessions SET expires_at=0 WHERE token_hash=?', (app.digest(token),))
        self.assertEqual(self.request('/api/host/invites', cookie=cookie)[0], 401)

    def test_persistent_rate_limit(self):
        for _ in range(10):
            self.assertEqual(self.request('/api/host/login', {'password': 'incorrect'})[0], 401)
        self.assertEqual(self.request('/api/host/login', {'password': app.PASSWORD})[0], 429)
        with app.connect() as db:
            db.execute('UPDATE rate_limits SET expires_at=0')
        self.login()


if __name__ == '__main__':
    unittest.main()
