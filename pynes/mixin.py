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


class ModuleWrapperMixin(object):

    def visit_Module(self, node):
        node.body.insert(0, get_import('pynes.asm', '*'))
        ast.fix_missing_locations(node)
        return self.generic_visit(node)


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


class MathOperationMixin(object):

    def visit_Expr(self, node):
        self.generic_visit(node)
        return node
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
