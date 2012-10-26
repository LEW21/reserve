"""BaseHTTPRequestHandler that implements the Python WSGI protocol (PEP 3333)

This is both an example of how WSGI can be implemented, and a basis for running
simple web applications on a local machine, such as might be done when testing
or debugging an application.  It has not been reviewed for security issues,
however, and we strongly recommend that you use a "real" web server for
production use.

For example usage, see the 'if __name__=="__main__"' block at the end of the
module.  See also the BaseHTTPRequestHandler module docs for other API information.
"""

from http.server import BaseHTTPRequestHandler
import sys
import urllib.parse
from wsgiref.handlers import SimpleHandler
from platform import python_implementation

__version__ = "0.1"
__all__ = ['WSGIRequestHandler']

server_version = "reserve/" + __version__
sys_version = python_implementation() + "/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version

class ServerHandler(SimpleHandler):
	def close(self):
		try:
			self.request_handler.log_request(self.status.split(' ',1)[0], self.bytes_sent)
		finally:
			SimpleHandler.close(self)

class WSGIRequestHandler(BaseHTTPRequestHandler):
	server_version = "WSGIServer/" + __version__

	def get_environ(self):
		if '?' in self.path:
			path, query = self.path.split('?', 1)
		else:
			path, query = self.path, ''

		env = {
			'GATEWAY_INTERFACE': 'CGI/1.1',
#			'SERVER_NAME': '',
#			'SERVER_PORT': '',
			'SCRIPT_NAME': '',
			'SERVER_PROTOCOL': self.request_version,
			'SERVER_SOFTWARE': self.server_version,
			'REQUEST_METHOD': self.command,
			'PATH_INFO': urllib.parse.unquote_to_bytes(path).decode('iso-8859-1'),
			'QUERY_STRING': query,
			'REMOTE_HOST': self.address_string(),
			'REMOTE_ADDR': self.client_address[0],
			'CONTENT_TYPE': self.headers.get('content-type', ''),
			'CONTENT_LENGTH': self.headers.get('content-length', ''),
		}

		for k, v in self.headers.items():
			k=k.replace('-','_').upper(); v=v.strip()
			if k in env:
				continue                    # skip content length, type,etc.
			if 'HTTP_'+k in env:
				env['HTTP_'+k] += ','+v     # comma-separate multiple headers
			else:
				env['HTTP_'+k] = v
		return env

	def get_stderr(self):
		return sys.stderr

	def handle(self):
		"""Handle a single HTTP request"""

		self.raw_requestline = self.rfile.readline()
		if not self.parse_request(): # An error code has been sent, just exit
			return

		handler = ServerHandler(
			self.rfile, self.wfile, self.get_stderr(), self.get_environ()
		)
		handler.server_software = software_version
		handler.request_handler = self      # backpointer for logging
		handler.run(self.server.application)
