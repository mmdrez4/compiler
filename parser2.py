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
    Param_list = 9
    Param = 10
    Param_prime = 11
    Compound_stmt = 12
    Statement_list = 13
    Statement = 14
    Expression_stmt = 15
    Selection_stmt = 16
    Else_stmt = 17
    Iteration_stmt = 18
    Return_stmt = 19
    Return_stmt_prime = 20
    Expression = 21
    B = 22
    H = 23
    Simple_expression_zegond = 24
    Simple_expression_prime = 25
    C = 26
    Relop = 27
    Additive_expression = 28
    Additive_expression_prime = 29
    Additive_expression_zegond = 30
    D = 31
    Addop = 32
    Term = 33
    Term_prime = 34
    Term_zegond = 35
    G = 36
    Factor = 37
    Var_call_prime = 38
    Var_prime = 39
    Factor_prime = 40
    Factor_zegond = 41
    Args = 42
    Arg_list = 43
    Arg_list_prime = 44


non_terminals = {
    'Program': [['Declaration-list', '$']],
    'Declaration-list': [['Declaration', 'Declaration-list'], ['e']],
    'Declaration': [['Declaration-initial', 'Declaration-prime']],
    'Declaration-initial': [['Type-specifier', 'ID']],
    'Declaration-prime': [['Fun-declaration-prime'], ['Var-declaration-prime']],
    'Var-declaration-prime': [[';'], ['[', 'NUM', ']', ';']],
    'Fun-declaration-prime': [['(', 'Params', ')', 'Compound-stmt']],
    'Type-specifier': [['int'], ['void']],
    'Params': [['int', 'ID', 'Param-prime', 'Param-list'], ['void']],
    'Param-list': [[',', 'Param', 'Param-list'], ['e']],
    'Param': [['Declaration-initial', 'Param-prime']],
    'Param-prime': [['[', ']'], ['e']],
    'Compound-stmt': [['{', 'Declaration-list', 'Statement-list', '}']],
    'Statement-list': [['Statement', 'Statement-list'], ['e']],
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
    'C': [['Relop', 'Additive-expression'], ['e']],
    'Relop': [['<'], ['==']],
    'Additive-expression': [['Term', 'D']],
    'Additive-expression-prime': [['Term-prime', 'D']],
    'Additive-expression-zegond': [['Term-zegond', 'D']],
    'D': [['Addop', 'Term', 'D'], ['e']],
    'Addop': [['+'], ['-']],
    'Term': [['Factor', 'G']],
    'Term-prime': [['Factor-prime', 'G']],
    'Term-zegond': [['Factor-zegond', 'G']],
    'G': [['*', 'Factor', 'G'], ['e']],
    'Factor': [['(', 'Expression', ')'], ['ID', 'Var-call-prime'], ['NUM']],
    'Var-call-prime': [['(', 'Args', ')'], ['Var-prime']],
    'Var-prime': [['[', 'Expression', ']'], ['e']],
    'Factor-prime': [['(', 'Args', ')'], ['e']],
    'Factor-zegond': [['(', 'Expression', ')'], ['NUM']],
    'Args': [['Arg-list'], ['e']],
    'Arg-list': [['Expression', 'Arg-list-prime']],
    'Arg-list-prime': [[',', 'Expression', 'Arg-list-prime'], ['e']]
}

