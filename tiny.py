# Parser and type system for the Tiny language
#
# Latest version on https://github.com/NitricCS/tiny-project
# Kirill Borisov, 108144, Uni Passau

from src.STLexer import STLexer
from src.STParser import STParser
from sys import exit

if __name__ == "__main__":
    try:
        data = open("./code/program.tiny").read()
    except FileNotFoundError:
        print("Code file not found. Please place your program code into \'/code/program.tiny\'.")
        exit()

    lexer = STLexer()

    tokens = lexer.tokenize(data)              # tokens for parser
    tokens_temp = lexer.tokenize(data)         # tokens for error handling

    tokens_static = {}
    for tok in tokens_temp:
        tokens_static[tok.index] = (tok.type, tok.value)
    
    parser = STParser("./output.log", tokens_static)
    parser.parse(tokens)