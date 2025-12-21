# Introduction
The lexer is really responsible for taking an incoming source file and converting it into a set of tokens that will be used as inputs for the parsing stage.

## BASIC Implementation
The current implementation of the tokenizer is fully compliant with Dartmouth BASIC 1964 edition.  It seems to also be compatible with variants such as Vintage BASIC.   Maybe in the future it will handle other variants such as C64 BASIC or Sinclair BASIC

### Supported Tokens
The current tokenizer supports the following constructs

- Numbers
- Operators
- Parenthesis

## Testing
If you wish to test the the tokenizer then you can run

```bash
pytest
```