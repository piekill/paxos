import logging
import socket

class EndPoint:
    """Represents a target for sending of messages.

    This is the base class for all types of communication channels in
    DistAlgo. It uniquely identifies a "node" in the distributed system. In
    most scenarios, a process will only be associated with one EndPoint
    instance. The 'self' keyword in DistAlgo is ultimately translated into an
    instance of this class.

    """

    def __init__(self, name=None):
        if name is None:
            self._name = socket.gethostname()
        else:
            self._name = name
        self._proc = None
        self._log = logging.getLogger("runtime.EndPoint")
        self._address = None

    def send(self, data, src, timestamp = 0):
        pass

    def recv(self, block, timeout = None):
        pass

    def setname(self, name):
        self._name = name

    def getlogname(self):
        if self._address is not None:
            return "%s_%s" % (self._address[0], str(self._address[1]))
        else:
            return self._name

    def close(self):
        pass

    ###################################################
    # Make the EndPoint behave like a Process object:

    def is_alive(self):
        if self._proc is not None:
            return self._proc.is_alive()
        else:
            self._log.warn("is_alive can only be called from parent process.")
            return self

    def join(self):
        if self._proc is not None:
            return self._proc.join()
        else:
            self._log.warn("join can only be called from parent process.")
            return self

    def terminate(self):
        if self._proc is not None:
            return self._proc.terminate()
        else:
            self._log.warn("terminate can only be called from parent process.")
            return self
   
    ###################################################

    def __getstate__(self):
        return ("EndPoint", self._address, self._name)

    def __setstate__(self, value):
        proto, self._address, self._name = value
        self._log = logging.getLogger("runtime.EndPoint")

    def __str__(self):
        if self._address is not None:
            return str(self._address)
        else:
            return self._name

    def __repr__(self):
        if self._address is not None:
            return str(self._address[1])
        else:
            return self._name

    def __hash__(self):
        return hash(self._address)

    def __eq__(self, obj):
        if not hasattr(obj, "_address"):
            return False
        return self._address == obj._address
    def __lt__(self, obj):
        return self._address < obj._address
    def __le__(self, obj):
        return self._address <= obj._address
    def __gt__(self, obj):
        return self._address > obj._address
    def __ge__(self, obj):
        return self._address >= obj._address
    def __ne__(self, obj):
        if not hasattr(obj, "_address"):
            return True
        return self._address != obj._address
