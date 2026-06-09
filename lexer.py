import ply.lex as lex

# Definición de tokens obligatorios para el DSL de Presupuestos
tokens = (
    'ID', 'NUMERO', 'MAS', 'MENOS', 'POR', 'DIVIDIDO', 'ASIGNAR',
    'SI', 'ENTONCES', 'PAR_IZQ', 'PAR_DER', 'MAYOR', 'MENOR', 'IGUAL',
    'CALCULAR_IMPUESTO', 'PUNTO_Y_COMA'
)

# Expresiones regulares para tokens simples
t_MAS            = r'\+'
t_MENOS          = r'-'
t_POR            = r'\*'
t_DIVIDIDO       = r'/'
t_ASIGNAR        = r'='
t_PAR_IZQ        = r'\('
t_PAR_DER        = r'\)'
t_MAYOR          = r'>'
t_MENOR          = r'<'
t_IGUAL          = r'=='
t_PUNTO_Y_COMA   = r';'

# Reglas para palabras reservadas (Keywords)
def t_SI(t):
    r'SI'
    return t

def t_ENTONCES(t):
    r'ENTONCES'
    return t

def t_CALCULAR_IMPUESTO(t):
    r'CALCULAR_IMPUESTO'
    return t

# Regla para Identificadores (Variables)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# Regla para Números (Enteros o Flotantes)
def t_NUMERO(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# Caracteres ignorados (espacios y tabulaciones)
t_ignore = ' \t'

# Rastreo de números de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos
# Manejo de errores léxicos corregido en lexer.py
def t_error(t):
    mensaje = f"Error Léxico: Carácter inválido '{t.value[0]}' en la línea {t.lexer.lineno}."
    linea = t.lexer.lineno
    
    # Lanzamos un SyntaxError para que el backend lo capture y aborte la compilación
    err = SyntaxError(mensaje)
    err.lineno = linea
    raise err
# Construcción del analizador léxico
lexer = lex.lex()