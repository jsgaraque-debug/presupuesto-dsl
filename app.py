import os
import re
from flask import Flask, render_template, request, jsonify
from lexer import lexer
from parser import parser
from semantic import AnalizadorSemantico

app = Flask(__name__)

# Categorización de tokens para la tabla visual
CATEGORIAS_TOKEN = {
    'ID':                 'Identificador',
    'NUMERO':             'Literal numérico',
    'MAS':                'Operador aritmético',
    'MENOS':              'Operador aritmético',
    'POR':                'Operador aritmético',
    'DIVIDIDO':           'Operador aritmético',
    'ASIGNAR':            'Operador de asignación',
    'MAYOR':              'Operador relacional',
    'MENOR':              'Operador relacional',
    'IGUAL':              'Operador relacional',
    'SI':                 'Palabra reservada',
    'ENTONCES':           'Palabra reservada',
    'CALCULAR_IMPUESTO':  'Palabra reservada / función',
    'PAR_IZQ':            'Separador',
    'PAR_DER':            'Separador',
    'PUNTO_Y_COMA':       'Separador',
}

def extraer_tokens(codigo_fuente):
    """Pasa el lexer por el código y retorna la lista de tokens categorizados."""
    lexer.lineno = 1
    lexer.input(codigo_fuente)
    resultado = []
    orden = 1
    
    try:
        while True:
            tok = lexer.token()
            if not tok:
                break
            resultado.append({
                'orden':     orden,
                'valor':     str(tok.value),
                'tipo':      tok.type,
                'categoria': CATEGORIAS_TOKEN.get(tok.type, 'Desconocido'),
                'linea':     tok.lineno,
            })
            orden += 1
        return resultado, None
    except SyntaxError as err_lexico:
        return resultado, err_lexico


def extraer_ultima_variable(tabla_simbolos_raw):
    """
    Devuelve un dict con la última variable registrada en la tabla de símbolos:
    { 'nombre': 'BALANCE', 'tipo': 'NUMBER', 'valor': 1800.0 }
    Si la tabla está vacía retorna None.
    """
    if not tabla_simbolos_raw:
        return None

    ultimo_nombre = list(tabla_simbolos_raw.keys())[-1]
    ultimo_raw    = tabla_simbolos_raw[ultimo_nombre]          # ej. "NUMBER (Valor en RAM: 1800.0)"
    match = ultimo_raw.match(r'^(\w+)\s*\(Valor en RAM:\s*(.+)\)$') if hasattr(ultimo_raw, 'match') else re.match(r'^(\w+)\s*\(Valor en RAM:\s*(.+)\)$', ultimo_raw)

    tipo  = match.group(1) if match else 'NUMBER'
    valor_str = match.group(2) if match else '0'

    try:
        valor = float(valor_str)
    except ValueError:
        valor = 0.0

    return {
        'nombre': ultimo_nombre,
        'tipo':   tipo,
        'valor':  valor,
    }


@app.route('/')
def home():
    ruta_test = os.path.join('examples', 'test.text')
    if os.path.exists(ruta_test):
        with open(ruta_test, 'r', encoding='utf-8') as archivo:
            codigo_defecto = archivo.read()
    else:
        codigo_defecto = (
            "LUZ = 120;\n"
            "RENTA = 1500;\n"
            "GASTO_EXTRA = 100 + 50 + LUZ;\n"
            "GASTO_FIJO = RENTA + LUZ;\n"
            "SI GASTO_FIJO > 1000 ENTONCES CALCULAR_IMPUESTO(RENTA);"
        )
    return render_template('index.html', codigo=codigo_defecto)


