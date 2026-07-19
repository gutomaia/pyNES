import ast
from functools import wraps


def debug_comment(func):
    @wraps(func)
    def wrap_visit(self, node):
        self.comment(node)
        return func(self, node)

    return wrap_visit


class Ident:
    def __init__(self, name):
        self.name = name
        self.assigns = 0
        self.address = None
        self.initial_value = None
        self.size = 1

    @property
    def label(self):
        return self.name


class _Renamer(ast.NodeTransformer):
    def __init__(self, mapping):
        self.mapping = mapping

    def visit_Name(self, node):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node


class ScopeMangler(ast.NodeTransformer):
    """Renames function parameters and local variables to
    '<function>_<name>' so every function gets statically allocated,
    collision-free variable slots (no software stack)."""

    def visit_FunctionDef(self, node):
        # mangling must be idempotent: trees are shared between the
        # variable table and the translator
        if getattr(node, '_pynes_mangled', False):
            return node
        node._pynes_mangled = True
        # names declared global keep their module-level identity,
        # exactly like Python
        globals_declared = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Global):
                globals_declared.update(stmt.names)
        bound = {arg.arg for arg in node.args.args}
        augmented = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        bound.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                bound.add(elt.id)
            elif isinstance(stmt, ast.AugAssign) and isinstance(
                stmt.target, ast.Name
            ):
                augmented.add(stmt.target.id)
            elif isinstance(stmt, ast.AnnAssign) and isinstance(
                stmt.target, ast.Name
            ):
                bound.add(stmt.target.id)
            elif isinstance(stmt, ast.For):
                if isinstance(stmt.target, ast.Name):
                    bound.add(stmt.target.id)
                elif isinstance(stmt.target, ast.Tuple):
                    for elt in stmt.target.elts:
                        if isinstance(elt, ast.Name):
                            bound.add(elt.id)
        # augmented assignment makes a name local (like Python); with
        # no binding assignment it can never be initialized, which in
        # Python is an UnboundLocalError at runtime
        unbound = augmented - bound - globals_declared
        if unbound:
            name = sorted(unbound)[0]
            raise UnboundLocalError(
                f"local variable {name!r} referenced before "
                f"assignment in {node.name!r} (assign it first, or "
                f'declare it global)'
            )
        local = (bound | augmented) - globals_declared
        mapping = {name: f'{node.name}_{name}' for name in local}
        renamer = _Renamer(mapping)
        for arg in node.args.args:
            arg.arg = mapping[arg.arg]
        node.body = [renamer.visit(stmt) for stmt in node.body]
        return node


def has_yield(node):
    """True when a function definition contains a yield, making it a
    generator task (compiled into a resumable state machine)."""
    return any(isinstance(n, ast.Yield) for n in ast.walk(node))


def annotate_uint16_returns(functions):
    """Functions annotated `-> uint16` return 16 bits. The names
    they return are inferred as uint16 locals: their first
    assignment is rewritten into an annotated declaration, so the
    whole 16-bit machinery (allocation, math) applies."""
    uint16_funcs = set()
    for function in functions:
        if not (
            isinstance(function.returns, ast.Name)
            and function.returns.id == 'uint16'
        ):
            continue
        uint16_funcs.add(function.name)
        returned = {
            node.value.id
            for node in ast.walk(function)
            if isinstance(node, ast.Return)
            and isinstance(node.value, ast.Name)
        }
        for node in ast.walk(function):
            if not isinstance(
                node, (ast.FunctionDef, ast.While, ast.For, ast.If)
            ):
                continue
            for i, stmt in enumerate(node.body):
                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in returned
                ):
                    returned.discard(stmt.targets[0].id)
                    node.body[i] = ast.copy_location(
                        ast.AnnAssign(
                            target=stmt.targets[0],
                            annotation=ast.Name(id='uint16', ctx=ast.Load()),
                            value=stmt.value,
                            simple=1,
                        ),
                        stmt,
                    )
    return uint16_funcs


def _is_uint16_call(value, uint16_funcs):
    """True for calls to functions returning uint16."""
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id in uint16_funcs
    )


TEMP_VARS = (
    'temp_var',
    'temp_left',
    'temp_right',
    'temp_cmp',
    'temp_mul',
    'temp16_lo',
    'temp16_hi',
    'yield_value',
)


def _is_uint16_decl(value):
    """True for `x = uint16()` declarations."""
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == 'uint16'
    )


def _is_uint16_annotation(annotation):
    """True for `x: uint16` annotations."""
    return isinstance(annotation, ast.Name) and annotation.id == 'uint16'


class VarTable(ast.NodeVisitor):
    def __init__(self):
        self.vars = {}
        self.uint16_funcs = set()
        self.uint16_names = set()

    def get_var(self, name):
        if name not in self.vars:
            self.vars[name] = Ident(name)
        return self.vars[name]

    def visit_Name(self, node: ast.Name):
        self.get_var(node.id)
        # return super().visit_Assign(node)

    def visit_Call(self, node: ast.Call):
        # Function names are labels, not variables
        for arg in node.args:
            self.visit(arg)

    def visit_Assign(self, node: ast.Assign):
        # uint16 declaration: allocate two adjacent one-byte slots
        if (
            _is_uint16_decl(node.value)
            or _is_uint16_call(node.value, self.uint16_funcs)
        ) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            self.uint16_names.add(name)
            self.get_var(name).assigns += 1
            self.get_var(f'{name}__hi').assigns += 1
            self.visit(node.value)
            return
        # Handle single and multiple assignments
        for target in node.targets:
            if isinstance(target, ast.Tuple):
                # Handle tuple unpacking (elements may be names or
                # array subscripts, e.g. a[j], a[k] = a[k], a[j])
                for elt in target.elts:
                    if isinstance(elt, ast.Subscript):
                        # a subscript store mutates the array but
                        # does not bind the name (like Python)
                        self.get_var(elt.value.id)
                        self.visit(elt.slice)
                    else:
                        var = self.get_var(elt.id)
                        var.assigns += 1
            elif isinstance(target, ast.Subscript):
                self.get_var(target.value.id)
                self.visit(target.slice)
            else:
                # Handle single assignment
                name = target.id
                var = self.get_var(name)
                var.assigns += 1
                if isinstance(node.value, ast.Constant):
                    var.initial_value = node.value.value
                elif isinstance(node.value, ast.List):
                    var.size = len(node.value.elts)
                    var.initial_value = [elt.value for elt in node.value.elts]
        self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign):
        self.get_var(node.target.id).assigns += 1
        self.visit(node.value)

    def visit_For(self, node: ast.For):
        # the loop target is assigned by the loop itself
        if isinstance(node.target, ast.Name):
            self.get_var(node.target.id).assigns += 1
        elif isinstance(node.target, ast.Tuple):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self.get_var(elt.id).assigns += 1
        self.visit(node.iter)
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                'Only simple annotated assignments are supported'
            )
        name = node.target.id
        if _is_uint16_annotation(node.annotation):
            self.uint16_names.add(name)
            # two adjacent one-byte slots
            self.get_var(name).assigns += 1
            self.get_var(f'{name}__hi').assigns += 1
        else:
            self.get_var(name).assigns += 1
        if node.value is not None:
            self.visit(node.value)

    def locate(self, python_code):
        self.vars = {}
        self.uint16_names = set()
        tree = ScopeMangler().visit(ast.parse(python_code))
        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        self.uint16_funcs = annotate_uint16_returns(functions)
        for function in functions:
            # generator tasks keep their resume point in a state byte
            if has_yield(function):
                self.get_var(f'{function.name}__state')
        self.generic_visit(tree)
        for temp in TEMP_VARS:
            self.get_var(temp)
        address = 0x00
        for name, value in self.vars.items():
            value.address = address
            address += value.size
        return self.vars


