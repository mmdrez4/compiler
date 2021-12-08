import re
from anytree import Node, RenderTree, PreOrderIter
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
    "Program": "int",
    "Declaration-list": "int",
    "Declaration": "int",
    "Declaration-initial": "int",
    "Declaration-prime": ";",
    "Var-declaration-prime": ";",
    "Fun-declaration-prime": "(void) {int ID;}",
    "Type-specifier": "int",
    "Params": "void",
    "Param-list": ", int ID",
    "Param": "int ID",
    "Param-prime": "[]",
    "Compound-stmt": "{int ID;}",
    "Statement-list": ";",
    "Statement": ";",
    "Expression-stmt": ";",
    "Selection-stmt": "if (NUM); else;",
    "Else-stmt": "if (NUM); else;",
    "Iteration-stmt": "while (NUM);",
    "Return-stmt": "return;",
    "Return-stmt-prime": ";",
    "Expression": ";",
    "B": r'=|[',
    "H": "NUM",
    "Simple-expression-zegond": "NUM",
    "Simple-expression-prime": "()",
    "C": "< NUM",
    "Relop": "<",
    "Additive-expression": "NUM",
    "Additive-expression-prime": "()",
    "Additive-expression-zegond": "NUM",
    "D": "+ NUM",
    "Addop": "+",
    "Term": "NUM",
    "Term-prime": "()",
    "Term-zegond": "NUM",
    "G": "* NUM",
    "Factor": "NUM",
    "Var-call-prime": "()",
    "Var-prime": "[NUM]",
    "Factor-prime": "()",
    "Factor-zegond": "NUM",
    "Args": "NUM",
    "Arg-list": "NUM",
    "Arg-list-prime": ", NUM",
}

parse_tree_file = open('parse_tree.txt', 'w')
syntax_errors_file = open('syntax_errors.txt', 'w')


class Parser(object):
    def __init__(self, input_file):
        if not os.path.isabs(input_file):
            input_file = os.path.join(script_dir, input_file)
        self.scanner = Scanner(input_file)
        self.semantic_analyzer = SemanticAnalyser()
        self.code_generator = CodeGen()
        self._syntax_errors = []
        self.root = Node("Program")  # Start symbol
        self.parse_tree = self.root
        self.stack = [Node("$"), self.root]

        self.parse_tree_file = os.path.join(script_dir, "output", "parse_tree.txt")
        self.syntax_error_file = os.path.join(script_dir, "errors", "syntax_errors.txt")

    @property
    def syntax_errors(self):
        syntax_errors = []
        if self._syntax_errors:
            for lineno, error in self._syntax_errors:
                syntax_errors.append(f"#{lineno} : Syntax Error! {error}\n")
        else:
            syntax_errors.append("There is no syntax error.\n")
        return "".join(syntax_errors)

    def save_parse_tree(self):
        with open(self.parse_tree_file, "w", encoding="utf-8") as f:
            for pre, _, node in RenderTree(self.parse_tree):
                if hasattr(node, "token"):
                    f.write(f"{pre}{node.token}\n")
                else:
                    f.write(f"{pre}{node.name}\n")

    def save_syntax_errors(self):
        with open(self.syntax_error_file, "w") as f:
            f.write(self.syntax_errors)

    def _remove_node(self, node):
        try:
            # remove node from the parse tree
            parent = list(node.iter_path_reverse())[1]
            parent.children = [c for c in parent.children if c != node]
        except IndexError:
            pass

    def _clean_up_tree(self):
        ''' remove non terminals and unmet terminals from leaf nodes '''
        remove_nodes = []
        for node in PreOrderIter(self.parse_tree):
            if not node.children and not hasattr(node, "token") and node.name != "EPSILON":
                remove_nodes.append(node)

        for node in remove_nodes:
            self._remove_node(node)

    def parse(self):
        clean_up_needed = False
        token = self.scanner.get_next_token()
        new_nodes = []
        while True:
            token_type, a = token
            if token_type in ("ID", "NUM"):  # parser won't understand the lexim input in this case
                a = token_type

            current_node = self.stack[-1]  # check the top of the stack
            X = current_node.name

            if X.startswith("#SA"):  # X is an action symbol for semantic analyzer
                if X == "#SA_DEC_SCOPE" and a == "ID":
                    curr_lexim = self.scanner.id_to_lexim(token[1])
                self.semantic_analyzer.semantic_check(X, token, self.scanner.line_number)
                self.stack.pop()
                if X == "#SA_DEC_SCOPE" and a == "ID":
                    token = (token[0], self.scanner.update_symbol_table(curr_lexim))
            elif X.startswith("#CG"):  # X is an action symbol for code generator
                self.code_generator.code_gen(X, token)
                self.stack.pop()
            elif X in terminal_to_col.keys():  # X is a terminal
                if X == a:
                    if X == "$":
                        break
                    self.stack[-1].token = self.scanner.token_to_str(token)
                    self.stack.pop()
                    token = self.scanner.get_next_token()
                else:
                    SymbolTableManager.error_flag = True
                    if X == "$":  # parse stack unexpectedly exhausted
                        # self._clean_up_tree()
                        break
                    self._syntax_errors.append((self.scanner.line_number, f'Missing "{X}"'))
                    self.stack.pop()
                    clean_up_needed = True
            else:  # X is non-terminal
                # look up parsing table which production to use
                col = terminal_to_col[a]
                row = non_terminal_to_row[X]
                prod_idx = parsing_table[row][col]
                rhs = productions[prod_idx]

                if "SYNCH" in rhs:
                    SymbolTableManager.error_flag = True
                    if a == "$":
                        self._syntax_errors.append((self.scanner.line_number, "Unexpected EndOfFile"))
                        # self._clean_up_tree()
                        clean_up_needed = True
                        break
                    missing_construct = non_terminal_to_missing_construct[X]
                    self._syntax_errors.append((self.scanner.line_number, f'Missing "{missing_construct}"'))
                    self._remove_node(current_node)
                    self.stack.pop()
                elif "EMPTY" in rhs:
                    SymbolTableManager.error_flag = True
                    self._syntax_errors.append((self.scanner.line_number, f'Illegal "{a}"'))
                    token = self.scanner.get_next_token()
                else:
                    self.stack.pop()
                    for symbol in rhs:
                        if not symbol.startswith("#"):
                            new_nodes.append(Node(symbol, parent=current_node))
                        else:
                            new_nodes.append(Node(symbol))

                    for node in reversed(new_nodes):
                        if node.name != "EPSILON":
                            self.stack.append(node)
                # print(f"{X} -> {' '.join(rhs)}")  # prints out the productions used
                new_nodes = []

        self.semantic_analyzer.eof_check(self.scanner.line_number)
        if clean_up_needed:
            self._clean_up_tree()
        self.code_generator.code_gen("FINISH_PROGRAM", None)


if __name__ == "__main__":
    input_path = os.path.join(script_dir, "input/input_simple.c")
    parser = Parser(input_path)
    parser.parse()
    parser.save_parse_tree()
    parser.save_syntax_errors()
    parser.scanner.save_lexical_errors()
    parser.scanner.save_symbol_table()
    parser.scanner.save_tokens()
    parser.semantic_analyzer.save_semantic_errors()
    parser.code_generator.save_output()
