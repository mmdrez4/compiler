import re
from enum import Enum, unique
from anytree import Node, RenderTree, PreOrderIter
from enum import Enum, unique


# ENUM FOR ALL THE STATES
@unique
class State(Enum):
    START = 1
    NUM = 2
    ID = 3
    KEYWORD = 4
    SYMBOL = 5
    COMMENT = 6
    WHITESPACE = 7


# DEFINE REGEX FOR EACH STATE
num_regex = re.compile(r'[0-9]+')
ID_regex = re.compile(r'[A-Za-z][A-Za-z0-9]*')
keyword_regex = re.compile(r'if|else|void|int|repeat|break|until|return|endif')
symbol_regex = re.compile(r';|:|,|\[|]|\(|\)|{|\}|\+|-|\*|=|<|==')
comment_regex = re.compile(r'/\*.*\*/ | ///[^\n\r]+?(?:\*\)|[\n\r])')
space_regex = re.compile(r'\n|\r|\t|\v|\f|\s')
is_valid = re.compile(r"[A-Za-z]|[0-9]|;|:|,|\[|\]|\(|\)|{|}|\+|-|\*|=|<|==|/|\n|\r|\t|\v|\f|\s")

# CREATING FILES
symbols_file = open('symbol_table.txt', 'w')
tokens_file = open('tokens.txt', 'w')
errors_file = open('lexical_errors.txt', 'w')

# OPEN THE INPUT FILE AND INITIALIZE THE POINTER OF LINES
pointer = 1
input_file = open('input.txt', 'r')

# DEFINE FIRST AND FOLLOW
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

# DEFINE IMPORTANT VARIABLES
current_state = State.START
lexeme = ''
can_read = True
start_of_line = True
lexical_error = False
lexical_error_pointer = 0
tokens_file_pointer = 0
character = ''
identifiers = []


# GO BACK TO THE START STATE
def go_to_start_node():
    global lexeme, current_state
    lexeme = ''
    current_state = State.START


# CHECK IF OUR CHARACTER IS VALID(THE CHARACTER SHOULD BE ACCEPTED BY ANY THE DEFINED REGEXES)
def is_char_valid(c):
    return re.match(is_valid, c)


# ADD NUMBER OF A LINE IN FILES
def numbering_tokens_lines():
    global tokens_file_pointer
    if pointer != tokens_file_pointer:
        if tokens_file_pointer != 0:
            tokens_file.write("\n")
        tokens_file.write(str(pointer) + ".")
        tokens_file.write("\t")
        tokens_file_pointer = pointer


# ADDING TOKEN TO TOKENS.TXT
def add_tokens_to_file(token, final_lexeme):
    numbering_tokens_lines()
    tokens_file.write("(" + token + ", " + final_lexeme + ") ")
    go_to_start_node()


# WRITE TOKENS IN THE TOKENS_FILE
def get_token_name():
    if current_state != State.START:
        numbering_tokens_lines()
        if current_state == State.NUM:
            return "NUM"
        elif current_state == State.ID:
            if re.match(keyword_regex, lexeme):
                return "KEYWORD"
            elif re.match(ID_regex, lexeme):
                if lexeme not in identifiers:
                    identifiers.append(lexeme)
                return "ID"
        elif current_state == State.SYMBOL:
            return "SYMBOL"
    else:
        return "START"


# WRITE ERRORS SUCH AS INVALID INPUT AND NUMBER AND COMMENTING PROBLEMS IN ERRORS_FILE
def error_handling(type, final_lexeme, line_pointer):
    global lexical_error, lexical_error_pointer
    lexical_error = True
    if line_pointer != lexical_error_pointer:
        if lexical_error_pointer != 0:
            errors_file.write("\n")
        errors_file.write(str(line_pointer) + ".")
        errors_file.write("\t")
        lexical_error_pointer = line_pointer
    if type == "input":
        errors_file.write("(" + final_lexeme + ", Invalid input) ")
    elif type == "number":
        errors_file.write("(" + final_lexeme + ", Invalid number) ")
    elif type == "Unmatched comment":
        errors_file.write("(*/, Unmatched comment) ")
    elif type == "Unclosed comment":
        errors_file.write("(" + final_lexeme[0:7] + "..., Unclosed comment) ")
    go_to_start_node()


