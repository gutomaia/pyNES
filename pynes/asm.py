from pynes.c6502 import opcodes
from pynes.utils import Context
import sys

__all__ = opcodes.keys()


class InstructionProxy():

    def __init__(self, name):
        self.i = name
        self.context = Context()

    def __call__(self, *args, **kw):
        if self.context == None:
            raise Exception('no context')

        if len(args) == 1 or 'addr' in kw:
            addr = args[0] or kw['addr']
            self.context += '%s %s\n' % (self.i, addr)
        else:
            self.context += '%s\n' % self.i


class Wrapper(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        if name in opcodes.keys():
            return InstructionProxy(name)
        elif hasattr(self.wrapped, name):
            return getattr(self.wrapped, name)
        else:
            raise AttributeError(name)


sys.modules[__name__] = Wrapper(sys.modules[__name__])
