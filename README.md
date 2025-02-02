# Introduction
This is an experimental compiler that can be used to generate math datasets.
At a high level the various cli's provided can perform the following tasks..

- generate synthetic data consisting of arithmetic expressions
- generate arithmetic expressions
- tokenize arithmetic expressions
- parse artithmetic expressions into an Abstract Syntax Tree
- compile arithmetic expressions

## Examples
For example, if you wish to generate a jsonl file that generates an expression, generates an abstract syntax tree of the expression, generates a sample arithmetic question for the expression, and some steps for the solving the expression including the answer, you can use the following command

```bash
uv run main.py "3 + 5 * (10 - 4)" --format jsonl
```

if you wish to generate an llm prettified version of the questions and explanations, you can run

```bash
uv run main.py "3 + 5 * (10 - 4)" --llm "phi4" --format jsonl
```

## Installation
The following outlines how to install the math compiler on your machine

### pip
If you are using pip, you can perform the following

To install dependencies

```bash
pip install -r requirements.txt
```

## uv
If you are using uv you should install uv first

```bash
pip install uv
```

and then resync dependencies

```bash
uv sync --reinstall
```

## Unit Test
To run unit testing

```bash
pytest
```

or

```bash
uv run pytest
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
The following shows how to use the arithmetic compiler cl.  The compiler cli, accepts a math expression (one that has been generated from the expression generator), runs it through the tokenizer (similar to the tokenizer cli), and then runs the tokenized version of the expression through the parser to generate an Abstract Syntax Tree (AST).  From the abstract syntax tree, the compiler will generate a natural language instruction from a range of options in a template list, for the specified instruction.  In the example below the compiler cli will use the default infix_expression_calculator_instruction.

```bash
python main.py "3 + 5 * (10 - 4)"
```

#### using an llm

```bash
python main.py "3 + 5 * (10 - 4)" --llm "mistral-nemo"
```


### generating chat sample
```bash
python generate_chat_samples.py -n 5 -d "very easy" --llm "granite3.1-dense" > chat_samples_medium.jsonl
```

### generating verifier sample
```bash
python generate_verifier_samples.py -n 20 -d "very easy" --llm "granite3.1-dense" > output/verifier_samples_medium.jsonl
```