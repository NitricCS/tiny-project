# Main logic for Tiny
#
# Kirill Borisov, 108144

from sly import Parser
from src.STLexer import STLexer
from src.STLogger import STLogger
from src.TinyTyping import TinyTyping
from src.SlyLogger import SlyLogger

class STParser(Parser):
    tokens = STLexer.tokens              # token set from lexer
    symbol_table = [[]]                  # symbol table for variable scoping
    token_dict = {}                      # hash table for program's tokens
    varvalues = {}                       # dynamic hash table for variable values

    err = False                          # syntax error flag
    err_defined = False                  # defined syntax error flag
    
    log = SlyLogger(open("./sysout.log", "w"))        # default SLY logging is redirected from cli to file

    def __init__ (self, log_path, token_dict):
        self.logger = STLogger(log_path)              # a path to save the results to
        self.typer = TinyTyping()                     # typing methods
        self.token_dict = token_dict
    
    ### Grammar Description Below ###
    # Grammar expressions are transformed into methods that are immediately invoked
    # This allows for symbol, type and overflow checks on the fly
    ###
    @_('functions')
    def program(self, p):
        global_scope = list(reversed(self.symbol_table[0]))
        if not self.err:
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
        ref = self.lookup_id(p.ext_id, p.lineno)   # var lookup
        if not ref:
            return p[0]
        
        type0 = self.lookup_type(p.ext_id[0])     # type check
        if p[2][3] == "var":                      # only checking first operand
            type1 = self.lookup_type(p[2][0])
        if p[2][3] == "literal":
            type1 = self.typer.get_literal_type(p[2][0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return p[0]
        
        self.varvalues[p.ext_id[0]] = p[2][4]
        return p[0]

    @_('ext_id ASSIGNMENT_OP rel_expression')
    def assignment(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)       # var lookup
        if not ref:
            return p[0]
        
        type0 = self.lookup_type(p.ext_id[0])           # type check
        if type0 != "bool":                             # comparative expr results are always boolean
            self.logger.log_type_error_rel(type0, p.lineno)
        return p[0]

    @_('ext_id ASSIGNMENT_OP func_call')
    def assignment(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)            # variable lookup
        if not ref:
            return p[0]
        
        type0 = self.lookup_type(p.ext_id[0])                # type check
        type1 = self.lookup_type(p.func_call[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        
        self.logger.log_warning_overflow("func", p.lineno)   # overflow checks aren't available for function calls
        self.varvalues[p.ext_id[0]] = -1
        return (p[0])
    
    @_('ext_id ASSIGNMENT_OP literal')
    def assignment(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)            # variable lookup
        if not ref:
            return (p[0], p[2])
        
        type0 = self.lookup_type(p.ext_id[0])                # type check
        type1 = self.typer.get_literal_type(p.literal)
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return (p[0], p[2])
        
        value = p.literal                                  # overflow check
        if self.typer.overflow_check_assign(type1, value):
            self.logger.log_overflow(type0, p.lineno)
            self.varvalues[p.ext_id[0]] = -1
            return (p[0], p[2])
        
        self.varvalues[p.ext_id[0]] = p.literal      # save value to hastable
        return (p[0], p[2])
    
    @_('ext_id ASSIGNMENT_OP ext_id')
    def assignment(self, p):
        ref0 = self.lookup_id(p.ext_id0, p.lineno)            # variable lookup
        ref1 = self.lookup_id(p.ext_id1, p.lineno)
        if not ref0 or not ref1:
            return (p[0], p[2])
        
        type0 = self.lookup_type(p.ext_id0[0])                # type check
        type1 = self.lookup_type(p.ext_id1[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return (p[0], p[2])
        
        # overflow checks aren't necessary for assignments a = b since both variables have been checked for overflows before
        self.varvalues[p.ext_id0[0]] = self.varvalues[p.ext_id1[0]]      # save value to hastable
        return (p[0], p[2])
    
    # Return statement
    @_('RETURN_KW literal',
       'RETURN_KW IDENTIFIER')
    def return_statement(self, p):
        return ('return', p[1])
    
    # Function call
    @_('IDENTIFIER LP [ ext_id ] [ { COMMA ext_id } ] RP')
    def func_call(self, p):
        self.lookup(p.IDENTIFIER, p.lineno)               # lookup the function name
        if (p.ext_id0):                                   # collect and lookup args
            args = self.get_args(p[2], p[3], p.lineno)
            for arg in args:
                self.lookup(arg, p.lineno)
            return (p[0], p[2], p[3])
        return (p.IDENTIFIER, None, None)
    
    # Binary expressions
    @_('ext_id bin_op ext_id')
    def bin_expression(self, p):
        ref0 = self.lookup_id(p.ext_id0, p.lineno)           # variables lookup
        ref1 = self.lookup_id(p.ext_id1, p.lineno)
        if not ref0 or not ref1:
            return (p[0], p[1], p[2], 'var', -1)

        type0 = self.lookup_type(p.ext_id0[0])              # type check
        type1 = self.lookup_type(p.ext_id1[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return (p[0], p[1], p[2], 'var', -1)

        try:                                              # overflow check
            value0 = self.varvalues[p.ext_id0[0]]
            value1 = self.varvalues[p.ext_id1[0]]
            if not (value0 == -1 or value1 == -1):
                if self.typer.overflow_check(type0, value0, value1, p.bin_op):
                    self.logger.log_overflow(type0, p.lineno)
                    res = -1
                else:
                    res = self.typer.calculate(type0, value0, value1, p.bin_op)
            else:         # variables have been corrupted by previous overflows
                self.logger.log_warning_overflow("dmg", p.lineno)
                res = -1
        except KeyError:                 # variables weren't initialized before
            self.logger.log_warning_overflow("init", p.lineno)
            res = -1
        return (p[0], p[1], p[2], 'var', res)
    
    @_('literal bin_op ext_id')
    def bin_expression(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)             # variable lookup
        if not ref:
            return (p[0], p[1], p[2], 'literal', -1)
        
        type0 = self.typer.get_literal_type(p.literal)       # type check
        type1 = self.lookup_type(p.ext_id[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return (p[0], p[1], p[2], 'var', -1)

        try:                                              # overflow check
            value = self.varvalues[p.ext_id[0]]
            if not value == -1:
                if self.typer.overflow_check(type0, value, p.literal, p.bin_op):
                    self.logger.log_overflow(type0, p.lineno)
                    res = -1
                else:
                    res = self.typer.calculate(type0, value, p.literal, p.bin_op)
            else:         # variable has been corrupted by previous overflows
                self.logger.log_warning_overflow("dmg", p.lineno)
                res = -1
        except KeyError:                 # variable wasn't initialized before
            self.logger.log_warning_overflow("init", p.lineno)
            res = -1
        return (p[0], p[1], p[2], 'literal', res)
    
    @_('ext_id bin_op literal')
    def bin_expression(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)             # variable lookup
        if not ref:
            return (p[0], p[1], p[2], 'literal', -1)
        
        type0 = self.typer.get_literal_type(p.literal)       # type check
        type1 = self.lookup_type(p.ext_id[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return (p[0], p[1], p[2], 'var', -1)
        
        try:                                              # overflow check
            value = self.varvalues[p.ext_id[0]]
            if not value == -1:
                if self.typer.overflow_check(type0, value, p.literal, p.bin_op):
                    self.logger.log_overflow(type0, p.lineno)
                    res = -1
                else:
                    res = self.typer.calculate(type0, value, p.literal, p.bin_op)
            else:         # variable has been corrupted by previous overflows
                self.logger.log_warning_overflow("dmg", p.lineno)
                res = -1
        except KeyError:                                 # variable wasn't initialized before
            self.logger.log_warning_overflow("init", p.lineno)
            res = -1
        return (p[0], p[1], p[2], 'var', res)
    
    @_('literal bin_op literal')
    def bin_expression(self, p):
        type0 = self.typer.get_literal_type(p.literal0)                           # type check
        type1 = self.typer.get_literal_type(p.literal1)
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
            return (p[0], p[1], p[2], 'literal', -1)
        
        if self.typer.overflow_check(type0, p.literal0, p.literal1, p.bin_op):    # overflow check
            self.logger.log_overflow(type0, p.lineno)
            return (p[0], p[1], p[2], 'literal', -1)
        res = self.typer.calculate(type0, p.literal0, p.literal1, p.bin_op)       # new value saved
        return (p[0], p[1], p[2], 'literal', res)
    
    # Comparative (bool) expressions
    @_('ext_id rel_op ext_id')
    def rel_expression(self, p):
        ref0 = self.lookup_id(p.ext_id0, p.lineno)              # lookup the variables
        ref1 = self.lookup_id(p.ext_id1, p.lineno)
        if not ref0 or not ref1:
            return (p[0], p[1], p[2])

        type0 = self.lookup_type(p.ext_id0[0])                  # type check
        type1 = self.lookup_type(p.ext_id1[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        return (p[0], p[1], p[2])
    
    @_('ext_id rel_op literal',
       'literal rel_op ext_id')
    def rel_expression(self, p):
        ref = self.lookup_id(p.ext_id, p.lineno)                 # lookup the variable
        if not ref:
            return (p[0], p[1], p[2])
        
        type0 = self.typer.get_literal_type(p.literal)           # type check
        type1 = self.lookup_type(p.ext_id[0])
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        return (p[0], p[1], p[2])
    
    @_('literal rel_op literal')
    def rel_expression(self, p):
        type0 = self.typer.get_literal_type(p.literal0)           # type check
        type1 = self.typer.get_literal_type(p.literal1)
        if not self.typer.is_of_same_type(type0, type1):
            self.logger.log_type_error(type0, type1, p.lineno)
        return (p[0], p[1], p[2])
    
    # operators
    @_('PLUS_OP', 'MINUS_OP', 'MULTIPLY_OP', 'DIVIDE_OP')
    def bin_op(self, p):
        return p[0]

    @_('EQUAL_OP', 'NOT_EQUAL_OP', 'MORE_OP', 'LESS_OP', 'EQ_OR_MORE_OP', 'EQ_OR_LESS_OP')
    def rel_op(self, p):
        return p[0]
    
    # lower-level nonterminals
    @_('INT_KW', 'FLOAT_KW', 'CHAR_KW', 'BOOL_KW')
    def vartype(self, p):
        return p[0]

    @_('int_val', 'float_val', 'bool_val', 'char_val')
    def literal(self, p):
        return p[0]
    
    # terminals
    @_('CONST_CHAR')
    def char_val(self, p):
        return p.CONST_CHAR[1]    # only save the symbol without ' '

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
        if 'tuple' in str(type(mandatory[0])):          # check if first argument is an array name with index
            args = [mandatory[0][0]]
        else:
            args = [mandatory[0]]                       # add first argument to return list
        self.lookup_array_length(mandatory[0], lineno)  # lookup array length identifier in the symbol table
        for arg in optional:                            # check if optional arguments are present
            if (arg):
                for tok in arg:
                    var = tok[1]
                    if 'tuple' in str(type(var)):       # array check
                        args.append(var[0])
                    else:
                        args.append(var)
                    self.lookup_array_length(var, lineno)  # array length lookup
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
    
    # Get variable type from a symbol table
    def lookup_type(self, variable):
        for scope in reversed(self.symbol_table):
            for symbol in scope:
                if variable in symbol:
                    return symbol[0]
        return None
    
    # Lookup method for extended ID (simple name or array[index])
    def lookup_id(self, ext_id, lineno):
        args = [ext_id[0]]
        if (len(ext_id) > 1):
            index = ext_id[1][1]
            if index[0] not in ['0','1','2','3','4','5','6','7','8','9']:
                args.append(index)
        for arg in args:
            res = self.lookup(arg, lineno)
        return res
    
    # Lookup method for array lengths represented as names
    def lookup_array_length(self, ext_id, lineno):
        args = []
        if ('tuple' in str(type(ext_id))):
            length = ext_id[1][1]
            if length[0] not in ['0','1','2','3','4','5','6','7','8','9']:
                args.append(length)
        for arg in args:
            self.lookup(arg, lineno)
    
    # Syntax error handling
    def error(self, p):
        self.err = True
        if not p:
            if not self.err_defined:
                self.logger.log_syntax_error("eof", p.lineno)
            return
        
        # Global variable declaration
        if p.type == 'SEMICOLON':
            self.err_defined = True
            i = self.get_prev_index(p.index)                # get previous token
            if self.token_dict[i][0] == 'IDENTIFIER':       # make sure it's a variable name
                i = self.get_prev_index(i)                  # the make sure the previous one is a comma or a type
                if self.token_dict[i][0] == 'COMMA' or self.token_dict[i][0] == 'INT_KW' or self.token_dict[i][0] == 'FLOAT_KW' or self.token_dict[i][0] == 'CHAR_KW' or self.token_dict[i][0] == 'BOOL_KW':
                    self.logger.log_syntax_error("global", p.lineno)
            self.errok()
            self.restart()
        
        # Declaration after other statements
        elif p.type == 'INT_KW' or p.type == 'FLOAT_KW' or p.type == 'CHAR_KW' or p.type == 'BOOL_KW':
            self.err_defined = True
            self.logger.log_syntax_error("decl", p.lineno)
            self.errok()
            self.restart()
        
        # Initialization of a variable on declaration    // int a = 1 //
        elif p.type == 'ASSIGNMENT_OP':
            self.err_defined = True
            i = self.get_prev_index(self.get_prev_index(p.index))   # check previous tokens
            if self.token_dict[i][0] == 'COMMA' or self.token_dict[i][0] == 'INT_KW' or self.token_dict[i][0] == 'FLOAT_KW' or self.token_dict[i][0] == 'CHAR_KW' or self.token_dict[i][0] == 'BOOL_KW':
                self.logger.log_syntax_error("init", p.lineno)
            self.errok()
            self.restart()

        # Other syntax errors
        else:
            if not self.err_defined:
                self.logger.log_syntax_error("generic", p.lineno)
            self.errok()
            self.restart()
        
    # Method to get an index of a previous token from a tokenized program
    def get_prev_index(self, index):
        i = index
        while True:
            i = i - 1
            if i in self.token_dict:
                return i
            if i == -1:
                return -1