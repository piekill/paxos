from .base import InsertSelf, ProcessMembers, ProcessRun
from .info import ClassInfo
from .send import SendTransformer
from .await import AwaitTransformer
from .event import EventTransformer
from .label import LabelTransformer
from .mesgcomp import SentReceivedTransformer
from .consts import DISTALGO_BASE_CLASSNAME
from ast import *


class DistalgoTransformer(NodeTransformer):
    """The main compiler routine.

    Walks the top level class definitions in the module.
    """

    def __init__(self):
        super().__init__()
        self.classinfos = {}

    prefix = parse("""
import multiprocessing
import time
import sys
import types
import traceback
import os
import stat
import signal
import time
import logging
import threading
import warnings

from logging import DEBUG
from logging import INFO
from logging import ERROR
from logging import CRITICAL
from logging import FATAL

from distalgo.runtime.udp import UdpEndPoint
from distalgo.runtime.tcp import TcpEndPoint
from distalgo.runtime.event import *
from distalgo.runtime.util import *
from distalgo.runtime import DistProcess
""").body

    def visit_Module(self, node):
        node = self.generic_visit(node)
        newbody = list(DistalgoTransformer.prefix)
        newbody.extend(node.body)
        node.body = newbody
        return node

    def visit_ClassDef(self, node):
        if (self.isPClass(node)):
            return self.processPClass(node)
        else:
            return self.processClass(node)

    @staticmethod
    def isPClass(node):
        """Checks whether the class defined by 'node' is a P(rocess)Class.

        A PClass is any class that is derived from 'DistProcess'.
        """
        result = False
        for b in node.bases:
            if (isinstance(b, Name)):
                if (b.id == DISTALGO_BASE_CLASSNAME):
                    result = True
                    break
        return result

    def processClass(self, node):
        """Compiles a normal class.

        For normal (non-P) classes we simply support omitting the 'self'
        identifier before member references.
        """
        info = ClassInfo(node.name)

        # 1. gather member funcs and vars
        ProcessMembers(info).visit(node)

        # 2. Take care of 'self'
        iself = InsertSelf(info)
        node = iself.visit(node)

        self.info = info
        return node


    def processPClass(self, node):
        """Transforms a DisProcess Class.
        """
        info = ClassInfo(node.name)

        # 0. gather member funcs and vars
        node = ProcessMembers(info).visit(node)

        node = SendTransformer(info).visit(node)

        # 1. Transform query primitives 'sent' and 'received'
        node = SentReceivedTransformer(info).visit(node)

        # 2. Transform 'await'
        node = AwaitTransformer(info).visit(node)

        # 3. Transform and gather labels
        nodete = LabelTransformer(info).visit(node)

        # 4. Transform and gather events
        node = EventTransformer(info).visit(node)

        # 5. Add in new member funcs
        node.body.extend(info.newdefs)

        # 6. Take care of 'self'
        node = InsertSelf(info).visit(node)

        # 7. Generate the __init__ method
        node.body.insert(0, self.genInitFunc(info))

        self.classinfos[node] = info
        return node

    def genInitFunc(self, inf):
        body = []
        body.append(Call(Attribute(Name(DISTALGO_BASE_CLASSNAME, Load()),
                                   "__init__", Load()),
                         [Name("self", Load()), Name("parent", Load()),
                          Name("initq", Load()), Name("channel", Load()),
                          Name("log", Load())],
                         [], None, None))
        body.append(inf.genEventPatternStmt())
        body.append(inf.genSentPatternStmt())
        body.append(inf.genLabelEventsStmt())
        body.extend(inf.newstmts)

        arglist = [arg("self", None), arg("parent", None), arg("initq", None),
                   arg("channel", None), arg("log", None)]
        args = arguments(arglist, None, None, [], None,
                         None, [], None)
        return FunctionDef("__init__", args, body, [], None)


##########
