"""JSONS Handler
"""
__version__ = "0.3"
__all__ = ["Stream", "Handler", "launch"]

from . import find_app
import json

class Stream:
	def __init__(self, stream):
		self.stream = stream

	def write(self, data):
		self.stream.write(json.dumps(data) + '\n')
		self.stream.flush()

	def __iter__(self):
		for line in self.stream:
			yield json.loads(line)

	def __next__(self):
		return next(iter(self))

	def read(self):
		return next(self)

def Handler(app):
	def handle_request(socket, client_address, server):
		with socket.makefile('rw') as stream:
			stream = Stream(stream)
			for message in stream:
				stream.write(app(message))
	return handle_request

def launch(args):
	return Handler(find_app(args, 'jsons handler.', 'reserve.jsons app'))
