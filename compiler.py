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
symbol_regex = re.compile(r';|:|,|[|]|(|)|{|}|/+/|-|/*/|=|<|==')
comment_regex = re.compile(r'/\*.*\*/ | /\/\/[^\n\r]+?(?:\*\)|[\n\r])')
space_regex = re.compile(r'\n|\r|\t|\v|\f')

symbols_file = open('symbol_table.txt', 'a')
tokens_file = open('tokens.txt', 'w')
errors_file = open('lexical_errors.txt', 'w')

symbols_file.writelines(["if", "\nelse", "\nvoid", "\nint", "\nrepeat", "\nbreak", "\nuntil", "\nreturn", "main\n"])

pointer = 1
input_file = open('input.txt', 'r')
# input_lines = input_file.readlines()

current_state = State.START
lexeme = ''
can_read = True
character = ''
while True:
    if can_read:
        character = input_file.read(1)
    if not character:
        break
    if character == "\n":
        pointer += 1
        continue

    # TODO if our example is 125d what should we do?
    if current_state == State.NUM:
        if re.match(num_regex, character):
            lexeme += character
        else:
            lexeme += character
            if re.match(r'[0-9]+', character):
                # error handling for 125d
                errors_file.write("(" + lexeme + " Invalid number) ")
                lexeme = ''
                current_state = State.START
    # TODO if our example is elseff what should we do?
    elif current_state == State.ID or current_state == State.KEYWORD:
        if re.match(ID_regex, character):
            lexeme += character
        else:
            current_state = State.START
            if re.match(keyword_regex, lexeme):
                tokens_file.write("(KEYWORD, " + lexeme + ") ")
            else:
                tokens_file.write("(ID, " + lexeme + ") ")
            lexeme = ''
            can_read = False
    elif current_state == State.SYMBOL:
        if character == '=':
            tokens_file.write("(SYMBOL, " + "==" + ") ")

        else:
            tokens_file.write("(SYMBOL, " + "=" + ") ")
    elif current_state == State.COMMENT:
        if re.match(comment_regex, character):
            pass
        else:
            lexeme += character
    # does'nt be in any state!
    else:
        can_read = True
        if character == "*":
            if len(lexeme) > 1:
                pass
        else:
            if re.match(space_regex, character):
                pass
            else:
                lexeme += character

        if re.match(num_regex, i):
            tokens_file.write("(NUM, " + i + ") ")

        elif re.match(ID_regex, i):
            tokens_file.write("(ID, " + i + ") ")
            if i not in symbols_file.read():
                symbols_file.write(i)

        elif re.match(keyword_regex, i):
            tokens_file.write("(KEYWORD, " + i + ") ")

        elif re.match(symbol_regex, character):
            if character == '=':
                current_state = State.SYMBOL
            else:
                tokens_file.write("(SYMBOL, " + character + ") ")

        elif re.match(comment_regex, i):
            continue
        else:
            errors_file.write("(" + character + ", Invalid input) ")

        # elif re.match(r'[0-9]+'):
        #     errors_file.write("(" + i + " Invalid number) ")
        # elif i.__eq__("*/"):
        #     errors_file.write("(*/, Unmatched comment) ")
        # elif i.startswith("/*"):
        #     errors_file.write("(/*, Unclosed comment) ")
        # else:
        #     errors_file.write("(" + i + ", Invalid input) ")

    # elif re.match(ID_regex, i):
    #     tokens_file.write("(KEYWORD, " + i + ") ")
    #     pointer += 1


pointer += 1
errors_file.write('\n')
tokens_file.write('\n')
symbols_file.write('\n')
