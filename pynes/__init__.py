# -*- coding: utf-8 -*-
import sys
from pynes.python import pynes_compiler

def write_bin_code(code, file):
    target = open(file, 'wb')
    for opcode in code:
        target.write(chr(opcode))
    target.close()

def press_start():
    f = open(sys.argv[0])
    code = f.read()
    f.close()
    pynes_compiler(code, filename=sys.argv[0]+'.nes')
