from pynes.c6502 import opcodes
from pynes.utils import Context
import sys

this = sys.modules[__name__]


class Asm(object):
    context = Context()

    def __init__(self, *args, **kw):
        if 'instruction' in kw:
            self.i = kw['instruction']

    def __call__(self, *args, **kw):
        if self.context == None:
            raise Exception('no context')

        if len(args) == 1 or 'addr' in kw:
            addr = args[0] or kw['addr']
            self.context += '%s %s\n' % (self.i, addr)
        else:
            self.context += '%s\n' % self.i


for k,v in opcodes.items():
    setattr(this, k, Asm(instruction=k))
