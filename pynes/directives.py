# -*- coding: utf-8 -*-

from asm import register_var

def d_inesprg(arg):
    register_var('inesprg', arg)

def d_ineschr(arg):
    register_var('ineschr', arg)

def d_inesmap(arg):
    register_var('inesmap', arg)

def d_inesmir(arg):
    register_var('inesmir', arg)

def d_bank(arg):
    pass

def d_org(arg):
    pass

directive_list = {}
directive_list['.inesprg'] = d_inesprg
directive_list['.ineschr'] = d_ineschr
directive_list['.inesmap'] = d_inesmap
directive_list['.inesmir'] = d_inesmir
directive_list['.bank'] = d_bank
directive_list['.org'] = d_org

