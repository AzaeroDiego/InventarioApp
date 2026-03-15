// Utilidades JavaScript para la aplicación de inventario

// Formatear moneda
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN',
        minimumFractionDigits: 2
    }).format(valor);
}

// Mostrar notificación
function mostrarNotificacion(mensaje, tipo = 'info') {
    const clases = {
        'success': 'alert-success',
        'error': 'alert-error',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };

    const alerta = document.createElement('div');
    alerta.className = `alert ${clases[tipo]}`;
    alerta.innerHTML = `
        <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${mensaje}</span>
    `;

    document.querySelector('.content').insertBefore(alerta, document.querySelector('.content').firstChild);

    setTimeout(() => {
        alerta.remove();
    }, 5000);
}

// Validar formulario antes de enviar
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let valido = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#e74c3c';
            valido = false;
        } else {
            input.style.borderColor = '';
        }
    });

    return valido;
}

// Copiar al portapapeles
function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto).then(() => {
        mostrarNotificacion('¡Copiado!', 'success');
    }).catch(() => {
        mostrarNotificacion('Error al copiar', 'error');
    });
}

// Exportar tabla a CSV (simple)
function exportarTablaCSV(tableId, nombreArchivo) {
    const tabla = document.getElementById(tableId);
    if (!tabla) return;

    let csv = [];
    const filas = tabla.querySelectorAll('tr');

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('th, td');
        let fila_csv = [];

        celdas.forEach(celda => {
            fila_csv.push('"' + celda.textContent.trim() + '"');
        });

        csv.push(fila_csv.join(','));
    });

    const csvContenido = csv.join('\n');
    const blob = new Blob([csvContenido], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${nombreArchivo}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Imprimir elemento
function imprimirElemento(elementId) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;

    const ventana = window.open('', '_blank');
    ventana.document.write('<html><head><title>Imprimir</title>');
    ventana.document.write('<link rel="stylesheet" href="' + document.querySelector('link').href + '">');
    ventana.document.write('</head><body>');
    ventana.document.write(elemento.innerHTML);
    ventana.document.write('</body></html>');
    ventana.document.close();
    ventana.print();
}

// Confirmar acción
function confirmar(mensaje = '¿Estás seguro?') {
    return confirm(mensaje);
}

// Cargar alertas del sistema
function cargarAlertas() {
    fetch('/api/alertas/no-leidas')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('alertas-count');
            if (badge && data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'inline-block';
            }
        })
        .catch(error => console.log('Error cargando alertas:', error));
}

// Mostrar código QR
function mostrarQR(productoId) {
    fetch(`/api/producto/${productoId}/qr`)
        .then(response => response.json())
        .then(data => {
            if (data.qr_url) {
                const modal = document.createElement('div');
                modal.className = 'modal show';
                modal.innerHTML = `
                    <div class="modal-content" style="max-width: 400px;">
                        <div class="modal-header">
                            <h3 class="modal-title">Código QR - ${data.nombre}</h3>
                            <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
                        </div>
                        <div class="modal-body" style="text-align: center;">
                            <img src="${data.qr_url}" alt="QR" style="max-width: 300px;">
                            <p style="margin-top: 15px; color: #7f8c8d; font-size: 13px;">
                                <strong>SKU:</strong> ${data.sku}
                            </p>
                        </div>
                        <div class="modal-footer">
                            <a href="${data.qr_url}" download class="btn btn-primary">
                                <i class="fas fa-download"></i> Descargar
                            </a>
                            <button onclick="window.print();this.closest('.modal').remove();" class="btn btn-secondary">
                                <i class="fas fa-print"></i> Imprimir
                            </button>
                            <button onclick="this.closest('.modal').remove();" class="btn btn-light">
                                <i class="fas fa-times"></i> Cerrar
                            </button>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Cerrar modales al hacer click fuera
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.remove();
    }
});

// Cargar estadísticas
function cargarEstadisticas(contenedorId = 'estadisticas') {
    const contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;

    fetch('/api/estadisticas')
        .then(response => response.json())
        .then(data => {
            console.log('Estadísticas cargadas:', data);
        })
        .catch(error => console.log('Error cargando estadísticas:', error));
}

// Inicializar tooltips (ejemplo)
function inicializarTooltips() {
    const elementos = document.querySelectorAll('[title]');
    elementos.forEach(elemento => {
        elemento.addEventListener('mouseenter', function() {
            // Implementar comportamiento tooltip si es necesario
        });
    });
}

// Ejecutar en carga de página
document.addEventListener('DOMContentLoaded', function() {
    cargarAlertas();
    inicializarTooltips();

    // Recargar alertas cada 30 segundos
    setInterval(cargarAlertas, 30000);
});
