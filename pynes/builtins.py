"""Python builtins that exist only when targeting the NES.

These functions are not Python re-implementations: they compile to
6502 code so normal Python syntax works on the console. They are kept
in their own namespace so they can be shadowed by user definitions or
library imports exactly like Python builtins.
"""

import ast

from pynes.library import Library, NesFunction
from neslib.library import lib as neslib


class Print(NesFunction):
    """Polymorphic print: dispatches to the NES output routine that
    matches the argument width."""

    def caller_code(self, translator, args):
        if len(args) != 1:
            raise TypeError('print() takes exactly one argument')
        arg = args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            raise NotImplementedError('print(str) is not supported yet')
        # numeric values reuse the neslib decimal routines; only the
        # variant actually referenced gets bundled into the ROM
        neslib.externs['put_num'](translator, args)

    def runtime_code(self):
        return ''


pynes_lib = Library('pynes')
pynes_lib.function(Print())
