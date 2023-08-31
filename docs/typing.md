[Back to README](../README.md)
# Typing system for Tiny
Typing system methods are located in __TinyTyping.py__ and contain methods for:
1. Type detection of literals
2. Overflow checks for assignments and binary operations
3. Operation results calculation for future overflow checks

Those methods are used in the [main logic file](./main_logic.md) to perform necessary type and overflow checks.

Literal types have to be detected based on the contents since all literals (except for _float_) are strings after tokenization and parsing.

Overflow checks are done through calculation and comparison by taking the following limits into account:
* 0 <= __int16__ <= 65535
* 1.175494351e-38 <= __float32__ <= 3.402823466e+38 _or_ __float32__ == 0
* 32 <= __char8 symbol code__ <= 255