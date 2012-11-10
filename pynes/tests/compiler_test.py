import unittest

from pynes.compiler import lexical, syntax, semantic, \
    t_zeropage, t_address, t_separator


class CompilerTest(unittest.TestCase):

    def setUp(self):
        self.zeropage = dict(
            type = 'T_ADDRESS',
            value = '$00'
        )
        self.address10 = dict(
            type = 'T_ADDRESS',
            value = '$1234'
        )
        self.separator = dict(
            type = 'T_SEPARATOR',
            value = ','
        )

    def test_t_zeropage(self):
        self.assertTrue(t_zeropage([self.zeropage],0))

    def test_t_address(self):
        self.assertTrue(t_address([self.address10],0))

    def test_t_separator(self):
        self.assertTrue(t_separator([self.separator],0))

    def test_compile_more_than_on_instruction(self):
        code = '''
            SEC         ;clear the carry
            LDA $20     ;get the low byte of the first number
            '''
        tokens = lexical(code)
        self.assertEquals(6, len(tokens))
        self.assertEquals('T_ENDLINE', tokens[0]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[1]['type'])
        self.assertEquals('T_ENDLINE', tokens[2]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[3]['type'])
        self.assertEquals('T_ADDRESS', tokens[4]['type'])
        self.assertEquals('T_ENDLINE', tokens[5]['type'])
        ast = syntax(tokens)
        self.assertEquals(2, len(ast))

    def test_compile_decimal(self):
        code = '''
            LDA #128
            STA $0203
        '''
        tokens = lexical(code)
        self.assertEquals(7, len(tokens))
        self.assertEquals('T_ENDLINE', tokens[0]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[1]['type'])
        self.assertEquals('T_DECIMAL_NUMBER', tokens[2]['type'])
        self.assertEquals('T_ENDLINE', tokens[3]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[4]['type'])
        self.assertEquals('T_ADDRESS', tokens[5]['type'])
        self.assertEquals('T_ENDLINE', tokens[6]['type'])

    def test_unknow_code_on_lexical(self):
        code = '''
            unknowcode
        '''
