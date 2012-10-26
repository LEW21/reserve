import socket
import socketserver

__version__ = "0.1"
__all__ = ['TCPServer', 'UDPServer']

def server_from_fd(fd, server, handler):
	import fdsocket
	s = socket.fromfd(fd, fdsocket.getfamily(fd), 0)
	return server(s, handler)

class TCPServer(socketserver.TCPServer):
	def __init__(self, server_socket, handler):
		socketserver.BaseServer.__init__(self, (), handler)
		self.socket = server_socket

	@classmethod
	def fromfd(server, fd, handler):
		return server_from_fd(fd, server, handler)

class UDPServer(socketserver.UDPServer):
	def __init__(self, server_socket, handler):
		socketserver.BaseServer.__init__(self, (), handler)
		self.socket = server_socket

	@classmethod
	def fromfd(server, fd, handler):
		return server_from_fd(fd, server, handler)
