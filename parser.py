import re
from anytree import Node, RenderTree, PreOrderIter
from enum import Enum, unique


@unique
class Transition(Enum):
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
    Else_stmt = 18
    Iteration_stmt = 19
    Return_stmt = 20
    Return_stmt_prime = 21
    Switch_stmt = 22
    Case_stmts = 23
    Case_stmt = 24
    Default_stmt = 25
    Expression = 26
    B = 27
    H = 28
    Simple_expression_zegond = 29
    Simple_expression_prime = 30
    C = 31
    Relop = 32
    Additive_expression = 33
    Additive_expression_prime = 34
    Additive_expression_zegond = 35
    D = 36
    Addop = 37
    Term = 38
    Term_prime = 39
    Term_zegond = 40
    G = 41
    Factor = 42
    Var_call_prime = 43
    Var_prime = 44
    Factor_prime = 45
    Factor_zegond = 46
    Args = 47
    Arg_list = 48
    Arg_list_prime = 49


non_terminals = {
    'Program': [['Declaration-list', '$']],
    'Declaration-list': [['Declaration', 'Declaration-list'], ['EPSILON']],
    'Declaration': [['Declaration-initial', 'Declaration-prime']],
    'Declaration-initial': [['Type-specifier', 'ID']],
    'Declaration-prime': [['Fun-declaration-prime'], ['Var-declaration-prime']],
    'Var-declaration-prime': [[';'], ['[', 'NUM', ']', ';']],
    'Fun-declaration-prime': [['(', 'Params', ')', 'Compound-stmt']],
    'Type-specifier': [['int'], ['void']],
    'Params': [['int', 'ID', 'Param-prime', 'Param-list'], ['void']],
    'Param-list': [[',', 'Param', 'Param-list'], ['EPSILON']],
    'Param': [['Declaration-initial', 'Param-prime']],
    'Param-prime': [['[', ']'], ['EPSILON']],
    'Compound-stmt': [['{', 'Declaration-list', 'Statement-list', '}']],
    'Statement-list': [['Statement', 'Statement-list'], ['EPSILON']],
    'Statement': [['Expression-stmt'], ['Compound-stmt'], ['Selection-stmt'], ['Iteration-stmt'], ['Return-stmt']],
    'Expression-stmt': [['Expression', ';'], ['break', ';'], [';']],
    'Selection-stmt': [['if', '(', 'Expression', ')', 'Statement', 'Else-stmt']],
    'Else-stmt': [['endif'], ['else', 'Statement', 'endif']],
    'Iteration-stmt': [['repeat', 'Statement', 'until', '(', 'Expression', ')']],
    'Return-stmt': [['return', 'Return-stmt-prime']],
    'Return-stmt-prime': [[';'], ['Expression', ';']],
    'Expression': [['Simple-expression-zegond'], ['ID', 'B']],
    'B': [['=', 'Expression'], ['[', 'Expression', ']', 'H'], ['Simple-expression-prime']],
    'H': [['=', 'Expression'], ['G', 'D', 'C']],
    'Simple-expression-zegond': [['Additive-expression-zegond', 'C']],
    'Simple-expression-prime': [['Additive-expression-prime', 'C']],
    'C': [['Relop', 'Additive-expression'], ['EPSILON']],
    'Relop': [['<'], ['==']],
    'Additive-expression': [['Term', 'D']],
    'Additive-expression-prime': [['Term-prime', 'D']],
    'Additive-expression-zegond': [['Term-zegond', 'D']],
    'D': [['Addop', 'Term', 'D'], ['EPSILON']],
    'Addop': [['+'], ['-']],
    'Term': [['Factor', 'G']],
    'Term-prime': [['Factor-prime', 'G']],
    'Term-zegond': [['Factor-zegond', 'G']],
    'G': [['*', 'Factor', 'G'], ['EPSILON']],
    'Factor': [['(', 'Expression', ')'], ['ID', 'Var-call-prime'], ['NUM']],
    'Var-call-prime': [['(', 'Args', ')'], ['Var-prime']],
    'Var-prime': [['[', 'Expression', ']'], ['EPSILON']],
    'Factor-prime': [['(', 'Args', ')'], ['EPSILON']],
    'Factor-zegond': [['(', 'Expression', ')'], ['NUM']],
    'Args': [['Arg-list'], ['EPSILON']],
    'Arg-list': [['Expression', 'Arg-list-prime']],
    'Arg-list-prime': [[',', 'Expression', 'Arg-list-prime'], ['EPSILON']]
}

