# Logger Module for Symbol Table
#
# Kirill Borisov, 108144

from os import path
from tabulate import tabulate

class STLogger():
    table_ostream = []
    resolution_table = []
    err_log = ""
    wrn_log = ""

    def __init__(self, log_path):
        self.path = path.abspath(log_path)
        self.table_ostream = []
    
    def save_scope(self, scope):
        self.table_ostream.append(scope)
    
    # Variable resolution log
    def log_reference(self, variable, line, declared):
        self.resolution_table.append([line, variable, declared])
    
    # Variable not declared error log
    def log_error(self, variable, line):
        new_log = "ERROR: Reference \"" + variable + "\" in line " + str(line) + " is not declared before use\n"
        self.err_log = self.err_log + new_log
    
    # Duplicate declaration error log
    def log_insertion_error(self, variable, line):
        new_log = "ERROR: Duplicate declaration of reference \"" + variable + "\" in current scope (line " + str(line) + ")\n"
        self.err_log = self.err_log + new_log
    
    def log_syntax_error(self, error_type, line):
        match error_type:
            case "global":
                new_log = "Syntax error in line " + str(line) + ": Global variables are not allowed\n"
            case "init":
                new_log = "Syntax error in line " + str(line) + ": Variables should be declared and initialized separately\n"
            case "decl":
                new_log = "Syntax error in line " + str(line) + ": Variable declarations should be made in the beginning of each function\n"
            case "generic":
                new_log = "Syntax error in line " + str(line) + ": Undefined error\n"
        self.err_log = self.err_log + new_log
    
    def log_type_error(self, type1, type2, line):
        new_log = "Type error in line " + str(line) + ": Operation on " + type1 + " and " + type2 + "\n"
        self.err_log = self.err_log + new_log
    
    def log_type_error_rel(self, vartype, line):
        new_log = "Type error in line " + str(line) + ": Boolean operation result can't be assigned to \"" + vartype + "\".\n"
        self.err_log = self.err_log + new_log
    
    def log_overflow(self, type, line):
        new_log = "Type \"" + type + "\" overflow in line " + str(line) + "\n"
        self.err_log = self.err_log + new_log
    
    def log_warning_overflow(self, warning_type, line):
        match warning_type:
            case "init":
                new_log = "WARNING: Unable to check for overflows, variable not initialized in line " + str(line) + "\n"
            case "dmg":
                new_log = "WARNING: Unable to check for overflows in line " + str(line) + ". Variable value is corrupted."
            case "func":
                new_log = "WARNING: Unable to check for overflows in line " + str(line) + ". Overflows not checked for function calls.\n"
        self.wrn_log = self.wrn_log + new_log

    def log_main_error(self):
        new_log = "ERROR: main() function isn't declared or isn't last\n"
        self.err_log = self.err_log + new_log
    
    def make_log(self):
        f = open(self.path, "w", encoding="utf-8")
        for scope in self.table_ostream:
            txt = str(scope) + "\n"
            f.write(txt)
        f.write("\n")

        if self.err_log:
            f.write(self.err_log)
            print(self.err_log)
            f.write("\n")

        if self.wrn_log:
            f.write(self.wrn_log)
            print(self.wrn_log)
            f.write("\n")

        if not self.err_log and not self.wrn_log:
            print("No errors found")
        
        f.write(tabulate(self.resolution_table, headers=["Line", "Ref", "Decl"]))
        f.close()