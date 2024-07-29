# Example usage (this part can be in a separate test or main file):
from lexer.arithmetic_expression import ArithmeticExpression


# Example usage
if __name__ == "__main__":
    # set the my test expression
    expression = "3 + 5 * (10 - -4.5)"

    # setup the parser
    parser = ArithmeticExpression(expression)

    # parse
    tokens = parser.parse()

    # print the tokens as a dictionary
    print("tokens:")
    print(tokens)

    # print the tokens as json
    print("json:")
    json_output = parser.parse_as_json()
    print(json_output)
