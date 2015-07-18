# -*- coding: utf-8 -*-
import ast
from pynes.mixin import StructMixin, MathOperationMixin, LogicOperationMixin


class PyNesVisitor(ast.NodeVisitor):

    def __init__(self, *args, **kwargs):
        self.symbol_table = {}
        self._scope = []

    @property
    def scope(self):
        return ':'.join(self._scope)

    def new_symbol(self, name, **kwargs):
        if name not in self.symbol_table:
            self.symbol_table[name] = kwargs
        else:
            if self.symbol_table[name]['type'] in ['int', 'string']:
                self.symbol_table[name]['assigns'] += 1

    def visit_ImportFrom(self, node):
        for m in node.names:
            name = m.name
            module = '%s.%s' % (node.module, m.name)
            if m.asname:
                name - m.asname
            self.new_symbol(name, type='module', module=module)
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        self.new_symbol(node.name, type='function')
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_Call(self, node):
        print node.func.id

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(node.value, ast.Num):
                self.new_symbol(t.id, type='int', assigns=1, scope=self.scope)
            elif isinstance(node.value, ast.Str):  # TODO: checkover Python3
                self.new_symbol(t.id, type='string', assigns=1, scope=self.scope)

    def visit_AugAssign(self, node):
        if isinstance(node.value, ast.Num):
            self.new_symbol(node.target.id, type='int', assigns=1)

    def get_symbol_table(self):
        return self.symbol_table


class PyNesTransformer(ast.NodeTransformer, StructMixin, MathOperationMixin, LogicOperationMixin):
    pass
