# -*- coding: utf-8 -*-

from re import match
import re

def analyse(code, tokenTypes):
    tokens = []
    ttype = None
    line = 1
    column = 1
    while(len(code)!=0):
        found = False
        for tokenType in tokenTypes:
            m = match(tokenType['regex'], code, re.S)
            ttype = tokenType
            if m:
                found = True
                if (tokenType['store']):
                    tokens.append(
                        dict (
                            type=tokenType['type'],
                            value=m.group(0),
                            line=line,
                            column=column
                        )
                    )
                    #print tokenType['type'] + ' ' + m.group(0)
                if m.group(0) == "\n":
                    line += 1
                    column = 1
                else:
                    column = column + len(m.group(0))
                code = code[len(m.group(0)):]
                break;
        if not found:
            raise Exception('Unknow Token Code:'+code[0:500])
    return tokens
