import re
from enum import Enum, unique


@unique
class State(Enum):
    Program = 0
    Declaration_list = 1
    Declaration = 2
    Declaration_initial = 3
    Declaration_prime = 4
    Var_declaration_prime = 5
    Fun_declaration_prime = 6
    Type_specifier = 7
    Params = 8
    Param_list_void_abtar = 9
    Param_list = 10
    Param = 11
    Param_prime = 12
    Compound_stmt = 13
    Statement_list = 14
    Statement = 15
    Expression_stmt = 16
    Selection_stmt = 17
    Iteration_stmt = 18
    Return_stmt = 19
    Return_stmt_prime = 20
    Switch_stmt = 21
    Case_stmts = 22
    Case_stmt = 23
    Default_stmt = 24
    Expression = 25
    B = 26
    H = 27
    Simple_expression_zegond = 28
    Simple_expression_prime = 29
    C = 30
    Relop = 31
    Additive_expression = 32
    Additive_expression_prime = 33
    Additive_expression_zegond = 34
    D = 35
    Addop = 36
    Term = 37
    Term_prime = 38
    Term_zegond = 39
    G = 40
    Factor = 41
    Var_call_prime = 42
    Var_prime = 43
    Factor_prime = 44
    Factor_zegond = 45
    Args = 46
    Arg_list = 47
    Arg_list_prime = 48

first_of_non_terminals = {
    "Program"                       : "int",
    "Declaration-list"              : "int",
    "Declaration"                   : "int",
    "Declaration-initial"           : "int",
    "Declaration-prime"             : ";",
    "Var-declaration-prime"         : ";",
    "Fun-declaration-prime"         : "(void) {int ID;}",
    "Type-specifier"                : "int",
    "Params"                        : "void",
    "Param-list"                    : ", int ID",
    "Param"                         : "int ID",
    "Param-prime"                   : "[]",
    "Compound-stmt"                 : "{int ID;}",
    "Statement-list"                : ";",
    "Statement"                     : ";",
    "Expression-stmt"               : ";",
    "Selection-stmt"                : "if (NUM); else;",
    "Else-stmt"                     : "if (NUM); else;",
    "Iteration-stmt"                : "while (NUM);",
    "Return-stmt"                   : "return;",
    "Return-stmt-prime"             : ";",
    "Expression"                    : ";",
    "B"                             : r'=|[',
    "H"                             : "NUM",
    "Simple-expression-zegond"      : "NUM",
    "Simple-expression-prime"       : "()",
    "C"                             : "< NUM",
    "Relop"                         : "<",
    "Additive-expression"           : "NUM",
    "Additive-expression-prime"     : "()",
    "Additive-expression-zegond"    : "NUM",
    "D"                             : "+ NUM",
    "Addop"                         : "+",
    "Term"                          : "NUM",
    "Term-prime"                    : "()",
    "Term-zegond"                   : "NUM",
    "G"                             : "* NUM",
    "Factor"                        : "NUM",
    "Var-call-prime"                : "()",
    "Var-prime"                     : "[NUM]",
    "Factor-prime"                  : "()",
    "Factor-zegond"                 : "NUM",
    "Args"                          : "NUM",
    "Arg-list"                      : "NUM",
    "Arg-list-prime"                : ", NUM",
}



class Parser(object):
    def __init__(self, next_token):
        self.token = next_token

    def parser(self, token):
        if token == "int":

        elif token ==


