# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
import argparse

from pynes.composer import compose
import pynes.compiler


def press_start(asm=False):
    filename = sys.argv[0]
    pyfile = open(filename)
    code = pyfile.read()
    pyfile.close()
    game = compose(code)
    asmcode = game.to_asm()

    if (asm):
        asm_filename = filename + '.asm'
        asm_file = open(asm_filename, 'w')
        asm_file.write(asmcode)
        asm_file.close()
        print(asm_filename)


def write_bin_code(code, file):
    target = open(file, 'wb')
    for opcode in code:
        target.write(chr(opcode))
    target.close()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pynes",
        description='pyNES - Python programming for Nintendo 8bits',
        epilog='')

    subparsers = parser.add_subparsers(
        title="subcommands", description="utilities", help="aditional help")

    py_cmd = subparsers.add_parser('py')
    py_cmd.add_argument('-o', '--output', metavar='OUTPUT',
                        help="output NES file")
    py_cmd.add_argument('-a', '--asm', action='store_true',
                        help="generate ASM file")
    py_cmd.add_argument('-v', '--verbose', action='store_true',
                        help="verbose output")
    py_cmd.add_argument('-p', '--path', metavar='PATH',
                        help="path for assets")

    py_cmd.add_argument('input', nargs='?', metavar='INPUT',
                        help="input Python file")
    py_cmd.set_defaults(func=exec_py)

    chr_cmd = subparsers.add_parser('chr')
    chr_cmd.set_defaults(func=chr_cmd)

    asm_cmd = subparsers.add_parser('asm')  # TODO, aliases=['asm'])
    asm_cmd.add_argument('input', nargs='?', metavar='INPUT',
                         help="input c6502 asm file")
    asm_cmd.add_argument('-o', '--output', metavar='OUTPUT',
                         help="output NES file")
    asm_cmd.add_argument('-p', '--path', metavar='PATH',
                         help="path for assets")
    asm_cmd.set_defaults(func=exec_asm)

    nt_cmd = subparsers.add_parser('nt')  # TODO aliases=['nametable']
    nt_cmd.add_argument('input', nargs='?', metavar='INPUT',
                        help="input c6502 asm file")
    nt_cmd.set_defaults(func=exec_nametable)

    img_cmd = subparsers.add_parser('img')  # TODO aliases=['image']
    img_cmd.add_argument('input', nargs='?', metavar='INPUT',
                         help="input nametable")
    img_cmd.set_defaults(func=exec_nametable)

    args = parser.parse_args(argv[1:])
    args.func(args)


def exec_py(args):
    pynes.composer.compose_file(args.input, output=args.output,
                                asm=args.asm, path=args.path)


def exec_asm(args):
    pynes.compiler.compile_file(args.input, output=args.output,
                                path=args.path)


def exec_chr(args):
    pass


def exec_nametable(args):
    pass


def exec_image(args):
    pass