first_of_non_terminals = {
    'Program': ['$', 'int', 'void'],
    'Declaration-list': ['EPSILON', 'int', 'void'],
    'Declaration': ['int', 'void'],
    'Declaration-initial': ['int', 'void'],
    'Declaration-prime': ['(', ';', '['],
    'Var-declaration-prime': [';', '['],
    'Fun-declaration-prime': ['('],
    'Type-specifier': ['int', 'void'],
    'Params': ['int', 'void'],
    'Param-list': [',', 'EPSILON'],
    'Param': ['int', 'void'],
    'Param-prime': ['[', 'EPSILON'],
    'Compound-stmt': ['{'],
    'Statement-list': ['EPSILON', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
    'Statement': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
    'Expression-stmt': ['break', ';', 'ID', '(', 'NUM'],
    'Selection-stmt': ['if'],
    'Else-stmt': ['endif', 'else'],
    'Iteration-stmt': ['repeat'],
    'Return-stmt': ['return'],
    'Return-stmt-prime': [';', 'ID', '(', 'NUM'],
    'Expression': ['ID', '(', 'NUM'],
    'B': ['=', '[', '(', '*', '+', '-', '<', '==', 'EPSILON'],
    'H': ['=', '*', 'EPSILON', '+', '-', '<', '=='],
    'Simple-expression-zegond': ['(', 'NUM'],
    'Simple-expression-prime': ['(', '*', '+', '-', '<', '==', 'EPSILON'],
    'C': ['EPSILON', '<', '=='],
    'Relop': ['<', '=='],
    'Additive-expression': ['(', 'ID', 'NUM'],
    'Additive-expression-prime': ['(', '*', '+', '-', 'EPSILON'],
    'Additive-expression-zegond': ['(', 'NUM'],
    'D': ['EPSILON', '+', '-'],
    'Addop': ['+', '-'],
    'Term': ['(', 'ID', 'NUM'],
    'Term-prime': ['(', '*', 'EPSILON'],
    'Term-zegond': ['(', 'NUM'],
    'G': ['*', 'EPSILON'],
    'Factor': ['(', 'ID', 'NUM'],
    'Var-call-prime': ['(', '[', 'EPSILON'],
    'Var-prime': ['[', 'EPSILON'],
    'Factor-prime': ['(', 'EPSILON'],
    'Factor-zegond': ['(', 'NUM'],
    'Args': ['EPSILON', 'ID', '(', 'NUM'],
    'Arg-list': ['ID', '(', 'NUM'],
    'Arg-list-prime': [',', 'EPSILON']
}

follow_of_non_terminals = {
    'Program': [],
    'Declaration-list': ['$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}'],
    'Declaration': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}'],
    'Declaration-initial': ['(', ';', '[', ',', ')'],
    'Declaration-prime': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}'],
    'Var-declaration-prime': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}'],
    'Fun-declaration-prime': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}'],
    'Type-specifier': ['ID'],
    'Params': [')'],
    'Param-list': [')'],
    'Param': [',', ')'],
    'Param-prime': [',', ')'],
    'Compound-stmt': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif',
                      'else', 'until'],
    'Statement-list': ['}'],
    'Statement': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Expression-stmt': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Selection-stmt': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Else-stmt': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Iteration-stmt': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Return-stmt': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Return-stmt-prime': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif', 'else', 'until'],
    'Expression': [';', ')', ']', ','],
    'B': [';', ')', ']', ','],
    'H': [';', ')', ']', ','],
    'Simple-expression-zegond': [';', ')', ']', ','],
    'Simple-expression-prime': [';', ')', ']', ','],
    'C': [';', ')', ']', ','],
    'Relop': ['(', 'ID', 'NUM'],
    'Additive-expression': [';', ')', ']', ','],
    'Additive-expression-prime': ['<', '==', ';', ')', ']', ','],
    'Additive-expression-zegond': ['<', '==', ';', ')', ']', ','],
    'D': ['<', '==', ';', ')', ']', ','],
    'Addop': ['(', 'ID', 'NUM'],
    'Term': ['+', '-', ';', ')', '<', '==', ']', ','],
    'Term-prime': ['+', '-', '<', '==', ';', ')', ']', ','],
    'Term-zegond': ['+', '-', '<', '==', ';', ')', ']', ','],
    'G': ['+', '-', '<', '==', ';', ')', ']', ','],
    'Factor': ['*', '+', '-', ';', ')', '<', '==', ']', ','],
    'Var-call-prime': ['*', '+', '-', ';', ')', '<', '==', ']', ','],
    'Var-prime': ['*', '+', '-', ';', ')', '<', '==', ']', ','],
    'Factor-prime': ['*', '+', '-', '<', '==', ';', ')', ']', ','],
    'Factor-zegond': ['*', '+', '-', '<', '==', ';', ')', ']', ','],
    'Args': [')'],
    'Arg-list': [')'],
    'Arg-list-prime': [')']
}

