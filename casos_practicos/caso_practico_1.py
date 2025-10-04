"""Caso práctico 1: análisis de expresiones aritméticas.

Este script ilustra cómo un analizador sintáctico sencillo procesa las
expresiones "3 + 4 * 2" y "(3 + 4) * 2", mostrando la construcción del
árbol de derivación y la evaluación paso a paso respetando las reglas de
precedencia y asociatividad de los operadores aritméticos básicos.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable, Iterator, List, Tuple


class TokenType(Enum):
    """Tipos de tokens admitidos por el analizador."""

    NUMBER = auto()
    PLUS = auto()
    TIMES = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """Token reconocido por el analizador léxico."""

    type: TokenType
    lexeme: str


class Lexer:
    """Divide una cadena en tokens comprensibles por el parser."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0

    def _peek(self) -> str:
        return self.source[self.position] if self.position < len(self.source) else ""

    def _advance(self) -> str:
        char = self._peek()
        self.position += 1
        return char

    def tokens(self) -> Iterator[Token]:
        while self.position < len(self.source):
            char = self._peek()
            if char.isspace():
                self._advance()
                continue
            if char.isdigit():
                yield self._number()
                continue
            if char == "+":
                self._advance()
                yield Token(TokenType.PLUS, "+")
                continue
            if char == "*":
                self._advance()
                yield Token(TokenType.TIMES, "*")
                continue
            if char == "(":
                self._advance()
                yield Token(TokenType.LPAREN, "(")
                continue
            if char == ")":
                self._advance()
                yield Token(TokenType.RPAREN, ")")
                continue
            raise ValueError(f"Símbolo inesperado: {char!r}")
        yield Token(TokenType.EOF, "")

    def _number(self) -> Token:
        start = self.position
        while self._peek().isdigit():
            self._advance()
        return Token(TokenType.NUMBER, self.source[start : self.position])


class ASTNode:
    """Nodo base del árbol sintáctico."""

    def evaluate(self) -> Tuple[int, List[str]]:
        raise NotImplementedError

    def pretty(self, prefix: str = "", is_tail: bool = True) -> Iterable[str]:
        raise NotImplementedError


@dataclass
class Number(ASTNode):
    value: int

    def evaluate(self) -> Tuple[int, List[str]]:
        return self.value, []

    def pretty(self, prefix: str = "", is_tail: bool = True) -> Iterable[str]:
        yield f"{prefix}{'└── ' if is_tail else '├── '}Número({self.value})"


@dataclass
class BinaryOp(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode

    def evaluate(self) -> Tuple[int, List[str]]:
        left_value, left_steps = self.left.evaluate()
        right_value, right_steps = self.right.evaluate()
        if self.operator == "+":
            result = left_value + right_value
            operation = f"Adición: {left_value} + {right_value} = {result}"
        elif self.operator == "*":
            result = left_value * right_value
            operation = f"Multiplicación: {left_value} * {right_value} = {result}"
        else:
            raise ValueError(f"Operador no soportado: {self.operator}")
        return result, left_steps + right_steps + [operation]

    def pretty(self, prefix: str = "", is_tail: bool = True) -> Iterable[str]:
        connector = "└── " if is_tail else "├── "
        yield f"{prefix}{connector}Expr({self.operator})"
        next_prefix = prefix + ("    " if is_tail else "│   ")
        yield from self.left.pretty(next_prefix, False)
        yield from self.right.pretty(next_prefix, True)


class Parser:
    """Analizador predictivo recursivo para la gramática LL(1)."""

    def __init__(self, tokens: Iterator[Token]):
        self.tokens = iter(tokens)
        self.current = next(self.tokens)

    def _consume(self, expected: TokenType) -> Token:
        if self.current.type != expected:
            raise ValueError(f"Se esperaba {expected} y se encontró {self.current.type}")
        token = self.current
        if expected != TokenType.EOF:
            self.current = next(self.tokens)
        return token

    def parse(self) -> ASTNode:
        expr = self._expression()
        self._consume(TokenType.EOF)
        return expr

    def _expression(self) -> ASTNode:
        node = self._term()
        while self.current.type == TokenType.PLUS:
            self._consume(TokenType.PLUS)
            node = BinaryOp("+", node, self._term())
        return node

    def _term(self) -> ASTNode:
        node = self._factor()
        while self.current.type == TokenType.TIMES:
            self._consume(TokenType.TIMES)
            node = BinaryOp("*", node, self._factor())
        return node

    def _factor(self) -> ASTNode:
        if self.current.type == TokenType.NUMBER:
            value = int(self._consume(TokenType.NUMBER).lexeme)
            return Number(value)
        if self.current.type == TokenType.LPAREN:
            self._consume(TokenType.LPAREN)
            expr = self._expression()
            self._consume(TokenType.RPAREN)
            return expr
        raise ValueError(f"Token inesperado: {self.current}")


def analyze_expression(expression: str) -> Tuple[ASTNode, int, List[str]]:
    lexer = Lexer(expression)
    tokens = lexer.tokens()
    parser = Parser(tokens)
    tree = parser.parse()
    result, steps = tree.evaluate()
    return tree, result, steps


def display_analysis(expression: str) -> None:
    print("=" * 80)
    print(f"Expresión: {expression}")
    tree, result, steps = analyze_expression(expression)
    print("\nÁrbol sintáctico:")
    for line in tree.pretty():
        print(line)
    print("\nEvaluación paso a paso:")
    if steps:
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step}")
    else:
        print("Sin operaciones intermedias.")
    print(f"\nResultado: {result}")


if __name__ == "__main__":
    print("Caso Práctico 1: Análisis de Expresiones Aritméticas")
    print("Gramática utilizada:")
    print("  Expresión -> Término (+ Término)*")
    print("  Término -> Factor (* Factor)*")
    print("  Factor -> Número | ( Expresión )")
    print("\nLa gramática respeta la precedencia de la multiplicación sobre la suma y la\nizquierda asociatividad de ambos operadores.\n")

    for sample in ["3 + 4 * 2", "(3 + 4) * 2"]:
        display_analysis(sample)

    print("\nConclusión:")
    print(
        "El ejemplo muestra cómo la precedencia y asociatividad determinan el orden "+
        "de evaluación y, por ende, el resultado final de cada expresión."
    )
