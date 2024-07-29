# Example usage (this part can be in a separate test or main file):
from instructions.infix_expression_calculator_instruction import InfixExpressionCalculatorInstruction
from lexer.arithmetic_expression import ArithmeticExpression


# Example usage
if __name__ == "__main__":
    # set the my test expression
    expression = "3 + 5 * (10 - -4.5)"
    
    # Create an instance of InfixExpressionCalculatorInstruction
    arithmetic_expression = ArithmeticExpression(expression)
    json_expression = arithmetic_expression.parse_as_json()
    
    # Initialize the instruction with the JSON and original expression
    instruction = InfixExpressionCalculatorInstruction(json_expression, expression)
    
    # Create the instruction and get different outputs
    created_instruction = instruction.create_instruction()
    
    print("Instruction (dictionary format):")
    print(created_instruction)
    print()
    
    print("Instruction in JSON format:")
    print(instruction.to_json())
    print()
    
    print("Instruction in JSONL format:")
    print(instruction.to_jsonl())
    print()
    
    print("Instruction in LLaMA2 format:")
    print(instruction.to_llama2())
    print()
    
    print("Instruction in QA format:")
    print(instruction.to_qa())
    print()
