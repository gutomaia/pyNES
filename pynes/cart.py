import ast
import copy

from nesasm.compiler import Cartridge, lexical, semantic, syntax
from neslib.library import lib

from pynes.translator import (
    TEMP_VARS,
    PythonTo6502,
    ScopeMangler,
    VarTable,
    _Renamer,
    annotate_uint16_returns,
    has_yield,
)
from pynes.builtins import pynes_lib
from pynes.chr import TILE_SIZE, encode_stage, encode_tile
from pynes.types import CHR_TYPES, RAM_TYPES, ROM_TYPES

ENTRY_POINTS = ('reset', 'nmi', 'irq')

RESET_PREAMBLE = [
    'SEI',
    'CLD',
    'LDX #$FF',
    'TXS',
    'INX',
    'STX $2000',
    'STX $2001',
    'vblank_wait_1:',
    'BIT $2002',
    'BPL vblank_wait_1',
    'vblank_wait_2:',
    'BIT $2002',
    'BPL vblank_wait_2',
]


def _fold_str(node):
    """Evaluate a constant string expression: literals plus '+' and
    '*' (so stage rows can be written as e.g. '.' * 128)."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _fold_str(node.left) + _fold_str(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _fold_str(node.left) * _fold_str(node.right)
    raise NotImplementedError('Stage rows must be constant string expressions')


class _ConstSubstituter(ast.NodeTransformer):
    """Replaces names of compile-time constants (e.g. tile indexes)
    with their literal values."""

    def __init__(self, constants):
        self.constants = constants

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.constants:
            return ast.copy_location(
                ast.Constant(value=self.constants[node.id]), node
            )
        return node


class CartVarTable(VarTable):
    """Variable collector that ignores called function names."""

    def visit_Call(self, node):
        for arg in node.args:
            self.visit(arg)


class _CallSpecializer(ast.NodeTransformer):
    """Rewrites calls that pass arrays to user functions.

    nesasm has no label arithmetic, so runtime array pointers are
    impossible: instead every call site binds its arrays at compile
    time, targeting a specialized copy of the function.
    """

    def __init__(self, functions, array_names):
        self.functions = {f.name: f for f in functions}
        self.array_names = array_names
        self.requests = {}  # specialized name -> (function, {param: array})
        self.plain_called = set()

    def visit_Call(self, node):
        self.generic_visit(node)
        if not isinstance(node.func, ast.Name):
            return node
        function = self.functions.get(node.func.id)
        if function is None:
            return node
        params = [arg.arg for arg in function.args.args]
        array_args = {}
        scalar_args = []
        for param, arg in zip(params, node.args):
            if isinstance(arg, ast.Name) and arg.id in self.array_names:
                array_args[param] = arg.id
            else:
                scalar_args.append(arg)
        if not array_args:
            self.plain_called.add(function.name)
            return node
        specialized = function.name + ''.join(
            f'__{name}' for name in array_args.values()
        )
        self.requests[specialized] = (function, array_args)
        node.func.id = specialized
        node.args = scalar_args
        return node


class Cart:
    """NES cartridge builder: turns a Python module with entry point
    decorators (@reset, @nmi, @irq) into a complete nesasm source,
    linking the runtime of the given libraries."""

    def __init__(
        self,
        libraries=None,
        prg_banks=1,
        chr_banks=0,
        mapper=0,
        mirroring=1,
        org=0xC000,
        chr_data=None,
    ):
        if libraries is None:
            libraries = [lib, pynes_lib]
        else:
            libraries = list(libraries) + [pynes_lib]
        self.libraries = libraries
        self.prg_banks = prg_banks
        self.chr_banks = chr_banks
        self.mapper = mapper
        self.mirroring = mirroring
        self.org = org
        self.chr_data = chr_data

    def _entry_name(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in (
                ENTRY_POINTS
            ):
                return decorator.id
        return None

    def _collect_entries(self, tree):
        entries = {}
        declarations = []
        functions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                # every function follows Python scoping: assignments
                # are locals unless declared global
                node = ScopeMangler().visit(node)
                entry = self._entry_name(node)
                if entry is None:
                    functions.append(node)
                else:
                    entries[entry] = node
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                declarations.append(node)
            else:
                raise NotImplementedError(
                    'Unsupported top-level statement: '
                    f'{type(node).__name__}'
                )
        if 'reset' not in entries:
            raise ValueError('Missing @reset entry point')
        return entries, declarations, functions

    def _collect_declarations(self, declarations):
        """Classify module-level declarations into RAM variables,
        RAM initial values and ROM data."""
        ram_vars = {}
        ram_init = {}
        rom_data = {}
        chr_tiles = {}
        stages = {}
        for node in declarations:
            if isinstance(node, ast.AnnAssign):
                # typed declaration: score: uint16 = 40320
                if not isinstance(node.target, ast.Name) or not isinstance(
                    node.annotation, ast.Name
                ):
                    raise NotImplementedError(
                        'Only simple annotated declarations are supported'
                    )
                type_name = node.annotation.id
                if type_name not in RAM_TYPES:
                    raise NotImplementedError(
                        f'Unsupported annotation: {type_name!r}'
                    )
                name = node.target.id
                ram_vars[name] = RAM_TYPES[type_name]
                if node.value is not None:
                    if not isinstance(node.value, ast.Constant):
                        raise NotImplementedError(
                            'Annotated declarations require constant '
                            'initial values'
                        )
                    ram_init[name] = node.value.value
                continue
            if len(node.targets) != 1 or not isinstance(
                node.targets[0], ast.Name
            ):
                raise NotImplementedError(
                    'Only simple top-level declarations are supported'
                )
            name = node.targets[0].id
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(
                value.value, int
            ):
                ram_vars[name] = 1
                ram_init[name] = value.value
            elif isinstance(value, ast.List):
                # module-level array: RAM allocation plus initial
                # values written at RESET
                if not all(
                    isinstance(elt, ast.Constant) for elt in value.elts
                ):
                    raise NotImplementedError(
                        'Only constant array declarations are supported'
                    )
                ram_vars[name] = len(value.elts)
                ram_init[name] = [elt.value for elt in value.elts]
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in RAM_TYPES
            ):
                ram_vars[name] = RAM_TYPES[value.func.id]
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in CHR_TYPES
            ):
                arg = value.args[0]
                chr_tiles[name] = [elt.value for elt in arg.elts]
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id == 'stage'
            ):
                rows = [_fold_str(elt) for elt in value.args[0].elts]
                legend = {
                    key.value: tile_name.id
                    for key, tile_name in zip(
                        value.args[1].keys, value.args[1].values
                    )
                }
                stages[name] = (rows, legend)
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in ROM_TYPES
            ):
                arg = value.args[0]
                if value.func.id == 'string':
                    rom_data[name] = [ord(c) for c in arg.value] + [0]
                else:  # rom
                    rom_data[name] = [elt.value for elt in arg.elts]
            else:
                raise NotImplementedError(
                    f'Unsupported top-level declaration: {name!r}'
                )
        return ram_vars, ram_init, rom_data, chr_tiles, stages

    def _make_translator(self, functions):
        # builtins are always available, but resolve after user defs
        # and explicitly imported externs
        translator = PythonTo6502(
            libraries=self.libraries, builtins=pynes_lib.externs
        )
        for function in functions:
            translator.functions[function.name] = [
                arg.arg for arg in function.args.args
            ]
        return translator

    @staticmethod
    def _set_parents(node):
        for stmt in ast.walk(node):
            for child in ast.iter_child_nodes(stmt):
                setattr(child, '_parent', stmt)

    def _translate_body(self, translator, node):
        self._set_parents(node)
        start = len(translator.output)
        for stmt in node.body:
            translator.visit(stmt)
        return translator.output[start:]

    def _translate_functions(self, translator, functions):
        start = len(translator.output)
        for function in functions:
            self._set_parents(function)
            translator.visit_FunctionDef(function)
        return translator.output[start:]

    @staticmethod
    def _find_arrays(entries, functions, ram_vars, ram_init, rom_data):
        """Names bound to arrays: ROM data, module-level array
        declarations, and every list literal assigned in an entry
        point or function."""
        names = set(rom_data)
        names.update(n for n, size in ram_vars.items() if size > 2)
        names.update(
            n for n, value in ram_init.items() if isinstance(value, list)
        )
        for node in list(entries.values()) + list(functions):
            for stmt in ast.walk(node):
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.value, ast.List)
                    and isinstance(stmt.targets[0], ast.Name)
                ):
                    names.add(stmt.targets[0].id)
        return names

    def _specialize_functions(self, entries, functions, array_names):
        """Bind array arguments at compile time: each call passing an
        array targets a specialized copy of the function with the
        parameter replaced by the array itself. Locals (and generator
        state) are renamed so every specialization stays isolated."""
        specializer = _CallSpecializer(functions, array_names)
        for node in list(entries.values()) + list(functions):
            specializer.visit(node)
        if not specializer.requests:
            return functions, set()
        # function names still referenced directly (plain calls, or
        # task names passed to step()/reset_task()) keep the original
        referenced = set(specializer.plain_called)
        function_names = {f.name for f in functions}
        for node in list(entries.values()) + list(functions):
            for n in ast.walk(node):
                if isinstance(n, ast.Name) and n.id in function_names:
                    referenced.add(n.id)
        specialized_names = {
            function.name for function, _ in specializer.requests.values()
        }
        kept = [
            function
            for function in functions
            if function.name in referenced
            or function.name not in specialized_names
        ]
        removed = function_names - {function.name for function in kept}
        specialized = [
            self._specialize(function, name, array_args)
            for name, (function, array_args) in specializer.requests.items()
        ]
        return kept + specialized, removed

    @staticmethod
    def _specialize(function, specialized, array_args):
        new = copy.deepcopy(function)
        prefix = f'{function.name}_'
        mapping = dict(array_args)
        for n in ast.walk(new):
            if (
                isinstance(n, ast.Name)
                and n.id.startswith(prefix)
                and n.id not in mapping
            ):
                mapping[n.id] = f'{specialized}_{n.id[len(prefix):]}'
        new.name = specialized
        new.args.args = [
            arg for arg in new.args.args if arg.arg not in array_args
        ]
        for arg in new.args.args:
            if arg.arg.startswith(prefix) and arg.arg not in mapping:
                mapping[arg.arg] = f'{specialized}_{arg.arg[len(prefix):]}'
            arg.arg = mapping.get(arg.arg, arg.arg)
        _Renamer(mapping).visit(new)
        return new

    @staticmethod
    def _runtime_routines(library):
        """Split the library runtime into named routines: blocks are
        separated by blank lines and named by their first label. Every
        label lives in the library's namespace (neslib__put_str)."""
        routines = {}
        for asm in library.runtime_asm:
            asm = library.namespaced(asm)
            block = []
            for line in asm.splitlines() + ['']:
                if line.strip():
                    block.append(line)
                elif block:
                    name = block[0].split(':')[0].strip()
                    routines[name] = block
                    block = []
        return routines

    @staticmethod
    def _called_labels(lines):
        labels = set()
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[0] in ('JSR', 'JMP'):
                labels.add(parts[1])
        return labels

    def _used_routines(self, program, routines):
        """Cartridge space is precious: only the routines transitively
        reachable from the program get bundled. A label the program
        already defines (a user function shadowing the library, as in
        Python scoping) is never bundled twice."""
        defined = {
            line.strip()[:-1] for line in program if line.strip().endswith(':')
        }
        needed = self._called_labels(program) & set(routines) - defined
        pending = list(needed)
        while pending:
            for callee in (
                self._called_labels(routines[pending.pop()])
                & set(routines) - defined
            ):
                if callee not in needed:
                    needed.add(callee)
                    pending.append(callee)
        return needed

    @staticmethod
    def _annotate_uint16_returns(functions):
        """uint16 returns are a compiler concern: delegate to the
        translator-level helper."""
        return annotate_uint16_returns(functions)

    def _collect_vars(self, entries, functions=(), extra_labels=()):
        vartable = CartVarTable()
        for node in list(entries.values()) + list(functions):
            for stmt in node.body:
                vartable.visit(stmt)
        for function in functions:
            # generator tasks keep their resume point in a state byte
            if has_yield(function):
                vartable.get_var(f'{function.name}__state').assigns += 1
            # parameters are assigned by the caller
            for arg in function.args.args:
                vartable.get_var(arg.arg).assigns += 1
            # function names are labels, not variables
            vartable.vars.pop(function.name, None)
        for label in extra_labels:
            vartable.vars.pop(label, None)
        for temp in TEMP_VARS:
            vartable.get_var(temp)
        address = 0x00
        for var in vartable.vars.values():
            var.address = address
            address += var.size
        return vartable.vars

    def _place_tiles(self, chr_tiles):
        """Assign CHR indexes (from 1: tile 0 stays blank) and encode
        the tiles into a copy of the CHR bank."""
        tile_indexes = {name: 1 + i for i, name in enumerate(chr_tiles)}
        chr_data = bytearray(self.chr_data or b'')
        for name, art in chr_tiles.items():
            offset = tile_indexes[name] * TILE_SIZE
            chr_data[offset : offset + TILE_SIZE] = encode_tile(art)
        return tile_indexes, bytes(chr_data)

    def compile(self, source):
        tree = ast.parse(source)
        entries, declarations, functions = self._collect_entries(tree)
        (
            ram_vars,
            ram_init,
            rom_data,
            chr_tiles,
            stages,
        ) = self._collect_declarations(declarations)
        tile_indexes, chr_data = self._place_tiles(chr_tiles)
        for name, (rows, legend) in stages.items():
            legend_indexes = {
                char: tile_indexes[tile_name]
                for char, tile_name in legend.items()
            }
            rom_data[name] = list(encode_stage(rows, legend_indexes))
        constants = {}
        for library in self.libraries:
            constants.update(library.constants)
        constants.update(tile_indexes)
        if constants:
            substituter = _ConstSubstituter(constants)
            for node in list(entries.values()) + functions:
                substituter.visit(node)
        array_names = self._find_arrays(
            entries, functions, ram_vars, ram_init, rom_data
        )
        functions, removed_functions = self._specialize_functions(
            entries, functions, array_names
        )
        uint16_funcs = self._annotate_uint16_returns(functions)
        variables = self._collect_vars(entries, functions, removed_functions)
        defined = set(ram_vars) | set(rom_data) | set(TEMP_VARS)
        for name, var in variables.items():
            if (
                var.assigns == 0
                and name not in defined
                and not name.startswith('mem_')
            ):
                raise NameError(f'name {name!r} is not defined')
        translator = self._make_translator(functions)
        translator.bind_imports(tree)
        translator.uint16_vars = {
            name for name, size in ram_vars.items() if size == 2
        }
        translator.generator_funcs = {
            function.name for function in functions if has_yield(function)
        }
        translator.uint16_funcs = uint16_funcs

        out = []
        out.append('; Generated by pyNES')
        out.append(f'.inesprg {self.prg_banks}')
        out.append(f'.ineschr {self.chr_banks}')
        out.append(f'.inesmap {self.mapper}')
        out.append(f'.inesmir {self.mirroring}')
        out.append('')

        library_ram = {}
        for library in self.libraries:
            library_ram.update(getattr(library, 'ram', {}))

        if variables or ram_vars or library_ram:
            out.append('.rsset $0000')
            for name, size in library_ram.items():
                out.append(f'{name} .rs {size}')
            for name, size in ram_vars.items():
                if size == 2 and not isinstance(ram_init.get(name), list):
                    # uint16: two adjacent labels, no label arithmetic
                    # in nesasm so the hi byte needs its own name
                    out.append(f'{name} .rs 1')
                    out.append(f'{name}__hi .rs 1')
                else:
                    out.append(f'{name} .rs {size}')
            allocated = set(library_ram) | set(ram_vars) | set(rom_data)
            for var in variables.values():
                if var.label not in allocated:
                    out.append(f'{var.label} .rs {var.size}')
            out.append('')

        out.append('.bank 0')
        out.append(f'.org ${self.org:04X}')
        out.append('')

        out.append('RESET:')
        out.extend(RESET_PREAMBLE)
        generator_states = [
            f'{function.name}__state'
            for function in functions
            if has_yield(function)
        ]
        if generator_states:
            # generator tasks start fresh (RAM is garbage on boot)
            out.append('LDA #0')
            for state in generator_states:
                out.append(f'STA {state}')
        for name, value in ram_init.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    out.append(f'LDA #{item}')
                    out.append(f'LDX #{i}')
                    out.append(f'STA {name},X')
            elif ram_vars.get(name) == 2:
                out.append(f'LDA #{value & 0xFF}')
                out.append(f'STA {name}')
                out.append(f'LDA #{(value >> 8) & 0xFF}')
                out.append(f'STA {name}__hi')
            else:
                out.append(f'LDA #{value}')
                out.append(f'STA {name}')
        out.extend(self._translate_body(translator, entries['reset']))
        out.append('forever:')
        out.append('JMP forever')
        out.append('')

        out.append('NMI:')
        if 'nmi' in entries:
            out.extend(self._translate_body(translator, entries['nmi']))
        out.append('RTI')
        out.append('')

        out.append('IRQ:')
        if 'irq' in entries:
            out.extend(self._translate_body(translator, entries['irq']))
        out.append('RTI')
        out.append('')

        if functions:
            out.append('; functions')
            out.extend(self._translate_functions(translator, functions))
            out.append('')

        for library in self.libraries:
            routines = self._runtime_routines(library)
            needed = self._used_routines(out, routines)
            if not needed:
                continue
            out.append(f'; runtime: {library.name}')
            for name, block in routines.items():
                if name in needed:
                    out.extend(block)
                    out.append('')

        if rom_data:
            out.append('; data')
            for name, data in rom_data.items():
                out.append(f'{name}:')
                for i in range(0, len(data), 16):
                    chunk = data[i : i + 16]
                    out.append(
                        '.db ' + ', '.join(f'${byte:02X}' for byte in chunk)
                    )
            out.append('')

        out.append(f'.bank {self.prg_banks * 2 - 1}')
        out.append('.org $E000')
        out.append('.org $FFFA')
        out.append('.dw NMI')
        out.append('.dw RESET')
        out.append('.dw IRQ')
        out.append('')

        if self.chr_banks and chr_data:
            out.append(f'.bank {self.prg_banks * 2}')
            out.append('.org $0000')
            for i in range(0, len(chr_data), 16):
                chunk = chr_data[i : i + 16]
                out.append(
                    '.db ' + ', '.join(f'${byte:02X}' for byte in chunk)
                )
            out.append('')

        return '\n'.join(out)

    def to_nes(self, source):
        """Compile Python source all the way to iNES ROM bytes."""
        asm = self.compile(source)
        cartridge = Cartridge()
        tokens = lexical(asm)
        tree = syntax(tokens)
        semantic(tree, True, cartridge)
        return bytes(bytearray(cartridge.get_ines_code()))
