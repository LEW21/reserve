"""HTTP Handler

Supports only reserve's internal app protocol, so to use it with WSGI
you need to pass a wsgi.Handler.

Like the whole Python http module, it is not meant for use in production.
You should serve your application as SCGI/FCGI/... instead and a real web server
as a frontend.
"""
__version__ = "0.4"
__all__ = ["Handler", "launch"]

from http.server import BaseHTTPRequestHandler
import sys
from platform import python_implementation
from .cgi import Env
from .util import lazy
from . import find_app

class HTTPRequestHandler(BaseHTTPRequestHandler):
	def __init__(self, socket, info):
		self.server_version = info.server.software
		self.socket = socket
		self.info = info
		super().__init__(socket, info.remote.addr, info.server)

	def parse_request(self):
		ret = super().parse_request()
		self.headers[":method"]  = self.command
		self.headers[":path"]    = self.path
		self.headers[":version"] = self.request_version
		self.headers[":host"]    = self.headers["host"]
		self.headers[":scheme"]  = "http"
		return ret

	def get_environ(self):
		return Env.from_headers(self.headers, self.info)

	def handle(self):
		"""Handle a single HTTP request"""

		self.raw_requestline = self.rfile.readline()

		if not self.parse_request(): # An error code has been sent, just exit
			return

		self.app(self.rfile, self.wfile, sys.stderr, self.get_environ())

def Handler(app):
	class handle_http_request(HTTPRequestHandler):
		def setup(self):
			self.app = app
			super().setup()

	return handle_http_request

def launch(args):
	return Handler(find_app(args, 'reserve HTTP handler.', 'reserve.http app'))
