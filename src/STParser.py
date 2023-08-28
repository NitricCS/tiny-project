# Parser for Symbol Table
#
# Kirill Borisov, 108144

from sly import Parser
from STLexer import STLexer
from STLogger import STLogger

class STParser(Parser):
    tokens = STLexer.tokens
    symbol_table = [[]]

    def __init__ (self, log_path):
        self.logger = STLogger(log_path)              # a path to save the results to

    ### Grammar Description Below ###
    @_('functions')
    def program(self, p):
        self.logger.save_scope(self.symbol_table.pop())
        self.logger.make_log()
        return p.functions
    
    # Function declarations
    @_('{ function }')
    def functions(self, p):
        return p[0]
    
    @_('INT_KW MAIN_KW LP RP open_scope LCB declarations statements RCB close_scope',
       'vartype IDENTIFIER open_scope internal_decl LCB declarations statements RCB close_scope')
    def function(self, p):
        self.insert( (p[1], p.lineno) )
        return (p[0], p[1])
    @_('')
    def open_scope(self, p):
        self.symbol_table.append([])
    @_('')
    def close_scope(self, p):
        self.logger.save_scope(self.symbol_table.pop())
    
    # Function parameters declaration
    @_('LP vartype ext_id [ { COMMA vartype ext_id } ] RP')
    def internal_decl(self, p):
        ids = self.get_func_params(p[2], p[3], p.lineno)
        for id in ids:
            self.insert ( (id, p.lineno) )
    
    # Body declarations
    @_('{ declaration }')
    def declarations(self, p):
        return p[0]
    
    @_('vartype ext_id [ { COMMA ext_id } ] SEMICOLON ')
    def declaration(self, p):
        ids = self.get_args(p[1], p[2], p.lineno)
        for id in ids:
            self.insert ( (id, p.lineno) )
        return p[1]
    
    # Extended ID: plain identifier or array identifier
    @_('IDENTIFIER [ LSB int_val RSB ]',
       'IDENTIFIER [ LSB IDENTIFIER RSB ]',
       'IDENTIFIER')
    def ext_id(self, p):
        if len(p) > 1:
            return (p[0], p[1])
        else:
            return p[0]

    # Body nonterminals
    @_('{ statement }')
    def statements(self, p):
        return p[0]

    @_('assignment SEMICOLON',
       'if_statement',
       'while_statement',
       'return_statement SEMICOLON')
    def statement(self, p):
        return p[0]
    
    # If and while statements
    @_('IF_KW LP ext_id RP LCB statements RCB [ ELSE_KW LCB statements RCB ]')
    def if_statement(self, p):
        self.lookup_id(p.ext_id, p.lineno)
    
    @_('IF_KW LP rel_expression RP LCB statements RCB [ ELSE_KW LCB statements RCB ]')
    def if_statement(self, p):
        pass
    
    @_('WHILE_KW LP ext_id RP LCB statements RCB')
    def while_statement(self, p):
        self.lookup_id(p.ext_id, p.lineno)
    
    @_('WHILE_KW LP rel_expression RP LCB statements RCB')
    def while_statement(self, p):
        pass
    
    # Assignment statement
    @_('ext_id ASSIGNMENT_OP bin_expression',
       'ext_id ASSIGNMENT_OP rel_expression',
       'ext_id ASSIGNMENT_OP literal',
       'ext_id ASSIGNMENT_OP func_call')
    def assignment(self, p):
        self.lookup_id(p.ext_id, p.lineno)
    
    @_('ext_id ASSIGNMENT_OP ext_id')
    def assignment(self, p):
        self.lookup_id(p.ext_id0, p.lineno)
        self.lookup_id(p.ext_id1, p.lineno)
    
    # Return statement
    @_('RETURN_KW literal',
       'RETURN_KW IDENTIFIER')
    def return_statement(self, p):
        return ('return', p[1])
    
    # Function call
    @_('IDENTIFIER LP ext_id [ { COMMA ext_id } ] RP')
    def func_call(self, p):
        self.lookup(p.IDENTIFIER, p.lineno)
        args = self.get_args(p[2], p[3], p.lineno)
        for arg in args:
            self.lookup(arg, p.lineno)
    
    # Binary expressions
    @_('ext_id bin_op ext_id')
    def bin_expression(self, p):
        self.lookup_id(p.ext_id0, p.lineno)
        self.lookup_id(p.ext_id1, p.lineno)
    
    @_('ext_id bin_op literal',
       'literal bin_op ext_id')
    def bin_expression(self, p):
        self.lookup_id(p.ext_id, p.lineno)
    
    @_('literal bin_op literal')
    def bin_expression(self, p):
        return (p[0], p[1], p[2])
    
    # Comparative expressions
    @_('ext_id rel_op ext_id')
    def rel_expression(self, p):
        self.lookup_id(p.ext_id0, p.lineno)
        self.lookup_id(p.ext_id1, p.lineno)
        return (p[0], p[1], p[2])
    
    @_('ext_id rel_op literal',
       'literal rel_op ext_id')
    def rel_expression(self, p):
        self.lookup_id(p.ext_id, p.lineno)
        return (p[0], p[1], p[2])
    
    @_('literal rel_op literal')
    def rel_expression(self, p):
        return (p[0], p[1], p[2])
    
    # Operators
    @_('PLUS_OP', 'MINUS_OP', 'MULTIPLY_OP', 'DIVIDE_OP')
    def bin_op(self, p):
        return p[0]

    @_('EQUAL_OP', 'NOT_EQUAL_OP', 'MORE_OP', 'LESS_OP', 'EQ_OR_MORE_OP', 'EQ_OR_LESS_OP')
    def rel_op(self, p):
        return p[0]
    
    # Lower-level nonterminals    
    @_('INT_KW', 'FLOAT_KW', 'CHAR_KW', 'BOOL_KW')
    def vartype(self, p):
        return p[0]

    @_('int_val', 'float_val', 'bool_val', 'char_val')
    def literal(self, p):
        return p[0]

    @_('CONST_CHAR')
    def char_val(self, p):
        return p.CONST_CHAR

    @_('TRUE_KW', 'FALSE_KW')
    def bool_val(self, p):
        return p[0]

    @_('CONST_NUMBER')
    def int_val(self, p):
        return p.CONST_NUMBER

    @_('CONST_NUMBER PERIOD CONST_NUMBER')
    def float_val(self, p):
        return float(p[0] + '.' + p[2])
    ### Grammar Description End ###

    # Get arguments for multiple declarations
    def get_args(self, mandatory, optional: list, lineno):
        args = [mandatory[0]]
        self.lookup_array_length(mandatory, lineno)
        for arg in optional:
            if (arg):
                for tok in arg:
                    var = tok[1]
                    self.lookup_array_length(var, lineno)
                    args.append(var[0])
        return args
    
    # Get multiple function parameters
    def get_func_params(self, mandatory, optional: list, lineno):
        args = [mandatory[0]]
        self.lookup_array_length(mandatory, lineno)
        for arg in optional:
            if (arg):
                for tok in arg:
                    var = tok[2]
                    self.lookup_array_length(var, lineno)
                    args.append(var[0])
        return args
    
    # Insert symbol into table
    def insert(self, variable):               # variable[1] is id, variable[2] is lineno
        last = len(self.symbol_table) - 1     # index of top list in the stack
        if self.is_in_current_scope(variable[0], last):
            self.logger.log_insertion_error(variable[0], variable[1])
        else:
            self.symbol_table[last].append(variable)

    # Check if a symbol is present in the current scope
    def is_in_current_scope(self, variable, last_index):
        current_scope = self.symbol_table[last_index]     # stack top is current scope
        for symbol in current_scope:
            if variable in symbol:
                    return True
    
    # Lookup method
    def lookup(self, variable, lineno):
        for scope in reversed(self.symbol_table):         # look through symbol table from top to bottom
            for symbol in scope:                          # <symbol> is (<variable>, <line_number>)
                if variable in symbol:
                    self.logger.log_reference(variable, lineno, symbol[1])
                    return True
        self.logger.log_error(variable, lineno)
        return False
    
    # Lookup method for extended ID
    def lookup_id(self, ext_id, lineno):
        args = [ext_id[0]]
        if (len(ext_id) > 1):
            index = ext_id[1][1]
            if index[0] not in ['0','1','2','3','4','5','6','7','8','9']:
                args.append(index)
        for arg in args:
            self.lookup(arg, lineno)
            # Lookup method for extended ID

    def lookup_array_length(self, ext_id, lineno):
        args = []
        if (len(ext_id) > 1):
            length = ext_id[1][1]
            if length[0] not in ['0','1','2','3','4','5','6','7','8','9']:
                args.append(length)
        for arg in args:
            self.lookup(arg, lineno)


if __name__ == "__main__":
    lexer = STLexer()
    parser = STParser("./symbol_table.log")

    data = open("./samples/program.tiny").read()

    s = lexer.tokenize(data)
    p = parser.parse(s)
    print (p)