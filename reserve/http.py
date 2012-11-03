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
from .cgi import Env
from . import find_app

class CivilizedBaseRequestHandler:
	def __init__(self, input, output, err, info):
		self.input = input
		self.output = output
		self.err = err
		self.info = info

		self.server_version = info.server.software
		super().__init__(info.socket, info.remote.addr, info.server)

	def setup(self):
		self.connection = self.request
		self.rfile = self.input.buffer
		self.wfile = self.output.buffer

	def finish(self):
		pass

class HTTPRequestHandler(CivilizedBaseRequestHandler, BaseHTTPRequestHandler):
	def parse_request(self):
		ret = super().parse_request()
		self.headers[":method"]  = self.command
		self.headers[":path"]    = self.path
		self.headers[":version"] = self.request_version
		self.headers[":host"]    = self.headers["host"]
		self.headers[":scheme"]  = "http"
		return ret

	@property
	def environ(self):
		return Env.from_headers(self.headers, self.info)

	def handle(self):
		"""Handle a single HTTP request"""

		self.raw_requestline = self.rfile.readline()

		if not self.parse_request(): # An error code has been sent, just exit
			return

		self.app(self.input, self.output, self.err, self.environ)

def Handler(app):
	class handle_http_request(HTTPRequestHandler):
		def setup(self):
			self.app = app
			super().setup()

	return handle_http_request

def launch(args):
	return Handler(find_app(args, 'reserve HTTP handler.', 'reserve.http app'))
