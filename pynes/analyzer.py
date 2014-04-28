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


def analyse(code, token_types):
    for line, line_code in enumerate(code_line_generator(code), 1):
        column = 1
        while column <= len(line_code):
            remaining_line_code = line_code[column - 1:]
            for ttype in token_types:
                m = match(ttype['regex'], remaining_line_code, re.S)
                if m:
                    value = m.group(0)
                    if ttype['store']:
                        yield dict(
                            type=ttype['type'],
                            value=value,
                            line=line,
                            column=column
                        )
                    column += len(value)
                    break
            else:
                raise Exception('Unknown token at column {}:' + line_code)

