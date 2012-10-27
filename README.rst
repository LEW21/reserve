======================================
 reserve - Python server. Redesigned. 
======================================

reserve is a **generic** Python server (and server library). It means it's able to host any type of application, not only wsgi apps like the **web** servers do.

Requirements:
-------------

- sdlaunch - reserve doesn't contain socket opening nor daemonizing code, it depends on sdlaunch for that (or alternatively you can use systemd socket activation)
- fdsocket - python's sockets, when creating them from a file descriptor, require their user to provide some information unobtainable from Python, but easy to get from C. fdsocket provides that information.

Usage
-----
::

	sdlaunch -b "[::]:80" -- reserve app [args...]

where:

- ``::`` is the IPv6 address to listen on (``::`` means all)
- ``80`` is the port
- ``app`` is the name of application you want to serve
- ``[args...]`` is a list of arguments to pass to the application (optional)

Application definition
----------------------
Application is a python module containing a ``launch(args)`` callable - where args is an array of strings.

It should return a request handler callable - ``handle(socket, client_address, server)``, where:

- ``socket`` is a newly opened socket
- ``client_address`` is a tuple containing client's IP and port
- ``server`` is a TCPServer object that you probably should not touch

Bundled applications
--------------------
reserve currently bundles only one reserve app - ``http``. Together with ``wsgi`` subapplication it can be used to serve WSGI apps.

The API for writing subapplications of ``http`` is currently undocumented and considered a implementation detail. You should not use it, as it might change at any point in the future. Still, you may use it together with ``wsgi`` - as that is guaranteed to remain backwards compatible.

Serving WSGI apps
-----------------
::

	sdlaunch -b "[::]:80" -- reserve app http wsgi wsgi-app-name [args...]

where ``wsgi-app-name`` is a python module containing a ``launch(args)`` callable (like with normal reserve app)

It should return a WSGI (PEP 3333) application callable.

**Warning:** You should not use reserve.http in production. You should serve your application as SCGI/FCGI/... instead and use a real web server as a frontend.

reserve does not currently support SCGI/FCGI/..., but in the near future it will.
