"""Resumen estructurado de análisis sintáctico.

Este módulo organiza y muestra la información proporcionada sobre
análisis sintáctico utilizando una estructura jerárquica de secciones.
Se puede ejecutar directamente para imprimir el contenido completo o
listar títulos disponibles y seleccionar una sección específica desde la
línea de comandos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import fill
import argparse
from typing import Iterable, List


LINE_WIDTH = 90


@dataclass
class Section:
    """Representa un apartado del contenido."""

    title: str
    description: str = ""
    bullet_points: List[str] = field(default_factory=list)
    subsections: List["Section"] = field(default_factory=list)

    def iter_sections(self) -> Iterable["Section"]:
        """Itera sobre todas las secciones descendientes, incluyéndose."""

        yield self
        for subsection in self.subsections:
            yield from subsection.iter_sections()

    def render(self, level: int = 0) -> str:
        """Devuelve una representación textual legible de la sección."""

        indent = "  " * level
        header = f"{indent}{self.title}\n"
        body_lines = [header]

        if self.description:
            wrapped = fill(self.description, LINE_WIDTH)
            body_lines.append("\n".join(f"{indent}{line}" for line in wrapped.splitlines()))

        if self.bullet_points:
            for bullet in self.bullet_points:
                wrapped = fill(bullet, LINE_WIDTH)
                bullet_lines = [f"{indent}- {wrapped.splitlines()[0]}"]
                bullet_lines.extend(
                    f"{indent}  {line}" for line in wrapped.splitlines()[1:]
                )
                body_lines.append("\n".join(bullet_lines))

        if self.subsections:
            for subsection in self.subsections:
                body_lines.append("\n" + subsection.render(level + 1))

        return "\n".join(body_lines)


def build_content() -> Section:
    """Construye la jerarquía de secciones a partir del texto fuente."""

    grammar_def = Section(
        title="5.1 Definición y Clasificación de Gramáticas",
        description=(
            "Una gramática es un conjunto finito de reglas que define todas las "
            "oraciones válidas de un lenguaje. Estas reglas describen la "
            "estructura y combinaciones permitidas de los elementos "
            "lingüísticos."
        ),
        bullet_points=[
            "La jerarquía de Chomsky clasifica las gramáticas en cuatro tipos "
            "según su poder generativo.",
            "Las gramáticas son esenciales en compiladores, procesamiento de "
            "lenguaje natural, análisis de código y sistemas de traducción "
            "automática.",
        ],
        subsections=[
            Section(
                title="Jerarquía de Chomsky",
                subsections=[
                    Section(
                        title="Gramáticas Regulares (Tipo 3)",
                        description=(
                            "Las más simples; reconocidas por autómatas finitos y "
                            "útiles para patrones básicos como expresiones regulares "
                            "o números telefónicos."
                        ),
                    ),
                    Section(
                        title="Gramáticas Libres de Contexto (Tipo 2)",
                        description=(
                            "Reconocidas por autómatas de pila. Fundamentales para los "
                            "lenguajes de programación y el análisis sintáctico "
                            "moderno."
                        ),
                    ),
                    Section(
                        title="Gramáticas Sensibles al Contexto (Tipo 1)",
                        description=(
                            "Sus reglas dependen del contexto que rodea a los símbolos, "
                            "lo que permite modelar aspectos complejos de lenguajes "
                            "naturales."
                        ),
                    ),
                    Section(
                        title="Gramáticas Recursivamente Enumerables (Tipo 0)",
                        description=(
                            "Sin restricciones en sus reglas y reconocidas por "
                            "máquinas de Turing; representan el máximo poder "
                            "computacional."
                        ),
                    ),
                ],
            ),
        ],
    )

    cfg_section = Section(
        title="5.2 Gramáticas Libres de Contexto (GLC)",
        description=(
            "En una GLC cada producción tiene un único no terminal en el lado "
            "izquierdo, por lo que la sustitución no depende del contexto. La "
            "forma general es A → γ, donde γ puede contener terminales y no "
            "terminales."
        ),
        bullet_points=[
            "Ejemplo: S → NP VP, que descompone una oración en un sintagma "
            "nominal seguido de un sintagma verbal.",
            "Aplicaciones clave: lenguajes de programación, procesamiento de "
            "lenguaje natural, diseño de compiladores y sistemas de traducción "
            "automática.",
        ],
    )

    derivation_trees = Section(
        title="5.3 Árboles de Derivación",
        description=(
            "Los árboles de derivación ilustran la estructura jerárquica de una "
            "oración según una gramática. Muestran paso a paso la construcción "
            "desde el símbolo inicial hasta los terminales."
        ),
        bullet_points=[
            "Los nodos internos representan categorías sintácticas.",
            "Las hojas contienen los símbolos terminales de la oración final.",
            "Las relaciones jerárquicas revelan cómo se agrupan los "
            "constituyentes.",
        ],
        subsections=[
            Section(
                title="Ejemplo: 'El gato duerme'",
                bullet_points=[
                    "La raíz S se expande en SN y SV.",
                    "El SN se descompone en el determinante 'El' y el nombre "
                    "'gato'.",
                    "El SV contiene el verbo 'duerme', produciendo la oración "
                    "final.",
                ],
            )
        ],
    )

    cnf = Section(
        title="5.4 Forma Normal de Chomsky",
        description=(
            "La Forma Normal de Chomsky (FNC) restringe las producciones para "
            "simplificar algoritmos de análisis sintáctico."),
        bullet_points=[
            "Producciones permitidas: A → BC, A → a, y S → ε (solo para el "
            "símbolo inicial).",
            "Ventajas: facilita algoritmos como CYK, simplifica el análisis "
            "computacional y permite optimizaciones.",
            "Toda gramática libre de contexto puede transformarse a FNC sin "
            "perder poder generativo.",
        ],
    )

    syntax_diagrams = Section(
        title="5.5 Diagramas de Sintaxis",
        description=(
            "Los diagramas de sintaxis ofrecen una representación visual de las "
            "reglas gramaticales mediante símbolos y flechas, útiles en el "
            "diseño de compiladores."),
        subsections=[
            Section(
                title="Diagramas de Transición",
                description=(
                    "Muestran el flujo de análisis a través de estados y "
                    "transiciones, facilitando la implementación de analizadores "
                    "automáticos."
                ),
            ),
            Section(
                title="Diagramas de Rieles",
                description=(
                    "Representan reglas como caminos con opciones alternativas y "
                    "bucles para repeticiones."
                ),
            ),
            Section(
                title="Aplicación en Compiladores",
                description=(
                    "Ayudan a visualizar el comportamiento esperado de un "
                    "analizador sintáctico y a comprender reglas complejas."
                ),
            ),
        ],
    )

    ambiguity = Section(
        title="5.6 Eliminación de la Ambigüedad",
        description=(
            "La ambigüedad ocurre cuando una oración admite múltiples "
            "interpretaciones. Resolverla es clave tanto en lenguajes naturales "
            "como de programación."),
        bullet_points=[
            "Ejemplo: 'Vi al hombre con el telescopio', que puede significar que "
            "el hablante usó el telescopio o que el hombre lo portaba.",
            "Estrategias: reescritura de gramáticas, restricciones semánticas, "
            "análisis contextual y reglas de precedencia.",
        ],
    )

    parsers = Section(
        title="5.7 Tipos de Analizadores Sintácticos",
        description=(
            "Los analizadores determinan si una cadena pertenece al lenguaje de "
            "una gramática y construyen su estructura sintáctica."),
        subsections=[
            Section(
                title="Analizadores Ascendentes (Bottom-Up)",
                description=(
                    "Construyen el árbol desde las hojas hasta la raíz mediante "
                    "reducciones. Ejemplos: LR(1), SLR y LALR."
                ),
            ),
            Section(
                title="Analizadores Descendentes (Top-Down)",
                description=(
                    "Parten del símbolo inicial y expanden derivaciones hasta "
                    "generar la entrada. Ejemplos: LL(1), descenso recursivo y "
                    "análisis predictivo."
                ),
            ),
        ],
    )

    predictive_table = Section(
        title="5.8 Matriz Predictiva, FIRST y FOLLOW",
        description=(
            "La matriz LL(1) se construye a partir de los conjuntos FIRST y "
            "FOLLOW, fundamentales para analizadores predictivos."),
        bullet_points=[
            "FIRST(γ) contiene los terminales que pueden iniciar cadenas "
            "derivadas de γ.",
            "FOLLOW(A) contiene los terminales que pueden aparecer después del "
            "no terminal A.",
            "El cálculo de FIRST y FOLLOW es iterativo y permite construir la "
            "tabla predictiva LL(1).",
        ],
    )

    error_handling = Section(
        title="5.9 Manejo de Errores en Análisis Sintáctico",
        description=(
            "Un analizador robusto debe detectar, reportar y recuperarse de "
            "errores. La calidad de este proceso es crítica para compiladores e "
            "intérpretes."),
        bullet_points=[
            "Detección de errores mediante la validación de reglas.",
            "Reporte claro que indique ubicación y naturaleza del problema.",
            "Técnicas de inserción o eliminación de tokens para corregir "
            "fallos.",
            "Recuperación por pánico descartando símbolos hasta un punto de "
            "sincronización.",
        ],
        subsections=[
            Section(
                title="Caso práctico: 'Los estudiantes escriben programas complejos'",
                bullet_points=[
                    "Paso 1: tokenización de la oración.",
                    "Paso 2: construcción del árbol sintáctico con S → SN SV.",
                    "Paso 3: cálculo de FIRST y FOLLOW (por ejemplo, FIRST(S) = {Los}).",
                    "Paso 4: verificación de ambigüedades y errores.",
                    "Análisis detallado que revisa concordancia, dependencias y "
                    "completitud estructural.",
                ],
            )
        ],
    )

    module6 = Section(
        title="Módulo 6: Casos Prácticos en Lenguajes de Programación",
        description=(
            "Explora cómo se aplican las técnicas de análisis sintáctico en "
            "construcciones típicas de lenguajes de programación."),
        subsections=[
            Section(
                title="Expresiones Aritméticas",
                description=(
                    "Analiza precedencia y asociatividad, por ejemplo (a + b) * c, "
                    "usando reglas Expresión → Término (+ Término)* y Término → "
                    "Factor (* Factor)*."
                ),
            ),
            Section(
                title="Declaración de Variables",
                description=(
                    "Interpreta sentencias como int x = 10; con reglas "
                    "Declaración → Tipo ID (= Expresión)? ; y Tipo → int | float | "
                    "string."
                ),
            ),
            Section(
                title="Estructuras de Control",
                description=(
                    "Examinar sentencias if y while, incluyendo la resolución del "
                    "'else colgante'."
                ),
                bullet_points=[
                    "Regla general: Sentencia → if (Condición) { Bloque } | while (Condición) { Bloque }",
                    "Impacto: una gramática correcta evita ambigüedades en la "
                    "asociación del 'else'.",
                ],
            ),
            Section(
                title="Definición de Funciones",
                description=(
                    "Describe firmas y cuerpos de funciones con la regla "
                    "Función → Tipo ID (Parámetros) { Bloque } y la producción de "
                    "parámetros opcionales."
                ),
            ),
            Section(
                title="Caso práctico 2: Análisis de estructuras de control",
                description=(
                    "Ejemplo de cómo un analizador maneja una sentencia if-else "
                    "anidada para resolver el 'else colgante'."
                ),
                bullet_points=[
                    "Gramática resolutiva que asocia el else con el if más cercano.",
                    "Tokenización previa de la sentencia.",
                    "Construcción del árbol sintáctico abstracto (AST).",
                    "Aplicación de reglas de precedencia para asociar correctamente "
                    "las cláusulas else.",
                ],
            ),
        ],
    )

    return Section(
        title="Análisis Sintáctico: Fundamentos y Técnicas Clave",
        description=(
            "Resumen de conceptos esenciales de análisis sintáctico para "
            "lenguajes naturales y de programación."),
        subsections=[
            grammar_def,
            cfg_section,
            derivation_trees,
            cnf,
            syntax_diagrams,
            ambiguity,
            parsers,
            predictive_table,
            error_handling,
            module6,
        ],
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Muestra un resumen estructurado del análisis sintáctico."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista los títulos disponibles en el contenido",
    )
    parser.add_argument(
        "--section",
        type=str,
        help="Imprime solo la sección cuyo título coincida (búsqueda insensible a mayúsculas).",
    )
    return parser.parse_args()


def list_titles(root: Section) -> str:
    """Genera una lista de títulos jerárquicos."""

    lines = []
    for section in root.iter_sections():
        depth = title_depth(root, section)
        prefix = "  " * depth + ("- " if depth else "")
        lines.append(f"{prefix}{section.title}")
    return "\n".join(lines)


def title_depth(root: Section, target: Section, level: int = 0) -> int:
    if root is target:
        return level
    for subsection in root.subsections:
        depth = title_depth(subsection, target, level + 1)
        if depth != -1:
            return depth
    return -1


def find_section(root: Section, title: str) -> Section | None:
    lower = title.lower()
    for section in root.iter_sections():
        if section.title.lower() == lower:
            return section
    return None


def main() -> None:
    args = parse_arguments()
    content = build_content()

    if args.list:
        print(list_titles(content))
        return

    if args.section:
        section = find_section(content, args.section)
        if not section:
            raise SystemExit(f"Sección no encontrada: {args.section}")
        print(section.render())
        return

    print(content.render())


if __name__ == "__main__":
    main()
