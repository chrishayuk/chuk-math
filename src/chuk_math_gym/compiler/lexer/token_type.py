class TokenType:
    # Numeric and identifier types
    NUMBER = 'NUMBER'
    IDENTIFIER = 'IDENTIFIER'
    FUNCTION = 'FUNCTION'
    WHITESPACE = 'WHITESPACE'
    UNKNOWN = 'UNKNOWN'

    # Punctuation
    COMMA = 'COMMA'
    COLON = 'COLON'
    SEMI = 'SEMI'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    DOLLAR = 'DOLLAR'
    PERCENT = 'PERCENT'

    # Operators
    EQ = 'EQ'            # '=' and '=='
    NE = 'NE'            # '!=' and '<>'
    LE = 'LE'            # '<='
    LT = 'LT'            # '<'
    GE = 'GE'            # '>='
    GT = 'GT'            # '>'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    POW = 'POW'
    DOT = 'DOT'
    AND = 'AND'          # '&&'
    OR = 'OR'            # '||'
    NOT = 'NOT'          # '!'
