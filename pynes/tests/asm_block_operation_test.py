# -*- coding: utf-8 -*-
import unittest

from pynes.asm import *
from pynes.block import AsmBlock, MemoryAddress


class AsmBlockOperationTest(unittest.TestCase):

    def assert_expr(self, expr, code):
        self.assertEquals(str(expr), code)

    def assert_type(self, obj, type_name, instruction_name=None, address_mode=None):
        self.assertEquals(type(obj).__name__, type_name)
        if (instruction_name):
            self.assertEquals(obj.name, instruction_name)
        if (address_mode):
            self.assertEquals(obj.address_mode, address_mode)

    def test_immediate_proxy_plus_one_returns_imeddiate_instruction(self):
        expression = LDA + 1
        self.assert_type(expression, 'Instruction')
        self.assertEquals(expression.address_mode, 'imm')

    def test_immediate_proxy_plus_one_plus_single_proxy_return_asmblock_with_two_instructions(self):
        expression = LDA + 1 + CLC
        self.assert_type(expression, 'AsmBlock')
        self.assertEquals(len(expression), 2)
        self.assert_type(expression.get(0), 'Instruction', 'LDA')
        self.assert_type(expression.get(1), 'Instruction', 'CLC')
        actual = str(expression)
        expected = '\n'.join([
            'LDA #1',
            'CLC'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_immediate_proxy_plus_one_plus_single_proxy_plus_immediate_proxy_return_asmblock_with_instruction_proxy_at_last(self):
        expression = LDA + 1 + CLC + ADC
        self.assert_type(expression, 'AsmBlock')
        self.assertEquals(len(expression), 3)
        self.assert_type(expression.get(0), 'Instruction', 'LDA')
        self.assert_type(expression.get(1), 'Instruction', 'CLC')
        self.assert_type(expression.get(2), 'InstructionProxy', 'ADC')

    def test_complete_sum(self):
        expression = LDA + 1 + CLC + ADC + 1
        self.assert_type(expression, 'AsmBlock')
        self.assertEquals(len(expression), 3)
        self.assert_type(expression.get(0), 'Instruction', 'LDA', 'imm')
        self.assert_type(expression.get(1), 'Instruction', 'CLC', 'sngl')
        self.assert_type(expression.get(2), 'Instruction', 'ADC', 'imm')
        actual = str(expression)
        expected = '\n'.join([
            'LDA #1',
            'CLC',
            'ADC #1'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_adc_plus_one_returns_immediate_instruction(self):
        result = ADC + 1
        self.assert_type(result, 'Instruction')
        self.assertEquals(result.address_mode, 'imm')
        self.assertEquals(result.param, 1)

    def test_cpm_plus_zp_string_returns_zeropage_instruction(self):
        result = CMP + '$44'
        self.assert_type(result, 'Instruction')
        self.assertEquals(result.address_mode, 'zp')
        self.assertEquals(result.param, '$44')

    def test_cpm_plus_absolute_addr_returns_zeropage_instruction(self):
        result = CMP + '$4400'
        self.assert_type(result, 'Instruction')
        self.assertEquals(result.address_mode, 'abs')
        self.assertEquals(result.param, '$4400')

    def test_call_a_sngl_proxy_returns_a_instruction(self):
        result = CLC()
        self.assert_type(result, 'Instruction')
        self.assertEquals(result.address_mode, 'sngl')
        self.assertEquals(result.param, None)

    def test_call_immediate_proxy_with_int_returns_instruction(self):
        result = ADC(1)
        self.assert_type(result, 'Instruction')
        self.assertEquals(result.address_mode, 'imm')
        self.assertEquals(result.param, 1)

    def test_adc_plus_two_returns_immediate_instruction_2(self):
        result = ADC + 2
        self.assert_type(result, 'Instruction')
        self.assertEquals(result.address_mode, 'imm')
        self.assertEquals(result.param, 2)

    def test_instruction_plus_instruction_returns_asmblock(self):
        instruction_1 = ADC + 1
        instruction_2 = ADC + 2
        result = instruction_1 + instruction_2
        self.assert_type(result, 'AsmBlock')
        self.assert_type(result.get(0), 'Instruction')
        self.assert_type(result.get(1), 'Instruction')
        actual = str(result)
        expected = '\n'.join([
            'ADC #1',
            'ADC #2'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_clc_plus_adc_returns_asmblock_with_instruction_and_instruction_proxy(self):
        result = CLC + ADC
        self.assert_type(result, 'AsmBlock')
        self.assertEquals(len(result), 2)
        self.assert_type(result.get(0), 'Instruction')
        self.assert_type(result.get(1), 'InstructionProxy')

    def test_clc_adc_one_returns_asmblock_with_two_instructions(self):
        result = CLC + ADC + 1
        self.assert_type(result, 'AsmBlock')
        self.assertEquals(len(result), 2)
        self.assert_type(result.get(0), 'Instruction')
        self.assert_type(result.get(1), 'Instruction')
        actual = str(result)
        expected = '\n'.join([
            'CLC',
            'ADC #1'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_asmblock_with_instruction_and_instruction_proxy_plus_one_returns_asmblock_with_two_instructions(self):
        result = AsmBlock(CLC, ADC) + 1
        self.assert_type(result, 'AsmBlock')
        self.assertEquals(len(result), 2)
        self.assert_type(result.get(0), 'Instruction')
        self.assert_type(result.get(1), 'Instruction')
        actual = str(result)
        expected = '\n'.join([
            'CLC',
            'ADC #1'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_asmblock_with_instruction_and_instruction_and_one_returns_asmblock_with_two_instructions(self):
        result = AsmBlock(CLC, ADC, 1)
        self.assert_type(result, 'AsmBlock')
        self.assertEquals(len(result), 2)
        self.assert_type(result.get(0), 'Instruction')
        self.assert_type(result.get(1), 'Instruction')
        actual = str(result)
        expected = '\n'.join([
            'CLC',
            'ADC #1'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_asmblock_plus_asmblock(self):
        result = AsmBlock(SEI) + AsmBlock(TXS)
        # self.assertEquals(len(result), 2)
        # self.assert_type(result.get(0), 'AsmBlock')
        # self.assert_type(result.get(1), 'AsmBlock')
        actual = str(result)
        expected = '\n'.join([
            'SEI',
            'TXS'
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_expression_asl_plus_a(self):
        self.assert_expr(ASL + A, 'ASL A')

    def test_expression_stx_with_addr_2000(self):
        self.assert_expr(STX + '$4017', 'STX $4017')

    def test_asm_block_with_instruction_and_instruction_abs(self):
        result = (
            LDX + 40 +
            STX + '$4017')
        self.assert_type(result, 'AsmBlock')
        self.assertEquals(len(result), 2)
        actual = str(result)
        expected = '\n'.join([
            'LDX #40',
            'STX $4017',
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_instruction_with_memory_address_label(self):
        result = BPL + MemoryAddress('vblank')

        self.assert_type(result, 'Instruction')
        actual = str(result)
        expected = 'BPL vblank'

        self.assertEquals(actual, expected)

    def test_regular_reset(self):
        result = (
            SEI +
            CLD +
            LDX + 40 +
            STX + '$4017' +
            LDX + 0xFF +
            TXS +
            INX +
            STX + '$2000' +
            STX + '$2001')

        self.assert_type(result, 'AsmBlock')
        self.assertEquals(len(result), 9)
        actual = str(result)
        expected = '\n'.join([
            'SEI',
            'CLD',
            'LDX #40',
            'STX $4017',
            'LDX #255',
            'TXS',
            'INX',
            'STX $2000',
            'STX $2001',
            ]) + '\n'
        self.assertEquals(actual, expected)

    def test_eee(self):
        self.assert_expr(ADC + 0x0a, 'ADC #10')

    def test_ee1(self):
        return
        result = ADC + '$10'
        actual = str(result)
        expected = 'ADC $10'
        self.assertEquals(actual, expected)

    def test_fff(self):
        return
        result = ADC + ['$10', X]
        actual = str(result)
        expected = 'ADC $10, X'
        self.assertEquals(actual, expected)
