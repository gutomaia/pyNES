# -*- coding: utf-8 -*-

import ast
from pynes.mixin import MathOperationMixin, LogicOperationMixin, ModuleWrapperMixin

class PyNesTransformer(ast.NodeTransformer, ModuleWrapperMixin, MathOperationMixin, LogicOperationMixin):
    pass
