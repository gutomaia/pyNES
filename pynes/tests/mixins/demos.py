import os
import importlib
from functools import lru_cache

from pynes.tests.nes_runner import NESRunner
from pynes.tests.unit.fceux_runner import FCEUXRunner
from pynes.tests.factorial_demo_spec import (
    FactorialOneLineSpec,
    FactorialMultilineSpec,
)


DEMOS_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        '..',
        '..',
        'demos',
    )
)
PROJECT_ROOT = os.path.dirname(DEMOS_DIR)


def get_demo_filename(demo):
    """Resolve a demo by name across the category subfolders
    (hello/, math/, sorters/, graphics/, ...)."""
    name = os.path.basename(demo)
    for root, _, files in sorted(os.walk(DEMOS_DIR)):
        if name in files:
            return os.path.join(root, name)
    raise FileNotFoundError(f'demo {demo!r} not found under {DEMOS_DIR}')


@lru_cache(maxsize=None)
def get_runner(demo):
    with open(get_demo_filename(demo)) as f:
        runner = NESRunner(f.read())
    return runner


def load_runner(demo):
    runner = get_runner(demo)
    runner.run_reset()
    return runner


def load_fceux_runner(demo):
    with open(get_demo_filename(demo)) as f:
        runner = FCEUXRunner(f.read())
    return runner


def text(runner, x, y, length):
    base = 0x2000 + y * 32 + x
    return bytes(runner.ppu.vram[base : base + length])


class AbstractFactorialBase:

    def get_demo_filename(self):
        return self.demo_filename

    def get_demo_module(self):
        path = get_demo_filename(self.get_demo_filename())
        relative = os.path.relpath(path, PROJECT_ROOT)
        return relative[: -len('.py')].replace(os.sep, '.')

    def get_demo_attribute(self, attr_name):
        module_path = self.get_demo_module()
        try:
            module = importlib.import_module(module_path)
            attr = getattr(module, attr_name)
            return attr
        except ModuleNotFoundError:
            print(f"Error: The module '{module_path}' could not be found.")
            raise
        except AttributeError:
            print(
                f"Error: The attribute '{attr_name}' "
                f"does not exist in '{module_path}'."
            )
            raise

    def get_factorial_function(self):
        return self.get_demo_attribute('factorial')

    def get_factorial_result(self):
        func = self.get_factorial_function()
        return func(self.get_factorial_factor())


class AbstractFactorialOneLine(AbstractFactorialBase, FactorialOneLineSpec):
    demo_filename = None

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner(cls.demo_filename)

    def get_factorial_factor(self):
        try:
            label = self.get_demo_attribute('label')
            return int(label[0])
        except AttributeError:
            return 5

    def when_factorial_demo_runs(self):
        pass

    def assert_text(self, x, y, expected):
        self.assertEqual(text(self.runner, x, y, len(expected)), expected)

    def assert_factorial_result(self, x, y):
        self.assertEqual(
            text(self.runner, x, y, len(str(self.get_factorial_result()))),
            str(self.get_factorial_result()).encode(),
        )


class AbstractFactorialFCEUXOneLine(
    AbstractFactorialBase, FactorialOneLineSpec
):
    demo_filename = None

    @classmethod
    def setUpClass(cls):
        cls.runner = load_fceux_runner(cls.demo_filename)
        cls.runner.start_fceux()

    @classmethod
    def tearDownClass(cls):
        # Ensure the background process is terminated and ports are cleared after tests finish
        cls.runner.close_fceux()

    def get_factorial_factor(self):
        try:
            label = self.get_demo_attribute('label')
            return int(label[0])
        except AttributeError:
            return 5

    def when_factorial_demo_runs(self):
        self.runner._run()

    def text(self, x, y, length):
        base = 0x2000 + y * 32 + x
        return bytes(self.runner.ppu.vram[base : base + length])

    def assert_text(self, x, y, expected):
        self.assertEqual(self.text(x, y, len(expected)), expected)

    def assert_factorial_result(self, x, y):
        self.assertEqual(
            self.text(x, y, len(str(self.get_factorial_result()))),
            str(self.get_factorial_result()).encode(),
        )


class AbstractFactorialMultiline(
    AbstractFactorialBase, FactorialMultilineSpec
):
    demo_filename = None

    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner(cls.demo_filename)

    def get_factorial_factor(self):
        return 5

    def when_factorial_demo_runs(self):
        pass

    def expected_result(self):
        func = self.get_factorial_function()
        check = func(0)
        if check.__class__.__name__ == 'generator':
            return list(func(self.get_factorial_factor()))
        return [func(value) for value in range(self.get_factorial_factor())]

    def assert_each_line_has_its_factorial(self):
        for index, result in enumerate(self.expected_result()):
            line = 10 + index
            self.assertEqual(
                text(self.runner, 12, line, 3),
                b'%03d' % result,
                f'line {line} (factorial({index}))',
            )


class AbstractFactorialFCEUXMultiline(
    AbstractFactorialBase, FactorialMultilineSpec
):
    demo_filename = None

    @classmethod
    def setUpClass(cls):
        cls.runner = load_fceux_runner(cls.demo_filename)
        cls.runner.start_fceux()

    @classmethod
    def tearDownClass(cls):
        cls.runner.close_fceux()

    def get_factorial_factor(self):
        return 5

    def when_factorial_demo_runs(self):
        self.runner._run()

    def expected_result(self):
        func = self.get_factorial_function()
        check = func(0)
        if check.__class__.__name__ == 'generator':
            return list(func(self.get_factorial_factor()))
        return [func(value) for value in range(self.get_factorial_factor())]

    def assert_each_line_has_its_factorial(self):
        for index, result in enumerate(self.expected_result()):
            line = 10 + index
            self.assertEqual(
                bytes(self.runner.ppu.vram[0x2000 + line * 32 + 12 : 0x2000 + line * 32 + 15]),
                b'%03d' % result,
                f'line {line} (factorial({index}))',
            )
