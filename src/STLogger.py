# Logger Module for Symbol Table
#
# Kirill Borisov, 108144

from os import path
from tabulate import tabulate

class STLogger():
    table_ostream = []
    resolution_table = []
    err_log = ""

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
        new_log = "ERROR: Reference " + variable + " in line " + str(line) + " is not declared within the scope of use\n"
        self.err_log = self.err_log + new_log
    
    # Duplicate declaration error log
    def log_insertion_error(self, variable, line):
        new_log = "ERROR: Duplicate declaration of reference " + variable + " in current scope (line " + str(line) + ")\n"
        self.err_log = self.err_log + new_log
    
    def make_log(self):
        f = open(self.path, "w", encoding="utf-8")
        for scope in self.table_ostream:
            txt = str(scope) + "\n"
            f.write(txt)
        f.write("\n")
        f.write(self.err_log)
        f.write("\n")
        f.write(tabulate(self.resolution_table, headers=["Line", "Ref", "Decl"]))
        f.close()