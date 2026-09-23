"""Vercel entry point. Only allowlisted public assets and authenticated APIs are served."""
import os
from urllib.parse import parse_qs, urlparse
from server.app import Handler, initialize

if not os.environ.get('DATABASE_URL') or len(os.environ.get('FC5K_HOST_PASSWORD', '')) < 16:
    raise RuntimeError('Production database and host password must be configured.')
initialize()


class handler(Handler):
    def resolve_path(self):
        query = parse_qs(urlparse(self.path).query)
        if '_route' in query:
            self.path = '/' + query['_route'][0].lstrip('/')

    def do_GET(self):
        self.resolve_path()
        super().do_GET()

    def do_POST(self):
        self.resolve_path()
        super().do_POST()
