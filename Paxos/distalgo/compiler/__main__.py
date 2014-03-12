"""Main entry point"""

import sys,os
import time

if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "python -m distalgo"

RUNTIMEPKG = "runtime"
RUNTIMEFILES = ["event.py", "endpoint.py", "udp.py", "tcp.py", "sim.py", "util.py"]

stderr = sys.stderr
stdout = sys.stdout

def parseArgs(argv):

    import optparse
    p = optparse.OptionParser()

    p.add_option("-p", action="store_true", dest='printsource')
    p.add_option("-F", action="store_true", dest='genfull')
    p.add_option("--full", action="store_true", dest='genfull')
    p.add_option("-O", action="store_true", dest='optimize')
    p.add_option("-D", action="store", dest='rootdir')
    p.add_option("-o", action="store", dest="outfile")
    p.add_option("-i", action="store_true", dest="geninc")
    p.add_option("--use-set", action="store_true", dest="useset")
    p.add_option("-S", action="store_true", dest="useset")
    p.add_option("-2", action="store_true", dest="gentwo")

    p.set_defaults(printsource=False,
                   genfull=False,
                   optimize=False,
                   outfile=None,
                   rootdir=os.getcwd(),
                   useset=False,
                   geninc=False,
                   gentwo=False)

    return p.parse_args()


def printUsage(name):
    usage = """
Usage: %s [-p] [-o outfile] <infile>
     where <infile> is the file name of the distalgo source
"""
    sys.stderr.write(usage % name)

from .codegen import to_source
from .compiler import dist_compile
from .transformation import Three2Two

def main():
    opts, args = parseArgs(sys.argv)

    from .consts import set_use_set_for_queue
    set_use_set_for_queue(opts.useset)

    start = time.time()
    runtime = []
    if opts.genfull:
        for f in RUNTIMEFILES:
            p = os.path.join(opts.rootdir, RUNTIMEPKG, f)
            if not os.path.isfile(p):
                sys.stderr.write("File %s not found. Please specify root directory using -D.\n"%p)
                sys.exit(1)
            else:
                pfd = open(p, "r")
                runtime.extend(pfd.readlines())
                pfd.close()
    postamble = ["\nif __name__ == \"__main__\":\n",
                 "    main()\n"]

    if len(args) == 0:
        stderr.write("error: no input files.\n")
        return 1

    for f in args:
        infd = open(f, 'r')
        pytree, classinfos = dist_compile(infd)
        infd.close()

        if opts.gentwo:
            pytree = Three2Two().visit(pytree)
        pysource = to_source(pytree)

        if opts.printsource:
            stdout.write(pysource)
        else:
            doti = f.rfind(".")
            purename = f[0:doti]
            outfile = purename + ".py"
            outfd = open(outfile, 'w')
            if opts.genfull:
                outfd.writelines(runtime)
            outfd.write(pysource)
            if opts.genfull:
                outfd.writelines(postamble)
            outfd.close()


            sys.stderr.write("Written compiled file %s.\n"% outfile)

    elapsed = time.time() - start
    sys.stderr.write("\nTotal compilation time: %f second(s).\n" % elapsed)
    return 0

if __name__ == '__main__':
    main()
