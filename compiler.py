import re
from enum import Enum, unique


@unique
class State(Enum):
    START = 1
    NUM = 2
    ID = 3
    KEYWORD = 4
    SYMBOL = 5
    COMMENT = 6
    WHITESPACE = 7


num_regex = re.compile(r'[0-9]+')
ID_regex = re.compile(r'[A-Za-z][A-Za-z0-9]*')
keyword_regex = re.compile(r'if|else|void|int|repeat|break|until|return|main')
symbol_regex = re.compile(r';|:|,|\[|]|\(|\)|{|\}|\+|-|\*|=|<|==')
comment_regex = re.compile(r'/\*.*\*/ | ///[^\n\r]+?(?:\*\)|[\n\r])')
space_regex = re.compile(r'\n|\r|\t|\v|\f|\s')
# is_valid = num_regex or ID_regex or keyword_regex or symbol_regex or space_regex
is_valid = re.compile(r"[A-Za-z]|[0-9]|;|:|,|\[|\]|\(|\)|{|}|\+|-|\*|=|<|==|/|\n|\r|\t|\v|\f|\s")

symbols_file = open('symbol_table.txt', 'w')
tokens_file = open('tokens.txt', 'w')
errors_file = open('lexical_errors.txt', 'w')

pointer = 1
input_file = open('input.txt', 'r')

current_state = State.START
lexeme = ''
can_read = True
start_of_line = True
lexical_error = False
lexical_error_pointer = 1
character = ''
identifiers = []


def go_to_start_node():
    global lexeme, current_state
    lexeme = ''
    current_state = State.START


def is_char_valid(c):
    return re.match(is_valid, c)


def goal_state_with_star(token, final_lexeme):
    global can_read
    tokens_file.write(str(pointer) + ".")
    tokens_file.write("(" + token + ", " + final_lexeme + ") ")
    go_to_start_node()
    can_read = False


def tokenized():
    tokens_file.write(str(pointer) + ".")
    if current_state == State.NUM:
        tokens_file.write("(NUM, " + lexeme + ") ")
    elif current_state == State.ID:
        if re.match(keyword_regex, lexeme):
            tokens_file.write("(KEYWORD, " + lexeme + ") ")
        elif re.match(ID_regex, lexeme):
            tokens_file.write("(ID, " + lexeme + ") ")
            if lexeme not in identifiers:
                identifiers.append(lexeme)
    elif current_state == State.SYMBOL:
        tokens_file.write("(SYMBOL, " + lexeme + ") ")
    go_to_start_node()


def error_handling(type, final_lexeme):
    global lexical_error, lexical_error_pointer
    lexical_error = True
    if pointer != lexical_error_pointer:
        errors_file.write(str(pointer) + ".")
        lexical_error_pointer = pointer
    if type == "input":
        errors_file.write("(" + final_lexeme + ", Invalid input) ")
    elif type == "number":
        errors_file.write("(" + final_lexeme + ", Invalid number) ")
    elif type == "Unmatched comment":
        errors_file.write("(*/, Unmatched comment) ")
    elif type == "Unclosed comment":
        errors_file.write("(" + final_lexeme[0:7] + "..., Unclosed comment) ")
    go_to_start_node()


while True:
    if can_read:
        character = input_file.read(1)
    if not character:
        # TODO i have some doubts about two lines below
        if lexical_error:
            errors_file.write('\n')
        else:
            errors_file.write("There is no lexical error.")
        tokens_file.write('\n')
        break
    if character == "\n":
        pointer += 1
        tokens_file.write('\n')
        continue

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
                error_handling("Unmatched comment", "")
            else:
                error_handling("input", lexeme)
                can_read = False
            continue

        elif re.match(num_regex, character):
            lexeme += character
            current_state = State.NUM
            # tokens_file.write("(NUM, " + character + ") ")

        elif re.match(ID_regex, character):
            lexeme += character
            current_state = State.ID
            # tokens_file.write("(ID, " + character + ") ")
            # if i not in symbols_file.read():
            #     symbols_file.write(character)

        # elif re.match(keyword_regex, character):
        # tokens_file.write("(KEYWORD, " + character + ") ")

        elif re.match(symbol_regex, character):
            if character == '=':
                lexeme += character
                current_state = State.SYMBOL
            else:
                tokens_file.write(str(pointer) + ".")
                tokens_file.write("(SYMBOL, " + character + ") ")

        elif re.match(space_regex, character):
            continue
        else:
            error_handling("input", character)


    #TODO does'nt be in the start state!
    else:
        if re.match(space_regex, character):
            tokenized()
        else:
            # TODO NUM:
            #  if our example is 125d what should we do? and set False to can_read
            if current_state == State.NUM:
                if re.match(num_regex, character):
                    lexeme += character
                else:
                    if is_char_valid(character):
                        if re.match(r'[A-Za-z]', character):
                            lexeme += character
                            error_handling("number", lexeme)
                        else:
                            goal_state_with_star("NUM", lexeme)
                    else:
                        lexeme += character
                        error_handling("number", lexeme)



            # TODO ID AND KEYWORD:
            #  if our example is elseff what should we do?
            elif current_state == State.ID:
                if re.match(ID_regex, character):
                    lexeme += character
                else:
                    if is_char_valid(character):
                        if re.match(keyword_regex, lexeme):
                            # if lexeme not in keywords:
                            #     keywords.append(lexeme)
                            goal_state_with_star("KEYWORD", lexeme)
                        else:
                            if lexeme not in identifiers:
                                identifiers.append(lexeme)
                                goal_state_with_star("ID", lexeme)
                    else:
                        lexeme += character
                        error_handling("input", lexeme)


            # TODO SYMBOL
            elif current_state == State.SYMBOL:
                if is_char_valid(character):
                    if character == '=':
                        lexeme = "=="
                        tokenized()
                    else:
                        # TODO what if we have =* and then space?
                        lexeme = "="
                        goal_state_with_star("SYMBOL", lexeme)
                else:
                    lexeme += character
                    error_handling("input", lexeme)


            # TODO COMMENT:
            #  complete this one
            elif current_state == State.COMMENT:
                comment_pointer = 0
                if character == '*':
                    comment_pointer = pointer
                    lexeme += "*"
                    while True:
                        character = input_file.read(1)
                        if not character:
                            error_handling("Unclosed comment", lexeme)
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
                    errors_file.write(str(pointer) + ".")
                    errors_file.write("(" + lexeme + ", Invalid input) ")
                    lexical_error = True
                    go_to_start_node()
                    can_read = False

symbols_file.writelines(["1.\tif", "\n2.\telse", "\n3.\tvoid", "\n4.\tint", "\n5.\trepeat",
                         "\n6.\tbreak", "\n7.\tuntil", "\n8.\treturn", "\n9.\tmain\n"])

j = 10
for identifier in identifiers:
    symbols_file.write(str(j) + '.\t' + identifier + "\n")
    j += 1
