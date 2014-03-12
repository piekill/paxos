from ast import *
import re

 # FIXME: hackish!
UPDATE_ATTRS = {"remove", "extend", "append", "add", "update", "delete"}

class SelfMangler(NodeTransformer):
    """This transforms 'self.a' to '_DP_P_self_a'
    """

    def __init__(self, cls):
        super().__init__()
        self._name = "_DP_" + cls.name +  "_self"

    def visit_Attribute(self, node):
        node = self.generic_visit(node)

        if isinstance(node.value, Name) and node.value.id == "self":
            node = Name(self._name + "_" + node.attr, node.ctx)

        return node

class SelfDemangler(NodeTransformer):
    """This demangles the self reference
    """

    def __init__(self, cls):
        super().__init__()
        self._regex = "^_DP_" + cls.name + "_self_(.+)$"

    def visit_Name(self, node):
        mo = re.match(self._regex, node.id)
        if mo is not None:
            return Attribute(Name("self", Load()),
                             mo.group(1), Load())
        else:
            return self.generic_visit(node)


class PredicateMangler(NodeTransformer):
    """This inlines the message predicate functions.
    """

    def __init__(self, info):
        super().__init__()
        self.preds = info.evtpreds

    def visit_Call(self, node):
        node = self.generic_visit(node)

        if (isinstance(node.func, Attribute) and
            isinstance(node.func.value, Name) and
            node.func.value.id == "self" and
            node.func.attr in self.preds):

            return self.preds[node.func.attr]

        else:
            return node