@app.route('/compilar', methods=['POST'])
def compilar():
    datos = request.get_json()
    codigo_fuente = datos.get('codigo', '').strip()

    if not codigo_fuente:
        return jsonify({
            'exito': False,
            'fase_error': 'Inicial',
            'linea': '',
            'logs': ['Error: Código fuente vacío.'],
            'simbolos': {},
            'tokens': [],
            'codigo_objeto': '',
            'ultima_variable': None,
        })

    # --- NORMALIZACIÓN CRÍTICA DE LÍNEAS ---
    codigo_fuente = codigo_fuente.replace('\r\n', '\n').replace('\r', '\n')

    # --- FASE LÉXICA: extraer tokens para la tabla visual ---
    tokens_tabla, error_lexico_previo = extraer_tokens(codigo_fuente)

    if error_lexico_previo:
        mensaje_error = str(error_lexico_previo)
        linea_err = error_lexico_previo.lineno if error_lexico_previo.lineno else 1
        return jsonify({
            'exito': False,
            'fase_error': 'Léxica',
            'linea': linea_err,
            'logs': ["[FASE FRONT-END]: Error detectado en el Lexer.", mensaje_error],
            'simbolos': {},
            'tokens': tokens_tabla,
            'codigo_objeto': '// Generación de código abortada por fallas léxicas.',
            'ultima_variable': None,
        })

    # --- FASE 1 & 2: ANÁLISIS SINTÁCTICO ---
    try:
        lexer.lineno = 1
        ast_generado = parser.parse(codigo_fuente, lexer=lexer)
        
        if ast_generado is None:
            raise SyntaxError("Error Sintáctico: Estructura gramatical irreconocible.")

    except SyntaxError as err_sintaxis:
        mensaje_error = str(err_sintaxis)
        linea_err = err_sintaxis.lineno if err_sintaxis.lineno else "Desconocida"
        
        return jsonify({
            'exito': False,
            'fase_error': 'Sintáctica',
            'linea': linea_err,
            'logs': ["[FASE FRONT-END]: Error detectado en el Parser.", mensaje_error],
            'simbolos': {},
            'tokens': tokens_tabla,
            'codigo_objeto': '// Generación de código abortada por fallas sintácticas.',
            'ultima_variable': None,
        })

    # --- FASE 3: ANÁLISIS SEMÁNTICO Y BACK-END ---
    try:
        analizador = AnalizadorSemantico()
        resultado_correcto = analizador.analizar_y_ejecutar(ast_generado)

        linea_semantica = ""
        if not resultado_correcto:
            ultimo_log = analizador.logs_consola[-1] if analizador.logs_consola else ""
            match_var = re.search(r"variable\s+'([^']+)'", ultimo_log, re.IGNORECASE)
            if match_var:
                nombre_var = match_var.group(1)
                for t in tokens_tabla:
                    if t['valor'] == nombre_var:
                        linea_semantica = t['linea']
                        break

        tabla_resultados = {}
        for var, info in analizador.tabla_simbolos.simbolos.items():
            tabla_resultados[var] = f"{info['tipo']} (Valor en RAM: {info['valor']})"

        # ── NUEVA LÓGICA: última variable calculada ──────────────────────────
        ultima_var = extraer_ultima_variable(tabla_resultados)
        # ─────────────────────────────────────────────────────────────────────

        return jsonify({
            'exito': resultado_correcto,
            'fase_error': 'Ninguna' if resultado_correcto else 'Semántica',
            'linea': linea_semantica,
            'logs': analizador.logs_consola,
            'simbolos': tabla_resultados,
            'tokens': tokens_tabla,
            'codigo_objeto': "\n".join(analizador.codigo_generado) if resultado_correcto else '// Errores semánticos detectados.',
            'ultima_variable': ultima_var if resultado_correcto else None,
        })

    except Exception as e:
        msg_error = str(e)
        linea_critica = ""
        match_linea = re.search(r'(?:l&iacute;nea|linea|line)\s*(\d+)', msg_error, re.IGNORECASE)
        if match_linea:
            linea_critica = match_linea.group(1)

        return jsonify({
            'exito': False,
            'fase_error': 'Compilación General',
            'linea': linea_critica,
            'logs': [f"Error crítico en el Pipeline: {msg_error}"],
            'simbolos': {},
            'tokens': tokens_tabla,
            'codigo_objeto': '',
            'ultima_variable': None,
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)