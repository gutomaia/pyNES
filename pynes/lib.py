from types import FunctionType
from pynes.block import AsmBlock, MemoryAddress
from pynes.asm import Instruction, InstructionProxy, JSR


def ignoredef(func):
    return func


class asm_def(object):

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], FunctionType):
            self.func = args[0]
            self.has_arguments = False
        else:
            self.has_arguments = True

        self.calls = 0

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, value):
        self._func = value
        self.symbol = MemoryAddress(self.func.__name__)

    def __call__(self, *args, **kwargs):
        if self.has_arguments:
            self.func = args[0]
            args = args[1:]

        result = self.func(*args, **kwargs)
        print result
        if isinstance(result, Instruction) or isinstance(result, InstructionProxy):
            result = AsmBlock(result)
        result.get(0).label = self.symbol
        if self.calls <= 1:
            if isinstance(result, AsmBlock):
                pass
            return result

        if result.size > 128:
            pass
            # TODO: return JSL + '$1234'
        # return JSR + '$1234'
        return JSR + self.symbol
