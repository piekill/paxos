from ast import *

class StackedVisitor(NodeVisitor):
    """This visitor puts nodes onto a stack as it descends the tree.
    """

    def __init__(self):
        super().__init__()
        self.ancestors = []

    def visit(self, node):
        self.ancestors.append(node)
        res = super().visit(node)
        self.ancestors.pop()
        return res

class StackedTransformer(StackedVisitor):

    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            old_value = getattr(node, field, None)
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
