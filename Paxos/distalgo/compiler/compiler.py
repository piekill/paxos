from ast import *
from .dist import DistalgoTransformer
from .codegen import to_source
from .mangler import SelfMangler, PredicateMangler

def dist_compile(fd):
    distree = parse(fd.read())
    dt = DistalgoTransformer()
    pytree = dt.visit(distree)

    return (pytree, dt.classinfos)

def dist_compile_to_string(fd):
    distree = parse(fd.read())
    pytree = DistalgoTransformer().visit(distree)

    return to_source(pytree)

def dist_compile_to_file(fd, outfd):
    distree = parse(fd.read())
    pytree = DistalgoTransformer().visit(distree)
    source = to_source(pytree)
    outfd.write(source)

    return pytree

def dist_compile_with_interface(fd, intfd):
    pytree, cinfos = dist_compile(fd)
    inttree = parse(intfd.read())
