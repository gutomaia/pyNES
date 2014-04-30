# -*- coding: utf-8 -*-
from pynes.tests import ComposerTestCase


class ComposerSlideTest(ComposerTestCase):

    def test_mario(self):
        self.path = 'fixtures/nerdynights/scrolling/'
        f = open('pynes/examples/slides.py')
        code = f.read()
        f.close()
        (
            self.assert_asm_from(code)


                .has('.rsset $0000')
                .and_then('slide .rs 1')

                .and_then('.bank 0')
                .and_then('WAITVBLANK:')
                .and_then('RESET:')
                .and_then('JSR WAITVBLANK')
                .and_then('CLEARMEM:')
                .and_then('JSR WAITVBLANK')
                .and_then('LoadPalettes:')
            # .and_then('LDA #%10000000')

                .and_then('LDA #00')
                .and_then('STA slide')
                .and_then('STA $2000')
            # .and_then('LDA #%00010000')
                .and_then('STA $2001')

                .and_then('NMI:')

                .and_then('JoyPad1A:')
                .and_then('LDA slide')
                .and_then('CLC')
                .and_then('ADC #01')
                .and_then('STA slide')
                .and_then('EndA:')

                .and_then('.bank 1')

            # .and_then('palette:')
            # .and_then('tinymario:')
            # .and_then('mario:')
        )
