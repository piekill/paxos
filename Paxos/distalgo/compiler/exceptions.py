
class DistAlgoCompileError(Exception):
    """Base class for all compiler related errors."""
    pass

class InvalidLabelException(DistAlgoCompileError):
    pass

class InvalidEventException(DistAlgoCompileError):
    pass

class InvalidAwaitException(DistAlgoCompileError):
    pass

class InvalidReceivedException(DistAlgoCompileError):
    pass

class InvalidSentException(DistAlgoCompileError):
    pass

class InvalidSendException(DistAlgoCompileError):
    pass
