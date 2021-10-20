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
keyword_regex = re.compile(r'if|else|void|int|repeat|break|until|return')
symbol_regex = re.compile(r';|:|,|\[|]|\(|\)|{|\}|\+|-|\*|=|<|==')
comment_regex = re.compile(r'/\*.*\*/ | ///[^\n\r]+?(?:\*\)|[\n\r])')
space_regex = re.compile(r'\n|\r|\t|\v|\f|\s')
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
lexical_error_pointer = 0
tokens_file_pointer = 0
character = ''
identifiers = []


def go_to_start_node():
    global lexeme, current_state
    lexeme = ''
    current_state = State.START


def is_char_valid(c):
    return re.match(is_valid, c)


def numbering_tokens_lines():
    global tokens_file_pointer
    if pointer != tokens_file_pointer:
        if tokens_file_pointer != 0:
            tokens_file.write("\n")
        tokens_file.write(str(pointer) + ".")
        tokens_file.write("\t")
        tokens_file_pointer = pointer


def goal_state_with_star(token, final_lexeme):
    numbering_tokens_lines()
    global can_read
    tokens_file.write("(" + token + ", " + final_lexeme + ") ")
    go_to_start_node()
    can_read = False


def tokenized():
    if current_state != State.START:
        numbering_tokens_lines()
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


while True:
    if can_read:
        character = input_file.read(1)
    if not character:
        # TODO i have some doubts about two lines below
        if lexical_error:
            errors_file.write('\n')
        else:
            errors_file.write("There is no lexical error.")
        print("hello")
        tokenized()
        tokens_file.write('\n')
        break
    if character == "\n":
        if lexeme == '/':
            error_handling("input", lexeme, pointer)
        tokenized()
        pointer += 1
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
                error_handling("Unmatched comment", "", pointer)
            elif re.match(space_regex, character):
                lexeme = "*"
                current_state = State.SYMBOL
                tokenized()
            else:
                lexeme += character
                error_handling("input", lexeme, pointer)
            continue

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
                tokenized()

        elif re.match(space_regex, character):
            continue
        else:
            error_handling("input", character, pointer)


    #TODO does'nt be in the start state!
    else:
        if re.match(space_regex, character):
            if lexeme == '/':
                error_handling("input", lexeme, pointer)
            else:
                tokenized()
        else:
            # TODO NUM:
            #  if our example is 125d what should we do? and set False to can_read
            if current_state == State.NUM:
                if re.match(num_regex, character):
                    if lexeme == "194":
                        print(lexeme)
                    lexeme += character
                else:
                    if is_char_valid(character):
                        if re.match(r'[A-Za-z]', character):
                            lexeme += character
                            error_handling("number", lexeme, pointer)
                        else:
                            goal_state_with_star("NUM", lexeme)
                    else:
                        lexeme += character
                        error_handling("number", lexeme, pointer)



            # TODO ID AND KEYWORD:
            #  if our example is elseff what should we do?
            elif current_state == State.ID:
                if re.match("[A-Za-z0-9]", character):
                    lexeme += character
                else:
                    if is_char_valid(character):
                        if re.match(keyword_regex, lexeme):
                            goal_state_with_star("KEYWORD", lexeme)
                        else:
                            if lexeme not in identifiers:
                                identifiers.append(lexeme)
                            goal_state_with_star("ID", lexeme)
                    else:
                        lexeme += character
                        error_handling("input", lexeme, pointer)


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
                    error_handling("input", lexeme, pointer)


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
                    error_handling("input", lexeme, pointer)
                    can_read = False

symbols_file.writelines(["1.\tif", "\n2.\telse", "\n3.\tvoid", "\n4.\tint", "\n5.\trepeat",
                         "\n6.\tbreak", "\n7.\tuntil", "\n8.\treturn\n"])

j = 9
for identifier in identifiers:
    symbols_file.write(str(j) + '.\t' + identifier + "\n")
    j += 1