class PythonTo6502:
    def __init__(self, libraries=None, builtins=None):
        self.output = []
        self.label_count = 0
        self.loop_end_labels = []
        self.loop_continue_labels = []
        self.debug_comment = True
        self.uint16_vars = set()
        self.externs = {}
        self.const_funcs = {}
        self.builtins = builtins or {}
        self.functions = {}
        self.generator_funcs = set()
        self.uint16_funcs = set()
        self.builtin_iters = {
            'range': self._for_over_range,
            'enumerate': self._for_over_enumerate,
        }
        self.libraries = libraries or []
        for library in self.libraries:
            self.externs.update(library.externs)
            self.const_funcs.update(getattr(library, 'const_funcs', {}))

    def bind_imports(self, tree):
        """Apply Python name binding from the source's import lines:
        `from <library> import a, b as c` restricts the visible
        externs to exactly the imported names, so aliasing resolves
        collisions between libraries. Sources without library imports
        keep every extern implicitly bound (the twin specs carry no
        import lines)."""
        registries = {library.name: library for library in self.libraries}
        bound_externs = {}
        bound_consts = {}
        imported = False
        for node in getattr(tree, 'body', []):
            if not isinstance(node, ast.ImportFrom):
                continue
            library = registries.get(node.module)
            if library is None:
                # not a function library (e.g. pynes.types)
                continue
            imported = True
            for alias in node.names:
                local = alias.asname or alias.name
                if alias.name in library.externs:
                    bound_externs[local] = library.externs[alias.name]
                elif alias.name in getattr(library, 'const_funcs', {}):
                    bound_consts[local] = library.const_funcs[alias.name]
                # other names (entry decorators, constants) are
                # resolved elsewhere
        if imported:
            self.externs = bound_externs
            self.const_funcs = bound_consts

    def translate(self, python_code):
        # Parse Python code into an AST, mangling function scopes
        tree = ScopeMangler().visit(ast.parse(python_code))
        # the compiler is self-sufficient: generator tasks and
        # uint16 returns are discovered from the source itself
        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        self.uint16_funcs |= annotate_uint16_returns(functions)
        for function in functions:
            if has_yield(function):
                self.generator_funcs.add(function.name)
            self.functions.setdefault(
                function.name, [arg.arg for arg in function.args.args]
            )
        ast.fix_missing_locations(tree)

        # Traverse the AST and generate 6502 assembly code
        self.visit(tree)

        # Return the generated assembly code
        return '\n'.join(self.output)

    def comment(self, node):
        if not self.debug_comment:
            return
        code = ast.unparse(node).split('\n')
        for line in code:
            self.output.append(f'; {line}')

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        raise NotImplementedError(
            f'Visit method not implemented for {type(node).__name__}'
        )

    def visit_Expr(self, node):
        self.visit(node.value)

    def visit_Pass(self, node):
        pass

    def visit_Global(self, node):
        # scoping is resolved by the ScopeMangler; no code to emit
        pass

    @debug_comment
    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise NotImplementedError('Only direct calls are supported')
        name = node.func.id
        # Python resolution order: a def in the program shadows any
        # imported or implicitly bound library extern
        if name in self.functions:
            params = self.functions[name]
            if len(node.args) != len(params):
                raise NotImplementedError(
                    f'{name}() takes {len(params)} arguments '
                    f'({len(node.args)} given)'
                )
            for arg, param in zip(node.args, params):
                self._eval_to_a(arg)
                self.output.append(f'STA {param}')
            self.output.append(f'JSR {name}')
        elif name in self.externs:
            self.externs[name](self, node.args)
        elif name in self.builtins:
            # Python builtins (print, etc.) resolve last and are never
            # shadowed by imports; they may still be hidden by a user def
            self.builtins[name](self, node.args)
        else:
            raise NameError(f'name {name!r} is not defined')

    def _fold_const(self, node):
        """Fold a call to a const function with constant arguments into
        an ast.Constant with its result."""
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in self.const_funcs
            and all(isinstance(arg, ast.Constant) for arg in node.args)
        ):
            value = self.const_funcs[node.func.id](
                *[arg.value for arg in node.args]
            )
            return ast.Constant(value=value)
        return node

    def _eval_to_a(self, node):
        """Evaluate an expression, leaving the result in the A register."""
        node = self._fold_const(node)
        if isinstance(node, ast.Constant):
            self.output.append(f'LDA #{node.value}')
        elif isinstance(node, ast.Name):
            self.output.append(f'LDA {node.id}')
        else:
            # BinOp, Subscript and Call all leave their result in A
            self.visit(node)

    @staticmethod
    def _is_simple_index(index):
        """Simple indexes load directly into X/Y without touching A."""
        return isinstance(index, (ast.Constant, ast.Name))

    def _load_index(self, index, register='X'):
        """Load an array index into the X or Y register."""
        if isinstance(index, ast.Constant):
            self.output.append(f'LD{register} #{index.value}')
        elif isinstance(index, ast.Name):
            self.output.append(f'LD{register} {index.id}')
        else:
            # expression index (e.g. arr[j + 1]): evaluate into A,
            # then transfer. Clobbers A.
            self._eval_to_a(index)
            self.output.append(f'TA{register}')

    def visit_Subscript(self, node):
        """Load an array element into the A register."""
        if not isinstance(node.value, ast.Name):
            raise NotImplementedError('Only named arrays are supported')
        self._load_index(node.slice, 'X')
        self.output.append(f'LDA {node.value.id},X')

    @debug_comment
    def visit_FunctionDef(self, node):
        if has_yield(node):
            self._translate_generator(node)
            return
        self._returns_uint16 = node.name in self.uint16_funcs
        self.output.append(f'{node.name}:')
        for stmt in node.body:
            self.visit(stmt)
        if not (node.body and isinstance(node.body[-1], ast.Return)):
            self.output.append('RTS')
        self._returns_uint16 = False

    def _translate_generator(self, node):
        """Compile a generator function into a resumable state machine.

        A state byte selects where to continue: 0 runs the body from
        the start, each yield k saves state k and returns, and the
        dispatch resumes right after it on the next call. Locals are
        statically allocated, so loops survive the suspension. The
        routine leaves 1 in A while the task is alive and 0 once the
        body runs to completion (driven one step at a time by step()).
        """
        name = node.name
        state = f'{name}__state'
        total = sum(isinstance(n, ast.Yield) for n in ast.walk(node))
        self._generator = {'name': name, 'index': 0}
        self.output.append(f'{name}:')
        self.output.append(f'LDA {state}')
        self.output.append(f'BNE {name}__d0')
        self.output.append(f'JMP {name}__begin')
        self.output.append(f'{name}__d0:')
        for k in range(1, total + 1):
            self.output.append(f'CMP #{k}')
            self.output.append(f'BNE {name}__d{k}')
            self.output.append(f'JMP {name}__resume_{k}')
            self.output.append(f'{name}__d{k}:')
        # exhausted (or unknown) state: report the task as finished
        self.output.append('LDA #0')
        self.output.append('RTS')
        self.output.append(f'{name}__begin:')
        for stmt in node.body:
            self.visit(stmt)
        # falling off the end finishes the task
        self.output.append('LDA #255')
        self.output.append(f'STA {state}')
        self.output.append('LDA #0')
        self.output.append('RTS')
        self._generator = None

    def visit_Yield(self, node):
        if not getattr(self, '_generator', None):
            raise NotImplementedError('yield outside a generator task')
        self._generator['index'] += 1
        index = self._generator['index']
        name = self._generator['name']
        # a yielded value is published in yield_value, where a
        # 'for x in task(...):' loop picks it up
        if node.value is not None:
            self._eval_to_a(node.value)
            self.output.append('STA yield_value')
        self.output.append(f'LDA #{index}')
        self.output.append(f'STA {name}__state')
        self.output.append('LDA #1')
        self.output.append('RTS')
        self.output.append(f'{name}__resume_{index}:')

    @debug_comment
    def visit_Return(self, node):
        if node.value is not None and getattr(self, '_returns_uint16', False):
            self._return_uint16(node.value)
            return
        if node.value is not None:
            self._eval_to_a(node.value)
        self.output.append('RTS')

    def _return_uint16(self, value):
        """Return 16 bits: A holds the low byte, X the high byte,
        the same convention load_arg16 uses."""
        value = self._fold_const(value)
        if isinstance(value, ast.Constant):
            self.output.append(f'LDX #{(value.value >> 8) & 0xFF}')
            self.output.append(f'LDA #{value.value & 0xFF}')
        elif isinstance(value, ast.Name):
            if value.id in self.uint16_vars:
                self.output.append(f'LDX {value.id}__hi')
            else:
                self.output.append('LDX #0')
            self.output.append(f'LDA {value.id}')
        else:
            raise NotImplementedError(
                'uint16 returns support constants and variables only'
            )
        self.output.append('RTS')

    def load_arg8(self, arg):
        """Load an 8-bit argument into the A register."""
        # any expression works: calls, subscripts and arithmetic all
        # leave their result in A
        self._eval_to_a(arg)

    def load_arg16(self, arg):
        """Load a 16-bit argument into X (high byte) and A (low byte)."""
        arg = self._fold_const(arg)
        if isinstance(arg, ast.Constant):
            value = arg.value
            self.output.append(f'LDX #{(value >> 8) & 0xFF}')
            self.output.append(f'LDA #{value & 0xFF}')
        elif isinstance(arg, ast.Name):
            if arg.id in self.uint16_vars:
                self.output.append(f'LDX {arg.id}__hi')
            else:
                self.output.append('LDX #0')
            self.output.append(f'LDA {arg.id}')
        elif self._is_linear_const_call(arg):
            self._load_linear_const_call(arg)
        else:
            raise NotImplementedError(
                '16-bit variable arguments are not supported yet'
            )

    def _is_linear_const_call(self, arg):
        """A const function call with exactly one runtime argument,
        e.g. NTADR_A(12, line)."""
        return (
            isinstance(arg, ast.Call)
            and isinstance(arg.func, ast.Name)
            and arg.func.id in self.const_funcs
            and sum(not isinstance(a, ast.Constant) for a in arg.args) == 1
        )

    def _load_linear_const_call(self, arg):
        """Expand a const function called with one runtime argument.

        The function must be linear in that argument (f(v) = base +
        slope * (v % period), checked by probing the whole 8-bit
        domain) with a power-of-two slope and period, which covers the
        nametable helpers: NTADR_A(x, y) advances 32 bytes per row and
        wraps at row 32 (tile coordinates are 5-bit fields). The
        result lands in X (high) and A (low) via the temp16 pair.
        """
        func = self.const_funcs[arg.func.id]
        index = next(
            i
            for i, a in enumerate(arg.args)
            if not isinstance(a, ast.Constant)
        )

        def probe(v):
            values = [a.value for a in arg.args if isinstance(a, ast.Constant)]
            values.insert(index, v)
            return func(*values)

        base = probe(0)
        slope = probe(1) - base
        period = next(
            (
                candidate
                for candidate in (2, 4, 8, 16, 32, 64, 128, 256)
                if all(
                    probe(v) == base + slope * (v % candidate)
                    for v in range(256)
                )
            ),
            None,
        )
        if slope <= 0 or slope & (slope - 1) or period is None:
            raise NotImplementedError(
                f'{arg.func.id} is not linear with a power-of-two '
                'slope in its runtime argument'
            )
        shift = slope.bit_length() - 1
        self._eval_to_a(arg.args[index])
        if period < 256:
            # wrap exactly like the compile-time fold would
            self.output.append(f'AND #{period - 1}')
        self.output.append('STA temp16_lo')
        self.output.append('LDA #0')
        self.output.append('STA temp16_hi')
        for _ in range(shift):
            self.output.append('ASL temp16_lo')
            self.output.append('ROL temp16_hi')
        self.output.append('CLC')
        self.output.append('LDA temp16_lo')
        self.output.append(f'ADC #{base & 0xFF}')
        self.output.append('STA temp16_lo')
        self.output.append('LDA temp16_hi')
        self.output.append(f'ADC #{(base >> 8) & 0xFF}')
        self.output.append('TAX')
        self.output.append('LDA temp16_lo')

    def load_arg8_x(self, arg):
        """Load an 8-bit argument into the X register."""
        arg = self._fold_const(arg)
        if isinstance(arg, ast.Constant):
            self.output.append(f'LDX #{arg.value}')
        elif isinstance(arg, ast.Name):
            self.output.append(f'LDX {arg.id}')
        else:
            raise NotImplementedError('Unsupported argument expression')

    def visit_Name(self, node):
        # Handle memory location access
        if node.id.startswith('mem_'):
            addr = int(node.id.split('_')[1], 16)
            if addr < 0x100:  # Zero page
                self.output.append(f'LDA ${addr:02X}')
            else:  # Absolute addressing
                self.output.append(f'LDA ${addr:04X}')
        return node.id

    def visit_Constant(self, node):
        return node.value

    def _is_uint16_operand(self, node):
        """True when a comparison operand is a declared uint16 variable."""
        return isinstance(node, ast.Name) and node.id in self.uint16_vars

    def visit_Compare(self, node):
        left = node.left
        ops = node.ops
        comparators = node.comparators
        if len(ops) == 1 and len(comparators) == 1:
            comparator = comparators[0]
            op = ops[0]

            # uint16 equality/inequality: combine both bytes into Z
            left_is_16 = self._is_uint16_operand(left)
            right_is_16 = self._is_uint16_operand(comparator)
            if (
                isinstance(op, (ast.Eq, ast.NotEq))
                and (left_is_16 or right_is_16)
            ):
                self._compare_uint16_eq(left, comparator)
                return

            # An expression index on the right side clobbers A, so it
            # must be loaded into Y before the left operand
            if isinstance(
                comparator, ast.Subscript
            ) and not self._is_simple_index(comparator.slice):
                self._load_index(comparator.slice, 'Y')

            # An expression on the right side clobbers A, so it is
            # evaluated into a scratch byte before the left operand
            expression_comparator = not isinstance(
                comparator, (ast.Constant, ast.Name, ast.Subscript)
            )
            if expression_comparator:
                self.visit(comparator)
                self.output.append('STA temp_cmp')

            # Load the left operand into A
            if isinstance(left, ast.Name):
                self.output.append(f'LDA {left.id}')
            elif isinstance(left, ast.Subscript):
                self.visit_Subscript(left)
            elif isinstance(left, (ast.Call, ast.BinOp)):
                # Calls and expressions leave their result in A
                self.visit(left)
            else:
                raise NotImplementedError(
                    'Unsupported comparison left operand type'
                )

            # Compare against the right operand
            if expression_comparator:
                self.output.append('CMP temp_cmp')
            elif isinstance(comparator, ast.Constant):
                self.output.append(f'CMP #{comparator.value}')
            elif isinstance(comparator, ast.Name):
                self.output.append(f'CMP {comparator.id}')
            elif isinstance(comparator, ast.Subscript):
                if not isinstance(comparator.value, ast.Name):
                    raise NotImplementedError(
                        'Only named arrays are supported'
                    )
                if self._is_simple_index(comparator.slice):
                    self._load_index(comparator.slice, 'Y')
                self.output.append(f'CMP {comparator.value.id},Y')
            else:
                raise NotImplementedError('Unsupported comparison value type')
        else:
            raise NotImplementedError('Unsupported comparison')

    def _compare_uint16_eq(self, left, right):
        """Emit a comparison that leaves Z=1 iff the two 16-bit operands
        are equal. Supports uint16 variable vs constant and uint16 vs
        uint16 variable; the caller then BEQ/BNEs on the result."""
        if isinstance(left, ast.Name) and left.id in self.uint16_vars:
            var_name = left.id
            if isinstance(right, ast.Constant):
                hi, lo = (right.value >> 8) & 0xFF, right.value & 0xFF
                self.output.append(f'LDA {var_name}__hi')
                self.output.append(f'EOR #{hi}')
                self.output.append(f'ORA {var_name}')
                self.output.append(f'EOR #{lo}')
            elif isinstance(right, ast.Name) and right.id in self.uint16_vars:
                self.output.append(f'LDA {var_name}__hi')
                self.output.append(f'EOR {right.id}__hi')
                self.output.append(f'ORA {var_name}')
                self.output.append(f'EOR {right.id}')
            else:
                raise NotImplementedError(
                    'uint16 == supports constants and other uint16 vars'
                )
        elif (
            isinstance(right, ast.Name)
            and right.id in self.uint16_vars
            and isinstance(left, ast.Constant)
        ):
            hi, lo = (left.value >> 8) & 0xFF, left.value & 0xFF
            self.output.append(f'LDA {right.id}__hi')
            self.output.append(f'EOR #{hi}')
            self.output.append(f'ORA {right.id}')
            self.output.append(f'EOR #{lo}')
        else:
            raise NotImplementedError(
                'uint16 equality needs at least one uint16 operand'
            )

    def visit_Module(self, node):
        # Set parent references for the AST
        for stmt in ast.walk(node):
            for child in ast.iter_child_nodes(stmt):
                setattr(child, '_parent', stmt)

        # Register user-defined functions first so calls can resolve
        functions = [
            stmt for stmt in node.body if isinstance(stmt, ast.FunctionDef)
        ]
        for function in functions:
            self.functions[function.name] = [
                arg.arg for arg in function.args.args
            ]

        # Visit the main flow
        for stmt in node.body:
            if not isinstance(stmt, ast.FunctionDef):
                self.visit(stmt)

        # Emit function bodies after the main flow, jumping over them
        if functions:
            end_label = self._generate_label()
            self.output.append(f'JMP {end_label}')
            for function in functions:
                self.visit(function)
            self.output.append(f'{end_label}:')
            self.output.append('NOP')

    def _store_to(self, target):
        """Store the A register into a Name or Subscript target."""
        if isinstance(target, ast.Name):
            self.output.append(f'STA {target.id}')
        elif isinstance(target, ast.Subscript):
            if not isinstance(target.value, ast.Name):
                raise NotImplementedError('Only named arrays are supported')
            if self._is_simple_index(target.slice):
                self._load_index(target.slice, 'X')
            else:
                # expression index clobbers A: preserve the value on
                # the stack while computing the index
                self.output.append('PHA')
                self._load_index(target.slice, 'X')
                self.output.append('PLA')
            self.output.append(f'STA {target.value.id},X')
        else:
            raise NotImplementedError('Unsupported assignment target')

    def _assign_uint16(self, name, value):
        """Emit a 16-bit assignment to a uint16 variable."""
        value = self._fold_const(value)
        if isinstance(value, ast.Constant):
            lo, hi = value.value & 0xFF, (value.value >> 8) & 0xFF
            self.output.append(f'LDA #{lo}')
            self.output.append(f'STA {name}')
            self.output.append(f'LDA #{hi}')
            self.output.append(f'STA {name}__hi')
        elif isinstance(value, ast.Name) and value.id in self.uint16_vars:
            self.output.append(f'LDA {value.id}')
            self.output.append(f'STA {name}')
            self.output.append(f'LDA {value.id}__hi')
            self.output.append(f'STA {name}__hi')
        elif isinstance(value, ast.Name):
            # 8-bit variable: zero-extend
            self.output.append(f'LDA {value.id}')
            self.output.append(f'STA {name}')
            self.output.append('LDA #0')
            self.output.append(f'STA {name}__hi')
        elif isinstance(value, ast.BinOp) and isinstance(value.op, ast.Mult):
            self._uint16_mul(name, value)
        elif isinstance(value, ast.BinOp) and isinstance(
            value.op, (ast.Add, ast.Sub)
        ):
            if not (
                isinstance(value.left, ast.Name) and value.left.id == name
            ):
                raise NotImplementedError(
                    'uint16 add/sub must be of the form x = x + value'
                )
            self._uint16_add_sub(name, value.op, value.right)
        else:
            raise NotImplementedError('Unsupported uint16 assignment')

    def _uint16_add_sub(self, name, op, operand):
        """Emit 16-bit x += / -= operand with carry propagation."""
        operand = self._fold_const(operand)
        if isinstance(op, ast.Add):
            prep, inst = 'CLC', 'ADC'
        else:
            prep, inst = 'SEC', 'SBC'
        if isinstance(operand, ast.Constant):
            lo, hi = operand.value & 0xFF, (operand.value >> 8) & 0xFF
            lo_arg, hi_arg = f'#{lo}', f'#{hi}'
        elif isinstance(operand, ast.Name):
            if operand.id in self.uint16_vars:
                lo_arg, hi_arg = operand.id, f'{operand.id}__hi'
            else:
                lo_arg, hi_arg = operand.id, '#0'
        else:
            raise NotImplementedError('Unsupported uint16 operand')
        self.output.append(prep)
        self.output.append(f'LDA {name}')
        self.output.append(f'{inst} {lo_arg}')
        self.output.append(f'STA {name}')
        self.output.append(f'LDA {name}__hi')
        self.output.append(f'{inst} {hi_arg}')
        self.output.append(f'STA {name}__hi')

    def _uint16_mul(self, name, value):
        """Emit x = x * n (uint16 x, uint8 n) by repeated addition."""
        left, right = value.left, value.right
        if isinstance(right, ast.Name) and right.id == name:
            left, right = right, left
        if not (
            isinstance(left, ast.Name)
            and left.id == name
            and isinstance(right, ast.Name)
        ):
            raise NotImplementedError(
                'uint16 multiply must be of the form x = x * var'
            )
        mul_loop = self._generate_label()
        mul_end = self._generate_label()
        self.output.append(f'LDA {name}')
        self.output.append('STA temp16_lo')
        self.output.append(f'LDA {name}__hi')
        self.output.append('STA temp16_hi')
        self.output.append('LDA #0')
        self.output.append(f'STA {name}')
        self.output.append(f'STA {name}__hi')
        self.output.append(f'LDX {right.id}')
        self.output.append(f'{mul_loop}:')
        self.output.append('CPX #0')
        self.output.append(f'BEQ {mul_end}')
        self.output.append('CLC')
        self.output.append(f'LDA {name}')
        self.output.append('ADC temp16_lo')
        self.output.append(f'STA {name}')
        self.output.append(f'LDA {name}__hi')
        self.output.append('ADC temp16_hi')
        self.output.append(f'STA {name}__hi')
        self.output.append('DEX')
        self.output.append(f'JMP {mul_loop}')
        self.output.append(f'{mul_end}:')

    @debug_comment
    def visit_AnnAssign(self, node):
        """Typed declaration: `x: uint16 = 400` or bare `x: uint16`."""
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                'Only simple annotated assignments are supported'
            )
        name = node.target.id
        if _is_uint16_annotation(node.annotation):
            self.uint16_vars.add(name)
            if node.value is not None:
                self._assign_uint16(name, node.value)
            return
        # any other annotation (e.g. uint8) compiles as a plain assign
        if node.value is not None:
            assign = ast.Assign(
                targets=[node.target],
                value=node.value,
            )
            ast.copy_location(assign, node)
            assign._parent = getattr(node, '_parent', None)
            self.visit_Assign(assign)

    @debug_comment
    def visit_Assign(self, node):
        # uint16 declaration: x = uint16() marks x as 16-bit
        if _is_uint16_decl(node.value) and isinstance(
            node.targets[0], ast.Name
        ):
            name = node.targets[0].id
            self.uint16_vars.add(name)
            if node.value.args:
                self._assign_uint16(name, node.value.args[0])
            return

        # a call to a -> uint16 function makes the target 16-bit
        if _is_uint16_call(node.value, self.uint16_funcs) and isinstance(
            node.targets[0], ast.Name
        ):
            name = node.targets[0].id
            self.uint16_vars.add(name)
            # the call returns A = low byte, X = high byte
            self._eval_to_a(node.value)
            self.output.append(f'STA {name}')
            self.output.append(f'STX {name}__hi')
            return

        # 16-bit assignment to a declared uint16 variable
        if (
            isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in self.uint16_vars
        ):
            self._assign_uint16(node.targets[0].id, node.value)
            return

        # Handle tuple assignment: a, b = x, y (e.g. pythonic swap)
        if isinstance(node.targets[0], ast.Tuple):
            targets = node.targets[0].elts
            if not isinstance(node.value, ast.Tuple) or len(
                node.value.elts
            ) != len(targets):
                raise NotImplementedError(
                    'Tuple assignment requires matching tuples on '
                    'both sides'
                )
            # evaluate every value onto the stack first, so swaps
            # read the old values before any target is written
            for value in node.value.elts:
                self._eval_to_a(value)
                self.output.append('PHA')
            for target in reversed(targets):
                self.output.append('PLA')
                self._store_to(target)
            return

        # Handle array element assignment: arr[i] = value
        if isinstance(node.targets[0], ast.Subscript):
            self._eval_to_a(node.value)
            self._store_to(node.targets[0])
            return

        # Handle array literal assignment: arr = [1, 2, 3]
        if isinstance(node.value, ast.List):
            array_name = node.targets[0].id
            for i, elt in enumerate(node.value.elts):
                if not isinstance(elt, ast.Constant):
                    raise NotImplementedError(
                        'Only constant array literals are supported'
                    )
                self.output.append(f'LDA #{elt.value}')
                self.output.append(f'LDX #{i}')
                self.output.append(f'STA {array_name},X')
            return

        # Handle memory location assignment first
        if not isinstance(node.targets[0], ast.Tuple) and node.targets[
            0
        ].id.startswith('mem_'):
            target = node.targets[0]
            var_name = target.id
            addr = int(var_name.split('_')[1], 16)
            if isinstance(node.value, ast.Name):
                # Load from variable then store to memory
                self.output.append(f'LDA {node.value.id}')
                if addr < 0x100:  # Zero page
                    self.output.append(f'STA ${addr:02X}')
                else:  # Absolute addressing
                    self.output.append(f'STA ${addr:04X}')
            return

        # Handle tuple unpacking
        if isinstance(node.targets[0], ast.Tuple):
            if isinstance(node.value, ast.Tuple):
                # Unpack values one by one
                for target, value in zip(
                    node.targets[0].elts, node.value.elts
                ):
                    if isinstance(value, ast.Constant):
                        self.output.append(f'LDA #{value.value}')
                    elif isinstance(value, ast.Name):
                        self.output.append(f'LDA {value.id}')
                    else:
                        # Visit the value first - this handles expressions
                        self.visit(value)
                    self.output.append(f'STA {target.id}')
            return

        # Handle regular assignments
        if isinstance(node.value, ast.Constant):
            self.output.append(f'LDA #{node.value.value}')
        elif isinstance(node.value, ast.Name):
            self.output.append(f'LDA {node.value.id}')
        else:
            # Visit the value first - this handles IfExp and other expressions
            self.visit(node.value)

        # Store the result in all target variables
        for target in node.targets:
            self.output.append(f'STA {target.id}')

    @debug_comment
    def visit_AugAssign(self, node):
        var_name = node.target.id

        # 16-bit augmented assignment on a uint16 variable
        if var_name in self.uint16_vars:
            if isinstance(node.op, (ast.Add, ast.Sub)):
                self._uint16_add_sub(var_name, node.op, node.value)
            elif isinstance(node.op, ast.Mult):
                fake = ast.BinOp(
                    left=ast.Name(id=var_name, ctx=ast.Load()),
                    op=node.op,
                    right=node.value,
                )
                self._uint16_mul(var_name, fake)
            else:
                raise NotImplementedError(
                    'Unsupported uint16 augmented assignment'
                )
            return

        # Handle complex expressions in the value
        if isinstance(node.value, (ast.BinOp, ast.Subscript, ast.Call)):
            # Visit the expression first (result lands in A)
            self.visit(node.value)
            # Store result in temp variable
            self.output.append('STA temp_var')
            var_value_str = 'temp_var'
        elif isinstance(node.value, ast.Constant):
            var_value = node.value.value
            var_value_str = f'#{var_value}'
        elif isinstance(node.value, ast.Name):
            var_value = None
            var_value_str = node.value.id
        else:
            raise NotImplementedError(
                'Unsupported value type in augmented assignment: '
                f'{type(node.value)}'
            )

        if isinstance(node.op, ast.Add):
            if isinstance(node.value, ast.Constant) and var_value == 1:
                # Use INC for += 1
                self.output.append(f'INC {var_name}')
            else:
                self.output.append(f'LDA {var_name}')
                self.output.append('CLC')
                self.output.append(f'ADC {var_value_str}')
                self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.Sub):
            if isinstance(node.value, ast.Constant) and var_value == 1:
                # Use DEC for -= 1
                self.output.append(f'DEC {var_name}')
            else:
                self.output.append(f'LDA {var_name}')
                self.output.append('SEC')
                self.output.append(f'SBC {var_value_str}')
                self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.BitAnd):
            # Handle augmented bitwise AND
            self.output.append(f'LDA {var_name}')
            self.output.append(f'AND {var_value_str}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.BitOr):
            # Handle augmented bitwise OR
            self.output.append(f'LDA {var_name}')
            self.output.append(f'ORA {var_value_str}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.BitXor):
            # Handle augmented bitwise XOR
            self.output.append(f'LDA {var_name}')
            self.output.append(f'EOR {var_value_str}')
            self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.LShift):
            # Handle augmented left shift
            if isinstance(node.value, ast.Constant):
                # For constant shifts, we can optimize by multiplying by 2^n
                shift_amount = var_value  # Use the shift amount directly
                self.output.append(f'LDA {var_name}')
                # Multiply by shift_amount using repeated ASL
                for _ in range(shift_amount):
                    self.output.append('ASL A')
                self.output.append(f'STA {var_name}')
            else:
                # For variable shifts, we need a loop
                self.output.append(f'LDA {var_name}')
                loop_label = f'shift_left_loop_{len(self.output)}'
                end_label = f'shift_left_end_{len(self.output)}'
                self.output.append(f'LDX {var_value_str}')
                self.output.append(f'BEQ {end_label}')
                self.output.append(f'{loop_label}:')
                self.output.append('ASL A')
                self.output.append('DEX')
                self.output.append(f'BNE {loop_label}')
                self.output.append(f'{end_label}:')
                self.output.append(f'STA {var_name}')
        elif isinstance(node.op, ast.RShift):
            # Handle augmented right shift
            if isinstance(node.value, ast.Constant):
                # For constant shifts, we can optimize by dividing by 2^n
                shift_amount = var_value  # Use the shift amount directly
                self.output.append(f'LDA {var_name}')
                # Divide by shift_amount using repeated LSR
                for _ in range(shift_amount):
                    self.output.append('LSR A')
                self.output.append(f'STA {var_name}')
            else:
                # For variable shifts, we need a loop
                self.output.append(f'LDA {var_name}')
                loop_label = f'shift_right_loop_{len(self.output)}'
                end_label = f'shift_right_end_{len(self.output)}'
                self.output.append(f'LDX {var_value_str}')
                self.output.append(f'BEQ {end_label}')
                self.output.append(f'{loop_label}:')
                self.output.append('LSR A')
                self.output.append('DEX')
                self.output.append(f'BNE {loop_label}')
                self.output.append(f'{end_label}:')
                self.output.append(f'STA {var_name}')

    def visit_BinOp(self, node):
        # Get the operands first
        left = node.left
        right = node.right

        # Handle shift operations
        if isinstance(node.op, ast.LShift):
            # Visit the left operand first
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_var')
            # Visit the right operand
            self.visit(right)
            # Store shift amount in X register
            self.output.append('TAX')
            # Load value to shift
            self.output.append('LDA temp_var')
            # Perform shift
            loop_label = f'shift_left_loop_{len(self.output)}'
            end_label = f'shift_left_end_{len(self.output)}'
            self.output.append(f'BEQ {end_label}')
            self.output.append(f'{loop_label}:')
            self.output.append('ASL A')
            self.output.append('DEX')
            self.output.append(f'BNE {loop_label}')
            self.output.append(f'{end_label}:')
        elif isinstance(node.op, ast.RShift):
            # Visit the left operand first
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_var')
            # Visit the right operand
            self.visit(right)
            # Store shift amount in X register
            self.output.append('TAX')
            # Load value to shift
            self.output.append('LDA temp_var')
            # Perform shift
            loop_label = f'shift_right_loop_{len(self.output)}'
            end_label = f'shift_right_end_{len(self.output)}'
            self.output.append(f'BEQ {end_label}')
            self.output.append(f'{loop_label}:')
            self.output.append('LSR A')
            self.output.append('DEX')
            self.output.append(f'BNE {loop_label}')
            self.output.append(f'{end_label}:')
        # Handle nested binary operations on the left side
        if isinstance(left, ast.BinOp):
            self.visit(left)
            # Store result in temp variable
            self.output.append('STA temp_left')
            left_value = 'temp_left'
        elif isinstance(left, ast.Name):
            left_value = left.id
        elif isinstance(left, ast.Constant):
            left_value = f'#{left.value}'
        else:
            raise NotImplementedError(
                f'Unsupported left operand type: {type(left)}'
            )

        # Handle nested binary operations on the right side
        if isinstance(right, ast.BinOp):
            self.visit(right)
            # Store result in temp variable
            self.output.append('STA temp_right')
            right_value = 'temp_right'
        elif isinstance(right, ast.Name):
            right_value = right.id
        elif isinstance(right, ast.Constant):
            right_value = f'#{right.value}'
        else:
            raise NotImplementedError(
                f'Unsupported right operand type: {type(right)}'
            )

        # Get parent context to find where to store the result
        parent = getattr(node, '_parent', None)
        target_var = None
        if isinstance(parent, ast.Assign) and isinstance(
            parent.targets[0], ast.Name
        ):
            target_var = parent.targets[0].id

        # Handle multiplication by repeated addition
        if isinstance(node.op, ast.Mult):
            mul_loop = self._generate_label()
            mul_end = self._generate_label()
            self.output.append(f'LDA {left_value}')
            self.output.append('STA temp_mul')
            self.output.append(f'LDX {right_value}')
            self.output.append('LDA #0')
            self.output.append(f'{mul_loop}:')
            self.output.append('CPX #0')
            self.output.append(f'BEQ {mul_end}')
            self.output.append('CLC')
            self.output.append('ADC temp_mul')
            self.output.append('DEX')
            self.output.append(f'JMP {mul_loop}')
            self.output.append(f'{mul_end}:')
            if target_var:
                self.output.append(f'STA {target_var}')
            return

        # Load left value and perform operation
        self.output.append(f'LDA {left_value}')

        if isinstance(node.op, ast.Add):
            self.output.append('CLC')
            self.output.append(f'ADC {right_value}')
        elif isinstance(node.op, ast.Sub):
            self.output.append('SEC')
            self.output.append(f'SBC {right_value}')
        elif isinstance(node.op, ast.BitAnd):
            self.output.append(f'AND {right_value}')
        elif isinstance(node.op, ast.BitOr):
            self.output.append(f'ORA {right_value}')
        elif isinstance(node.op, ast.BitXor):
            self.output.append(f'EOR {right_value}')
        elif isinstance(node.op, ast.LShift):
            self.output.append(f'LDA {left_value}')
            # For each shift count, we'll ASL (Arithmetic Shift Left)
            if isinstance(right, ast.Constant):
                for _ in range(right.value):
                    self.output.append('ASL A')
            else:
                self.output.append(f'LDX {right_value}')
                shift_loop = self._generate_label()
                self.output.append(f'{shift_loop}:')
                self.output.append('ASL A')
                self.output.append('DEX')
                self.output.append(f'BNE {shift_loop}')
        elif isinstance(node.op, ast.RShift):
            self.output.append(f'LDA {left_value}')
            # For each shift count, we'll LSR (Logical Shift Right)
            if isinstance(right, ast.Constant):
                for _ in range(right.value):
                    self.output.append('LSR A')
            else:
                self.output.append(f'LDX {right_value}')
                shift_loop = self._generate_label()
                self.output.append(f'{shift_loop}:')
                self.output.append('LSR A')
                self.output.append('DEX')
                self.output.append(f'BNE {shift_loop}')

        # Store the result if we're in an assignment context
        if target_var:
            self.output.append(f'STA {target_var}')

    def _branch_if_false(self, compare, false_label):
        """Emit a comparison and branch to false_label when it fails.

        Conditional branches only reach +-127 bytes, so they target a
        local trampoline that JMPs to the real (possibly far) label.
        """
        near = self._generate_label()
        cont = self._generate_label()
        self._emit_branch_false(compare, near)
        self.output.append(f'JMP {cont}')
        self.output.append(f'{near}:')
        self.output.append(f'JMP {false_label}')
        self.output.append(f'{cont}:')

    def _emit_branch_false(self, compare, false_label):
        if isinstance(compare, ast.Name):
            # Truthiness: a bare variable is true when it is not zero
            self.output.append(f'LDA {compare.id}')
            self.output.append(f'BEQ {false_label}')
            return
        if not isinstance(compare, ast.Compare):
            # Truthiness of an expression (e.g. if pad & PAD_RIGHT:)
            self._eval_to_a(compare)
            self.output.append('CMP #0')
            self.output.append(f'BEQ {false_label}')
            return
        if len(compare.ops) != 1:
            raise NotImplementedError('Unsupported condition')
        self.visit(compare)
        op = compare.ops[0]
        if isinstance(op, ast.Eq):
            self.output.append(f'BNE {false_label}')
        elif isinstance(op, ast.NotEq):
            self.output.append(f'BEQ {false_label}')
        elif isinstance(op, ast.Lt):
            self.output.append(f'BCS {false_label}')
        elif isinstance(op, ast.Gt):
            self.output.append(f'BCC {false_label}')
            self.output.append(f'BEQ {false_label}')
        elif isinstance(op, ast.GtE):
            self.output.append(f'BCC {false_label}')
        elif isinstance(op, ast.LtE):
            true_label = self._generate_label()
            self.output.append(f'BEQ {true_label}')
            self.output.append(f'BCS {false_label}')
            self.output.append(f'{true_label}:')
        else:
            raise NotImplementedError(
                f'Operator not supported {type(op).__name__}'
            )

    def _branch_if_true(self, compare, true_label):
        """Emit a comparison and branch to true_label when it succeeds.

        Uses the same trampoline as _branch_if_false to support far
        targets.
        """
        near = self._generate_label()
        cont = self._generate_label()
        self._emit_branch_true(compare, near)
        self.output.append(f'JMP {cont}')
        self.output.append(f'{near}:')
        self.output.append(f'JMP {true_label}')
        self.output.append(f'{cont}:')

    def _emit_branch_true(self, compare, true_label):
        if isinstance(compare, ast.Name):
            # Truthiness: a bare variable is true when it is not zero
            self.output.append(f'LDA {compare.id}')
            self.output.append(f'BNE {true_label}')
            return
        if not isinstance(compare, ast.Compare):
            # Truthiness of an expression (e.g. if pad & PAD_RIGHT:)
            self._eval_to_a(compare)
            self.output.append('CMP #0')
            self.output.append(f'BNE {true_label}')
            return
        if len(compare.ops) != 1:
            raise NotImplementedError('Unsupported condition')
        self.visit(compare)
        op = compare.ops[0]
        if isinstance(op, ast.Eq):
            self.output.append(f'BEQ {true_label}')
        elif isinstance(op, ast.NotEq):
            self.output.append(f'BNE {true_label}')
        elif isinstance(op, ast.Lt):
            self.output.append(f'BCC {true_label}')
        elif isinstance(op, ast.Gt):
            skip_label = self._generate_label()
            self.output.append(f'BEQ {skip_label}')
            self.output.append(f'BCS {true_label}')
            self.output.append(f'{skip_label}:')
        elif isinstance(op, ast.GtE):
            self.output.append(f'BCS {true_label}')
        elif isinstance(op, ast.LtE):
            self.output.append(f'BCC {true_label}')
            self.output.append(f'BEQ {true_label}')
        else:
            raise NotImplementedError(
                f'Operator not supported {type(op).__name__}'
            )

    def _test_branch_false(self, test, false_label):
        """Emit a condition (Compare, BoolOp or not-Compare) branching to
        false_label when it fails; otherwise execution falls through."""
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            # 'not X' fails exactly when X succeeds
            self._branch_if_true(test.operand, false_label)
            return
        if isinstance(test, ast.BoolOp):
            if isinstance(test.op, ast.And):
                # For AND, every condition must hold; any failure goes
                # false
                for value in test.values:
                    self._branch_if_false(value, false_label)
            elif isinstance(test.op, ast.Or):
                # For OR, any condition holding goes true; only the last
                # condition failing goes false
                true_label = self._generate_label()
                for value in test.values[:-1]:
                    self._branch_if_true(value, true_label)
                self._branch_if_false(test.values[-1], false_label)
                self.output.append(f'{true_label}:')
            else:
                raise NotImplementedError(
                    'Only AND/OR operators are supported'
                )
        else:
            self._branch_if_false(test, false_label)

    @debug_comment
    def visit_BoolOp(self, node):
        """Handle boolean operations like AND/OR"""
        false_label = self._generate_label()
        self._test_branch_false(node, false_label)
        return false_label

    @debug_comment
    def visit_If(self, node):
        self.comment(node.test)
        false_label = self._generate_label()
        end_label = self._generate_label()

        # Handle constant conditions (if True / if False) at compile time
        if isinstance(node.test, ast.Constant):
            branch = node.body if node.test.value else node.orelse
            for stmt in branch:
                self.comment(stmt)
                self.visit(stmt)
            return

        # Handle boolean operations (AND/OR)
        if isinstance(node.test, ast.BoolOp):
            false_label = self.visit(node.test)
            # Execute true block if all conditions passed
            for stmt in node.body:
                self.comment(stmt)
                self.visit(stmt)
            self.output.append(f'JMP {end_label}')
            # Handle false case
            self.output.append(f'{false_label}:')
            for stmt in node.orelse:
                self.comment(stmt)
                self.visit(stmt)
            self.output.append(f'{end_label}:')
            self.output.append('NOP')
            return

        # Handle simple comparisons (including 'not')
        self._test_branch_false(node.test, false_label)

        # Handle true block (fall-through case)
        for stmt in node.body:
            self.comment(stmt)
            self.visit(stmt)

        # Handle else block
        if node.orelse:
            self.output.append(f'JMP {end_label}')
            self.output.append(f'{false_label}:')
            for stmt in node.orelse:
                self.comment(stmt)
                self.visit(stmt)
            self.output.append(f'{end_label}:')
            self.output.append('NOP')
        else:
            self.output.append(f'{false_label}:')
            self.output.append('NOP')

    def visit_While(self, node):
        # Generate code for while loop
        start_label = self._generate_label()
        end_label = self._generate_label()

        # Start of loop body
        self.output.append(f'{start_label}:')

        # Check condition
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            # while True - no condition check needed
            pass
        elif isinstance(
            node.test, (ast.Compare, ast.BoolOp, ast.UnaryOp, ast.Name)
        ):
            self._test_branch_false(node.test, end_label)
        else:
            raise NotImplementedError(
                'Only comparisons, AND/OR/NOT, variables and True '
                'constant supported in while'
            )

        # Loop body
        self.loop_end_labels.append(end_label)
        self.loop_continue_labels.append(start_label)
        for stmt in node.body:
            self.visit(stmt)
        self.loop_end_labels.pop()
        self.loop_continue_labels.pop()

        # Jump back to start to check condition again
        self.output.append(f'JMP {start_label}')

        # End of loop
        self.output.append(f'{end_label}:')
        self.output.append('NOP')  # No-op instead of BRK

    @debug_comment
    def visit_For(self, node):
        if isinstance(node.iter, ast.Call) and isinstance(
            node.iter.func, ast.Name
        ):
            name = node.iter.func.id
            # python builtins with a 6502 counterpart (range,
            # enumerate, ...) live in a registry
            builtin = self.builtin_iters.get(name)
            if builtin is not None:
                builtin(node)
                return
            # 'for <name> in <task>(...)' drives a generator task to
            # completion, one iteration per yield
            if name in self.generator_funcs:
                self._for_over_generator(node)
                return
        # Only 'for <name> in range(...)' is supported
        self._for_over_range(node)

    def _for_over_enumerate(self, node):
        """for index, value in enumerate(task(...), start): the index
        counts iterations from start, the value comes from the
        yields."""
        if not (
            isinstance(node.target, ast.Tuple)
            and len(node.target.elts) == 2
            and all(isinstance(e, ast.Name) for e in node.target.elts)
        ):
            raise NotImplementedError(
                'enumerate unpacks (index, value) loop variables'
            )
        index_target, value_target = node.target.elts
        args = node.iter.args
        inner = args[0] if args else None
        if not (
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Name)
            and inner.func.id in self.generator_funcs
        ):
            raise NotImplementedError(
                'enumerate() supports generator tasks only'
            )
        start = args[1] if len(args) > 1 else ast.Constant(value=0)
        self._eval_to_a(start)
        self.output.append(f'STA {index_target.id}')
        self._generator_loop(node, inner, value_target.id, index_target.id)

    def _for_over_generator(self, node):
        """Drive a generator task to completion: each yield delivers
        its value to the loop variable and runs the body once."""
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                'Only simple loop variables are supported'
            )
        self._generator_loop(node, node.iter, node.target.id)

    def _generator_loop(self, node, call, value_name, index_name=None):
        if node.orelse:
            raise NotImplementedError('for/else is not supported')
        name = call.func.id
        params = self.functions.get(name, [])
        loop_label = self._generate_label()
        body_label = self._generate_label()
        end_label = self._generate_label()
        # calling a generator creates a fresh one with its arguments
        # bound once, exactly like Python
        self.output.append('LDA #0')
        self.output.append(f'STA {name}__state')
        for arg, param in zip(call.args, params):
            self._eval_to_a(arg)
            self.output.append(f'STA {param}')
        self.output.append(f'{loop_label}:')
        self.output.append(f'JSR {name}')
        self.output.append('CMP #0')
        self.output.append(f'BNE {body_label}')
        self.output.append(f'JMP {end_label}')
        self.output.append(f'{body_label}:')
        self.output.append('LDA yield_value')
        self.output.append(f'STA {value_name}')
        for stmt in node.body:
            self.visit(stmt)
        if index_name is not None:
            self.output.append(f'INC {index_name}')
        self.output.append(f'JMP {loop_label}')
        self.output.append(f'{end_label}:')
        # Python leaves the index at the last iterated value
        if index_name is not None:
            self.output.append(f'DEC {index_name}')

    def _for_over_range(self, node):
        if (
            not isinstance(node.iter, ast.Call)
            or not isinstance(node.iter.func, ast.Name)
            or node.iter.func.id != 'range'
        ):
            raise NotImplementedError('Only range() iteration is supported')
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                'Only simple loop variables are supported'
            )
        if node.orelse:
            raise NotImplementedError('for/else is not supported')

        args = node.iter.args
        if len(args) == 1:
            start, stop, step = None, args[0], None
        elif len(args) == 2:
            start, stop, step = args[0], args[1], None
        elif len(args) == 3:
            start, stop, step = args[0], args[1], args[2]
        else:
            raise NotImplementedError('range() requires 1 to 3 arguments')

        var_name = node.target.id
        start_label = self._generate_label()
        continue_label = self._generate_label()
        exit_label = self._generate_label()
        end_label = self._generate_label()

        # Initialize loop variable
        if start is None:
            self.output.append('LDA #0')
        elif isinstance(start, ast.Constant):
            self.output.append(f'LDA #{start.value}')
        elif isinstance(start, ast.Name):
            self.output.append(f'LDA {start.id}')
        else:
            raise NotImplementedError('Unsupported range() start')
        self.output.append(f'STA {var_name}')

        # Loop condition: exit when loop variable >= stop
        self.output.append(f'{start_label}:')
        self.output.append(f'LDA {var_name}')
        if isinstance(stop, ast.Constant):
            self.output.append(f'CMP #{stop.value}')
        elif isinstance(stop, ast.Name):
            self.output.append(f'CMP {stop.id}')
        else:
            raise NotImplementedError('Unsupported range() stop')
        # trampoline: the loop body may exceed branch range
        loop_body = self._generate_label()
        self.output.append(f'BCC {loop_body}')
        self.output.append(f'JMP {exit_label}')
        self.output.append(f'{loop_body}:')

        # Loop body
        self.loop_end_labels.append(end_label)
        self.loop_continue_labels.append(continue_label)
        for stmt in node.body:
            self.visit(stmt)
        self.loop_end_labels.pop()
        self.loop_continue_labels.pop()

        # Increment loop variable by step
        self.output.append(f'{continue_label}:')
        if step is None:
            self.output.append(f'INC {var_name}')
        elif isinstance(step, ast.Constant):
            if step.value <= 0:
                raise NotImplementedError(
                    'Only positive range() steps are supported'
                )
            if step.value == 1:
                self.output.append(f'INC {var_name}')
            else:
                self.output.append(f'LDA {var_name}')
                self.output.append('CLC')
                self.output.append(f'ADC #{step.value}')
                self.output.append(f'STA {var_name}')
        elif isinstance(step, ast.Name):
            self.output.append(f'LDA {var_name}')
            self.output.append('CLC')
            self.output.append(f'ADC {step.id}')
            self.output.append(f'STA {var_name}')
        else:
            raise NotImplementedError('Unsupported range() step')
        self.output.append(f'JMP {start_label}')

        # Normal exit: Python leaves the loop variable at the last
        # iterated value, so rewind the final increment. A break
        # jumps straight to end_label, keeping the variable as is.
        self.output.append(f'{exit_label}:')
        if step is None or (
            isinstance(step, ast.Constant) and step.value == 1
        ):
            self.output.append(f'DEC {var_name}')
        elif isinstance(step, ast.Constant):
            self.output.append(f'LDA {var_name}')
            self.output.append('SEC')
            self.output.append(f'SBC #{step.value}')
            self.output.append(f'STA {var_name}')
        else:
            self.output.append(f'LDA {var_name}')
            self.output.append('SEC')
            self.output.append(f'SBC {step.id}')
            self.output.append(f'STA {var_name}')

        # End of loop
        self.output.append(f'{end_label}:')
        self.output.append('NOP')

    def visit_Break(self, node):
        if self.loop_end_labels:
            self.output.append(f'JMP {self.loop_end_labels[-1]}')
        else:
            raise NotImplementedError('No loop to break')

    def visit_Continue(self, node):
        if self.loop_continue_labels:
            self.output.append(f'JMP {self.loop_continue_labels[-1]}')
        else:
            raise NotImplementedError('No loop to continue')

    def visit_IfExp(self, node):
        """Handle ternary operators like: x = 2 if y == 1 else 3"""
        end_label = self._generate_label()
        false_label = self._generate_label()

        # Visit the test condition
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            ops = node.test.ops
            comparators = node.test.comparators

            if len(ops) == 1 and len(comparators) == 1:
                comparator = comparators[0]
                op = ops[0]

                # Load left value
                if isinstance(left, ast.Name):
                    self.output.append(f'LDA {left.id}')
                elif isinstance(left, ast.Constant):
                    self.output.append(f'LDA #{left.value}')

                # Compare with right value
                if isinstance(comparator, ast.Constant):
                    self.output.append(f'CMP #{comparator.value}')
                elif isinstance(comparator, ast.Name):
                    self.output.append(f'CMP {comparator.id}')

                # Branch based on comparison
                if isinstance(op, ast.Eq):
                    self.output.append(f'BEQ {false_label}')
                elif isinstance(op, ast.NotEq):
                    self.output.append(f'BNE {false_label}')
                elif isinstance(op, ast.Lt):
                    self.output.append(f'BCC {false_label}')
                elif isinstance(op, ast.Gt):
                    self.output.append(f'BCS {false_label}')
                elif isinstance(op, ast.GtE):
                    self.output.append(f'BCC {false_label}')
                elif isinstance(op, ast.LtE):
                    self.output.append(f'BCS {false_label}')

        # False case (condition not met)
        if isinstance(node.orelse, ast.Constant):
            self.output.append(f'LDA #{node.orelse.value}')
        elif isinstance(node.orelse, ast.Name):
            self.output.append(f'LDA {node.orelse.id}')
        self.output.append(f'JMP {end_label}')

        # True case (condition met)
        self.output.append(f'{false_label}:')
        if isinstance(node.body, ast.Constant):
            self.output.append(f'LDA #{node.body.value}')
        elif isinstance(node.body, ast.Name):
            self.output.append(f'LDA {node.body.id}')

        # End of if expression
        self.output.append(f'{end_label}:')

    def _generate_label(self):
        label = f'label_{self.label_count}'
        self.label_count += 1
        return label
