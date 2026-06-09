
// 1. CONTROL DE VISTAS (Pestañas: programa.dsl vs Asistente Visual)

let modoActual = 'codigo';

function cambiarVista(modo) {
    modoActual = modo;
    const vistaCodigo = document.getElementById('contenedor-editor-codigo');
    const vistaFormulario = document.getElementById('contenedor-formulario-visual');
    const tabCodigo = document.getElementById('tab-codigo');
    const tabFormulario = document.getElementById('tab-formulario');

    // Validar que los elementos existan en el DOM para evitar errores raros
    if (!vistaCodigo || !vistaFormulario || !tabCodigo || !tabFormulario) return;

    if (modo === 'codigo') {
        vistaCodigo.style.display = 'block';
        vistaFormulario.style.display = 'none';
        
        // Estilos visuales activos / inactivos
        tabCodigo.classList.add('active');
        tabFormulario.classList.remove('active');
    } else {
        vistaCodigo.style.display = 'none';
        vistaFormulario.style.block = 'block'; // O 'flex' según tu grilla
        
        tabCodigo.classList.remove('active');
        tabFormulario.classList.add('active');
    }
}

// 2. COMPILACIÓN DESDE EL ASISTENTE (Formulario Interactivo)
// =============================================================================
function compilarDesdeFormulario() {
    // Capturamos los valores dinámicos ingresados por el usuario
    const sueldo = document.getElementById('form-sueldo')?.value.trim() || "0";
    const bono = document.getElementById('form-bono')?.value.trim() || "0";
    const arriendo = document.getElementById('form-arriendo')?.value.trim() || "0";
    const servicios = document.getElementById('form-servicios')?.value.trim() || "0";

    // Reconstruimos el código DSL. Si el usuario escribe letras, ej: SUELDO = tresmil;
    // tu backend en Flask disparará el error léxico o sintáctico automáticamente.
    const codigoGenerado = `
SUELDO = ${sueldo};
BONO = ${bono};
ARRIENDO = ${arriendo};
SERVICIOS = ${servicios};
ALIMENTACION = 400;

TOTAL_INGRESOS = SUELDO + BONO;
TOTAL_EGRESOS = ARRIENDO + SERVICIOS + ALIMENTACION;
BALANCE = TOTAL_INGRESOS - TOTAL_EGRESOS;

SI BALANCE > 1500 ENTONCES CALCULAR_IMPUESTO(BALANCE);
    `.trim();

    // Sincronizamos el editor clásico en la otra pestaña por si el usuario cambia de vista
    const editor = document.getElementById('codigo-editor') || document.querySelector('textarea');
    if (editor) {
        editor.value = codigoGenerado;
        // Si usas CodeMirror descomenta la línea de abajo:
        // if (window.editorCM) window.editorCM.setValue(codigoGenerated);
    }

    // Enviamos el código generado transparentemente al backend
    ejecutarCompilacionPipeline(codigoGenerado);
}

// =============================================================================
// 3. PIPELINE DE COMUNICACIÓN CON FLASK (AJAX / FETCH)
// =============================================================================
function ejecutarCompilacionPipeline(codigoSource) {
    console.log("[PIPELINE]: Iniciando proceso de compilación unificado...");
    
    fetch('/compilar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ codigo: codigoSource })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Respuesta inválida del servidor");
        }
        return response.json();
    })
    .then(data => {
        // Enviar la información devuelta por Flask a las respectivas tablas del Dashboard
        if (data.tokens) actualizarTablaTokens(data.tokens); // Función de tus tokens
        
        if (data.exito) {
            // Caso exitoso: actualiza RAM virtual y el código de tres direcciones/objeto
            actualizarTablaSimbolos(data.simbolos);
            if (typeof actualizarConsola === "function") actualizarConsola(data.logs, true);
            if (typeof actualizarDashboardKPI === "function") actualizarDashboardKPI(data.simbolos);
        } else {
            // Si el backend reporta fallas léxicas, sintácticas o semánticas
            actualizarTablaSimbolos({}); // Limpiar tabla si colapsó
            if (typeof mostrarModalError === "function") {
                mostrarModalError(data.fase_error, data.linea, data.logs);
            }
            if (typeof actualizarConsola === "function") actualizarConsola(data.logs, false);
        }
    })
    .catch(error => {
        console.error("Error crítico:", error);
        if (typeof mostrarModalError === "function") {
            mostrarModalError("Compilación General", "Desconocida", ["Error de comunicación o caída del servidor Flask."]);
        }
    });
}

// Opcional: Modifica tu botón clásico de COMPILAR del editor para que use la misma función base
function compilarDesdeEditor() {
    const editor = document.getElementById('codigo-editor') || document.querySelector('textarea');
    if (editor) {
        ejecutarCompilacionPipeline(editor.value.strip ? editor.value.strip() : editor.value);
    }
}

// =============================================================================
// 4. RENDERIZACIÓN DE INTERFAZ (Tus funciones nativas protegidas)
// =============================================================================
function actualizarTablaSimbolos(simbolos) {
    const symEmpty = document.getElementById('sym-empty');
    const symTable = document.getElementById('sym-table');
    const symBody = document.getElementById('sym-body');
    
    if (!symBody) return; 
    
    symBody.innerHTML = '';
    
    if (!simbolos || Object.keys(simbolos).length === 0) {
        if (symEmpty) symEmpty.style.display = 'flex';
        if (symTable) symTable.style.display = 'none';
        return;
    }
    
    if (symEmpty) symEmpty.style.display = 'none';
    if (symTable) symTable.style.display = 'table';
    
    for (const [variable, info] of Object.entries(simbolos)) {
        let tipo = "Variable";
        let valorRaw = "0";
        
        const match = info.match(/(.*?)\s*\(Valor en RAM:\s*([-\d.]+)\)/);
        
        if (match) {
            tipo = match[1].trim();  
            valorRaw = match[2]; 
        } else {
            valorRaw = info;
        }
        
        const numeroCasteado = parseFloat(valorRaw);
        const valorFormateado = !isNaN(numeroCasteado) 
            ? `$ ${numeroCasteado.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
            : escHtml(valorRaw);

        const claseBadge = tipo.toLowerCase().includes('literal') || tipo.toLowerCase().includes('number')
            ? 'cat-literal' 
            : 'cat-variable'; 
        
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td class="col-id"><strong>${escHtml(variable)}</strong></td>
            <td><span class="cat-badge ${claseBadge}">${escHtml(tipo)}</span></td>
            <td class="col-val" style="text-align: right; font-family: monospace;">${valorFormateado}</td>
        `;
        symBody.appendChild(fila);
    }
}

function escHtml(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}