# Symbol Table Implementation with SLY
This project builds a **symbol table** and provides **variable resolutions** for a code written in simplified C.\
It parses the code using a basic grammar and creates a symbol table using **static scoping**.

You can checkout the repo directly: https://github.com/NitricCS/symbol-table-sly.git

The solution contains
* a lexer that tokenizes the example code;
* a parser with a simplified grammar that detects declarations and some operators in the code;
* a logger that saves all checkpoints to a file.

A symbol table in this project is **dynamic** and only exists and makes sense at every given point during the parsing process. It isn't permanently stored and becomes empty once the parsing is over.

### Details
A symbol table is a **list that acts as a stack**. The last element of this list is the top of the stack and also **the current scope**.

A new scope is opened (a new top is added) every time the code enters a function, if statement or a for loop condition.\
On exit, the scope is closed and the top element is popped from the stack. From then on, that scope is useless and no longer exists in the table.

Whenever a variable is declared, it is saved into the current scope as a tuple _(<variable_name>, <line_number>)_. This allows to resolve references later through lookup.

### Usage
To execute the solution, run ``python symbol_table.py`` in the root directory.

It will use the code in _samples/example.cpp_ as a default input.\
To change the input, you can edit the Parser path in _symbol_table.py_.

The solution will generate a _symbol_table.log_ file in the root directory. It will contain the symbol table stack elements in the order of them being popped during the parsing, errors (if any), and the resolution table for all references in code.

### Requirements
The solution requires SLY for Python to be installed.\
You can make sure your system meets the requirements by running ``pip install -r requirements.txt``.