parse_tree_file = open('parse_tree.txt', 'w')
syntax_errors_file = open('syntax_errors.txt', 'w')
pointer = 1
syntax_file_pointer = 0


# def is_terminal(procedure):
#     return not (procedure in non_terminals.keys())


def numbering_syntax_error_lines():
    global syntax_file_pointer
    if pointer != syntax_file_pointer:
        if syntax_file_pointer != 0:
            syntax_errors_file.write("\n")
        syntax_errors_file.write("#" + str(pointer) + " : ")
        syntax_file_pointer = pointer


def add_syntax_error(error_type, lexeme, non_terminal):
    line_number = 0
    if error_type == "follow":
        syntax_errors_file.write("illegal " + lexeme + " found on line" + line_number)
    else:
        syntax_errors_file.write("missing " + non_terminal + " on line" + line_number)


current_state = Transition.Program
current_num = 0
can_get_token = True
syntax_error = False
scanner = []
root = Node('Program')

# MAIN PART // TODO
token = scanner.get_next_token()


def procedure_is_terminal(procedure):
    return not (procedure in non_terminals.keys())


def token_matches_branch(branch):
    for value in branch:
        is_terminal = procedure_is_terminal(value)
        if is_terminal:
            if token.value == value or token.type == value:
                return True
            return False
        else:
            if token in first_of_non_terminals[value]:
                return True
            if 'EPSILON' not in first_of_non_terminals[value]:
                return False
    return True


def program_procedure():
    global token

    procedure = 'Program'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):

        child = declaration_list_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == '$':
            child = Node('$', parent=root)

        return root
    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def declaration_list_procedure():
    global token

    procedure = 'Declaration-list'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = declaration_procedure()
        child.parent = root
        token = scanner.get_next_token()
        child = declaration_list_procedure()
        child.parent = root
    else:
        child = Node('epsilon', root)

    return root


