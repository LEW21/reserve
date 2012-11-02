"""WSGI Handler

If you want to serve a WSGI app, you should pass it to the Handler, and then pass
the Handler object to a protocol handler, like http.Handler.
"""
__version__ = "0.4"
__all__ = ["Handler", "launch"]

from wsgiref.handlers import SimpleHandler
from . import find_app

def Handler(app):
	def handle_wsgi_request(stdin, stderr, stdout, environ):
		handler = SimpleHandler(stdin, stderr, stdout, environ.vars, environ.server.multithread, environ.server.multiprocess)
		handler.run_once = not environ.server.multiconnection
		handler.server_software = environ.server.software
		handler.run(app)

	return handle_wsgi_request

def launch(args):
	return Handler(find_app(args, 'reserve WSGI handler.', 'wsgi app'))
