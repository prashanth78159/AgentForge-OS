
import re

TOKEN_REGEX = [
    ("AGENT", r'agent'),
    ("IDENTIFIER", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("STRING", r'"[^"]*"'),
    ("ARROW", r'->'),
    ("COLON", r':'),
    ("LPAREN", r'\('),
    ("RPAREN", r'\)'),
    ("LBRACE", r'{'),
    ("RBRACE", r'}'),
    ("COMMA", r','),
    ("SKIP", r'[ \t\n]+'),
]

def tokenize(code):
    tokens = []
    while code:
        for token_type, pattern in TOKEN_REGEX:
            match = re.match(pattern, code)
            if match:
                value = match.group(0)
                code = code[len(value):]

                if token_type != "SKIP":
                    tokens.append((token_type, value))
                break
        else:
            raise SyntaxError(f"Unexpected token: {code[:10]}")

    return tokens
