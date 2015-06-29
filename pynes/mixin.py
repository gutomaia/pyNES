# -*- coding: utf-8 -*-

import ast
from pynes.asm import *

def get_import(module_name, function_name):
    return ast.ImportFrom(
            module=module_name,
            names=[ast.alias(name=function_name, asname=None)],
            level=0
        )

def load_proxy(proxy):
    return ast.Name(id=proxy.name, ctx=ast.Load())

def get_node(obj):
    if type(obj).__name__ == 'InstructionProxy':
        obj = load_proxy(obj)
    return obj


def asm_nodes(func):
    def wrapper(*args, **kwargs):
        instructions = func(*args, **kwargs)[::-1]
        left = get_node(instructions.pop())
        right = get_node(instructions.pop())
        binOp = ast.BinOp(left=left, op=ast.Add(), right=right)
        while len(instructions) > 0:
            binOp = ast.BinOp(left=binOp, op=ast.Add(), right=get_node(instructions.pop()))
        return binOp
    return wrapper


class AssignMixin(object):

    def visit_Assign(self, node):
        self.generic_visit(node)
        print node


class StructMixin(object):

    def __init__(self, *args, **kwargs):
        self.module_lookup = {}
        self.names = {}

    def visit_ImportFrom(self, node):
        self.generic_visit(node)
        for m in node.names:
            if m.asname:
                self.module_lookup[m.asname] = '%s.%s' % (node.module, node.name)
            else:
                self.module_lookup[m.name] = '%s.%s' % (node.module, m.name)
        return node

    def visit_Module(self, node):
        node.body.insert(0, get_import('pynes.asm', '*'))
        ast.fix_missing_locations(node)
        self.generic_visit(node)
        print self.names
        print self.module_lookup
        return node

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        self.names[node.name] = 'a'
        # print dir(node)
        print node.decorator_list
        return node

    def is_valid_name(self, name):
        return name != 'pynes.lib.asm_def'

    def visit_Name(self, node):
        self.generic_visit(node)
        if self.is_valid_name(self.module_lookup.get(node.id, False)):
            self.names[node.id] = 'a'
        return node

class LogicOperationMixin(object):

    def visit_Call(self, node):
        if node.func.id == 'press_start':
            return None
        # print node.func.id
        self.generic_visit(node)
        return node

    def visit_Mod(self, node):
        return [AND]


class MathOperationMixin(object):

    def visit_Expr(self, node):
        self.generic_visit(node)
        if hasattr(node, 'value'):
            return node
        return None

        return ast.Expr(value=ast.Assign(
                    targets=[ast.Name(id='expr', ctx=ast.Store())],
                    value=node
                )
            )

    def visit_Add(self, node):
        return [CLC , ADC]

    def visit_Sub(self, node):
        return [SEC, SBC]

    def visit_Mult(self, node):
        return [ASL]

    def visit_Num(self, node):
        return [node]

    @asm_nodes
    def visit_BinOp(self, node):
        self.generic_visit(node)
        instructions = []
        if isinstance(node.left, ast.BinOp):
            next = node.left
            while isinstance(next, ast.BinOp):
                instructions.append(next.right)
                next = next.left
            instructions.reverse()
        else:
            instructions+= node.left
        instructions+= node.op

        if ASL not in node.op:
            instructions+= node.right

        return [LDA] + instructions
