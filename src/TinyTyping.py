# Type system for Tiny
#
# Kirill Borisov, 108144

class TinyTyping():
    # Method to check if types are the same
    def is_of_same_type(self, type1, type2):
        if type1 == type2:
            return True
        return False
    
    # Method to detect a type of a literal
    def get_literal_type(self, literal: str):
        if 'float' in str(type(literal)):          # floats are detected while parsing
            return "float"
        elif literal.isnumeric():                  # only true if value can be converted to a number
            return "int"
        elif (literal == "true") or (literal == "false"):   # detect bool
            return "bool"
        else:                # only char is possible if nothing else is true; any other option isn't allowed by a lexer
            return "char"
    
    # Method to check for overflows on assignment
    def overflow_check_assign(self, vartype, value):
        match vartype:
            case "int":                   # limits for unsigned int16
                if int(value) > 65535 or int(value) < 0:
                    return True
            case "float":                 # limits for float32
                if float(value) > 3.402823466e+38 or (float(value) < 1.175494351e-38 and float(value) != 0):
                    return True
            case "char":                  # characters below 32 are irrelevant, and above is beyond char8
                if ord(value) > 255 or ord(value) < 32:
                    return True
        return False
    
    # Method to check for overflows on arithmetics
    def overflow_check(self, vartype, value1, value2, operator):
        match vartype:
            case "int":
                if operator == "+":
                    if int(value1) + int(value2) > 65535:
                        return True
                if operator == "-":
                    if int(value1) - int(value2) < 0:
                        return True
                if operator == "*":
                    if int(value1) * int(value2) > 65535:
                        return True
            case "float":
                if operator == "+":
                    if float(value1) + float(value2) > 3.402823466e+38:
                        return True
                if operator == "-":
                    if (float(value1) - float(value2) < 1.175494351e-38) and (float(value1) - float(value2) != 0):
                        return True
                if operator == "*":
                    if float(value1) * float(value2) > 3.402823466e+38:
                        return True
                if operator == "/":                # float can overflow both ways on division
                    if (float(value1) - float(value2) < 1.175494351e-38) and (float(value1) - float(value2) != 0):
                        return True
                    if float(value1) * float(value2) > 3.402823466e+38:
                        return True
            case "char":
                if operator == "+":
                    if ord(value1) + ord(value2) > 255:
                        return True
                if operator == "-":
                    if ord(value1) - ord(value2) < 32:
                        return True
                if operator == "*":
                    if ord(value1) * ord(value2) > 255:
                        return True
                if operator == "/":
                    if int(ord(value1) / ord(value2)) < 32:
                        return True
        return False
    
    # Method to calculate operation results for the values hashtable
    def calculate(self, vartype, value1, value2, operator):
        match vartype:
            case "int":
                if operator == "+":
                    return int(value1) + int(value2)
                if operator == "-":
                    return int(value1) - int(value2)
                if operator == "*":
                    return int(value1) * int(value2)
                if operator == "/":
                    return int(int(value1) / int(value2))
            case "float":
                if operator == "+":
                    return float(value1) + float(value2)
                if operator == "-":
                    return float(value1) - float(value2)
                if operator == "*":
                    return float(value1) * float(value2)
                if operator == "/":
                    return float(value1) / float(value2)
            case "char":
                if operator == "+":
                    return chr(ord(value1) + ord(value2))
                if operator == "-":
                    return chr(ord(value1) - ord(value2))
                if operator == "*":
                    return chr(ord(value1) * ord(value2))
                if operator == "/":
                    return chr(int(ord(value1) / ord(value2)))
        return -1