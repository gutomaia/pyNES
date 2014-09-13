from pynes.c6502 import opcodes
from pynes.utils import Context, InvalidMemoryAddressing
import sys

registers = ['A', 'X', 'Y']

__all__ = list(opcodes.keys()) + registers


class Register(object):

    def __init__(self, register):
        self.r = register

class InstructionProxy():

    def __init__(self, name):
        self.i = name
        self.context = Context()
        self.context += '%s\n' % name


    def __call__(self, *args, **kw):
        if self.context == None:
            raise Exception('no context')

        # self.context -= 4

        if len(args) == 0 and 'sngl' not in  opcodes[self.i]:
            raise InvalidMemoryAddressing()

        if len(args) == 1 or 'addr' in kw:
            addr = args[0] or kw['addr']
            self.context += '%s %s\n' % (self.i, addr)
        else:
            self.context += '%s\n' % self.i

    def __str__(self):
        return self.i

class Wrapper(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.context = Context()

    def __getattr__(self, name):
        if name in opcodes.keys():
            return InstructionProxy(name)
        elif name in registers:
            return Register(name)
        elif hasattr(self.wrapped, name):
            return getattr(self.wrapped, name)
        else:
            raise AttributeError(name)


sys.modules[__name__] = Wrapper(sys.modules[__name__])
