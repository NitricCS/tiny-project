# Parser for Symbol Table
#
# Kirill Borisov, 108144

from sly import Parser
from STLexer import STLexer
from STLogger import STLogger
from TinyTyping import TinyTyping

class STParser(Parser):
    tokens = STLexer.tokens
    token_dict = {}
    symbol_table = [[]]
    varvalues = {}

    def __init__ (self, log_path, token_dict):
        self.logger = STLogger(log_path)              # a path to save the results to
        self.typer = TinyTyping()
        self.token_dict = token_dict
    
    # Syntax error handling
    def error(self, p):
        if not p:
            print("End of File!")
            return

        if p.type == 'SEMICOLON':
            i = self.get_prev_index(p.index)
            if self.token_dict[i][0] == 'IDENTIFIER':
                i = self.get_prev_index(i)
                if self.token_dict[i][0] == 'COMMA' or self.token_dict[i][0] == 'INT_KW' or self.token_dict[i][0] == 'FLOAT_KW' or self.token_dict[i][0] == 'CHAR_KW' or self.token_dict[i][0] == 'BOOL_KW':
                    self.logger.log_syntax_error("global", p.lineno)
            self.errok()
            self.restart()
        elif p.type == 'INT_KW' or p.type == 'FLOAT_KW' or p.type == 'CHAR_KW' or p.type == 'BOOL_KW':
            self.logger.log_syntax_error("init", p.lineno)
            self.errok()
            self.restart()
        elif p.type == 'ASSIGNMENT_OP':
            i = self.get_prev_index(self.get_prev_index(p.index))
            if self.token_dict[i][0] == 'COMMA' or self.token_dict[i][0] == 'INT_KW' or self.token_dict[i][0] == 'FLOAT_KW' or self.token_dict[i][0] == 'CHAR_KW' or self.token_dict[i][0] == 'BOOL_KW':
                self.logger.log_syntax_error("decl", p.lineno)
            self.errok()
            self.restart()
        else:
            self.logger.log_syntax_error("generic", p.lineno)
            self.errok()
            self.restart()
    
    def get_prev_index(self, index):
        i = index
        while True:
                i = i - 1
                if i in self.token_dict:
                    return i
                if i == -1:
                    return -1
    
    ### Grammar Description Below ###
    @_('functions')
    def program(self, p):
        global_scope = list(reversed(self.symbol_table[0]))
        if len(global_scope) == 0:
            self.logger.log_main_error()
        elif 'main' not in global_scope[0][1]:
            self.logger.log_main_error()
        self.logger.save_scope(self.symbol_table.pop())
        self.logger.make_log()
        return p.functions
    
    # Function declarations
    @_('{ function }')
    def functions(self, p):
        return p[0]

    @_('INT_KW MAIN_KW LP RP open_scope LCB declarations statements RCB close_scope',
       'vartype IDENTIFIER open_scope LP [ internal_decl ] RP LCB declarations statements RCB close_scope')
    def function(self, p):
        self.insert( p[0], p[1], p.lineno )
        return (p[0], p[1])
    @_('')
    def open_scope(self, p):
        self.symbol_table.append([])
    @_('')
    def close_scope(self, p):
        self.varvalues = {}
        self.logger.save_scope(self.symbol_table.pop())
    
    # Function parameters declaration
    @_('vartype ext_id [ { COMMA vartype ext_id } ]')
    def internal_decl(self, p):
        ids = self.get_func_params(p[1], p[2], p.lineno)
        vartypes = self.get_param_types(p[0], p[2], p.lineno)
        i = 0
        for id in ids:
            self.insert ( vartypes[i], id, p.lineno )
            i = i + 1
    
    # Body declarations
    @_('{ declaration }')
    def declarations(self, p):
        return p[0]
    
    @_('vartype ext_id [ { COMMA ext_id } ] SEMICOLON ')
    def declaration(self, p):
        ids = self.get_args(p[1], p[2], p.lineno)
        for id in ids:
            self.insert ( p.vartype, id, p.lineno )
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
    @_('ext_id ASSIGNMENT_OP bin_expression')
    def assignment(self, p):
        self.lookup_id(p.ext_id, p.lineno)
        type0 = self.lookup_type(p.ext_id[0])
        if p[2][3] == "var":                      # only checking first operand
            type1 = self.lookup_type(p[2][0])
        if p[2][3] == "literal":
            type1 = self.typer.get_literal_type(p[2][0])
        self.varvalues[p.ext_id[0]] = p[2][4]
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)

    @_('ext_id ASSIGNMENT_OP rel_expression')
    def assignment(self, p):
        self.lookup_id(p.ext_id, p.lineno)
        type0 = self.lookup_type(p.ext_id[0])
        if p[2][3] == "var":                      # only checking first operand
            type1 = self.lookup_type(p[2][0])
        if p[2][3] == "literal":
            type1 = self.typer.get_literal_type(p[2][0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)

    @_('ext_id ASSIGNMENT_OP func_call')
    def assignment(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)
        if not ref:
            return (p[0])
        type0 = self.lookup_type(p.ext_id[0])
        type1 = self.lookup_type(p.func_call[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        self.logger.log_warning_overflow("func", p.lineno)
        return (p[0])
    
    @_('ext_id ASSIGNMENT_OP literal')
    def assignment(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)
        if not ref:
            return (p[0], p[2])
        self.varvalues[p.ext_id[0]] = p.literal      # save value to hastable
        type0 = self.lookup_type(p.ext_id[0])
        type1 = self.typer.get_literal_type(p.literal)
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        return (p[0], p[2])
        # check for overflows !!!
    
    @_('ext_id ASSIGNMENT_OP ext_id')
    def assignment(self, p):
        self.lookup_id(p.ext_id0, p.lineno)
        self.lookup_id(p.ext_id1, p.lineno)
        self.varvalues[p.ext_id0[0]] = self.varvalues[p.ext_id1[0]]      # save value to hastable
        # add values to stack here
        type0 = self.lookup_type(p.ext_id0[0])
        type1 = self.lookup_type(p.ext_id1[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
    
    # Return statement
    @_('RETURN_KW literal',
       'RETURN_KW IDENTIFIER')
    def return_statement(self, p):
        return ('return', p[1])
    
    # Function call
    @_('IDENTIFIER LP [ ext_id ] [ { COMMA ext_id } ] RP')
    def func_call(self, p):
        self.lookup(p.IDENTIFIER, p.lineno)
        if (p.ext_id0):
            args = self.get_args(p[2], p[3], p.lineno)
            for arg in args:
                self.lookup(arg, p.lineno)
            return (p[0], p[2], p[3])
        return (p.IDENTIFIER, None, None)
    
    # Binary expressions
    @_('ext_id bin_op ext_id')
    def bin_expression(self, p):
        self.lookup_id(p.ext_id0, p.lineno)
        self.lookup_id(p.ext_id1, p.lineno)
        type0 = self.lookup_type(p.ext_id0[0])
        type1 = self.lookup_type(p.ext_id1[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        # check for overflows
        try:
            value0 = self.varvalues[p.ext_id0[0]]
            value1 = self.varvalues[p.ext_id1[0]]
            if not (value0 == -1 or value1 == -1):
                if self.typer.overflow_check(type0, value0, value1, p.bin_op):
                    self.logger.log_overflow(type0, p.lineno)
                    res = -1
                else:
                    res = self.typer.calculate(type0, value0, value1, p.bin_op)
            else:
                self.logger.log_warning_overflow("dmg", p.lineno)
                res = -1
        except KeyError:
            self.logger.log_warning_overflow("init", p.lineno)
            res = -1
        return (p[0], p[1], p[2], 'var', res)
    
    @_('literal bin_op ext_id')
    def bin_expression(self, p):
        self.lookup_id(p.ext_id, p.lineno)
        type0 = self.typer.get_literal_type(p.literal)
        type1 = self.lookup_type(p.ext_id[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        # check for overflows
        try:
            value = self.varvalues[p.ext_id[0]]
            if not value == -1:
                if self.typer.overflow_check(type0, value, p.literal, p.bin_op):
                    self.logger.log_overflow(type0, p.lineno)
                    res = -1
                else:
                    res = self.typer.calculate(type0, value, p.literal, p.bin_op)
            else:
                self.logger.log_warning_overflow("dmg", p.lineno)
                res = -1
        except KeyError:
            self.logger.log_warning_overflow("init", p.lineno)
            res = -1
        return (p[0], p[1], p[2], 'literal', res)
    
    @_('ext_id bin_op literal')
    def bin_expression(self, p):
        self.lookup_id(p.ext_id, p.lineno)
        type0 = self.typer.get_literal_type(p.literal)
        type1 = self.lookup_type(p.ext_id[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        # check for overflows
        try:
            value = self.varvalues[p.ext_id[0]]
            if not value == -1:
                if self.typer.overflow_check(type0, value, p.literal, p.bin_op):
                    self.logger.log_overflow(type0, p.lineno)
                    res = 0
                else:
                    res = self.typer.calculate(type0, value, p.literal, p.bin_op)
            else:
                self.logger.log_warning_overflow("dmg", p.lineno)
                res = -1
        except KeyError:
            self.logger.log_warning_overflow("init", p.lineno)
            res = -1
        return (p[0], p[1], p[2], 'var', res)
    
    @_('literal bin_op literal')
    def bin_expression(self, p):
        type0 = self.typer.get_literal_type(p.literal0)
        type1 = self.typer.get_literal_type(p.literal1)
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        # check for overflows
        if self.typer.overflow_check(type0, p.literal0, p.literal1, p.bin_op):
            self.logger.log_overflow(type0, p.lineno)
        res = self.typer.calculate(type0, p.literal0, p.literal1, p.bin_op)
        return (p[0], p[1], p[2], 'literal', res)
    
    # Comparative expressions
    @_('ext_id rel_op ext_id')
    def rel_expression(self, p):
        self.lookup_id(p.ext_id0, p.lineno)
        self.lookup_id(p.ext_id1, p.lineno)
        # check here that type(ext_id0)=type(ext_id1)
        type0 = self.lookup_type(p.ext_id0[0])
        type1 = self.lookup_type(p.ext_id1[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        return (p[0], p[1], p[2])
    
    @_('ext_id rel_op literal',
       'literal rel_op ext_id')
    def rel_expression(self, p):
        self.lookup_id(p.ext_id, p.lineno)
        # check here that type(literal)=type(ext_id)
        type0 = self.typer.get_literal_type(p.literal)
        type1 = self.lookup_type(p.ext_id[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        return (p[0], p[1], p[2])
    
    @_('literal rel_op literal')
    def rel_expression(self, p):
        # check here that type(literal0)=type(literal1)
        type0 = self.typer.get_literal_type(p.literal0)
        type1 = self.typer.get_literal_type(p.literal1)
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
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
        return p.CONST_CHAR[1]

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
    
    # Get function parameter types
    def get_param_types(self, mandatory, optional: list, lineno):
        vartypes = [mandatory]
        for vartype in optional:
            if (vartype):
                for tok in vartype:
                    vtype = tok[1]
                    vartypes.append(vtype)
        return vartypes
    
    # Insert symbol into table
    def insert(self, vartype, variable, lineno):               # variable[1] is id, variable[2] is lineno
        last = len(self.symbol_table) - 1     # index of top list in the stack
        if self.is_in_current_scope(variable, last):
            self.logger.log_insertion_error(variable, lineno)
        else:
            self.symbol_table[last].append((vartype, variable, lineno))

    # Check if a symbol is present in the current scope
    def is_in_current_scope(self, variable, last_index):
        current_scope = self.symbol_table[last_index]     # stack top is current scope
        for symbol in current_scope:
            if variable in symbol:
                    return True
    
    # Lookup method
    def lookup(self, variable, lineno):
        for scope in reversed(self.symbol_table):         # look through symbol table from top to bottom
            for symbol in scope:                          # <symbol> is (<type>, <variable>, <line_number>)
                if variable in symbol:
                    self.logger.log_reference(variable, lineno, symbol[2])
                    return True
        self.logger.log_error(variable, lineno)
        return False
    
    def lookup_type(self, variable):
        for scope in reversed(self.symbol_table):
            for symbol in scope:
                if variable in symbol:
                    return symbol[0]
        return None
    
    # Lookup method for extended ID
    def lookup_id(self, ext_id, lineno):
        args = [ext_id[0]]
        if (len(ext_id) > 1):
            index = ext_id[1][1]
            if index[0] not in ['0','1','2','3','4','5','6','7','8','9']:
                args.append(index)
        for arg in args:
            res = self.lookup(arg, lineno)
        return res

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
    
    data = open("./samples/program.tiny").read()

    s = lexer.tokenize(data)
    s1 = lexer.tokenize(data)
    td = {}
    for t in s1:
        td[t.index] = (t.type, t.value)
    parser = STParser("./symbol_table.log", td)
    p = parser.parse(s)
    print (p)