first_of_non_terminals = {
    'Program': ['$', 'int', 'void'],
    'Declaration-list': ['e', 'int', 'void'],
    'Declaration': ['int', 'void'],
    'Declaration-initial': ['int', 'void'],
    'Declaration-prime': ['(', ';', '['],
    'Var-declaration-prime': [';', '['],
    'Fun-declaration-prime': ['('],
    'Type-specifier': ['int', 'void'],
    'Params': ['int', 'void'],
    'Param-list': [',', 'e'],
    'Param': ['int', 'void'],
    'Param-prime': ['[', 'e'],
    'Compound-stmt': ['{'],
    'Statement-list': ['e', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
    'Statement': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
    'Expression-stmt': ['break', ';', 'ID', '(', 'NUM'],
    'Selection-stmt': ['if'],
    'Else-stmt': ['endif', 'else'],
    'Iteration-stmt': ['repeat'],
    'Return-stmt': ['return'],
    'Return-stmt-prime': [';', 'ID', '(', 'NUM'],
    'Expression': ['ID', '(', 'NUM'],
    'B': ['=', '[', '(', '*', '+', '-', '<', '==', 'e'],
    'H': ['=', '*', 'e', '+', '-', '<', '=='],
    'Simple-expression-zegond': ['(', 'NUM'],
    'Simple-expression-prime': ['(', '*', '+', '-', '<', '==', 'e'],
    'C': ['e', '<', '=='],
    'Relop': ['<', '=='],
    'Additive-expression': ['(', 'ID', 'NUM'],
    'Additive-expression-prime': ['(', '*', '+', '-', 'e'],
    'Additive-expression-zegond': ['(', 'NUM'],
    'D': ['e', '+', '-'],
    'Addop': ['+', '-'],
    'Term': ['(', 'ID', 'NUM'],
    'Term-prime': ['(', '*', 'e'],
    'Term-zegond': ['(', 'NUM'],
    'G': ['*', 'e'],
    'Factor': ['(', 'ID', 'NUM'],
    'Var-call-prime': ['(', '[', 'e'],
    'Var-prime': ['[', 'e'],
    'Factor-prime': ['(', 'e'],
    'Factor-zegond': ['(', 'NUM'],
    'Args': ['e', 'ID', '(', 'NUM'],
    'Arg-list': ['ID', '(', 'NUM'],
    'Arg-list-prime': [',', 'e']
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
current_state = Transition.Program
current_num = 0
can_get_token = True
syntax_error = False
scanner = []
root = Node('Program')


def numbering_syntax_error_lines():
    global syntax_file_pointer
    if pointer != syntax_file_pointer:
        if syntax_file_pointer != 0:
            syntax_errors_file.write("\n")
        syntax_errors_file.write("#" + str(pointer) + " : ")
        syntax_file_pointer = pointer


def add_syntax_error(error_type, lexeme, non_terminal):
    global syntax_error
    syntax_error = True
    numbering_syntax_error_lines()
    if error_type == "missing":
        syntax_errors_file.write("syntax error, missing " + non_terminal)
    elif error_type == "illegal type":
        syntax_errors_file.write("syntax error, illegal " + non_terminal)
    elif error_type == "illegal lexeme":
        syntax_errors_file.write("syntax error, illegal " + lexeme)
    elif error_type == "Unexpected EOF":
        syntax_errors_file.write("syntax error, Unexpected EOF")


def is_terminal(phrase):
    return phrase not in non_terminals


STATE_STACK = []
token = None


class Diagram:
    def __init__(self, procedure):
        self.procedure = procedure
        self.branch = self.get_branch()
        self.state = 0

    def get_branch(self):
        for i in range(len(non_terminals[self.procedure])):
            for j in range(len(non_terminals[self.procedure][i])):
                komaki = non_terminals[self.procedure][i][j]
                if komaki == 'e':
                    return i
                if is_terminal(komaki):
                    if token.value == komaki or token.type == komaki:
                        return i
                    else:
                        break
                else:
                    if token.value in first_of_non_terminals[komaki] or token.type in first_of_non_terminals[komaki]:
                        return i
                    elif 'e' not in first_of_non_terminals[komaki]:
                        break
                    elif j == len(non_terminals[self.procedure][i]) - 1:
                        return i

    def get_value(self):
        return non_terminals[self.procedure][self.branch][self.state]

    def move_forward(self):
        if self.state < len(non_terminals[self.procedure][self.branch]) - 1:
            self.state += 1
            return True
        return False


token = scanner.get_next_token()
token_type, token_lexeme = token[0], token[1]
state = Diagram('Program')
root = Node('Program')


def move_to_next_state():
    global state
    global root

    while not state.move_forward():
        state = STATE_STACK.pop()
        root = root.parent


while True:
    current_state = state.get_value()

    if current_state == 'e':
        Child = Node('epsilon', parent=root)
        move_to_next_state()

    elif is_terminal(current_state):
        if token.value == current_state or token.type == current_state:
            # matches. move both state and token
            if token.value == '$':
                child = Node('$', parent=root)
                break
            child = Node(f"({token.type}, {token.value})", parent=root)
            token = scanner.get_next_token()
            move_to_next_state()
        else:
            # missing token. don't change token and move state
            add_syntax_error("missing", token_lexeme, current_state)
            move_to_next_state()

    else:  # non-terminal state
        if token.value in first_of_non_terminals[current_state] or token.type in first_of_non_terminals[current_state]:
            STATE_STACK.append(state)
            state = Diagram(current_state)
            child = Node(current_state, parent=root)
            root = child

        else:
            if token.value in follow_of_non_terminals[current_state] or \
                    token.type in follow_of_non_terminals[current_state]:
                # missing procedure error. move state without changing the token
                if 'e' in first_of_non_terminals[current_state]:
                    STATE_STACK.append(state)
                    state = Diagram(current_state)
                    child = Node(current_state, parent=root)
                    root = child
                else:
                    add_syntax_error("missing", token_lexeme, current_state)
                    move_to_next_state()

            else:
                # illegal procedure error. don't move state and change token
                if token.value == '$':
                    add_syntax_error("Unexpected EOF", token_lexeme, current_state)
                    break
                else:
                    if token_type == 'ID' or token_type == "NUM":
                        add_syntax_error("illegal type", token_lexeme, current_state)
                    else:
                        add_syntax_error("illegal lexeme", token_lexeme, current_state)
                    token = scanner.get_next_token()

if not syntax_error:
    syntax_errors_file.write("There is no syntax error.")

with open('parse_tree.txt', 'w', encoding="utf-8") as tree:
    while root.parent:
        root = root.parent

    for pre, fill, node in RenderTree(root):
        tree.write("%s%s" % (pre, node.name) + "\n")

