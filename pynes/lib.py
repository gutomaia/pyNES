"""Function wrappers for external libraries"""

from types import FunctionType
from pynes.block import AsmBlock, MemoryAddress
from pynes.asm import Instruction, InstructionProxy, JSR, RTS


def ignoredef(func):
    return func


class asm_def(object):
    r"""A function decorator for an ASM Block function

    Example of waitvblank function::

        @asm_function
        def waitvblank():
            BIT('$2002')
            BPL(waitvblank)
            RTS()

    That must be translated to::

        waitvblank:
        BIT $2002
        BPL waitvblank
        RTS
    """

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], FunctionType):
            self.func = args[0]
            self.has_arguments = False
        else:
            self.has_arguments = True
        self.recursive = False
        self.calls = 0

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, value):
        self._func = value
        self.symbol = MemoryAddress(self.func.__name__)

    def asm(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        if isinstance(result, Instruction) or isinstance(result, InstructionProxy):
            result = AsmBlock(result)
        result.get(0).label = self.symbol
        if self.calls > 1:
            result += RTS
        return result

    def __call__(self, *args, **kwargs):
        if self.recursive:
            return self.symbol

        self.recursive = True
        if self.has_arguments:
            self.func = args[0]
            args = args[1:]

        if self.calls <= 1:
            return self.asm(*args, **kwargs)

        return JSR + self.symbol
