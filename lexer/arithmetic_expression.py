# arithmetic_expression.py
import json
from typing import List, Dict, Any
from lexer.tokenizer import Tokenizer, TokenizationError

class ArithmeticExpression:
    def __init__(self, expression: str):
        self.expression = expression.strip()

    def parse(self) -> List[Dict[str, Any]]:
        tokens = []
        try:
            # initialize a tokenizer for the expression
            tokenizer = Tokenizer(self.expression)

            # tokenize and to te list
            token_list = tokenizer.tokenize()

            # set the previous token to none
            previous_token = None

            # loop through the tokens
            for token in token_list:
                # get the current token
                token_dict = {
                    'type': token.type.lower(),
                    'value': token.value,
                    'position': token.position
                }

                # add the token to the to the tokens list
                tokens.append(token_dict)

                # Error handling for consecutive operators
                if previous_token and previous_token['type'] == 'operator' and token_dict['type'] == 'operator':
                    # invalid expression
                    raise ValueError(f"Invalid expression: consecutive operators '{previous_token['value']}{token_dict['value']}' at position {token_dict['position']}")

                # set the current token as the previous token
                previous_token = token_dict

            # Error handling for ending with an operator
            if tokens and tokens[-1]['type'] == 'operator':
                # invalid expression
                raise ValueError(f"Invalid expression: ends with an operator '{tokens[-1]['value']}'")

        except TokenizationError as error:
            # error parsing the expression
            raise ValueError(f"Error parsing expression '{self.expression}': {error}")
        
        # return the tokens
        return tokens

    def parse_as_json(self) -> str:
        # parse
        tokens = self.parse()

        # return as json
        return json.dumps({'tokens': tokens}, indent=2)
