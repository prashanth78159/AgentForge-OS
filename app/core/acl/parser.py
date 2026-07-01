
class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        token = self.current()
        if token and token[0] == token_type:
            self.pos += 1
            return token
        raise SyntaxError(f"Expected {token_type}, got {token}")

    def parse(self):
        return self.parse_agent()

    def parse_agent(self):
        self.eat("AGENT")
        name = self.eat("IDENTIFIER")[1]
        self.eat("LBRACE")

        nodes = []
        edges = []

        while self.current() and self.current()[0] != "RBRACE":
            if self.current()[0] == "IDENTIFIER":
                if self.tokens[self.pos + 1][0] == "COLON":
                    nodes.append(self.parse_node())
                elif self.tokens[self.pos + 1][0] == "ARROW":
                    edges.append(self.parse_edge())

        self.eat("RBRACE")

        return {
            "name": name,
            "nodes": nodes,
            "edges": edges
        }

    def parse_node(self):
        node_id = self.eat("IDENTIFIER")[1]
        self.eat("COLON")
        node_type = self.eat("IDENTIFIER")[1]

        self.eat("LPAREN")
        args = []

        while self.current()[0] != "RPAREN":
            token = self.eat("STRING")[1]
            args.append(token.strip('"'))

            if self.current()[0] == "COMMA":
                self.eat("COMMA")

        self.eat("RPAREN")

        return {
            "id": node_id,
            "type": node_type,
            "args": args
        }

    def parse_edge(self):
        source = self.eat("IDENTIFIER")[1]
        self.eat("ARROW")
        target = self.eat("IDENTIFIER")[1]

        return {"source": source, "target": target}
