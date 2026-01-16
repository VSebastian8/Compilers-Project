from compiler.tokenizer import tokenize

def test_tokenizer_basics() -> None:
    assert tokenize("  \n \t \n\n\n\n  ") == []
    assert tokenize("  if  3\nwhile") == ['if', '3', 'while']
    assert tokenize("  if  x12 321\tbreak") == ['if', 'x12', '321', 'break']