# GET TOKENS!!
def get_token():
    global character, current_state, can_read, lexeme, pointer

    if not character:
        if lexical_error:
            errors_file.write('\n')
        else:
            errors_file.write("There is no lexical error.")
        get_token_name()
        return get_token_name(), lexeme

    if character == "\n":
        if lexeme == '/':
            error_handling("input", lexeme, pointer)
        return get_token_name(), lexeme

    # WE ARE IN THE START STATE
    if current_state == State.START:
        lexeme = ''
        can_read = True
        if character == '/':
            lexeme += character
            current_state = State.COMMENT

        elif character == '*':
            lexeme += character
            character = input_file.read(1)
            if character == '/':
                error_handling("Unmatched comment", "", pointer)
            elif re.match(space_regex, character):
                lexeme = "*"
                current_state = State.SYMBOL
                return "SYMBOL", lexeme
            elif re.match(num_regex, character):
                current_state = State.START
                can_read = False
                return "SYMBOL", lexeme
            else:
                lexeme += character
                error_handling("input", lexeme, pointer)
            return

        elif re.match(num_regex, character):
            lexeme += character
            current_state = State.NUM

        elif re.match(ID_regex, character):
            lexeme += character
            current_state = State.ID

        elif re.match(symbol_regex, character):
            current_state = State.SYMBOL
            if character == '=':
                lexeme += character
            else:
                lexeme = character
                return "SYMBOL", lexeme

        elif re.match(space_regex, character):
            return
        else:
            error_handling("input", character, pointer)

    # WE ARE NOT IN THE START STATE
    else:
        if re.match(space_regex, character):
            if lexeme == '/':
                error_handling("input", lexeme, pointer)
            else:
                return get_token_name(), lexeme
        else:

            # 1
            # NUM STATE:
            if current_state == State.NUM:
                if re.match(num_regex, character):
                    lexeme += character
                else:
                    if is_char_valid(character):
                        if re.match(r'[A-Za-z]', character):
                            lexeme += character
                            error_handling("number", lexeme, pointer)
                        else:
                            can_read = False
                            return "NUM", lexeme
                    else:
                        lexeme += character
                        error_handling("number", lexeme, pointer)

            # 2
            # ID AND KEYWORD STATE:
            elif current_state == State.ID:
                if re.match("[A-Za-z0-9]", character):
                    lexeme += character
                else:
                    if is_char_valid(character):
                        if re.match(keyword_regex, lexeme):
                            can_read = False
                            return "KEYWORD", lexeme
                        else:
                            if lexeme not in identifiers:
                                identifiers.append(lexeme)
                            can_read = False
                            return "ID", lexeme
                    else:
                        lexeme += character
                        error_handling("input", lexeme, pointer)

            # 3
            # SYMBOL STATE
            elif current_state == State.SYMBOL:
                if is_char_valid(character):
                    if character == '=':
                        lexeme = "=="
                        return "SYMBOL", lexeme
                    else:
                        lexeme = "="
                        can_read = False
                        return "SYMBOL", lexeme
                else:
                    lexeme += character
                    error_handling("input", lexeme, pointer)

            # 4
            # COMMENT STATE
            elif current_state == State.COMMENT:
                comment_pointer = 0
                if character == '*':
                    comment_pointer = pointer
                    lexeme += "*"
                    while True:
                        character = input_file.read(1)
                        if not character:
                            error_handling("Unclosed comment", lexeme, comment_pointer)
                            break
                        lexeme += character
                        if character == "\n":
                            pointer += 1
                        elif character == "*":
                            character = input_file.read(1)
                            lexeme += character
                            if character == "/":
                                go_to_start_node()
                                break
                            else:
                                continue

                elif character == '/':
                    lexeme += "/"
                    while True:
                        character = input_file.read(1)
                        if not character:
                            go_to_start_node()
                            break
                        lexeme += character
                        if character == "\n":
                            pointer += 1
                            go_to_start_node()
                            break
                else:
                    if is_char_valid(character):
                        can_read = False
                    else:
                        lexeme += character
                    error_handling("input", lexeme, pointer)


def get_next_token():
    global character, pointer
    # WHILE LOOP FOR READING THE FILE CHARACTER BY CHARACTER
    while True:
        if can_read:
            character = input_file.read(1)

        # LAST UPDATE FOR TOKENS WHEN THERE IS NO CHARACTER ANYMORE
        if not character:
            token_t, token_l = get_token()
            if token_t != "START":
                add_tokens_to_file(token_t, token_l)
                return token_t, token_l
            return 'EOF', '$'

        # GO TO NEWLINE AND UPDATE THE LAST TOKEN
        if character == "\n":
            token_t, token_l = get_token()
            if token_t != "START":
                add_tokens_to_file(token_t, token_l)
                return token_t, token_l
            pointer += 1
            continue

        # CALL get_next_token METHOD FOR RECOGNIZING ALL THE TOKENS
        output = get_token()
        if output is not None:
            token_t, token_l = output[0], output[1]
            if len(token_t) > 0 and len(token_l) > 0:
                add_tokens_to_file(token_t, token_l)
                return token_t, token_l


