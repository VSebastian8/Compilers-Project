from compiler.tokenizer import Token
from compiler.token import Location
import compiler.ast as ast
import compiler.types as types


def parse(tokens: list[Token]) -> ast.Module:
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
        loc = peek().loc
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
        elif peek().text == "true":
            consume("true")
            return ast.Literal(True, loc=loc)
        elif peek().text == "false":
            consume("false")
            return ast.Literal(False, loc=loc)
        elif peek().text == "break":
            consume("break")
            return ast.LoopControl("break", loc=loc)
        elif peek().text == "continue":
            consume("continue")
            return ast.LoopControl("continue", loc=loc)
        elif peek().text == "fun":
            raise Exception(f"{loc}: can only define functions at top level")
        elif peek().text == "return":
            consume("return")
            return ast.Return(parse_expression(), loc=loc)
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
            return ast.Identifier(token.text, loc=loc)
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

    def parse_type() -> types.Type:
        if peek().text == "Int":
            consume("Int")
            return types.Int
        elif peek().text == "Bool":
            consume("Bool")
            return types.Bool
        if peek().text == "Unit":
            consume("Unit")
            return types.Unit
        elif peek().text == "(":
            consume("(")
            input_types = []
            while not peek().text == ")":
                input_types.append(parse_type())
                if peek().text == ",":
                    consume(",")
                    if peek().text == ")":
                        raise Exception(f'{peek().loc}: extra "," found')
                else:
                    if peek().text != ")":
                        raise Exception(
                            f'{peek().loc}: unexpected symbol "{peek().text}"'
                        )
            consume(")")
            consume("=>")
            output_type = parse_type()
            return types.FunType(input_types, output_type)
        raise Exception(f'{peek().loc}: expected type, found "{peek().text}"')

    def parse_var() -> ast.VarDec:
        var_tok = consume("var")
        left = consume()
        if left.ttype != "identifier":
            raise Exception(
                f'{peek().loc}: expected identifier after var, found "{left.text}"'
            )
        # Optional type declaration
        typ = types.Unit
        if peek().text == ":":
            consume(":")
            typ = parse_type()
        consume("=")
        right = parse_expression()
        return ast.VarDec(left.text, right, loc=var_tok.loc, typ=typ)

    def parse_block() -> ast.Block:
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
                if pos == len(tokens):
                    break
            else:
                # ; is optional after }
                if tokens[pos - 1].text == "}":
                    continue
                if peek().text != "}":
                    raise Exception(f"{peek().loc}: missing ;")
        if void:
            exps.append(ast.Literal(None))
        consume("}")
        return ast.Block(exps, loc=loc)

    def parse_while_expression() -> ast.While:
        loc = consume("while").loc
        condition = parse_expression()
        consume("do")
        block = parse_block()
        return ast.While(condition, block, loc=loc)

    def parse_fundef() -> ast.FunDef:
        consume("fun")
        token = consume()
        args = []
        arg_types = []
        if token.ttype != "identifier":
            raise Exception(f"{token.loc}: function name must be an identifier")
        consume("(")
        while not peek().text == ")":
            param = consume()
            if param.ttype != "identifier":
                raise Exception(
                    f"{param.loc}: expected function parameter, found {param.text}"
                )
            consume(":")
            typ = parse_type()
            args.append(ast.Identifier(param.text, typ=typ, loc=param.loc))
            arg_types.append(typ)
            if peek().text != ",":
                break
            consume(",")
        consume(")")
        consume(":")
        ret = parse_type()
        body = parse_block()
        return ast.FunDef(
            token.text,
            args,
            body,
            typ=types.FunType(arg_types, ret),
            loc=token.loc,
        )

    def parse_module() -> ast.Module:
        funs = []
        exps = []
        void = True
        while pos < len(tokens):
            void = False
            if pos == len(tokens):
                break
            if peek().text == "fun":
                funs.append(parse_fundef())
            else:
                exps.append(parse_var() if peek().text == "var" else parse_expression())
                if pos == len(tokens):
                    break
                if peek().text == ";":
                    void = True
                    consume(";")
                else:
                    if tokens[pos - 1].text == "}":
                        continue
                    break
        if void:
            exps.append(ast.Literal(None))
        return ast.Module(funs, exps)

    # Finall Parser Function Call
    result = parse_module()
    if pos < len(tokens):
        raise Exception(f"{peek().loc}: unexpected token {peek().text}")
    return result
