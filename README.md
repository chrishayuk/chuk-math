# Introduction
This is an experimental compiler that can be used to generate math datasets.

## TODO
- Use the LLM to produce a nice answer from question and result
- Integrate the explanation
- Use the LLM to smooth out the explanation
- Add the rest of the instructions
- Add a judge model for validating

## Installation
To install dependencies

```bash
pip install -r requirements.txt
```

## Unit Test
To run unit testing

```bash
pytest
```

## CLI
The following section describes the CLI tools, namely

- expression generator
- tokenizer
- parser
- compiler

### Expression Generator
The expression generator allows you to generate a random expression based on specified difficulty.
The following will generate a single easy expression

```bash
python expression_generator_cli
```

The following allows you to specify your difficulty setting for the expression

```bash
python expression_generator_cli.py --difficulty "easy"
```

There are 7 difficulty settings

- "very easy"
- "easy"
- "pretty easy"
- "medium"
- "hard"
- "pretty hard"
- "very hard”

### Tokenizer CLI
The following shows how to use the tokenizer cli.  The tokenizer cli, accepts a math expression (one that has been generated from the expression generator), and returns it in it's tokenized form.

```bash
python tokenizer_cli.py "379 * 85"
```

### AST CLI
The following shows how to use the parser (ast cli).  The ast cli, accepts a math expression (one that has been generated from the expression generator), runs it through the tokenizer (similar to the tokenizer cli), and then runs the tokenized version of the expression through the parser to generate an Abstract Syntax Tree (AST).

```bash
python tokenizer_cli.py "379 * 85"
```

### Compiler CLI

```bash
python main.py "3 + 5 * (10 - 4)" --llm "mistral-nemo"
```