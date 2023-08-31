[Back to README](../README.md)
# Main Logic Module for Tiny
The main logic module contains a parser, service methods, syntax error handling and on-the-fly checks.

The process of decomposing and checking the Tiny source code file looks like this:
1. Tokenization with the lexer.
2. Parsing based on the token set. Building a symbol table.
3. While parsing, name resolution checks are done through symbol table lookup.
4. __If the previous step was successful__, type checks are performed for relevant statements (see below).
5. __If two previous steps were successful__, overflow checks are performed for relevant statements (see below).

Thus, if any check fails, the following checks for the same statement fail as they make no sense.

Additionally, failed type check and failed overflow check will mark involved variables as corrupt to prevent further checks for statements containing those variables, as those checks would also make no sense.

## Parser
The parser in this project, like the lexer, is based on [SLY](https://github.com/dabeaz/sly).\
Although the SLY project active development has stopped, even older versions provide a good base for program parsing.

The Tiny code is parsed according to the task in the PDF. Any variations or additional symbols not described there will trigger a syntax error.\
__Comments are not allowed__ and will also trigger a syntax error.

The parser contains the Tiny grammar nonterminals. Grammar rules include special methods that are invoked immediately when a nonterminal matching that rule is detected by the parser.\
Those methods contain name resolution and typing logic steps triggered one after another as mentioned above.

## Error Handling
The parser also contains an *error()* method that is handling syntax errors it runs into. The following syntax errors are defined:
* global variable declaration
* declaration done in the wrong part of a function
* variable initialization on declaration
Other syntax errors are reported as undefined.\
Since any syntax error basically triggers a domino effect, generic syntax errors are only reported in the absence of defined syntax errors. Thus, it is possible that only after fixing defined syntax errors, undefined errors may appear in the CLI.

## Symbol Table
The symbol table in this project is based on a [SLY Symbol Table Implementation](https://github.com/NitricCS/symbol-table-sly) from me.

The symbol table is used to check for undeclared variables.

A symbol table is a **list that acts as a stack**. The last element of this list is the top of the stack and also **the current scope**.

A new scope is opened (a new top is added) every time the code enters a function.\
On exit, the scope is closed and the top element is popped from the stack. From then on, that scope is useless and no longer exists in the table.

Scopes aren't created when the program enters any other block (_while_ of _if_ statements) since variables can't be declared there. Thus, the maximum nesting depth of the table is __2__.

Whenever a variable is declared, it is saved into the current scope as a tuple _(<variable_name>, <line_number>)_. This allows to resolve references later through lookup.

The global scope in this project is only used to track function names because Tiny doesn't allow global variables.

## Type Checks
Type checks are performed for the following statements:
* assignments ``var = literal``
* assignments ``var = var``
* assignments ``var = binary_expression``
* assignments ``var = boolean_expression``
* assignments ``var = func_return_value``
* within any arithmetic binary expressions

Type checks are performed using types saved in the symbol table for variables and a *get_literal_type()* method for literals.

If a type check fails, the parser won't launch an overflow check for the statement it failed on. It will also mark the variable that failed as corrupted to invalidate any further overflow checks.

## Overflow Checks
Tiny allows the following types: _int16_, _float32_, _char8_ and _bool_.

Overflow checks are triggered for the following statements:
* all binary arithmetic expressions
* assignments ``var = literal``

Overflow checks are done by [calculating operation results and checking](./typing.md) is they're within bounds.

## What Isn't Checked
1. __Array index out of bounds__. Index error is a type of error that isn't checked by this solution since it's a separate type of error that requires an additional module and isn't involved in a type system.
2. __Direct array references__. Arrays in this solution are treated as variables and aren't separately marked. Thus, referring to an array without an index won't trigger an error since it's a separate error type not included in the project based on the task.