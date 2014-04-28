
from pynes.tests import HexTestCase
from pynes.compiler import lexical, syntax, semantic
from pynes.cartridge import Cartridge

'''
from pynes.examples.movingsprite_translated import game

class MovingSpriteTranslatedTest(HexTestCase):

    def __init__(self, testname):
        super(MovingSpriteTranslatedTest, self).__init__(testname)
        code = game.press_start()
        self.code = code
        tokens = lexical(code)
        self.ast = syntax(tokens)

    def test_inesprg_1(self):
        self.assertEquals('S_DIRECTIVE', self.ast[0]['type'])
        self.assertEquals('T_DIRECTIVE', self.ast[0]['children'][0]['type'])
        self.assertEquals('.inesprg', self.ast[0]['children'][0]['value'])

    def test_ineschr_1(self):
        self.assertEquals('S_DIRECTIVE', self.ast[1]['type'])
        self.assertEquals('T_DIRECTIVE', self.ast[1]['children'][0]['type'])
        self.assertEquals('.ineschr', self.ast[1]['children'][0]['value'])

    def test_inesmap_0(self):
        self.assertEquals('S_DIRECTIVE', self.ast[2]['type'])
        self.assertEquals('T_DIRECTIVE', self.ast[2]['children'][0]['type'])
        self.assertEquals('.inesmap', self.ast[2]['children'][0]['value'])

    def test_inesmir_1(self):
        self.assertEquals('S_DIRECTIVE', self.ast[3]['type'])
        self.assertEquals('T_DIRECTIVE', self.ast[3]['children'][0]['type'])
        self.assertEquals('.inesmir', self.ast[3]['children'][0]['value'])

    def test_bank_0(self):
        self.assertEquals('S_DIRECTIVE', self.ast[4]['type'])
        self.assertEquals('T_DIRECTIVE', self.ast[4]['children'][0]['type'])
        self.assertEquals('.bank', self.ast[4]['children'][0]['value'])

    def test_org_c0000(self):
        self.assertEquals('S_DIRECTIVE', self.ast[5]['type'])
        self.assertEquals('T_DIRECTIVE', self.ast[5]['children'][0]['type'])
        self.assertEquals('.org', self.ast[5]['children'][0]['value'])

    def test_waitvblank_bit_2002(self):
        self.assertEquals('S_ABSOLUTE', self.ast[6]['type'])
        self.assertEquals(['WAITVBLANK'], self.ast[6]['labels'])
        self.assertEquals('T_INSTRUCTION', self.ast[6]['children'][0]['type'])
        self.assertEquals('BIT', self.ast[6]['children'][0]['value'])

    def test_bpl_waitvblank(self):
        self.assertEquals('S_RELATIVE', self.ast[7]['type'])
        self.assertFalse('labels' in self.ast[7])
        self.assertEquals('T_INSTRUCTION', self.ast[7]['children'][0]['type'])
        self.assertEquals('BPL', self.ast[7]['children'][0]['value'])

    def test_rts(self):
        self.assertEquals('S_IMPLIED', self.ast[8]['type'])
        self.assertFalse('labels' in self.ast[8])
        self.assertEquals('T_INSTRUCTION', self.ast[8]['children'][0]['type'])
        self.assertEquals('RTS', self.ast[8]['children'][0]['value'])


    def test_asm_compiler(self):
        cart = Cartridge()
        cart.path = 'fixtures/movingsprite/'

        opcodes = semantic(self.ast, True, cart=cart)

        self.assertIsNotNone(opcodes)
        bin = ''.join([chr(opcode) for opcode in opcodes])
        with open('fixtures/movingsprite/movingsprite.nes', 'rb') as f:
            content = f.read()
        #TOSO self.assertHexEquals(content,bin)
'''
