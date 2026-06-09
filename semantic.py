# semantic.py
import sys
from symbol_table import TablaSimbolos

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.logs_consola = []
        self.codigo_generado = []

    def analizar_y_ejecutar(self, raiz_ast):
        self.logs_consola = []
        self.codigo_generado = []
        
        self.logs_consola.append("--- [INICIANDO PIPELINE SEMÁNTICO Y BACK-END] ---")
        
        try:
            # FASE 1: Verificación Semántica Estricta (Enlazado de Nombres)
            self.logs_consola.append("[FASE SEMÁNTICA]: Validando enlazado de nombres...")
            raiz_ast.chequeo_semantico(self.tabla_simbolos)
            self.logs_consola.append(" -> Éxito: No hay variables huérfanas.")

            # FASE 2: Optimización del Código (Plegado de Constantes)
            self.logs_consola.append("\n[FASE OPTIMIZACIÓN]: Ejecutando Plegado de Constantes en el AST...")
            raiz_ast = raiz_ast.optimizar()
            self.logs_consola.append(" -> Éxito: Árbol de Sintaxis Abstracta optimizado.")

            # FASE 3: Evaluación y Cálculo de Resultados Reales
            self.logs_consola.append("\n[FASE EVALUACIÓN]: Calculando operaciones aritméticas...")
            # Limpiamos la tabla para poblarla con los valores reales finales calculados
            self.tabla_simbolos.simbolos.clear()
            raiz_ast.evaluar(self.tabla_simbolos, self.logs_consola)
            self.logs_consola.append(" -> Éxito: Operaciones financieras procesadas y guardadas.")

            # FASE 4: Generación de Código Objeto (Simulación de Subrutinas)
            self.logs_consola.append("\n[FASE BACK-END]: Traduciendo llamadas a funciones a Ensamblador/C...")
            raiz_ast.generar_codigo(self.codigo_generado)
            self.logs_consola.append(" -> Éxito: Simulación de paso de parámetros por referencia completada.")

            return True

        except NameError as error_nombre:
            self.logs_consola.append(f"\n[VIOLACIÓN SEMÁNTICA]: {error_nombre}")
            return False
        except ZeroDivisionError as error_div:
            self.logs_consola.append(f"\n[ERROR MATEMÁTICO SEMÁNTICO]: {error_div}")
            return False
        except Exception as e:
            self.logs_consola.append(f"\n[ERROR INESPERADO]: {e}")
            return False