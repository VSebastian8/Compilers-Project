from compiler.token import Token, L
from compiler.tokenizer import tokenize

def test_tokenizer_basics() -> None:
    assert tokenize("  \n \t \n\n\n\n  ") == []
    assert tokenize("  if  3\nwhile") == [
        Token('if', 'identifier', (0, 2)), 
        Token('3', 'integer', (0, 6)), 
        Token('while', 'identifier', (1, 0))
        ]
    assert tokenize("  if  x12 321\tbreak") == [
        Token('if', 'identifier', L), 
        Token('x12', 'identifier', L), 
        Token('321', 'integer', L), 
        Token('break', 'identifier', L)
        ]
