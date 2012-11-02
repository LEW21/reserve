__version__ = "0.4"
__all__ = ['TCPServer', 'UDPServer', 'ConnectionInfo', 'ServerInfo', 'RemoteInfo']

import socket
import socketserver
from .util import lazy

def server_from_fd(fd, server, handler):
	import fdsocket
	s = socket.fromfd(fd, fdsocket.getfamily(fd), 0)
	return server(s, handler)

class InfoContainer:
	def __init__(self, **kwargs):
		for name, val in kwargs.items():
			setattr(self, name, val)

class EndPointInfo(InfoContainer):
	addr = None

class ServerInfo(EndPointInfo):
	software        = None
	multiconnection = None
	multithread     = None
	multiprocess    = None

class RemoteInfo(EndPointInfo):
	pass

class ConnectionInfo(InfoContainer):
	server = ServerInfo()
	remote = RemoteInfo()

class Address:
	def __init__(self, family, address, host=None):
		self.family = family
		self.address = address
		if host is not None:
			self.host = host

	def __getitem__(self, key):
		return self.address[key]

	@property
	def addr(self):
		if self.family in (socket.AF_INET, socket.AF_INET6):
			return self.address[0]
		else:
			return self.address

	@property
	def port(self):
		if self.family in (socket.AF_INET, socket.AF_INET6):
			return self.address[1]
		else:
			raise AttributeError("Only IP addresses have ports")

	@lazy
	def host(self):
		return socket.getnameinfo(self.address)[0]

class LazyAddress:
	def __init__(self, family, get):
		self.family = family
		self._get = get

	@lazy
	def address(self):
		return self._get()

server_version = "reserve/" + __version__
#sys_version = python_implementation() + "/" + sys.version.split()[0]
#software_version = server_version + ' ' + sys_version

def socketserverRequestHandler(app):
	def handle_request(socket, client_address, server):
		s = ServerInfo(software=server_version, multiconnection=True, multithread=False, multiprocess=False)
		c = ConnectionInfo(server=s)

		c.server.addr = LazyAddress(socket.family, lambda: socket.getsockname())
		c.remote.addr = Address(socket.family, client_address)

		app(socket, c)

	return handle_request

class TCPServer(socketserver.TCPServer):
	def __init__(self, server_socket, handler):
		socketserver.BaseServer.__init__(self, (), socketserverRequestHandler(handler))
		self.socket = server_socket

	@classmethod
	def fromfd(server, fd, handler):
		return server_from_fd(fd, server, handler)

class UDPServer(socketserver.UDPServer):
	def __init__(self, server_socket, handler):
		socketserver.BaseServer.__init__(self, (), socketserverRequestHandler(handler))
		self.socket = server_socket

	@classmethod
	def fromfd(server, fd, handler):
		return server_from_fd(fd, server, handler)
