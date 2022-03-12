"""Socket(context, socket_type)
   A 0MQ socket.
   These objects will generally be constructed via the socket() method of a Context object.
   Note: 0MQ Sockets are *not* threadsafe. **DO NOT** share them across threads.
   Parameters
   ----------
   context : Context
       The 0MQ Context this Socket belongs to.
   socket_type : int
       The socket type, which can be any of the 0MQ socket types:
       REQ, REP, PUB, SUB, PAIR, DEALER, ROUTER, PULL, PUSH, XPUB, XSUB.
   See Also
   --------
   .Context.socket : method for creating a socket bound to a Context.
   """