# ast_nodes.py

class Nodo:
    def chequeo_semantico(self, tabla_simbolos):
        raise NotImplementedError()

    def evaluar(self, tabla_simbolos, logs=None):
        """Calcula y retorna el valor real de la expresión en la RAM."""
        raise NotImplementedError()

    def optimizar(self):
        """Aplica Plegado de Constantes (Constant Folding) modificando el AST."""
        return self

    def generar_codigo(self, logs_asm):
        """Simula la traducción a código objeto (C y Ensamblador MIPS)."""
        pass


class NodoPrograma(Nodo):
    def __init__(self, instrucciones):
        self.instrucciones = instrucciones

    def chequeo_semantico(self, tabla_simbolos):
        for instruccion in self.instrucciones:
            instruccion.chequeo_semantico(tabla_simbolos)

    def evaluar(self, tabla_simbolos, logs=None):
        for instruccion in self.instrucciones:
            instruccion.evaluar(tabla_simbolos, logs)

    def optimizar(self):
        # Optimiza cada instrucción de la lista
        for i in range(len(self.instrucciones)):
            self.instrucciones[i] = self.instrucciones[i].optimizar()
        return self

    def generar_codigo(self, logs_asm):
        for instruccion in self.instrucciones:
            instruccion.generar_codigo(logs_asm)


class NodoAsignacion(Nodo):
    def __init__(self, nombre_id, expresion):
        self.nombre_id = nombre_id
        self.expresion = expresion

    def chequeo_semantico(self, tabla_simbolos):
        self.expresion.chequeo_semantico(tabla_simbolos)

        # Declaración temporal
        tabla_simbolos.declarar(self.nombre_id, 'NUMBER', 0)

    def evaluar(self, tabla_simbolos, logs=None):
        # Calcula la expresión
        valor_real = self.expresion.evaluar(tabla_simbolos, logs)

        # Guarda en tabla de símbolos
        tabla_simbolos.declarar(self.nombre_id, 'NUMBER', valor_real)

        # Mostrar resultado
        if logs is not None:
            logs.append(f"[RESULTADO] {self.nombre_id} = {valor_real}")

        return valor_real

    def optimizar(self):
        self.expresion = self.expresion.optimizar()
        return self

    def generar_codigo(self, logs_asm):
        self.expresion.generar_codigo(logs_asm)


class NodoOpBinaria(Nodo):
    def __init__(self, izq, op, der):
        self.izq = izq
        self.op = op
        self.der = der

    def chequeo_semantico(self, tabla_simbolos):
        self.izq.chequeo_semantico(tabla_simbolos)
        self.der.chequeo_semantico(tabla_simbolos)

    def evaluar(self, tabla_simbolos, logs=None):
        val_izq = self.izq.evaluar(tabla_simbolos, logs)
        val_der = self.der.evaluar(tabla_simbolos, logs)

        if self.op == 'MAS' or self.op == '+':
            return val_izq + val_der

        if self.op == 'MENOS' or self.op == '-':
            return val_izq - val_der

        if self.op == 'POR' or self.op == '*':
            return val_izq * val_der

        if self.op == 'DIVIDIDO' or self.op == '/':
            if val_der == 0:
                raise ZeroDivisionError(
                    "Error Semántico: División por cero detectada."
                )
            return val_izq / val_der

        return 0

    def optimizar(self):
        # Optimización recursiva
        self.izq = self.izq.optimizar()
        self.der = self.der.optimizar()

        # Plegado de constantes
        if isinstance(self.izq, NodoNumero) and isinstance(self.der, NodoNumero):
            val_optimizado = self.evaluar(None)

            print(f" -> [Optimización AST]: Simplificando a {val_optimizado}")

            return NodoNumero(val_optimizado)

        return self


class NodoNumero(Nodo):
    def __init__(self, valor):
        self.valor = valor

    def chequeo_semantico(self, tabla_simbolos):
        pass

    def evaluar(self, tabla_simbolos, logs=None):
        return float(self.valor)


