# -*- coding: utf-8 -*-

from unittest import TestCase
from types import GeneratorType
from pynes.analyzer import analyse, UnknownToken

asm_test_tokens = [
    dict(type='T_FAKE_INSTRUCTION', regex='^(ONE|TEST)', store=True),
    dict(type='T_SOME_SYMBOL', regex='^([*+-])', store=True),
    dict(type='T_ENDLINE', regex=r'^\n', store=True),
    dict(type='T_WHITESPACE', regex=r'^[ \t\r]+', store=False),
    dict(type='T_COMMENT', regex=r'^;[^\n]*', store=False)
]

class AnalyzerTest(TestCase):

    def test_raise_unknown_token(self):
        tokens = analyse('ONE *unknown', asm_test_tokens)
        self.assertIsInstance(tokens, GeneratorType)
        self.assertEquals('T_FAKE_INSTRUCTION', next(tokens)['type'])
        self.assertEquals('T_SOME_SYMBOL', next(tokens)['type'])
        with self.assertRaises(UnknownToken):
            next(tokens) # unknown

    def test_unknown_token_message(self):
        tokens = analyse(';test\n  @--Case \n;TUTEM acronym test',
                         asm_test_tokens)
        self.assertIsInstance(tokens, GeneratorType)
        try:
            list(tokens)
        except UnknownToken as ut:
            self.assertEquals(2, ut.line)
            self.assertEquals(3, ut.column)
            self.assertEquals('  @--Case \n', ut.line_code) # W/ trail wspaces
            self.assertEquals('Unknown token @(2,3):   @--Case', ut.message)
        else:
            self.fail("UnkownToken not raised")

    def test_empty_token_types_list(self):
        tokens = analyse('something', [])
        with self.assertRaises(UnknownToken):
            next(tokens) # unknown

    def test_empty_inputs(self):
        tokens = analyse('', [])
        with self.assertRaises(StopIteration):
            next(tokens) # unknown
