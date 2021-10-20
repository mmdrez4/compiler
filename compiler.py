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
symbol_regex = re.compile(r';|:|,|\[|]|\(|\)|\{|\}|/\+/|-|/\*/|=|<|==')
comment_regex = re.compile(r'/\*.*\*/ | /\/\/[^\n\r]+?(?:\*\)|[\n\r])')
space_regex = re.compile(r'\n|\r|\t|\v|\f|\s')
# is_valid = num_regex or ID_regex or keyword_regex or symbol_regex or space_regex
is_valid = re.compile(r"[A-Za-z]|[0-9]|;|:|,|\[|\]|\(|\)|{|}|\+|-|\*|=|<|==|/|\n|\r|\t|\v|\f|\s")

symbols_file = open('symbol_table.txt', 'w')
tokens_file = open('tokens.txt', 'w')
errors_file = open('lexical_errors.txt', 'w')

# symbols_file.writelines(["if", "\nelse", "\nvoid", "\nint", "\nrepeat", "\nbreak", "\nuntil", "\nreturn", "main\n"])

pointer = 1
input_file = open('input.txt', 'r')
# input_lines = input_file.readlines()

current_state = State.START
lexeme = ''
can_read = True
start_of_line = True
lexical_error = False
character = ''
keywords = []
identifiers = []


def go_to_start_node():
    global lexeme, current_state
    lexeme = ''
    current_state = State.START


def is_char_valid(c):
    return re.match(is_valid, c)


def goal_state(token, final_lexeme):
    global can_read
    tokens_file.write(str(pointer) + ".")
    tokens_file.write("(" + token + ", " + final_lexeme + ") ")
    go_to_start_node()
    can_read = False


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
        errors_file.write('\n')
        tokens_file.write('\n')
        continue

    # if re.match(r"[A-Za-z] | [0-9] | ;|:|,|[|]|(|)|{|}|/+/|-|/*/|=|<|== | \n|\r|\t|\v|\f", character):
    # if not re.match(is_valid, character):
    #     print(character)
    #     lexeme += character
    #     go_to_start_node()
    #     lexical_error = True
    #     errors_file.write(str(pointer) + ".")
    #     errors_file.write("(" + lexeme + ", Invalid input) ")
    #     continue
    if current_state == State.START:
        can_read = True
        if character == '/':
            lexeme += character
            current_state = State.COMMENT

        elif character == '*':
            lexeme += character
            character = input_file.read(1)
            if character == '/':
                errors_file.write(str(pointer) + ".")
                errors_file.write("(*/, Unmatched comment) ")
            else:
                errors_file.write(str(pointer) + ".")
                errors_file.write("(" + lexeme + ", Invalid input) ")
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
                current_state = State.SYMBOL
            else:
                tokens_file.write(str(pointer) + ".")
                tokens_file.write("(SYMBOL, " + character + ") ")

        elif re.match(space_regex, character):
            continue
        else:
            lexical_error = True
            errors_file.write(str(pointer) + ".")
            errors_file.write("(" + character + ", Invalid input) ")

        # elif re.match(r'[0-9]+'):
        #     errors_file.write("(" + i + " Invalid number) ")
        # elif i.__eq__("*/"):
        #     errors_file.write("(*/, Unmatched comment) ")
        # elif i.startswith("/*"):
        #     errors_file.write("(/*, Unclosed comment) ")
        # else:
        #     errors_file.write("(" + i + ", Invalid input) ")

    # TODO if our example is 125d what should we do? and set False to can_read
    if current_state == State.NUM:
        if re.match(num_regex, character):
            lexeme += character
        else:
            if is_char_valid(character):
                if re.match(space_regex, character):
                    tokens_file.write(str(pointer) + ".")
                    tokens_file.write("(NUM, " + lexeme + ") ")
                    go_to_start_node()
                elif re.match(r'[A-Za-z]', character):
                    lexeme += character
                    errors_file.write(str(pointer) + ".")
                    errors_file.write("(" + lexeme + ", Invalid number) ")
                    lexical_error = True
                    go_to_start_node()
                else:
                    # tokens_file.write(str(pointer) + ".")
                    # tokens_file.write("(NUM, " + lexeme + ") ")
                    # go_to_start_node()
                    # can_read = False
                    goal_state("NUM", lexeme)
            else:
                lexeme += character
                errors_file.write(str(pointer) + ".")
                errors_file.write("(" + lexeme + ", Invalid number) ")
                lexical_error = True
                go_to_start_node()

            # if re.match(r'[0-9]+', character):
            #     # error handling for 125d
            #     errors_file.write(str(pointer) + ".")
            #     errors_file.write("(" + lexeme + " Invalid number) ")
            #     lexical_error = True
            #     go_to_start_node()
    # TODO if our example is elseff what should we do?
    elif current_state == State.ID or current_state == State.KEYWORD:
        if re.match(ID_regex, character):
            lexeme += character
        else:
            current_state = State.START
            if re.match(keyword_regex, lexeme):
                if lexeme not in keywords:
                    keywords.append(lexeme)
                tokens_file.write(str(pointer) + ".")
                tokens_file.write("(KEYWORD, " + lexeme + ") ")
            else:
                if lexeme not in identifiers:
                    identifiers.append(lexeme)
                tokens_file.write(str(pointer) + ".")
                tokens_file.write("(ID, " + lexeme + ") ")
            go_to_start_node()
            can_read = False
    elif current_state == State.SYMBOL:
        if character == '=':
            tokens_file.write(str(pointer) + ".")
            tokens_file.write("(SYMBOL, " + "==" + ") ")
        else:
            tokens_file.write(str(pointer) + ".")
            tokens_file.write("(SYMBOL, " + "=" + ") ")
            can_read = False
        go_to_start_node()
    # TODO complete this one
    elif current_state == State.COMMENT:
        if character == '*':
            lexeme += "*"
            while True:
                character = input_file.read(1)
                if not character:
                    errors_file.write(str(pointer) + ".")
                    errors_file.write("(" + lexeme[0:7] + "..., Unclosed comment) ")
                    lexical_error = True
                    go_to_start_node()
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

        if re.match(comment_regex, character):
            pass
        else:
            lexeme += character

    # does'nt be in any state!
    else:

j = 0
for i, key in enumerate(keywords):
    print(i + 1)
    symbols_file.write(str(i + 1) + '.\t' + key + "\n")
    j = i + 1
for identifier in identifiers:
    j += 1
    symbols_file.write(str(j) + '.\t' + identifier + "\n")
