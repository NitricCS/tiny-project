# Type system for Tiny
#
# Kirill Borisov, 108144

class TinyTyping():
    def is_of_same_type(self, type1, type2):
        if type1 == type2:
            return True
        return False
    
    def get_literal_type(self, literal: str):
        if 'float' in str(type(literal)):
            return "float"
        elif literal.isnumeric():
            return "int"
        elif (literal == "true") or (literal == "false"):
            return "bool"
        else:
            return "char"
    
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
                    if float(value1) - float(value2) < 1.175494351e-38:
                        return True
                if operator == "*":
                    if float(value1) * float(value2) > 3.402823466e+38:
                        return True
                if operator == "/":
                    if float(value1) / float(value2) < 1.175494351e-38:
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
                    return int(value1) / int(value2)
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