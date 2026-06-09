import ply.yacc as yacc
from lexer import tokens
# Importación de los nodos del AST con sus nombres en español
from ast_nodes import (
    NodoPrograma, NodoAsignacion, NodoOpBinaria, 
    NodoNumero, NodoId, NodoLlamada, NodoCondicion, NodoSi
)

# LALR PARSER
# Regla inicial: El programa es una lista de instrucciones
def p_programa(p):
    '''programa : lista_instrucciones'''
    p[0] = NodoPrograma(p[1])

# Manejo de listas de instrucciones (una o más)
def p_lista_instrucciones_unica(p):
    '''lista_instrucciones : instruccion'''
    p[0] = [p[1]]

def p_lista_instrucciones_multiples(p):
    '''lista_instrucciones : lista_instrucciones instruccion'''
    p[0] = p[1] + [p[2]]

# Tipos de instrucciones permitidas en el DSL
def p_instruccion(p):
    '''instruccion : asignacion
                   | estructura_condicional
                   | llamada_funcion'''
    p[0] = p[1]

# Regla para asignaciones: VARIABLE = EXPRESION;
def p_asignacion(p):
    '''asignacion : ID ASIGNAR expresion PUNTO_Y_COMA'''
    p[0] = NodoAsignacion(p[1], p[3])

# Regla para condionales: SI CONDICION ENTONCES INSTRUCCION
def p_estructura_condicional(p):
    '''estructura_condicional : SI condicion ENTONCES instruccion'''
    p[0] = NodoSi(p[2], p[4])

# Regla para la subrutina: CALCULAR_IMPUESTO(EXPRESION);
def p_llamada_funcion(p):
    '''llamada_funcion : CALCULAR_IMPUESTO PAR_IZQ expresion PAR_DER PUNTO_Y_COMA'''
    p[0] = NodoLlamada('CALCULAR_IMPUESTO', p[3])

# Reglas para operaciones lógicas/condiciones
def p_condicion(p):
    '''condicion : expresion MAYOR expresion
                 | expresion MENOR expresion
                 | expresion IGUAL expresion'''
    p[0] = NodoCondicion(p[1], p[2], p[3])

# Reglas de precedencia y operaciones aritméticas binarias
precedence = (
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR', 'DIVIDIDO'),
)

def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion POR expresion
                 | expresion DIVIDIDO expresion'''
    p[0] = NodoOpBinaria(p[1], p[2], p[3])

# Expresiones agrupadas entre paréntesis
def p_expresion_agrupada(p):
    '''expresion : PAR_IZQ expresion PAR_DER'''
    p[0] = p[2]

# Factores básicos: Números llanos
def p_expresion_numero(p):
    '''expresion : NUMERO'''
    p[0] = NodoNumero(p[1])

# Factores básicos: Variables (Identificadores)
def p_expresion_id(p):
    '''expresion : ID'''
    p[0] = NodoId(p[1])

# Manejo formal y estricto de errores sintácticos
def p_error(p):
    if p:
        mensaje = f"Error Sintáctico: Token inesperado '{p.value}' en la línea {p.lineno}."
        linea = p.lineno
    else:
        mensaje = "Error Sintáctico: Fin de archivo (EOF) inesperado. Estructura incompleta."
        linea = "Fin de archivo"
        
    # Lanzamos la excepción para cortar el modo de recuperación de PLY de raíz
    raise SyntaxError(mensaje, (None, linea, None, None))

# Construcción del analizador sintáctico (Parser)
parser = yacc.yacc()