def declaration_procedure():
    global token

    procedure = 'Declaration'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = declaration_initial_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = declaration_prime_procedure()
        child.parent = root
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def declaration_initial_procedure():
    global token

    procedure = 'Declaration-initial'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = type_specifier_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.type == 'ID':
            child = Node(f"(ID, {token.value})", parent=root)
        else:
            pass
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def declaration_prime_procedure():
    global token

    procedure = 'Declaration-prime'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = fun_declaration_prime_procedure()
        child.parent = root
        return root
    if token_matches_branch(non_terminals[1]):
        child = var_declaration_prime_procedure()
        child.parent = root
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def var_declaration_prime_procedure():
    global token

    procedure = 'Var-declaration-prime'
    root = Node(procedure)

    if token_matches_branch(non_terminals[0]):
        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass
        return root
    if token_matches_branch(non_terminals[1]):
        if token.value == '[':
            child = Node('(SYMBOL, [)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.type == 'NUM':
            child = Node(f"(NUM, {token.value})", parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.value == ']':
            child = Node('(SYMBOL, ])', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def fun_declaration_prime_procedure():
    global token

    procedure = 'Fun-declaration-prime'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == '(':
            child = Node('(SYMBOL, ()', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = params_procedure()
        child.parent = root

        if token.value == ')':
            child = Node('(SYMBOL, ))', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = compound_stmt_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def type_specifier_procedure():
    global token
    procedure = 'Type-specifier'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == 'int':
            child = Node('(KEYWORD, int)', parent=root)
        else:
            pass
        return root
    if token_matches_branch(non_terminals[procedure][1]):
        if token.value == 'void':
            child = Node('(KEYWORD, void)', parent=root)
        else:
            pass
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def params_procedure():
    global token
    procedure = 'Params'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == 'int':
            child = Node('(KEYWORD, int)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.type == 'ID':
            child = Node(f"(ID, {token.value})", parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = param_prime_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = param_list_procedure()
        child.parent = root

        return root
    if token_matches_branch(non_terminals[procedure][1]):
        if token.value == 'void':
            child = Node('(KEYWORD, void)', parent=root)
        else:
            pass
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def param_list_procedure():
    global token

    procedure = 'Param-list'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == ',':
            child = Node('(SYMBOL, ,)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = param_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = param_list_procedure()
        child.parent = root

        return root

    child = Node('epsilon', parent=root)
    return root


def param_procedure():
    global token

    procedure = 'Param'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = declaration_initial_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = param_prime_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def param_prime_procedure():
    global token

    procedure = 'Param-prime'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure[0]]):
        if token.value == '[':
            child = Node('(SYMBOL, [)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.value == ']':
            child = Node('(SYMBOL, ])', parent=root)
        else:
            pass

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def compound_stmt_procedure():
    global token

    procedure = 'Compound-stmt'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == '{':
            child = Node('(SYMBOL, {)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = declaration_list_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = statement_list_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == '}':
            child = Node('(SYMBOL, }', parent=root)
        else:
            pass
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def statement_list_procedure():
    global token

    procedure = 'Statement-list'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = statement_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = statement_list_procedure()
        child.parent = root

        return root

    child = Node('epsilon', parent=root)
    return root


def statement_procedure():
    global token

    procedure = 'Statement'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = expression_stmt_procedure()
        child.parent = root

        return root

    if token_matches_branch(non_terminals[procedure][1]):
        child = compound_stmt_procedure()
        child.parent = root

        return root

    if token_matches_branch(non_terminals[procedure][2]):
        child = selection_stmt_procedure()
        child.parent = root

        return root

    if token_matches_branch(non_terminals[procedure][3]):
        child = iteration_stmt_procedure()
        child.parent = root

        return root

    if token_matches_branch(non_terminals[procedure][4]):
        child = return_stmt_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def expression_stmt_procedure():
    global token

    procedure = 'Expression-stmt'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = expression_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass
        return root
    if token_matches_branch(non_terminals[procedure][1]):
        if token.value == 'break':
            child = Node('(KEYWORD, break)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass
        return root
    if token_matches_branch(non_terminals[procedure][2]):
        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def selection_stmt_procedure():
    global token

    procedure = 'Selection-stmt'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == 'if':
            child = Node('(KEYWORD, if)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.value == '(':
            child = Node('(SYMBOL, ()', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = expression_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == ')':
            child = Node('(SYMBOL, ))', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = statement_procedure()
        child.parent = root

        token = scanner.get_next_token()
        child = else_stmt_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def else_stmt_procedure():
    global token

    procedure = 'Else-stmt'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == 'endif':
            child = Node('(KEYWORD, endif)', parent=root)
        else:
            pass

        return root
    if token_matches_branch(non_terminals[procedure][1]):
        if token.value == 'else':
            child = Node('(KEYWORD, else)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = statement_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == 'endif':
            child = Node('(KEYWORD, endif)', parent=root)
        else:
            pass
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def iteration_stmt_procedure():
    global token

    procedure = 'Iteration-stmt'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == 'repeat':
            child = Node('(KEYWORD, repeat)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = statement_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == 'until':
            child = Node('(KEYWORD, until)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        if token.value == '(':
            child = Node('(SYMBOL, ()', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = expression_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == ')':
            child = Node('(SYMBOL, ))', parent=root)
        else:
            pass

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def return_stmt_procedure():
    global token

    procedure = 'Return-stmt'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == 'return':
            child = Node('(KEYWORD, return)', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = return_stmt_prime_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def return_stmt_prime_procedure():
    global token

    procedure = 'Return-stmt-prime'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass

        return root
    if token_matches_branch(non_terminals[procedure][1]):
        child = expression_procedure()
        child.parent = root

        token = scanner.get_next_token()
        if token.value == ';':
            child = Node('(SYMBOL, ;)', parent=root)
        else:
            pass

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def expression_procedure():
    global token

    procedure = 'Expression'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        child = simple_expression_zegond_procedure()
        child.parent = root
        return root
    if token_matches_branch(non_terminals[procedure][1]):
        if token.type == 'ID':
            child = Node(f"(ID, {token.value})", parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = b_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def b_procedure():
    global token

    procedure = 'B'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == '=':
            child = Node(f"(ID, {token.value})", parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = expression_procedure()
        child.parent = root
        return root

    if token_matches_branch(non_terminals[procedure][1]):
        if token.type == '[':
            child = Node(f"(ID, {token.value})", parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = expression_procedure()
        child.parent = root

        if token.value == ']':
            child = Node('(SYMBOL, ])', parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = h_procedure()
        child.parent = root

        return root

    if token_matches_branch(non_terminals[procedure][2]):
        child = simple_expression_prime_procedure()
        child.parent = root
        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass


def h_procedure():
    global token

    procedure = 'H'
    root = Node(procedure)

    if token_matches_branch(non_terminals[procedure][0]):
        if token.value == '=':
            child = Node(f"(ID, {token.value})", parent=root)
            token = scanner.get_next_token()
        else:
            pass

        child = expression_procedure()
        child.parent = root
        return root

    if token_matches_branch(non_terminals[procedure][1]):
        child = g_procedure()
        child.parent = root

        child = d_procedure()
        child.parent = root

        child = c_procedure()
        child.parent = root

        return root

    if token in follow_of_non_terminals[procedure]:
        pass
    else:
        pass

def simple_expression_zegond():
    if token_matches_branch(non_terminals[procedure][1]):
        child = g_procedure()
        child.parent = root



# TODO


scanner.close_file()


def parser(token):
    global current_state, current_num, can_get_token, root
    token_type, lexeme = token

    if current_state == Transition.Program:
        if current_num == 0:
            if token_type in first_of_non_terminals["Declaration-list"]:
                current_state = Transition.Declaration_list
                child = Node('Declaration-list', parent=root)
                if token_type == "$":
                    child = Node('$', parent=root)
                    if syntax_error:
                        syntax_errors_file.write('\n')
                    else:
                        syntax_errors_file.write("There is no syntax error.")
                        return

            elif token_type in follow_of_non_terminals["Declaration-list"]:
                pass
            else:
                pass

    elif current_state == Transition.Declaration_list:
        if current_num == 0:
            if token_type in first_of_non_terminals["Declaration"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration-list"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Declaration-list"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration-list"]:
                pass
            else:
                pass

    elif current_state == Transition.Declaration:
        if current_num == 0:
            if token_type in first_of_non_terminals["Declaration-initial"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration-initial"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Declaration-initial"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration-initial"]:
                pass
            else:
                pass

    elif current_state == Transition.Declaration_initial:
        if current_num == 0:
            if token_type in first_of_non_terminals["Type-specifier"]:
                pass
            elif token_type in follow_of_non_terminals["Type-specifier"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["ID"]:
                pass
            elif token_type in follow_of_non_terminals["ID"]:
                pass
            else:
                pass

    elif current_state == Transition.Declaration_prime:
        if current_num == 0:
            if token_type in first_of_non_terminals["Fun-declaration-prime"]:
                pass
            elif token_type in first_of_non_terminals["Var-declaration-prime"]:
                pass
            elif token_type in follow_of_non_terminals["Fun-declaration-prime"]:
                pass
            elif token_type in follow_of_non_terminals["Var-declaration-prime"]:
                pass
            else:
                pass

    elif current_state == Transition.Var_declaration_prime:
        if current_num == 0:
            if lexeme == "[":
                pass
            elif lexeme == ";":
                pass
            else:
                pass
        elif current_num == 1:
            if token_type == "NUM":
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == "]":
                pass
            else:
                pass
        elif current_num == 3:
            if lexeme == ";":
                pass
            else:
                pass

    elif current_state == Transition.Fun_declaration_prime:
        if current_num == 0:
            if lexeme == "(":
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Params"]:
                pass
            elif token_type in follow_of_non_terminals["Params"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == ")":
                current_num = 3
            else:
                pass
        elif current_num == 3:
            if token_type in first_of_non_terminals["Compound-stmt"]:
                pass
            elif token_type in follow_of_non_terminals["Compound-stmt"]:
                pass
            else:
                pass

    elif current_state == Transition.Type_specifier:
        if current_num == 0:
            if lexeme == "int":
                pass
            elif lexeme == "void":
                pass
            else:
                pass

    elif current_state == Transition.Params:
        if current_num == 0:
            if lexeme == "int":
                pass
            elif lexeme == "void":
                pass
            else:
                pass
        elif current_num == 1:
            if token_type == "ID":
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["Param-prime"]:
                pass
            elif token_type in follow_of_non_terminals["Param-prime"]:
                pass
            else:
                pass
        elif current_num == 3:
            if token_type in first_of_non_terminals["Param-list"]:
                pass
            elif token_type in follow_of_non_terminals["Param-list"]:
                pass
            else:
                pass

    elif current_state == Transition.Param_list:
        if current_num == 0:
            if lexeme == ",":
                pass
            elif token_type in follow_of_non_terminals["Param-list"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Param"]:
                pass
            elif token_type in follow_of_non_terminals["Param"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["Param-list"]:
                pass
            elif token_type in follow_of_non_terminals["Param-list"]:
                pass
            else:
                pass

    elif current_state == Transition.Param:
        if current_num == 0:
            if token_type in first_of_non_terminals["Declaration-initial"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration-initial"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Param-prime"]:
                pass
            elif token_type in follow_of_non_terminals["Param-prime"]:
                pass
            else:
                pass

    elif current_state == Transition.Param_prime:
        if current_state == 0:
            if lexeme == "[":
                pass
            elif token_type in follow_of_non_terminals["Param-prime"]:
                pass
            else:
                pass
        if current_state == 1:
            if lexeme == "]":
                pass
            else:
                pass

    elif current_state == Transition.Compound_stmt:
        if current_num == 0:
            if lexeme == "{":
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Declaration-list"]:
                pass
            elif token_type in follow_of_non_terminals["Declaration-list"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["Statement-list"]:
                pass
            elif token_type in follow_of_non_terminals["Statement-list"]:
                pass
            else:
                pass
        elif current_num == 3:
            if lexeme == "}":
                pass
            else:
                pass

    elif current_state == Transition.Statement_list:
        if current_num == 0:
            if token_type in first_of_non_terminals["Statement"]:
                pass
            elif token_type in follow_of_non_terminals["Statement"]:
                pass
            elif token_type in follow_of_non_terminals["Statement-list"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in follow_of_non_terminals["Statement-list"]:
                pass
            elif token_type in follow_of_non_terminals["Statement-list"]:
                pass
            else:
                pass

    elif current_state == Transition.Statement:
        if current_num == 0:
            if token_type in first_of_non_terminals["Expression-stmt"]:
                pass
            elif token_type in follow_of_non_terminals["Expression-stmt"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in follow_of_non_terminals["Compound-stmt"]:
                pass
            elif token_type in follow_of_non_terminals["Compound-stmt"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in follow_of_non_terminals["Selection-stmt"]:
                pass
            elif token_type in follow_of_non_terminals["Selection-stmt"]:
                pass
            else:
                pass
        elif current_num == 3:
            if token_type in follow_of_non_terminals["Iteration-stmt"]:
                pass
            elif token_type in follow_of_non_terminals["Iteration-stmt"]:
                pass
            else:
                pass
        elif current_num == 4:
            if token_type in follow_of_non_terminals["Return-stmt"]:
                pass
            elif token_type in follow_of_non_terminals["Return-stmt"]:
                pass
            else:
                pass

    elif current_state == Transition.Expression_stmt:
        if current_num == 0:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                current_num = 1
                pass
            elif lexeme == "break":
                current_num = 2
                pass
            elif lexeme == ";":
                current_num = 3
                pass
            else:
                pass
        elif current_num == 1:
            if lexeme == ";":
                current_num = 3
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == ";":
                current_num = 3
                pass
            else:
                pass

    elif current_state == Transition.Selection_stmt:
        if current_num == 0:
            if lexeme == "if":
                current_num = 1
                pass
            else:
                pass
        elif current_num == 1:
            if lexeme == "(":
                current_num = 2
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 3
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 3:
            if lexeme == ")":
                current_num = 4
                pass
            else:
                pass
        elif current_num == 4:
            if token_type in first_of_non_terminals["Statement"]:
                current_num = 5
                pass
            elif token_type in follow_of_non_terminals["Statement"]:
                pass
            else:
                pass
        elif current_num == 5:
            if token_type in first_of_non_terminals["Else-stmt"]:
                current_num = 6
                pass
            elif token_type in follow_of_non_terminals["Else-stmt"]:
                pass
            else:
                pass

    elif current_state == Transition.Else_stmt:
        if current_num == 0:
            if lexeme == "else":
                current_num = 1
                pass
            elif lexeme == "endif":
                current_num = 3
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Statement"]:
                current_num = 2
                pass
            elif token_type in first_of_non_terminals["Statement"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == "endif":
                current_num = 3
                pass
            else:
                pass

    elif current_state == Transition.Iteration_stmt:
        if current_num == 0:
            if lexeme == "repeat":
                current_num = 1
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Statement"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Statement"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == "until":
                current_num = 3
                pass
            else:
                pass
        elif current_num == 3:
            if lexeme == "(":
                current_num = 4
                pass
            else:
                pass
        elif current_num == 4:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 5
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 5:
            if lexeme == ")":
                current_num = 6
                pass
            else:
                pass

    elif current_state == Transition.Return_stmt:
        if current_num == 0:
            if lexeme == "return":
                current_num = 1
                pass
            else:
                pass
        if current_num == 1:
            if token_type in first_of_non_terminals["Return-stmt-prime"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Return-stmt-prime"]:
                pass
            else:
                pass

    elif current_state == Transition.Return_stmt_prime:
        if current_num == 0:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            elif lexeme == ";":
                current_num = 2
                pass
            else:
                pass
        if current_num == 1:
            if lexeme == ";":
                current_num = 2
                pass
            else:
                pass
    elif current_state == Transition.Expression:
        if current_num == 0:
            if token_type == "ID":
                current_num = 1
                pass
            elif token_type in first_of_non_terminals["Simple-expression-zegond"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Simple-expression-zegond"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["B"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["B"]:
                pass
            else:
                pass

    elif current_state == Transition.B:
        if current_num == 0:
            if lexeme == "[":
                current_num = 1
                pass
            elif lexeme == "=":
                current_num = 4
                pass
            elif token_type in first_of_non_terminals["Simple-expression-prime"]:
                current_num = 5
                pass
            elif token_type in follow_of_non_terminals["Simple-expression-prime"]:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == "]":
                current_num = 3
                pass
            else:
                pass
        elif current_num == 3:
            if token_type in first_of_non_terminals["H"]:
                current_num = 5
                pass
            elif token_type in follow_of_non_terminals["H"]:
                pass
            else:
                pass
        elif current_num == 4:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 5
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass

    elif current_state == Transition.H:
        if current_num == 0:
            if lexeme == "=":
                current_num = 1
            elif token_type in first_of_non_terminals["G"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["G"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 4
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["D"]:
                current_num = 3
                pass
            elif token_type in follow_of_non_terminals["D"]:
                pass
            else:
                pass
        elif current_num == 3:
            if token_type in first_of_non_terminals["C"]:
                current_num = 4
                pass
            elif token_type in follow_of_non_terminals["C"]:
                pass
            else:
                pass

    elif current_state == Transition.Simple_expression_zegond:
        if current_num == 0:
            if token_type in first_of_non_terminals["Additive-expression-zegond"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Additive-expression-zegond"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["C"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["C"]:
                pass
            else:
                pass

    elif current_state == Transition.Simple_expression_prime:
        if current_num == 0:
            if token_type in first_of_non_terminals["Additive-expression-prime"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Additive-expression-prime"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["C"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["C"]:
                pass
            else:
                pass

    elif current_state == Transition.C:
        if current_num == 0:
            if token_type in first_of_non_terminals["Relop"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Relop"]:
                pass
            elif token_type in follow_of_non_terminals["C"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Additive-expression"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Additive-expression"]:
                pass
            else:
                pass
    elif current_state == Transition.Relop:
        if current_num == 0:
            if lexeme == "<":
                current_num = 1
                pass
            elif lexeme == "==":
                current_num = 1
                pass
            else:
                pass

    elif current_state == Transition.Additive_expression:
        if current_num == 0:
            if token_type in first_of_non_terminals["Term"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Term"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["D"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["D"]:
                pass
            else:
                pass

    elif current_state == Transition.Additive_expression_prime:
        if current_num == 0:
            if token_type in first_of_non_terminals["Term-prime"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Term-prime"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["D"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["D"]:
                pass
            else:
                pass

    elif current_state == Transition.Additive_expression_zegond:
        if current_num == 0:
            if token_type in first_of_non_terminals["Term-zegond"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Term-zegond"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["D"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["D"]:
                pass
            else:
                pass

    elif current_state == Transition.D:
        if current_num == 0:
            if token_type in first_of_non_terminals["Addop"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Addop"]:
                pass
            elif token_type in follow_of_non_terminals["D"]:
                current_num = 3
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Term"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Term"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["D"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["D"]:
                pass
            else:
                pass

    elif current_state == Transition.Addop:
        if current_num == 0:
            if lexeme == "+":
                current_num = 1
                pass
            elif lexeme == "-":
                current_num = 1
                pass
            else:
                pass

    elif current_state == Transition.Term:
        if current_num == 0:
            if token_type in first_of_non_terminals["Factor"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Factor"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["G"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["G"]:
                pass
            else:
                pass

    elif current_state == Transition.Term_prime:
        if current_num == 0:
            if token_type in first_of_non_terminals["Factor-prime"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Factor-prime"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["G"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["G"]:
                pass
            else:
                pass

    elif current_state == Transition.Term_zegond:
        if current_num == 0:
            if token_type in first_of_non_terminals["Factor-zegond"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Factor-zegond"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["G"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["G"]:
                pass
            else:
                pass

    elif current_state == Transition.G:
        if current_num == 0:
            if lexeme == "*":
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["G"]:
                current_num = 3
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Factor"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Factor"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["G"]:
                current_num = 3
                pass
            elif token_type in follow_of_non_terminals["G"]:
                pass
            else:
                pass

    elif current_state == Transition.Factor:
        if current_num == 0:
            if lexeme == "(":
                current_num = 1
                pass
            elif token_type == "ID":
                current_num = 3
                pass
            elif token_type == "NUM":
                current_num = 4
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == ")":
                current_num = 4
                pass
            else:
                pass
        elif current_num == 3:
            if token_type in first_of_non_terminals["Var-call-prime"]:
                current_num = 4
                pass
            elif token_type in follow_of_non_terminals["Var-call-prime"]:
                pass
            else:
                pass

    elif current_state == Transition.Var_call_prime:
        if current_num == 0:
            if lexeme == "(":
                current_num = 1
                pass
            elif token_type in first_of_non_terminals["Var-prime"]:
                current_num = 3
                pass
            elif token_type in follow_of_non_terminals["Var-prime"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Args"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Args"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == ")":
                current_num = 3
                pass
            else:
                pass

    elif current_state == Transition.Var_prime:
        if current_num == 0:
            if lexeme == "[":
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Var-prime"]:
                current_num = 3
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == "]":
                current_num = 3
                pass
            else:
                pass

    elif current_state == Transition.Factor_prime:
        if current_num == 0:
            if lexeme == "(":
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Factor-prime"]:
                current_num = 3
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Args"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Args"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == ")":
                current_num = 3
                pass
            else:
                pass

    elif current_state == Transition.Factor_zegond:
        if current_num == 0:
            if lexeme == "(":
                current_num = 1
                pass
            elif token_type == "NUM":
                current_num = 3
                pass
            else:
                pass
        elif current_state == 1:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 2:
            if lexeme == ")":
                current_state = 3
                pass
            else:
                pass

    elif current_state == Transition.Args:
        if current_num == 0:
            if token_type in first_of_non_terminals["Arg-list"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Arg-list"]:
                pass
            elif token_type in follow_of_non_terminals["Args"]:
                current_num = 1
                pass
            else:
                pass

    elif current_state == Transition.Arg_list:
        if current_num == 0:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Arg-list-prime"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Arg-list-prime"]:
                pass
            else:
                pass

    elif current_state == Transition.Arg_list_prime:
        if current_num == 0:
            if lexeme == ",":
                current_num = 1
                pass
            elif token_type in follow_of_non_terminals["Arg-list-prime"]:
                current_num = 3
                pass
            else:
                pass
        elif current_num == 1:
            if token_type in first_of_non_terminals["Expression"]:
                current_num = 2
                pass
            elif token_type in follow_of_non_terminals["Expression"]:
                pass
            else:
                pass
        elif current_num == 2:
            if token_type in first_of_non_terminals["Arg-list-prime"]:
                current_num = 3
                pass
            elif token_type in follow_of_non_terminals["Arg-list-prime"]:
                pass
            else:
                pass


if __name__ == "__main__":
    input_file = open('input.txt', 'r')
    while True:
        # if can_get_token:
        #     token_type, lexeme = token
        parser(input_file)
        break

    with open('parse_tree.txt', 'w', encoding="utf-8") as tree:
        while root.parent:
            root = root.parent
        for pre, fill, node in RenderTree(root):
            tree.write("%s%s" % (pre, node.name) + "\n")

    # parser = Parser(input_path)
    # parser.parse()
    # parser.save_parse_tree()
    # parser.save_syntax_errors()
    # parser.scanner.save_lexical_errors()
    # parser.scanner.save_symbol_table()
    # parser.scanner.save_tokens()
    # parser.semantic_analyzer.save_semantic_errors()
    # parser.code_generator.save_output()
