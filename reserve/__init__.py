__version__ = "0.3"
__all__ = ['TCPServer', 'UDPServer', 'launch', 'main', 'find_app']

from .server import TCPServer, UDPServer

def find_app(args, description, app_help):
	from argparse import ArgumentParser, Namespace
	import sys

	parser = ArgumentParser(prog=args[0], description=description)
	parser.add_argument('app', help=app_help)
	parser.add_argument('app_args', metavar='app_param', nargs='*', help='arguments for the app')

	if len(args) < 2 or args[1] in ("-h", "--help"):
		pargs = parser.parse_args(args[1:])
	else:
		pargs = Namespace()
		pargs.app = args[1]
		pargs.app_args = args[2:]

	try:
		app_name = "reserve." + pargs.app
		__import__(app_name)
	except ImportError:
		app_name = pargs.app
		__import__(app_name)

	app_module = sys.modules[app_name]
	return app_module.launch([args[0] + " " + pargs.app] + pargs.app_args)

def launch(args):
	from ctypes import CDLL
	import sys

	sd = CDLL("libsystemd-daemon.so")
	sd.SD_LISTEN_FDS_START = 3

	args[0] = 'reserve'
	app = find_app(args, 'Python server. Redesigned.', 'reserve app (eg. http)')

	n = sd.sd_listen_fds(1);

	if n > 1:
		print("Too many file descriptors received.", file=sys.stderr)
		exit(1)

	if n < 1:
		print("No file descriptors received.", file=sys.stderr)
		exit(1)

	fd = sd.SD_LISTEN_FDS_START

	return TCPServer.fromfd(fd, app)

def main(args):
	launch(args).serve_forever()