class NodoId(Nodo):
    def __init__(self, nombre_id):
        self.nombre_id = nombre_id

    def chequeo_semantico(self, tabla_simbolos):
        if not tabla_simbolos.esta_declarada(self.nombre_id):
            raise NameError(
                f"Error Semántico: La variable '{self.nombre_id}' "
                f"no ha sido declarada."
            )

    def evaluar(self, tabla_simbolos, logs=None):
        if tabla_simbolos is None:
            return 0

        return tabla_simbolos.obtener_valor(self.nombre_id)


class NodoLlamada(Nodo):
    def __init__(self, nombre_func, arg):
        self.nombre_func = nombre_func
        self.arg = arg

    def chequeo_semantico(self, tabla_simbolos):
        self.arg.chequeo_semantico(tabla_simbolos)

    def evaluar(self, tabla_simbolos, logs=None):
        valor = self.arg.evaluar(tabla_simbolos, logs)

    # Cálculo real del impuesto: 5% del valor recibido como argumento
        impuesto_calculado = round(valor * 0.05, 2)
        base_imponible     = round(valor, 2)
        valor_neto         = round(valor - impuesto_calculado, 2)

        if logs is not None:
            logs.append(f"[FUNCIÓN] {self.nombre_func}() — Iniciando cálculo fiscal")
            logs.append(f"  Base imponible (SUELDO)  : $ {base_imponible}")
            logs.append(f"  Tarifa aplicada          : 5%")
            logs.append(f"  Retención calculada      : $ {impuesto_calculado}")
            logs.append(f"  Ingreso neto final       : $ {valor_neto}")

        return impuesto_calculado

    def generar_codigo(self, logs_asm):
        valor_final_param = (
            float(self.arg.valor)
            if isinstance(self.arg, NodoNumero)
            else "dinámico"
        )

        logs_asm.append(
            f"// --- CÓDIGO FINAL SIMULADO ({self.nombre_func}) ---"
        )

        logs_asm.append(
            "// Mecanismo: Paso de parámetros por Referencia Simple"
        )

        logs_asm.append(f"float VALOR_ARG = {valor_final_param};")

        logs_asm.append(
            f"{self.nombre_func}(&VALOR_ARG);\n"
        )

        logs_asm.append(
            "# --- TRADUCCIÓN A ENSAMBLADOR (MIPS SIMULADO) ---"
        )

        logs_asm.append(
            "LI $v0, 4"
        )

        logs_asm.append(
            "LA $a0, VALOR_ARG"
        )

        logs_asm.append(
            f"JAL {self.nombre_func}\n"
        )


class NodoCondicion(Nodo):
    def __init__(self, izq, op, der):
        self.izq = izq
        self.op = op
        self.der = der

    def chequeo_semantico(self, tabla_simbolos):
        self.izq.chequeo_semantico(tabla_simbolos)
        self.der.chequeo_semantico(tabla_simbolos)

    def evaluar(self, tabla_simbolos, logs=None):
        val_izq = self.izq.evaluar(tabla_simbolos, logs)
        val_der = self.der.evaluar(tabla_simbolos, logs)

        if self.op == '>':
            return val_izq > val_der

        if self.op == '<':
            return val_izq < val_der

        if self.op == '=' or self.op == '==':
            return val_izq == val_der

        return False


class NodoSi(Nodo):
    def __init__(self, condicion, accion):
        self.condicion = condicion
        self.accion = accion

    def chequeo_semantico(self, tabla_simbolos):
        self.condicion.chequeo_semantico(tabla_simbolos)
        self.accion.chequeo_semantico(tabla_simbolos)

    def evaluar(self, tabla_simbolos, logs=None):
        resultado = self.condicion.evaluar(tabla_simbolos, logs)

        if logs is not None:
            logs.append(f"[CONDICIÓN] Resultado = {resultado}")

        if resultado:
            self.accion.evaluar(tabla_simbolos, logs)

    def optimizar(self):
        self.condicion = self.condicion.optimizar()
        self.accion = self.accion.optimizar()

        return self

    def generar_codigo(self, logs_asm):
        self.accion.generar_codigo(logs_asm)