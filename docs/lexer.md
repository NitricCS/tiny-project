[Back to README](../README.md)
# Lexer for Tiny
A lexer is responsible for program tokenization.\
It takes the input (code) and breaks it into tokens that are then passed to the parser.

The lexer used in this project is a [SLY lexer](https://github.com/dabeaz/sly).\
It tokenizes the program based on a set number of tokens.

Any token that isn't included in the set is not allowed by the compiler and will automatically raise an unexpected token exception.