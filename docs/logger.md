[Back to README](../README.md)
# Logger for Tiny Parser and Type System
The logger module contains methods for efficient error, warning and info logging.

Logger is capable of:
* logging syntax errors to file and CLI
* logging type errors to file and CLI
* logging overflows to file and CLI
* writing symbol table scopes to file
* writing name resolution table to file

Logger methods are called from the main logic module during parsing methods.

The log is formed, writtend into a file and passed to CLI once the last scope (global scope) of the program is closed during parsing.\
Thus, should unexpected errors occur, they will be handled through standard methods and the log won't be formed, since its only goal is logging parsing-related information.