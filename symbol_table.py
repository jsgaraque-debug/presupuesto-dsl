# symbol_table.py
class TablaSimbolos:
    def __init__(self):
        # Almacena: { 'nombre_variable': {'tipo': 'NUMBER', 'valor': 120} }
        self.simbolos = {}

    def declarar(self, nombre, tipo_nombre, valor=0):
        """Registra una variable con su tipo y su valor calculado actual."""
        self.simbolos[nombre] = {'tipo': tipo_nombre, 'valor': valor}

    def buscar(self, nombre):
        """Retorna el diccionario de propiedades de la variable si existe."""
        return self.simbolos.get(nombre, None)

    def obtener_valor(self, nombre):
        """Retorna el valor numérico de la variable."""
        info = self.buscar(nombre)
        return info['valor'] if info else None

    def esta_declarada(self, nombre):
        return nombre in self.simbolos

    def __str__(self):
        return str(self.simbolos)