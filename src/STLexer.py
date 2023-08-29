# Lexer (Tokenizer) for Symbol Table
#
# Kirill Borisov, 108144

from sly import Lexer

class STLexer(Lexer):
    tokens = {
        IF_KW, ELSE_KW, WHILE_KW, CONST_CHAR, CONST_NUMBER,
        PLUS_OP, MINUS_OP, MULTIPLY_OP, DIVIDE_OP,
        LP, LCB, RP, RCB, LSB, RSB,
        INT_KW, FLOAT_KW, CHAR_KW, BOOL_KW,
        TRUE_KW, FALSE_KW,
        MAIN_KW, RETURN_KW,
        EQUAL_OP, NOT_EQUAL_OP, MORE_OP, LESS_OP, EQ_OR_MORE_OP, EQ_OR_LESS_OP, ASSIGNMENT_OP,
        COMMA, PERIOD, SEMICOLON,
        IDENTIFIER,
    }

    ignore = ' \t'

    IF_KW = r'if'
    ELSE_KW = r'else'
    WHILE_KW = r'while'
    CONST_NUMBER = r'\d+'
    CONST_CHAR = r'".?"|\'.?\''

    PLUS_OP = r'\+'
    MINUS_OP = r'\-'
    MULTIPLY_OP = r'\*'
    DIVIDE_OP = r'\/'
    LP = r'\('
    LCB = r'\{'
    RP = r'\)'
    RCB = r'\}'
    LSB = r'\['
    RSB = r'\]'

    INT_KW = r'int'
    FLOAT_KW = r'float'
    CHAR_KW = r'char'
    BOOL_KW = r'bool'

    TRUE_KW = r'true'
    FALSE_KW = r'false'

    MAIN_KW = r'main\s?'
    RETURN_KW = r'return'

    EQUAL_OP = r'=='
    NOT_EQUAL_OP = r'!='
    MORE_OP = r'>'
    LESS_OP = r'<'
    EQ_OR_MORE_OP = r'>='
    EQ_OR_LESS_OP = r'<='
    ASSIGNMENT_OP = r'='

    COMMA = r','
    PERIOD = r'\.'
    SEMICOLON = r';'
    IDENTIFIER = r'[a-zA-Z]\w*'

    variable_tokens = [
        'IDENTIFIER',
        'CONST_STR',
        'CONST_NUMBER',
    ]

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

if __name__ == "__main__":
    data = open("./samples/program.tiny").read()
    lexer = STLexer()
    
    s = lexer.tokenize(data)

    # for tok in s:
    #     print('index=%r, type=%r, value=%r' % (tok.index, tok.type, tok.value))
    token_dict = {}
    for tok in s:
        token_dict[tok.index] = (tok.type, tok.value)
    print(token_dict)