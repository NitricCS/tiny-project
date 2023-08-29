# Parser and Type System for Tiny
This project contains a parser and a type system for a made-up language called **Tiny**.\
It parses the code using a grammar and checks for basic syntax and type errors as well as local scope overflows.

You can checkout the repo directly: https://github.com/NitricCS/tiny-project.git

The project uses a SLY-based symbol table project as a base: https://github.com/NitricCS/symbol-table-sly

### Usage
To run the solution, navigate to its directory and execute ``tiny.py SOURCE_FILE``.\
*SOURCE_FILE* can be a relative or absolute path to your file, but the file itself should only contain code and have a **.tiny** extension.

Syntax errors, type errors and basic overflows will be reported in your terminal.

The solution will also generate an _output.log_ file in the root directory. It will contain the symbol table stack elements in the order of them being popped during the parsing, errors, and the resolution table for all references in code.

### Requirements
The solution requires SLY for Python to be installed.\
You can make sure your system meets the requirements by running ``pip install -r requirements.txt``.