// Mostrar sección de tabs
function mostrarSeccion(id, event) {
  document.querySelectorAll(".tab-content").forEach(sec => sec.classList.remove("active"));
  document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));

  document.getElementById(id).classList.add("active");
  event.target.classList.add("active");
}

// Operaciones con Conjuntos

async function calcularConjunto() {
  let conjuntoA = document.getElementById("conjuntoA").value;
  let conjuntoB = document.getElementById("conjuntoB").value;
  let operacion = document.getElementById("operacionConjuntos").value;

  let response = await fetch("/operacion_conjuntos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conjuntoA, conjuntoB, operacion })
  });

  let data = await response.json();
  document.getElementById("resultado").innerText = data.resultado;
}
// Operaciones con Cadenas
async function calcularCadenas() {
  let cadenaA = document.getElementById("cadenaA").value;
  let cadenaB = document.getElementById("cadenaB").value;
  let operacion = document.getElementById("operacionCadenas").value;

  let response = await fetch("/operacion_cadenas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cadenaA, cadenaB, operacion })
  });

  let data = await response.json();
  document.getElementById("resultado").innerText = data.resultado;
}

// Ajustar inputs según la operación elegida en cadenas
function ajustarCadenas() {
  let operacion = document.getElementById("operacionCadenas").value;
  let inputB = document.getElementById("cadenaB");

  if (operacion === "potenciacion") {
    inputB.style.display = "inline-block";
    inputB.placeholder = "Digite la potencia (número)";
  } else if (operacion === "reflexion") {
    inputB.style.display = "none"; // ocultamos
    inputB.value = ""; // limpiar valor si estaba lleno
  } else {
    inputB.style.display = "inline-block";
    inputB.placeholder = "Cadena B o número";
  }
}

// Limpiar inputs y resultado
function limpiarCampos() {
  document.querySelectorAll("input").forEach(inp => inp.value = "");
  document.getElementById("resultado").innerText = "—";

  // reset de placeholders
  let inputB = document.getElementById("cadenaB");
  inputB.style.display = "inline-block";
  inputB.placeholder = "Cadena B o número";
}

// Operaciones con Lenguajes
async function calcularLenguajes() {
  let lenguajeA = document.getElementById("lenguajeA").value.split(",").map(s => s.trim()).filter(Boolean);
  let lenguajeB = document.getElementById("lenguajeB").value.split(",").map(s => s.trim()).filter(Boolean);
  let operacion = document.getElementById("operacionLenguajes").value;
  let potencia = parseInt(document.getElementById("potenciaLenguaje")?.value) || 1;

  let response = await fetch("/operacion_lenguajes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lenguajeA, lenguajeB, operacion, potencia })
  });

  let data = await response.json();
  document.getElementById("resultado").innerText = data.resultado;
}
function ajustarLenguajes() {
  const op = document.getElementById("operacionLenguajes").value;
  const inA = document.getElementById("lenguajeA");
  const inB = document.getElementById("lenguajeB");
  const inN = document.getElementById("potenciaLenguaje");

  // Mostrar por defecto
  inA.style.display = "inline-block";
  inB.style.display = "inline-block";
  inN.style.display = "inline-block";

  // Placeholders base
  inA.placeholder = "Lenguaje A (ej: a,b)";
  inB.placeholder = "Lenguaje B (ej: c,d)";
  inN.placeholder = "Potencia n (solo para Potenciación)";

  if (op === "concatenacion" || op === "union" || op === "interseccion" || op === "resta") {
    // Se usan L1 y L2
    inN.style.display = "none";
    inN.value = "";
  } else if (op === "potenciacion") {
    // Se usa solo L y n
    inB.style.display = "none";
    inB.value = "";
    inN.style.display = "inline-block";
    inN.placeholder = "n (entero ≥ 0)";
  } else if (op === "reflexion" || op === "kleene" || op === "positiva") {
    // Se usa solo L
    inB.style.display = "none";
    inB.value = "";
    inN.style.display = "none";
    inN.value = "";
  }
}
// Llama al cargar y en cada cambio
document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("operacionLenguajes");
  if (sel) {
    sel.addEventListener("change", ajustarLenguajes);
    ajustarLenguajes();
  }
});
