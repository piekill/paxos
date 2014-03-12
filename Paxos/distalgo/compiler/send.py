from ast import *
from .exceptions import InvalidSendException
from .consts import SENDMSG_FUNNAME

class SendTransformer(NodeTransformer):
    """Translates 'send' arguments into Tuples.
    """

    def __init__(self, info):
        self.info = info

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if (not (isinstance(node.func, Name) and
                 (node.func.id == SENDMSG_FUNNAME))):
            return node

        if (len(node.args) != 2):
            raise InvalidSendException()

        if (not isinstance(node.args[0], Call)):
            return node

        messCall = node.args[0]
        messTuple = Tuple([Str(messCall.func.id)] + messCall.args, Load())
        node.args[0] = messTuple
        return node
