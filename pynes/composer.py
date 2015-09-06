# -*- coding: utf-8 -*-
import ast
from pynes.mixin import (AssignMixin, StructMixin, MathOperationMixin,
                         LogicOperationMixin)


class PyNesVisitor(ast.NodeVisitor):

    def __init__(self, symbol_table=None, *args, **kwargs):
        self.symbol_table = symbol_table if symbol_table else {}
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
        arguments = [a.id for a in node.args.args]
        argument_table = {}
        for i, a in enumerate(arguments):
            argument_table[a] = {}
            argument_table[a]['types'] = set()
            argument_table[a]['pos'] = i
        self.new_symbol(node.name, type='function', arguments=arguments,
                        calls=0, argument=argument_table)
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_Call(self, node):
        self.symbol_table[node.func.id]['calls'] += 1
        for a in node.args:
            if isinstance(a, ast.Num):
                t = 'int'
            elif isinstance(a, ast.Name):
                t = self.symbol_table[a.id]['type']
            else:
                t = None
            if t:
                self.symbol_table[node.func.id]['argument']['x']['types'].add(t)
        for keyword in node.keywords:
            if isinstance(keyword.value, ast.Num):
                t = 'int'
            else:
                t = None
            if t:
                self.symbol_table[node.func.id]['argument'][keyword.arg]['types'].add(t)
        self.generic_visit(node)

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


class PyNesTransformer(ast.NodeTransformer, AssignMixin, StructMixin, MathOperationMixin, LogicOperationMixin):
    pass
