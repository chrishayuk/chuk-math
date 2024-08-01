from compiler.parser.arithmetic_expression import ArithmeticExpression
from instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction

if __name__ == "__main__":
    # Define the expression to be evaluated
    expression = "3 + 5 * (10 - 4)"

    # Parse the tokens into an AST using the ArithmeticExpression class
    arithmetic_expression = ArithmeticExpression(expression)

    ast = arithmetic_expression.parse()
    print("\nAbstract Syntax Tree (AST):")
    print(ast)

    # Optional: Convert the AST to JSON for visualization or further processing
    json_ast = arithmetic_expression.parse_as_json()
    print("\nAST as JSON:")
    print(json_ast)

    # Optional: Generate instructional outputs
    try:
        # Assuming InfixExpressionCalculatorInstruction expects JSON representation of the AST and the original expression
        instruction = InfixExpressionCalculatorInstruction(json_ast, expression)

        # Create the instruction and print different outputs
        created_instruction = instruction.create_instruction()

        print("\nInstruction (dictionary format):")
        print(created_instruction)

        print("\nInstruction in JSON format:")
        print(instruction.to_json())

        print("\nInstruction in JSONL format:")
        print(instruction.to_jsonl())

        print("\nInstruction in LLaMA2 format:")
        print(instruction.to_llama2())

        print("\nInstruction in QA format:")
        print(instruction.to_qa())

    except Exception as e:
        print(f"Error during instruction generation: {e}")
