## Steps

- [x] Tokenizer
- [x] Parser
- [x] Interpreter
- [x] Type Checker
- [x] IR Generator
- [x] Assembly Generator
- [x] Assembler

## Features

- [x] Integer literals
- [x] Boolean literals
- [x] Binary operators +, -, \*, /, %, ==, !=, <, <=, >, >=, and, or with precedence and left-associativity.
- [x] Unary operators - and not
- [x] Library functions print_int, read_int and print_bool
- [x] Blocks of statements
- [x] Local variables with initializers
- [x] Assignment statements (right-associative)
- [x] if-then and if-then-else
- [x] while loops
- [ ] break and continue
- [ ] functions

## Example Program

> ./compiler.sh compile programs/prime.txt --output=programs/is_prime
> chmod +x programs/is_prime
> ./programs/is_prime
