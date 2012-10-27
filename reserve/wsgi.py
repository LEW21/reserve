"""WSGI Handler

If you want to serve a WSGI app, you should pass it to the Handler, and then pass
the Handler object to a protocol handler, like http.Handler.
"""
__version__ = "0.1"
__all__ = ["Handler"]

from wsgiref.handlers import SimpleHandler

def Handler(app, multithread=False, multiprocess=False, run_once=False):
	def handleWSGI(stdin, stderr, stdout, environ):
		handler = SimpleHandler(stdin, stderr, stdout, environ.vars, multithread, multiprocess)
		handler.run_once = run_once
		handler.server_software = environ.vars["SERVER_SOFTWARE"]
		handler.run(app)

	return handleWSGI
