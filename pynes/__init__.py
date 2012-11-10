# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess
import logging
import argparse

from pynes.composer import compose

import pynes.compiler

def press_start(asm = False):
    filename = sys.argv[0]
    pyfile = open(filename)
    code = pyfile.read()
    pyfile.close()
    cart = compose(code)
    asmcode = cart.to_asm()

    if (asm):
        asm_filename = filename + '.asm'
        asm_file = open(asm_filename, 'w')
        asm_file.write(asmcode)
        asm_file.close()
        print asm_filename


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

    subparsers = parser.add_subparsers(
        title="subcommands", description="utilities", help="aditional help")

    py_cmd = subparsers.add_parser('py') #, aliases=['py'])
    py_cmd.add_argument('--output', metavar='OUTPUT', help="output NES file")
    py_cmd.add_argument('input', nargs='?', metavar='INPUT', help="input Python file")
    py_cmd.set_defaults(func=exec_py)

    chr_cmd = subparsers.add_parser('chr')
    chr_cmd.set_defaults(func=chr_cmd)

    asm_cmd = subparsers.add_parser('asm') #TODO, aliases=['asm'])
    asm_cmd.add_argument('input', nargs='?', metavar='INPUT', help="input c6502 asm file")
    asm_cmd.set_defaults(func=exec_asm)

    args = parser.parse_args(argv[1:])
    args.func(args)

def exec_py(args):
    pynes.composer.compose_file(args.input)

def exec_asm(args):
    pynes.compiler.compile_file(args.input)

def exec_chr(args):
    pass