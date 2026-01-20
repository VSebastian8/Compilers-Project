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
                text="",
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

    def parse_identifier() -> ast.Identifier:
        token = consume()
        if token.ttype != "identifier":
            raise Exception(f"{token.loc}: expected an identifier")
        return ast.Identifier(token.text)

    # Lower precedence + and -
    def parse_expression() -> ast.Expression:
        left = parse_term()
        while peek().text in ["+", "-"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()
            left = ast.BinaryOp(left, operator, right)
        return left

    # Higher precedence * and /
    def parse_term() -> ast.Expression:
        left = parse_factor()
        while peek().text in ["*", "/"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(left, operator, right)
        return left

    # Integer or identifier or ()
    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().text == "if":
            return parse_if_expression()
        elif peek().ttype == "integer":
            return parse_int_literal()
        elif peek().ttype == "identifier":
            return parse_identifier()
        else:
            raise Exception(
                f'{peek().loc}: expected "(", an integer literal or an identifier'
            )

    # ()
    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expr = parse_expression()
        consume(")")
        return expr

    def parse_right_expression() -> ast.Expression:
        # Parse the first term.
        left = parse_term()

        # While there are more `+` or '-'...
        if peek().text in ["+", "-"]:
            # Move past the '+' or '-'.
            operator_token = consume()
            operator = operator_token.text
            # Parse the operator on the right.
            right = parse_right_expression()
            # Combine it with the stuff we've accumulated on the left so far.
            left = ast.BinaryOp(left, operator, right)

        return left

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

    result = parse_expression()
    if pos < len(tokens):
        raise Exception(f"{peek().loc}: unexpected token {peek().text}")
    return result
