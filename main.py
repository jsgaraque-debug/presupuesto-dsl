import sys
from lexer import lexer
from parser import parser
from semantic import AnalizadorSemantico

def ejecutar_compilador(ruta_archivo):
    # 1. Leer el archivo de código fuente del DSL
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_archivo} no existe.")
        return

    print("      COMPILADOR DSL-PRESUPUESTO (SEMANA 2)       ")
    print(f"Código fuente detectado:\n{codigo_fuente.strip()}\n")

    # 2. Fase de Análisis Léxico y Sintáctico (Genera el AST)
    print("--- [FRENTE DEL COMPILADOR (LEXER/PARSER)] ---")
    ast_generado = parser.parse(codigo_fuente, lexer=lexer)
    
    if ast_generado is None:
        print("ERROR: El proceso se detuvo debido a errores sintácticos.")
        return
    print("Análisis sintáctico completado. AST construido con éxito.")

    # 3. Fase de Análisis Semántico 
    analizador_semantico = AnalizadorSemantico()
    es_valido = analizador_semantico.analizar_y_ejecutar(ast_generado)

    if es_valido:
        print(">>> Compilación parcial exitosa (Fases 1, 2 y 3 listas).")
    else:
        print(">>> Compilación fallida debido a la violación de reglas semánticas.")

if __name__ == "__main__":
    # Ejecución utilizando la ruta de ejemplo estructurada en el proyecto
    ejecutar_compilador("examples/test.text")