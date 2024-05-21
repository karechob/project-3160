"""
Instructions

 The following defines a simple language, in which a program consists of assignments and each variable is assumed 
to be of the integer type. For the sake of simplicity, only operators that give integer values are included. 
Write an interpreter for the language in a language of your choice. Your interpreter should be able to do the following 
for a given program: (1) detect syntax errors; (2) report uninitialized variables; and 
(3) perform the assignments if there is no error and print out the values of all the variables after all the assignments are done.

Program:
	Assignment*

Assignment:
	Identifier = Exp;

Exp: 
	Exp + Term | Exp - Term | Term

Term:
	Term * Fact  | Fact

Fact:
	( Exp ) | - Fact | + Fact | Literal | Identifier

Identifier:
     	Letter [Letter | Digit]*

Letter:
	a|...|z|A|...|Z|_

Literal:
	0 | NonZeroDigit Digit*
		
NonZeroDigit:
	1|...|9

Digit:
	0|1|...|9

must take commands from command line
"""
import argparse

# valid tokens
class Token:
    INTEGER, PLUS, MINUS, MUL, DIV, LPARENTH, RPARENTH, ASSIGN, VARIABLE, SEMICOLON, EOF = (
        'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'ASSIGN', 'LPARENTH', 'RPARENTH', 'VARIABLE', 'SEMICOLON', 'EOF'
    )


    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()

# lexical analyzer / scanner
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    # def peek(self):
    #     peek_pos = self.pos + 1
    #     if peek_pos > len(self.text) - 1:
    #         return None
    #     else:
    #         return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if result.startswith('0') and len(result) > 1:
            self.error()
        return int(result)

    def variable(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result
        
    def get_next_token(self):                   #reading tokens
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(Token.INTEGER, self.integer())

            if self.current_char.isalpha() or self.current_char == '_':
                return Token(Token.VARIABLE, self.variable())
            
            if self.current_char == '(':
                self.advance()
                return Token(Token.LPARENTH, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(Token.RPARENTH, ')')

            if self.current_char == '+':
                self.advance()
                return Token(Token.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(Token.MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(Token.MUL, '*')
            
            if self.current_char == '/':
                self.advance()
                return Token(Token.DIV, '/')

            if self.current_char == ';':
                self.advance()
                return Token(Token.SEMICOLON, ';')

            if self.current_char == '=':
                self.advance()
                return Token(Token.ASSIGN, '=')

            self.error()

        return Token(Token.EOF, None)

# interpreter class 
class Interpreter:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.variables = {}

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
        
# deals with parenthesis and the uniary minus
    def factor(self):
        negate = 0
        while self.current_token.type == Token.MINUS:
            negate += 1
            self.eat(Token.MINUS)

        token = self.current_token
        if token.type == Token.INTEGER:
            self.eat(Token.INTEGER)
            result = token.value
        elif token.type == Token.VARIABLE:
            var_name = token.value
            self.eat(Token.VARIABLE)
            result = self.variables.get(var_name, 0)
        elif token.type == Token.LPARENTH:
            self.eat(Token.LPARENTH)
            result = self.expr()
            self.eat(Token.RPARENTH)
        else:
            self.error("Invalid syntax with negation")

        if negate % 2 != 0:
            result = -result
        return result

# function that deals with division and multiplication
    def term(self):
        result = self.factor()
        while self.current_token.type in (Token.MUL, Token.DIV):
            token = self.current_token
            if token.type == Token.MUL:
                self.eat(Token.MUL)
                result *= self.factor()
            elif token.type == Token.DIV:
                self.eat(Token.DIV)
                divisor = self.factor()
                if divisor == 0:
                    raise Exception("Division by zero")
                result /= divisor
        return result

# fuction for dealing with expressions
    def expr(self):
        result = self.term()
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            token = self.current_token
            self.eat(token.type)
            if token.type == Token.MINUS and self.current_token.type == Token.PLUS:
                self.eat(Token.PLUS)
            result = result + self.term() if token.type == Token.PLUS else result - self.term()
        return result

# parser function
    def parse(self):
        while self.current_token.type != Token.EOF:
            if self.current_token.type == Token.VARIABLE:
                var_name = self.current_token.value
                self.eat(Token.VARIABLE)
                self.eat(Token.ASSIGN)
                var_value = self.expr()
                self.variables[var_name] = var_value
                self.eat(Token.SEMICOLON)
            else:
                self.error()

        return '\n'.join('{k} = {v}'.format(k=k, v=v) for k, v in self.variables.items())

# main reads input from command line
def main():
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else ''
    lexer = Lexer(text)
    interpreter = Interpreter(lexer)
    try:
        result = interpreter.parse()
        print(result)
    except Exception as e:
        print('error')


if __name__ == '__main__':
    main()