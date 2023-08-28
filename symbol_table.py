# Symbol Table Implementation
# Based on Simplified C Code
#
# Latest version on https://github.com/NitricCS/symbol-table-sly
#
# Kirill Borisov, 108144

from src.STLexer import STLexer
from src.STParser import STParser

if __name__ == "__main__":
    data = open("./samples/example.cpp").read()
    lexer = STLexer()

    parser = STParser("./symbol_table.log")     # result is saved to file
    s = lexer.tokenize(data)
    parser.parse(s)