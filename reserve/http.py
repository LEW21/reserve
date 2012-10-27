"""HTTP Handler

Supports only reserve's internal app protocol, so to use it with WSGI
you need to pass a wsgi.Handler.

Like the whole Python http module, it is not meant for use in production.
You should serve your application as SCGI/FCGI/... instead and a real web server
as a frontend.
"""
__version__ = "0.2"
__all__ = ["Handler", "launch"]

from http.server import BaseHTTPRequestHandler
import sys
from platform import python_implementation
from .cgi import Env
from . import find_app

server_version = "reserve/" + __version__
sys_version = python_implementation() + "/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version

class HTTPRequestHandler(BaseHTTPRequestHandler):
	server_version = server_version

	def parse_request(self):
		ret = super().parse_request()
		self.headers[":method"]  = self.command
		self.headers[":path"]    = self.path
		self.headers[":version"] = self.request_version
		self.headers[":host"]    = self.headers["host"]
		self.headers[":scheme"]  = "http"
		return ret

	def get_environ(self):
		return Env.from_headers(self.headers, {
			'SERVER_SOFTWARE': self.server_version,
			'REMOTE_ADDR': self.client_address[0],
			'REMOTE_PORT': self.client_address[1],
		})

	def handle(self):
		"""Handle a single HTTP request"""

		self.raw_requestline = self.rfile.readline()

		if not self.parse_request(): # An error code has been sent, just exit
			return

		self.app(self.rfile, self.wfile, sys.stderr, self.get_environ())

def Handler(app):
	class SpecificHTTPRequestHandler(HTTPRequestHandler):
		def setup(self):
			self.app = app
			super().setup()

	return SpecificHTTPRequestHandler

def launch(args):
	return Handler(find_app(args, 'reserve HTTP handler.', 'reserve.http app'))
