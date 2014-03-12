from ast import *
from .visitor import *

class Preprocessor(NodeTransformer):
    def __init__(self):
        super().__init__()
        self.inquant = False

    def visit_Call(self, node):
        if isinstance(node.func, Name) and node.func.id in {"any", "all"}:
            self.inquant = True
            result = self.generic_visit(node)
            self.inquant = False
            return result
        else:
            return self.generic_visit(node)

    def _visit_comp_1(self, node):
        if not self.inquant:
            return self.generic_visit(node)

        print("comp node: " , dump(node))
        self.inquant = False
        node = self.generic_visit(node)

        cond = node.elt if not isinstance(node, DictComp) else node.key

        targets = self._collect_vars(node.generators)
        #if (isinstance(cond, BoolOp) or isinstance(cond, Compare)):
        print(dump(cond))
        node.generators[-1].ifs.append(cond)

        if isinstance(node, DictComp):
            node.key = targets
            node.value = Name("True", Load())
        else:
            node.elt = targets

        return node

    # visit_ListComp = _visit_comp_1
    # visit_SetComp = _visit_comp_1
    # visit_DictComp = _visit_comp_1
    visit_GeneratorExp = _visit_comp_1

    def _collect_vars(self, generators):
        res = []
        for g in generators:
            res.append(g.target)

        if len(res) == 1:
            return res[0]
        else:
            return Tuple(res, Load())


class Three2Two(NodeTransformer):

    def visit_SetComp(self, node):
        node = self.generic_visit(node)

        return Call(Name("set", Load), [GeneratorExp(node.elt, node.generators)],
                    [], None, None)

