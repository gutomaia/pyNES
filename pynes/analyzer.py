# -*- coding: utf-8 -*-

from re import match
import re
from io import StringIO, BytesIO

def code_line_generator(code):
    ''' A generator for lines from a file/string, keeping the \n at end '''
    if isinstance(code, unicode):
        stream = StringIO(code)
    elif isinstance(code, str):
        stream = BytesIO(code)
    else:
        stream = code # Should be a file input stream, already

    while True:
        line = stream.readline()
        if line:
            yield line
        else: # Line is empty (without \n) at EOF
            break


def analyse(code, tokenTypes):
    code = "".join(code_line_generator(code))
    ttype = None
    line = 1
    column = 1
    while len(code) != 0:
        found = False
        for tokenType in tokenTypes:
            m = match(tokenType['regex'], code, re.S)
            ttype = tokenType
            if m:
                found = True
                if (tokenType['store']):
                    yield dict(
                        type=tokenType['type'],
                        value=m.group(0),
                        line=line,
                        column=column
                    )
                    #print tokenType['type'] + ' ' + m.group(0)
                if m.group(0) == "\n":
                    line += 1
                    column = 1
                else:
                    column = column + len(m.group(0))
                code = code[len(m.group(0)):]
                break
        if not found:
            raise Exception('Unknow Token Code:'+code[0:500])

