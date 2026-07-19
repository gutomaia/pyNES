from unittest import TestCase

from pynes.tests.mixins.demos import (
    AbstractFactorialFCEUXMultiline,
    AbstractFactorialFCEUXOneLine,
)


class FactorialDemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial.py'


class Factorial1DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_1.py'


class Factorial2DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_2.py'


class Factorial4DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_4.py'


class Factorial5DemoTest(AbstractFactorialFCEUXOneLine, TestCase):
    demo_filename = 'factorial_5.py'


class Factorial6DemoTest(AbstractFactorialFCEUXMultiline, TestCase):
    demo_filename = 'factorial_6.py'


class Factorial7DemoTest(AbstractFactorialFCEUXMultiline, TestCase):
    demo_filename = 'factorial_7.py'


class Factorial8DemoTest(AbstractFactorialFCEUXMultiline, TestCase):
    demo_filename = 'factorial_8.py'


class Factorial9DemoTest(AbstractFactorialFCEUXMultiline, TestCase):
    demo_filename = 'factorial_9.py'


class Factorial10DemoTest(AbstractFactorialFCEUXMultiline, TestCase):
    demo_filename = 'factorial_10.py'


class Factorial11DemoTest(AbstractFactorialFCEUXMultiline, TestCase):
    demo_filename = 'factorial_11.py'
