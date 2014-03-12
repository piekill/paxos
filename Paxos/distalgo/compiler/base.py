from .consts import DISTALGO_BASE_CLASSNAME
from ast import *

class InsertSelf(NodeTransformer):
    """ Inserts 'self' quantifier to class member variables and methods, adds
    'self' as first argument to member methods, and transforms 'self' into
    'self._id'. Should be the last step in the entire transformation.
    """

    def __init__(self, info):
        self.info = info
        self.selfName = Name("self", Load())
        self.localargs = set()
        self.isInAttr = False

    def visit_Name(self, node):
        if ((self.info.isMemberVar(node.id) or
             self.info.isMemberFunc(node.id)) and
            ((not node.id in self.localargs) or
             type(node.ctx) == Store)):
            return copy_location(Attribute(self.selfName, node.id, node.ctx),
                                 node)
        if (not self.isInAttr and node.id == "self" and type(node.ctx) == Load):
            return copy_location(Attribute(node, "_id", node.ctx), node)
        else:
            return node

    def visit_Attribute(self, node):
        self.isInAttr = True
        node = self.generic_visit(node)
        self.isInAttr = False
        return node

    def visit_FunctionDef(self, node):
        self.localargs = {a.arg for a in node.args.args}
        node = self.generic_visit(node)
        self.localargs = set()
        if (self.info.isMemberFunc(node.name)):
            node.args.args.insert(0, arg("self", None))
        return node

class ProcessMembers(NodeTransformer):
    """Extracts process local variable info from the 'setup' method.
    """

    def __init__(self, info):
        self.info = info

    class VarCollector(NodeVisitor):
        def __init__(self):
            self.vars = dict()

        def visit_assign_1(self, node):
            basetype = "object"
            if isinstance(node.value, Num):
                basetype = type(node.value.n).__name__
            elif isinstance(node.value, List):
                basetype = "list"
            elif isinstance(node.value, Dict):
                basetype = "dict"
            elif isinstance(node.value, Call):
                t = node.value.func
                if isinstance(t, Name):
                    if t.id in {"set", "dict", "list"}:
                        basetype = t.id

            targets = []
            if hasattr(node, "target"):
                targets = [node.target]
            elif hasattr(node, "targets"):
                targets = node.targets
            self._handle_targets(targets, basetype)

        def _handle_targets(self, targets, basetype):
            for n in targets:
                if isinstance(n, Name):
                    self.vars[n.id] = basetype
                elif isinstance(n, Tuple):
                    self._handle_targets(n.elts, basetype)

        visit_Assign = visit_assign_1
        visit_AugAssign = visit_assign_1

    def visit_FunctionDef(self, node):
        self.info.memberfuncs.add(node.name)
        if (node.name == "setup"):
            vc = ProcessMembers.VarCollector()
            vc.visit(node)
            self.info.membervars.update(vc.vars)

            argnames = {a.arg for a in node.args.args}
            for a in argnames:
                self.info.membervars[a] = "object"

            node.body.extend([Assign([Name(n, Store())], Name(n, Load()))
                              for n in argnames])
        return node


class ProcessRun(NodeTransformer):
    def __init__(self):
        self.stmt = Expr(Call
                         (Attribute(Name(DISTALGO_BASE_CLASSNAME, Load()),
                                    "run", Load()),
                          [Name("self", Load())],
                          [], None, None));

    def visit_FunctionDef(self, node):
        if (node.name == "run"):
            node.body.insert(0, self.stmt)
        return node             # We don't recurse down into FunctionDefs

