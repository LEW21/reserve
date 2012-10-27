"""CGI variable support toolkit. Private.

Request-related variables:
- REQUEST_METOD - :method in SPDY
- REQUEST_URI - :path in SPDY
- SERVER_PROTOCOL - :version in SPDY
- HTTP_HOST - :host in SPDY
- HTTPS - yes/on/1 iff :scheme == https
- CONTENT_LENGTH - content-length in HTTP/SPDY
- CONTENT_TYPE - content-type in HTTP/SPDY

Path-related variables:
- SCRIPT_NAME - path where the application is mounted, without trailing /. %-decoded.
- PATH_INFO - application-specific part of the path. %-decoded.
- QUERY_STRING - part of the URL going after ?. %-encoded.

- REQUEST_URI - URI as sent by the webbrowser. Most likely {SCRIPT_NAME}{PATH_INFO}?{QUERY_STRING}. %-encoded.
- DOCUMENT_URI - REQUEST_URI with QUERY_STRING removed. %-decoded.

- DOCUMENT_ROOT - server-defined directory. %-decoded.
- SCRIPT_FILENAME - most likely {DOCUMENT_ROOT}{SCRIPT_NAME}. %-decoded.
- PATH_TRANSLATED - most likely {DOCUMENT_ROOT}{PATH_INFO}. %-decoded.

Other CGI variables:
- AUTH_TYPE
- GATEWAY_INTERFACE
- REMOTE_{ADDR,PORT,HOST,IDENT,USER} - PORT is non-standard but always supported; HOST and IDENT are standard but usually unsupported.
- SERVER_{ADDR,PORT,NAME,SOFTWARE,*} - ADDR is non-standard but always supported; Some webservers add additional SERVER_ vars.
- DOCUMENT_{PATH_INFO,NAME} - Apache-specific, rather undocumented and useless.
"""

class Env:
	@classmethod
	def from_headers(cls, headers, server_vars):
		env = cls()
		env._headers = headers
		env._server = server_vars
		return env

	@classmethod
	def from_vars(cls, vars):
		env = cls()
		env._vars = fix_path_vars(vars)
		return env

	@property
	def headers(self):
		try:
			return self._headers
		except:
			self._headers = request_vars_to_headers(self.vars)
			return self._headers

	@property
	def vars(self):
		try:
			return self._vars
		except:
			self._vars = headers_to_request_vars(self._headers)
			self._vars.update(self._server)
			fix_path_vars(self._vars)
			return self._vars

	@property
	def server(self):
		try:
			return self._server
		except:
			return self.vars

autoconv_table = [
	(":method", "REQUEST_METHOD"),
	(":path", "REQUEST_URI"),
	(":version", "SERVER_PROTOCOL"),
	(":host", "HTTP_HOST"),
	(":scheme", "HTTPS", lambda cgi: "https" if cgi.get("HTTPS") in ("yes", "on", "1") else "http", lambda spdy: "1" if spdy[":scheme"] == "https" else "0"),
	("content-length", "CONTENT_LENGTH"),
	("content-type", "CONTENT_TYPE")
]

def autoconv(data, source, dest, func):
	converted = {}

	for conv in autoconv_table:
		if conv[dest] is None:
			continue

		try:
			converted[conv[dest]]
		except KeyError:
			f = None
			try:
				f = conv[func]
			except IndexError:
				pass

			if not f:
				f = lambda headers: headers[conv[source]]

			v = f(data)
			if v:
				converted[conv[dest]] = v

	return converted

def headers_to_request_vars(headers):
	env = autoconv(headers, 0, 1, 3)

	for k, v in headers.items():
		k = k.replace('-','_').upper()
		v = v.strip()

		if k in env: # skip content length, type
			continue

		k = "HTTP_" + k

		if k in env: # skip host
			continue

		env[k] = v

	return env

def request_vars_to_headers(env):
	headers = autoconv(env, 1, 0, 2)

	for k, v in env.items():
		if not k.startswith("HTTP_"):
			continue

		k = k[5:].replace('_', '-').lower()

		if k in env: # skip content length, type
			continue

		headers[k] = v

	return headers

from urllib.parse import quote, unquote

def fix_path_vars(env):
	try:
		env["DOCUMENT_URI"]
	except:
		try:
			if '?' in env["REQUEST_URI"]:
				doc_uri, env["QUERY_STRING"] = path.split('?', 1)
			else:
				doc_uri, env["QUERY_STRING"] = env["REQUEST_URI"], ""

			env["DOCUMENT_URI"] = unquote(doc_uri)
		except:
			# It's impossible to determine at this point.
			pass

	try:
		env["SCRIPT_NAME"]
	except:
		# Assume that we are mounted on /
		env["SCRIPT_NAME"] = ''

	try:
		env["PATH_INFO"]
	except:
		try:
			env["PATH_INFO"] = env["DOCUMENT_URI"][len(env["SCRIPT_NAME"]):]
		except:
			raise KeyError("No PATH_INFO, REQUEST_URI nor DOCUMENT_URI. It's impossible to determine path.")

	try:
		env["DOCUMENT_URI"]
	except:
		try:
			env["DOCUMENT_URI"] = env["SCRIPT_NAME"] + env["PATH_INFO"]
		except:
			pass

	try:
		env["REQUEST_URI"]
	except:
		try:
			env["REQUEST_URI"] = quote(env["DOCUMENT_URI"]) +  ("?" + env["QUERY_STRING"] if env.get("QUERY_STRING") else "")
		except:
			pass

	try:
		env["DOCUMENT_ROOT"]
	except:
		try:
			if env["SCRIPT_FILENAME"].endswith(env["SCRIPT_NAME"]):
				env["DOCUMENT_ROOT"] = env["SCRIPT_FILENAME"][:-len(env["SCRIPT_NAME"])]
		except:
			pass

	try:
		env["DOCUMENT_ROOT"]
	except:
		try:
			if env["PATH_TRANSLATED"].endswith(env["PATH_INFO"]):
				env["DOCUMENT_ROOT"] = env["PATH_TRANSLATED"][:-len(env["PATH_INFO"])]
		except:
			pass

	try:
		env["SCRIPT_FILENAME"]
	except:
		try:
			env["SCRIPT_FILENAME"] = env["DOCUMENT_ROOT"] + env["SCRIPT_NAME"]
		except:
			pass

	try:
		env["PATH_TRANSLATED"]
	except:
		try:
			env["PATH_TRANSLATED"] = env["DOCUMENT_ROOT"] + env["PATH_INFO"]
		except:
			pass

