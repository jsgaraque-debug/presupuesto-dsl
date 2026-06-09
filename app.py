from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


#Operaciones Con conjnutos
@app.route("/operacion_conjuntos", methods=["POST"])
def operacion_conjuntos():
    data = request.get_json()

    A = set(data.get("conjuntoA", "").replace(" ", "").split(",")) if data.get("conjuntoA") else set()
    B = set(data.get("conjuntoB", "").replace(" ", "").split(",")) if data.get("conjuntoB") else set()
    op = data.get("operacion")

    operaciones = {
        "pertenencia": lambda A, B: "B ⊆ A" if B.issubset(A) else "B ⊄ A",
        "union": lambda A, B: f"A ∪ B = {{{', '.join(sorted(A | B))}}}",
        "interseccion": lambda A, B: f"A ∩ B = {{{', '.join(sorted(A & B))}}}",
        "diferencia": lambda A, B: f"A - B = {{{', '.join(sorted(A - B))}}}",
        "complemento": lambda A, B: f"A \\ B = {{{', '.join(sorted(A - B))}}}",
        "simetrica": lambda A, B: f"A ∆ B = {{{', '.join(sorted(A ^ B))}}}",
    }

    resultado = operaciones.get(op, lambda A, B: "Operación no válida")(A, B)
    return jsonify({"resultado": resultado})

# Operaciones con Cadenas
@app.route("/operacion_cadenas", methods=["POST"])
def operacion_cadenas():
    data = request.get_json()
    A, B, op = data.get("cadenaA", ""), data.get("cadenaB", ""), data.get("operacion")

    def potenciacion(A, B):
        if B.isdigit():
            n = int(B)
            result = A * n  # concatenación n veces pegada
            # Si la potencia es muy larga, mostramos hasta 10 repeticiones + "..."
            if n > 10:
                return f"A^{n} = {A * 10}..."
            else:
                return f"A^{n} = {result}"
        return "La potencia debe ser un número entero"

    operaciones = {
        "concatenacion": lambda A, B: f"A·B = {A + B}",
        "potenciacion": potenciacion,
        "reflexion": lambda A, B: f"Aʳ = {A[::-1]}",
    }

    resultado = operaciones.get(op, lambda A, B: "Operación no válida")(A, B)
    return jsonify({"resultado": resultado})


#Operaciones con lenguajes
@app.route("/operacion_lenguajes", methods=["POST"])
def operacion_lenguajes():
    data = request.get_json()
    A = [s.strip() for s in data.get("lenguajeA", []) if s.strip()]
    B = [s.strip() for s in data.get("lenguajeB", []) if s.strip()]
    op = data.get("operacion")
    n = int(data.get("potencia", 1)) if str(data.get("potencia", "1")).isdigit() else 1

    if op == "concatenacion":
        res = [a + b for a in A for b in B]
        resultado = f"L1·L2 = {{{', '.join(res)}}}"

    elif op == "potenciacion":
        if n < 0:
            return jsonify({"resultado": "La potencia debe ser un entero ≥ 0"})
        if n == 0:
            res = ["ε"]
        else:
            res = A[:]
            for _ in range(n - 1):
                res = [x + y for x in res for y in A]
        resultado = f"L^{n} = {{{', '.join(res)}}}"

    elif op == "reflexion":
        res = [a[::-1] for a in A]
        resultado = f"Lʳ = {{{', '.join(res)}}}"

    elif op == "union":
        res = sorted(set(A) | set(B))
        resultado = f"L1 ∪ L2 = {{{', '.join(res)}}}"

    elif op == "interseccion":
        res = sorted(set(A) & set(B))
        resultado = f"L1 ∩ L2 = {{{', '.join(res)}}}"

    elif op == "resta":
        res = sorted(set(A) - set(B))
        resultado = f"L1 - L2 = {{{', '.join(res)}}}"

    elif op == "kleene":
        res = ["g"]  # siempre incluye ε
        for i in range(1, 4):  # hasta longitud 3
            nuevas = []
            if i == 1:
                nuevas = A[:]  # palabras base
            else:
                for palabra in res:
                    if palabra == "g":
                        continue
                    for simbolo in A:
                        nueva = palabra + simbolo  # concatenación sin espacios
                        if len(nueva) >= i and nueva not in nuevas:
                            nuevas.append(nueva)
            res.extend(nuevas)
        resultado = f"L* = {{{', '.join(res[:6])}, ...}}"

    elif op == "positiva":
        res = []
        for i in range(1, 4):  # hasta longitud 3
            nuevas = []
            if i == 1:
                nuevas = A[:]  # nivel 1 = alfabeto
            else:
                for palabra in res:
                    for simbolo in A:
                        nueva = palabra + simbolo
                        if len(nueva) >= i and nueva not in nuevas:
                            nuevas.append(nueva)
            res.extend(nuevas)
        resultado = f"L+ = {{{', '.join(res[:6])}, ...}}"

    else:
        resultado = "Operación no válida"

    return jsonify({"resultado": resultado})
if __name__ == "__main__":
    app.run(debug=True)


