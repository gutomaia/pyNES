# -*- coding: utf-8 -*-
import os
import sys
import re
import subprocess
import logging
import argparse

from pynes.python import pynes_compiler

import pynes.compiler

def rsset(size):
    pass

def wait_vblank():
    return
    '''
    WAITVBLANK:
      BIT $2002
      BPL WAITVBLANK
      RTS
    '''

def load_sprite(index):
    pass

def boot(reset, nmi):
    pass

def press_start():
    f = open(sys.argv[0])
    code = f.read()
    f.close()
    pynes_compiler(code, filename=sys.argv[0]+'.nes')

def write_bin_code(code, file):
    target = open(file, 'wb')
    for opcode in code:
        target.write(chr(opcode))
    target.close()

def main(argv = None):
    parser = argparse.ArgumentParser(
        prog="pynes",
        description='pyNES - Python programming for Nintendo 8bits',
        epilog='')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--py', type=str, metavar="FILE", help='compile python')
    group.add_argument('-a', '--asm', type=str, metavar="FILE", help='compile an asm file')
    group.add_argument('-c', '--chr', type=str, metavar="FILE", help='import chr')

    parser.add_argument('-o', '--out', type=argparse.FileType('wb', 0), metavar="FILE", help='output file for compile and convert')

    args = parser.parse_args(argv[1:])
    if args.asm == args.chr == None:
        parser.print_help()
    elif args.py != None:
        #pynes_compiler
        pass
    elif args.asm != None:
        pynes.compiler.compile(args.asm)