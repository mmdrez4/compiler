import re
import parser
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
def get_next_token():
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


# MAIN FUNCTION
if __name__ == "__main__":

    # WHILE LOOP FOR READING THE FILE CHARACTER BY CHARACTER
    while True:
        if can_read:
            character = input_file.read(1)

        # LAST UPDATE FOR TOKENS WHEN THERE IS NO CHARACTER ANYMORE
        if not character:
            (token_type, token_lexeme) = get_next_token()
            if token_type != "START":
                add_tokens_to_file(token_type, token_lexeme)
            break

        # GO TO NEWLINE AND UPDATE THE LAST TOKEN
        if character == "\n":
            (token_type, token_lexeme) = get_next_token()
            if token_type != "START":
                add_tokens_to_file(token_type, token_lexeme)
            pointer += 1
            continue

        # CALL get_next_token METHOD FOR RECOGNIZING ALL THE TOKENS
        output = get_next_token()
        if output is not None:
            (token_type, token_lexeme) = output[0], output[1]
            if len(token_type) > 0 and len(token_lexeme) > 0:
                add_tokens_to_file(token_type, token_lexeme)

    tokens_file.write('\n')
    # WRITE SYMBOLS NAMES IN THE SYMBOL_FILE AND ADD IDENTIFIERS TO THAT
    symbols_file.writelines(["1.\tif", "\n2.\telse", "\n3.\tvoid", "\n4.\tint", "\n5.\trepeat",
                             "\n6.\tbreak", "\n7.\tuntil", "\n8.\treturn\n"])
    j = 9
    for identifier in identifiers:
        symbols_file.write(str(j) + '.\t' + identifier + "\n")
        j += 1


