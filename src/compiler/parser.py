from compiler.tokenizer import Token
from compiler.token import Location
import compiler.ast as ast


def parse(tokens: list[Token]) -> ast.Expression:
    if len(tokens) == 0:
        raise Exception("Empty list of tokens")
    # Token index
    pos = 0

    # Doesn't modify pos
    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                text="EOF",
                ttype="end",
                loc=(tokens[-1].loc.row, tokens[-1].loc.col),
            )

    # Increments pos by one
    def consume(expected: str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.loc}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f"{token.loc}: expected one of: {comma_separated}")
        pos += 1
        return token

    def parse_int_literal() -> ast.Literal:
        token = consume()
        if token.ttype != "integer":
            raise Exception(f"{token.loc}: expected an integer literal")
        return ast.Literal(int(token.text), loc=token.loc)

    # Integer or identifier or ()
    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().text == "{":
            return parse_block()
        elif peek().text == "if":
            return parse_if_expression()
        elif peek().text == "while":
            return parse_while_expression()
        elif peek().ttype == "integer":
            return parse_int_literal()
        elif peek().text == "not" or peek().text == "-":
            return parse_unary_op()
        elif peek().ttype == "identifier":
            token = consume()
            if peek().text == "(":
                return parse_function_call(token)
            elif peek().text == "=":
                return parse_assignment(token)
            elif token.text == "var":
                raise Exception(
                    f"{peek().loc}: variable declaration only allowed inside blocks"
                )
            return ast.Identifier(token.text, loc=token.loc)
        else:
            raise Exception(f"{peek().loc}: unexpected token {peek().text}")

    # ()
    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    left_associative_binary_operators = [
        ["or"],
        ["and"],
        ["==", "!="],
        ["<", "<=", ">", ">="],
        ["+", "-"],
        ["*", "/", "%"],
    ]

    # Allow chaining of operators of same or lower precedence
    def parse_expression(precedence: int = 0) -> ast.Expression:
        if precedence == len(left_associative_binary_operators):
            return parse_factor()
        left = parse_expression(precedence + 1)
        while peek().text in left_associative_binary_operators[precedence]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_expression(precedence + 1)
            left = ast.BinaryOp(left, operator, right, loc=left.loc)
        return left

    # not | -
    def parse_unary_op() -> ast.UnaryOp:
        operator = consume()
        token = parse_factor()
        return ast.UnaryOp(operator.text, token, loc=operator.loc)

    # Right associative =
    def parse_assignment(left: Token) -> ast.Assignment:
        consume("=")
        right = parse_expression()
        return ast.Assignment(left.text, right, loc=left.loc)

    def parse_if_expression() -> ast.IfThenElse:
        if_tok = consume("if")
        condition = parse_expression()
        then_tok = consume("then")
        if then_tok.text != "then":
            raise Exception(f"{then_tok.loc}: expected keyword then")
        then = parse_expression()
        otherwise = None
        if peek().text == "else":
            consume("else")
            otherwise = parse_expression()
        return ast.IfThenElse(condition, then, otherwise, loc=if_tok.loc)

    def parse_function_call(token: Token) -> ast.FunctionCall:
        consume("(")
        args = []
        if peek().text != ")":
            # Function has at least 1 argument
            args.append(parse_expression())
            while peek().text == ",":
                consume(",")
                args.append(parse_expression())
        consume(")")
        return ast.FunctionCall(token.text, args, loc=token.loc)

    # ; is optional after
    def ends_in_block(exp: ast.Expression) -> bool:
        if isinstance(exp, ast.Block) or isinstance(exp, ast.While):
            return True
        if isinstance(exp, ast.IfThenElse):
            match (exp.otherwise):
                case None:
                    return ends_in_block(exp.then)
                case e:
                    return ends_in_block(e)
        return False

    def parse_var() -> ast.VarDec:
        var_tok = consume("var")
        assignment = parse_assignment(consume())
        return ast.VarDec(assignment.left, assignment.right, loc=var_tok.loc)

    def parse_block(top_level: bool = False) -> ast.Block:
        loc = Location(0, 0)
        if not top_level:
            loc = consume("{").loc
        exps = []
        void = True
        while not peek().text == "}":
            void = False
            exp = parse_var() if peek().text == "var" else parse_expression()
            exps.append(exp)
            if pos == len(tokens):
                break
            if peek().text == ";":
                consume(";")
                void = True
            else:
                if ends_in_block(exp):
                    continue
                if peek().text != "}":
                    raise Exception(f"{peek().loc}: missing ;")
        if void:
            exps.append(ast.Literal(None))
        if not top_level:
            consume("}")
        return ast.Block(exps, loc=loc)

    def parse_while_expression() -> ast.While:
        loc = consume("while").loc
        condition = parse_expression()
        consume("do")
        block = parse_block()
        return ast.While(condition, block, loc=loc)

    # Finall Parser Function Call
    top_level_result = parse_block(top_level=True)
    result: ast.Expression = (
        top_level_result
        if len(top_level_result.expressions) != 1
        else top_level_result.expressions[0]
    )
    if pos < len(tokens):
        raise Exception(f"{peek().loc}: unexpected token {peek().text}")
    return result
