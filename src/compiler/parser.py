from compiler.tokenizer import Token
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
                loc=tokens[-1].loc,
                ttype="end",
                text="EOF",
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
        return ast.Literal(int(token.text))

    # Integer or identifier or ()
    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().text == "if":
            return parse_if_expression()
        elif peek().ttype == "integer":
            return parse_int_literal()
        elif peek().text == "not" or peek().text == "-":
            return parse_unary_op()
        elif peek().ttype == "identifier":
            token = consume()
            if peek().text == "(":
                return parse_function_call(token.text)
            elif peek().text == "=":
                return parse_assignment(token)
            return ast.Identifier(token.text)
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
            left = ast.BinaryOp(left, operator, right)
        return left

    # not | -
    def parse_unary_op() -> ast.UnaryOp:
        operator = consume()
        token = parse_factor()
        return ast.UnaryOp(operator.text, token)

    # Right associative =
    def parse_assignment(left: Token) -> ast.Assignment:
        consume("=")
        right = parse_expression()
        return ast.Assignment(ast.Identifier(left.text), right)

    def parse_if_expression() -> ast.IfThenElse:
        consume("if")
        condition = parse_expression()
        then_tok = consume("then")
        if then_tok.text != "then":
            raise Exception(f"{then_tok.loc}: expected keyword then")
        then = parse_expression()
        otherwise = None
        if peek().text == "else":
            consume("else")
            otherwise = parse_expression()
        return ast.IfThenElse(condition, then, otherwise)

    def parse_function_call(name: str) -> ast.FunctionCall:
        consume("(")
        args = []
        if peek().text != ")":
            # Function has at least 1 argument
            args.append(parse_expression())
            while peek().text == ",":
                consume(",")
                args.append(parse_expression())
        consume(")")
        return ast.FunctionCall(name, args)

    result = parse_expression()
    if pos < len(tokens):
        raise Exception(f"{peek().loc}: unexpected token {peek().text}")
    return result
