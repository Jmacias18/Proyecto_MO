document.addEventListener('DOMContentLoaded', () => {
    // Ocultar la tabla de registros al cargar la página
    document.getElementById('tabla_registros').style.display = 'none';

    // Añadir evento de cambio al selector de fecha y departamento
    document.getElementById('fecha_select').addEventListener('change', filtrarRegistros);
    document.getElementById('depto_select').addEventListener('change', filtrarRegistros);
});

function filtrarRegistros() {
    const fechaSeleccionada = document.getElementById('fecha_select').value;
    const deptoSeleccionado = document.getElementById('depto_select').value;

    if (fechaSeleccionada === "" || deptoSeleccionado === "") {
        document.getElementById('tabla_registros').style.display = 'none';
        return;
    }

    // Llamada AJAX para obtener los registros filtrados por fecha y departamento
    fetch(`/horas_procesos/obtener_registros?fecha=${fechaSeleccionada}&departamento=${deptoSeleccionado}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('registros_tbody');
            tbody.innerHTML = ''; // Limpiar el contenido anterior

            data.registros.forEach(registro => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${registro.codigo_emp}</td>
                    <td>${registro.nombre_emp}</td>
                    <td>${registro.depto_emp}</td>
                    <td>
                        <input type="checkbox" class="form-check-input" name="inasistencia_${registro.codigo_emp}" ${registro.asistencia ? 'checked' : ''}>
                    </td>
                    ${[1, 2, 3, 4, 5, 6].map(i => `
                    <td>
                        <select class="form-select form-select-sm mb-2" name="proceso${i}_header">
                            <option value="">Selecciona Proceso</option>
                            {% for proceso in procesos %}
                            <option value="{{ proceso.id_pro }}">{{ proceso.nombre_pro }}</option>
                            {% endfor %}
                        </select>
                        <input type="time" class="form-control form-control-sm mb-2" name="inicio_proceso${i}_${registro.codigo_emp}" value="${registro[`inicio_proceso${i}`] || ''}" placeholder="Inicio" step="60">
                        <input type="time" class="form-control form-control-sm mb-2" name="fin_proceso${i}_${registro.codigo_emp}" value="${registro[`fin_proceso${i}`] || ''}" placeholder="Fin" step="60">
                        <input type="text" class="form-control form-control-sm mb-2" name="total_proceso${i}_${registro.codigo_emp}" value="${registro[`total_proceso${i}`] || ''}" readonly>
                    </td>
                    `).join('')}
                    <td>
                        <input type="number" class="form-control form-control-sm" name="horas_extras_${registro.codigo_emp}" value="${registro.hrsextras}">
                    </td>
                    <td>
                        <input type="number" class="form-control form-control-sm" name="total_${registro.codigo_emp}" value="${registro.totalhrs}" readonly>
                    </td>
                `;
                tbody.appendChild(row);
            });

            document.getElementById('tabla_registros').style.display = 'block';
        })
        .catch(error => {
            console.error('Error al obtener los registros:', error);
        });
}