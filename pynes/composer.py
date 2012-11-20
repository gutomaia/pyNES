# -*- coding: utf-8 -*-

import pynes.compiler
import ast
from re import match
from inspect import getmembers

import pynes.bitbag #TODO fix import to be able to remove this

from pynes.game import Game, PPU, PPUSprite, Joypad
from pynes.nes_types import NesType, NesRs, NesArray, NesString, NesSprite, NesChrFile
from pynes.compiler import compile

class OperationStack:

    def __init__(self):
        self._stack = []
        self._pile = []

    def __call__(self, operand = None):
        if operand != None:
            self._stack.append(operand)
        return self._stack

    def store(self):
        if len(self._stack) > 0:
            self._pile.append(self._stack)
            self._stack = []

    def current(self):
        return self._stack

    def wipe(self):
        self._stack = []

    def last(self):
        if len(self._pile) > 0:
            return self._pile[-1]
        return [] #TODO if none breaks some len()

    def pendding(self):
        return self._pile

    def resolve(self):
        return self._pile.pop()

class PyNesVisitor(ast.NodeVisitor):

    def __init__(self):
        self.stack = OperationStack()

    def generic_visit(self, node, debug = False):
        if isinstance(node, list):
            for n in node:
                if debug:
                    print(n)
                self.visit(n)
        else:
            for field, value in reversed(list(ast.iter_fields(node))):
                if debug:
                    print(value)
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            if debug:
                                print(item)
                            self.stack.store()
                            self.visit(item)
                elif isinstance(value, ast.AST):
                    self.visit(value)

    def visit_Import(self, node):
        pass

    def visit_If(self, node):
        if node.test.comparators[0].s == '__main__':
            pass
        else:
            print('IF')
            #print dir(node.test.comparators[0])
            #print node.test.comparators[0].s

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        if len(self.stack.current()) == 2 and len(self.stack.last()) == 2:
            if (isinstance(self.stack.last()[0], int) and
                isinstance(self.stack.last()[1], str) and #TODO op
                isinstance(self.stack.current()[0], PPUSprite) and
                isinstance(self.stack.current()[1], str)): #TODO how to check
                address = getattr(self.stack.current()[0], self.stack.current()[1])
                self.stack.wipe()
                operation = self.stack.last()[1]
                operand = self.stack.resolve()
                global game
                if operation == '+':
                    address += operand[0]
                elif operation == '-':
                    address -= operand[0]
                game += address.to_asm()

    def visit_Assign(self, node):
        global game
        if (len(node.targets) == 1):
            if isinstance(node.value, ast.Call):
                self.generic_visit(node)
                varname = node.targets[0].id
                call = node.value
                if call.func.id:
                    if (len(self.stack.last()) == 1 and
                        isinstance(self.stack.last()[0], NesType)):
                        rs = self.stack.resolve()[0]
                        self.stack.wipe()
                        game.set_var(varname, rs)
            elif isinstance(node.value, ast.List):
                self.generic_visit(node)
                #TODO: just umpile
                varname = node.targets[0].id
                assert isinstance(self.stack.last()[0], NesArray)
                assert varname == self.stack.current()[0]
                lst = [l.n for l in node.value.elts]
                game.set_var(varname, NesArray(lst))
            elif isinstance(node.value, ast.Str):
                self.generic_visit(node)
                varname = node.targets[0].id
                assert isinstance(self.stack.last()[0], NesString)
                assert varname == self.stack.current()[0]
                value = self.stack.resolve()[0]
                self.stack.wipe()
                game.set_var(varname, value)
            elif 'ctx' in dir(node.targets[0]): #TODO fix this please
                self.generic_visit(node) #TODO: upthis
                if len(self.stack.last()) == 1 and isinstance(self.stack.last()[0], int):
                    game += '  LDA #%d\n' % self.stack.resolve()[0]
                if len(self.stack.current()) == 2:
                    address = getattr(self.stack.current()[0], self.stack.current()[1])
                    game += '  STA $%04x\n' % address

    def visit_List(self, node):
        lst = [l.n for l in node.elts]
        self.stack(NesArray(lst))

    def visit_Attribute(self, node):
        self.generic_visit(node)
        attrib = node.attr
        self.stack(attrib)

    def visit_FunctionDef(self, node):
        global game
        if 'reset' == node.name:
            game.state = node.name.upper()
            game += game.init()
            self.generic_visit(node)
        elif 'nmi' == node.name:
            game.state = node.name.upper()
            self.generic_visit(node)
        elif  match('^joypad[12]_(a|b|select|start|up|down|left|right)', node.name):
            game.state = node.name
            self.generic_visit(node)
        else:
            game.state = node.name

    def visit_Call(self, node):
        global game
        if 'id' in dir(node.func):
            self.stack.store()
            if len(node.args) > 0:
                self.generic_visit(node.args)
                args = self.stack.current()
                self.stack.wipe()
            else:
                args = []
            if node.func.id not in game.bitpaks:
                obj = getattr(pynes.bitbag, node.func.id, None)
                if (obj):
                    try:
                        bp = obj(game)
                        game.bitpaks[node.func.id] = bp
                        self.stack(bp(*args))
                        game += bp.asm()
                    except TypeError as ex:
                        msg = ex.message.replace('__call__', node.func.id, 1)
                        raise(TypeError(msg))
                else:
                    raise(NameError("name '%s' is not defined" % node.func.id))
            else:
                bp = game.bitpaks[node.func.id]
                self.stack(bp(*args))
                game += bp.asm()
        else:
            self.generic_visit(node)
            attrib = getattr(self.stack.current()[0], self.stack.current()[1], None)
            self.stack.wipe()
            if callable(attrib):
                attrib()


    def visit_Add(self, node):
        self.stack('+')

    def visit_Sub(self, node):
        self.stack('-')

    def visit_BinOp(self, node):
        if (isinstance(node.left, ast.Num) and
            isinstance(node.right, ast.Num)):
            a = node.left.n
            b = node.right.n
            self.stack(a + b)
        else:
            self.generic_visit(node)

    def visit_Str(self, node):
        self.stack(NesString(node.s))

    def visit_Num(self, node):
        self.stack(node.n)

    def visit_Name(self, node):
        if node.id in game._vars:
            value = game.get_var(node.id)
            value.instance_name = node.id
            self.stack(value)
        else:
            self.stack(node.id) #TODO

game = None

def compose_file(input, output=None, path=None, asm=False):
    from os.path import dirname, realpath

    f = open(input)
    code = f.read()
    f.close()

    if path == None:
        path = dirname(realpath(input)) + '/'

    game = compose(code)
    asmcode = game.to_asm()
    if asm:
        asmfile = open('output.asm', 'w')
        asmfile.write(asmcode)
        asmfile.close()
    compile(asmcode, 'output.nes', path)

def compose(code, game_program = game):
    global game
    if game_program == None:
        game = game_program = Game()

    python_land = ast.parse(code)
    turist = PyNesVisitor()
    turist.visit(python_land)
    game = None
    return game_program