# PARSER
@unique
class Transition_Diagram(Enum):
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


parse_tree_file = open('parse_tree.txt', 'w')
syntax_errors_file = open('syntax_errors.txt', 'w')
syntax_file_pointer = 0

can_get_token = True
syntax_error = False


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


def is_in_first(token_t, token_l, transition):
    first = first_of_non_terminals[transition]
    if token_t in first:
        return True
    if token_l in first:
        return True
    return False


def is_in_follow(token_t, token_l, transition):
    follow = follow_of_non_terminals[transition]
    if token_t in follow:
        return True
    if token_l in follow:
        return True
    return False


class Transition:
    def __init__(self, procedure):
        self.procedure = procedure
        self.branch = self.get_branch()
        self.state_num = 0

    def get_branch(self):
        for i in range(len(non_terminals[self.procedure])):
            for j in range(len(non_terminals[self.procedure][i])):
                grammar = non_terminals[self.procedure][i][j]
                if grammar == 'e':
                    return i
                if grammar not in non_terminals:
                    if token_lexeme == grammar or token_type == grammar:
                        return i
                    else:
                        break
                else:
                    if is_in_first(token_type, token_lexeme, grammar):
                        return i
                    elif 'e' not in first_of_non_terminals[grammar]:
                        break
                    elif j == len(non_terminals[self.procedure][i]) - 1:
                        return i

    def move_forward(self):
        if self.state_num < len(non_terminals[self.procedure][self.branch]) - 1:
            self.state_num += 1
            return True
        return False


token_type, token_lexeme = get_next_token()
current_transition = Transition('Program')
program = Node('Program')
root = program
states = []


def move_to_next_state():
    global current_transition, root
    while not current_transition.move_forward():
        if states:
            current_transition = states.pop()
            root = root.parent


# MAIN FUNCTION
while True:
    transition_state = non_terminals[current_transition.procedure][current_transition.branch][
        current_transition.state_num]
    if transition_state == 'e':
        Node('epsilon', root)
        move_to_next_state()

    elif transition_state in non_terminals:
        if is_in_first(token_type, token_lexeme, transition_state):
            states.append(current_transition)
            current_transition = Transition(transition_state)
            root = Node(transition_state, root)

        elif is_in_follow(token_type, token_lexeme, transition_state):
            # missing procedure error. move state without changing the token
            if 'e' in first_of_non_terminals[transition_state]:
                states.append(current_transition)
                current_transition = Transition(transition_state)
                root = Node(transition_state, root)
            else:
                add_syntax_error("missing", token_lexeme, transition_state)
                move_to_next_state()

        # illegal procedure error. don't move state and change token
        elif token_lexeme == '$':
            add_syntax_error("Unexpected EOF", token_lexeme, transition_state)
            break
        elif token_type == 'ID' or token_type == "NUM":
            add_syntax_error("illegal type", token_lexeme, transition_state)
        else:
            add_syntax_error("illegal lexeme", token_lexeme, transition_state)
        token_type, token_lexeme = get_next_token()

    elif token_lexeme == transition_state or token_type == transition_state:
        # matches. move both state and token
        if token_lexeme == '$':
            Node('$', root)
            break
        Node("(" + token_type + ", " + token_lexeme + ")", root)
        token_type, token_lexeme = get_next_token()
        move_to_next_state()
    else:
        # missing token. don't change token and move state
        add_syntax_error("missing", token_lexeme, transition_state)
        move_to_next_state()

if not syntax_error:
    syntax_errors_file.write("There is no syntax error.")

# DRAW THE PARSE TREE
counter = 0
for pre, fill, node in RenderTree(program):
    if counter != 0:
        parse_tree_file.write("\n")
    counter += 1
    parse_tree_file.write("%s%s" % (pre, node.name))

tokens_file.write('\n')
# WRITE SYMBOLS NAMES IN THE SYMBOL_FILE AND ADD IDENTIFIERS TO THAT
symbols_file.writelines(["1.\tif", "\n2.\telse", "\n3.\tvoid", "\n4.\tint", "\n5.\trepeat",
                         "\n6.\tbreak", "\n7.\tuntil", "\n8.\treturn\n"])
counter = 9
for identifier in identifiers:
    symbols_file.write(str(counter) + '.\t' + identifier + "\n")
    counter += 1
