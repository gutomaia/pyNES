# -*- coding: utf-8 -*-
import unittest

from pynes.compiler import lexical, syntax

'''
Those tests are based on examples from:
http://nesdev.parodius.com/6502guid.txt
'''


class GuideTest(unittest.TestCase):

    def test_example_16_bit_subtraction_routine(self):
        ex_2 = '''
            SEC         ;clear the carry
            LDA $20     ;get the low byte of the first number
            SBC $22     ;add to it the low byte of the second
            STA $24     ;store in the low byte of the result
            LDA $21     ;get the high byte of the first number
            SBC $23     ;add to it the high byte of the second, plus carry
            STA $25     ;store in high byte of the result
            '''
        tokens = list(lexical(ex_2))
        self.assertEquals(21, len(tokens))
        ast = syntax(tokens)
        self.assertEquals(7, len(ast))

    def test_example_4_2(self):
        example_4_2 = '''
        ; Example 4-2.  Deleting an entry from an unordered list
        ;
        ; Delete the contents of $2F from a list whose starting
        ; address is in $30 and $31.  The first byte of the list
        ; is its length.
        ;

        deluel: LDY #$00     ; fetch element count
                LDA ($30),Y
                TAX          ; transfer length to X
                LDA $2F      ; item to delete
        nextel: INY          ; index to next element
                CMP ($30),Y  ; do entry and element match?
                BEQ delete   ; yes. delete element
                DEX          ; no. decrement element count
                BNE nextel   ; any more elements to compare?
                RTS          ; no. element not in list. done

        ; delete an element by moving the ones below it up one location

        delete: DEX          ; decrement element count
                BEQ deccnt   ; end of list?
                INY          ; no. move next element up
                LDA ($30),Y
                DEY
                STA ($30),Y
                INY
                JMP delete
        deccnt: LDA ($30,X)  ; update element count of list
                SBC #$01
                STA ($30,X)
                RTS
        '''
        tokens = list(lexical(example_4_2))
        self.assertEquals(96, len(tokens))

    def test_example_5_6(self):
        """
        example_5_6 = '''
        ; Example 5-6.  16-bit by 16-bit unsigned multiply
        ;
        ; Multiply $22 (low) and $23 (high) by $20 (low) and
        ; $21 (high) producing a 32-bit result in $24 (low) to $27 (high)
        ;

        mlt16:  LDA #$00     ; clear p2 and p3 of product
                STA $26
                STA $27
                LDX #$16     ; multiplier bit count = 16
        nxtbt:  LSR $21      ; shift two-byte multiplier right
                ROR $20
                BCC align    ; multiplier = 1?
                LDA $26      ; yes. fetch p2
                CLC
                ADC $22      ; and add m0 to it
                STA $26      ; store new p2
                LDA $27      ; fetch p3
                ADC $23      ; and add m1 to it
        align:  ROR A        ; rotate four-byte product right
                STA $27      ; store new p3
                ROR $26
                ROR $25
                ROR $24
                DEX          ; decrement bit count
                BNE nxtbt    ; loop until 16 bits are done
                RTS
        '''
        # TODO ROR A?
        # tokens = list(lexical(example_5_6))
        """

    def test_example_5_14(self):
        example_5_14 = '''
        ; Example 5-14.  Simple 16-bit square root.
        ;
        ; Returns the 8-bit square root in $20 of the
        ; 16-bit number in $20 (low) and $21 (high). The
        ; remainder is in location $21.

        sqrt16: LDY #$01     ; lsby of first odd number = 1
                STY $22
                DEY
                STY $23      ; msby of first odd number (sqrt = 0)
        again:  SEC
                LDA $20      ; save remainder in X register
                TAX          ; subtract odd lo from integer lo
                SBC $22
                STA $20
                LDA $21      ; subtract odd hi from integer hi
                SBC $23
                STA $21      ; is subtract result negative?
                BCC nomore   ; no. increment square root
                INY
                LDA $22      ; calculate next odd number
                ADC #$01
                STA $22
                BCC again
                INC $23
                JMP again
        nomore: STY $20      ; all done, store square root
                STX $21      ; and remainder
                RTS
        '''
        tokens = list(lexical(example_5_14))
        self.assertEquals(74, len(tokens))

        self.assertEquals('T_ENDLINE', tokens[0]['type'])
        self.assertEquals('T_ENDLINE', tokens[1]['type'])
        self.assertEquals('T_ENDLINE', tokens[2]['type'])
        self.assertEquals('T_ENDLINE', tokens[3]['type'])
        self.assertEquals('T_ENDLINE', tokens[4]['type'])
        self.assertEquals('T_ENDLINE', tokens[5]['type'])
        self.assertEquals('T_ENDLINE', tokens[6]['type'])

        self.assertEquals('T_LABEL', tokens[7]['type'])
        self.assertEquals('T_INSTRUCTION', tokens[8]['type'])
        self.assertEquals('T_HEX_NUMBER', tokens[9]['type'])
        self.assertEquals('T_ENDLINE', tokens[10]['type'])

        self.assertEquals('T_INSTRUCTION', tokens[11]['type'])
        self.assertEquals('T_ADDRESS', tokens[12]['type'])
        self.assertEquals('T_ENDLINE', tokens[13]['type'])

        self.assertEquals('T_INSTRUCTION', tokens[14]['type'])
        self.assertEquals('T_ENDLINE', tokens[15]['type'])

        self.assertEquals('T_INSTRUCTION', tokens[16]['type'])
        self.assertEquals('T_ADDRESS', tokens[17]['type'])
        self.assertEquals('T_ENDLINE', tokens[18]['type'])
