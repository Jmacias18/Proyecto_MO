document.addEventListener('DOMContentLoaded', () => {
    const now = new Date();
    document.getElementById('fecha_hora').textContent = now.toLocaleDateString();

    // Ocultar la tabla de empleados al cargar la página
    document.getElementById('tabla_empleados').style.display = 'none';

    // Delegación de eventos para los checkboxes
    document.getElementById('empleados_tbody').addEventListener('change', (event) => {
        if (event.target.classList.contains('copy-checkbox')) {
            handleCheckboxChange(event);
        } else if (event.target.classList.contains('delete-checkbox')) {
            handleDeleteCheckboxChange(event);
        }
    });

    // Añadir eventos de cambio a los campos de horas extras
    document.querySelectorAll('[name^="horas_extras_"]').forEach(input => {
        input.addEventListener('input', () => {
            const codigoEmp = input.name.split('_')[2];
            if (input.value < 0) input.value = 0; // No permitir valores negativos
            calcularTotalHoras(codigoEmp, 0); // Recalcular el total
        });
    });

    // Añadir evento de cambio al selector de departamento
    document.getElementById('depto_select').addEventListener('change', () => {
        restablecerFormulario();
        filtrarEmpleados();
    });

    // Añadir evento de envío al formulario para realizar la validación
    document.querySelector('form').addEventListener('submit', (event) => {
        if (!validarHorasRegistradas()) {
            event.preventDefault(); // Evitar el envío del formulario si la validación falla
        }
    });
});

// Función para validar si algún empleado tiene un proceso sin horas registradas
function validarHorasRegistradas() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let valid = true;
    let mensajeAlerta = '';

    filasEmpleados.forEach(fila => {
        if (fila.style.display !== 'none') { // Solo validar empleados visibles
            const codigoEmp = fila.dataset.codigo_emp;
            const inasistencia = document.querySelector(`[name="inasistencia_${codigoEmp}"]`).checked;
            const deleteCheckbox = fila.querySelector('.delete-checkbox').checked;

            // Verificar si el empleado no tiene inasistencia ni está marcado para eliminar
            if (!inasistencia && !deleteCheckbox) {
                let tieneHorasRegistradas = false;
                let horasRegistradas = new Set();

                for (let i = 1; i <= 6; i++) {
                    const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);

                    // Verificar si el campo de inicio y fin no están deshabilitados y contienen valores
                    if (inicio && fin && !inicio.disabled && !fin.disabled) {
                        if (!inicio.value || !fin.value) {
                            mensajeAlerta += `El empleado con código ${codigoEmp} tiene campos de inicio o fin vacíos en el proceso ${i}.<br>`;
                            valid = false;
                        } else {
                            tieneHorasRegistradas = true;
                            const horas = `${inicio.value}-${fin.value}`;
                            if (horasRegistradas.has(horas)) {
                                mensajeAlerta += `El empleado con código ${codigoEmp} tiene horas de inicio y fin idénticas en más de un proceso.<br>`;
                                valid = false;
                            } else {
                                horasRegistradas.add(horas);
                            }
                        }
                    }
                }

                // Si no tiene horas registradas en ningún campo desbloqueado
                if (!tieneHorasRegistradas) {
                    mensajeAlerta += `El empleado con código ${codigoEmp} no tiene horas registradas en ningún proceso.<br>`;
                    valid = false;
                }
            }
        }
    });

    // Si no es válido, mostramos el mensaje de alerta
    if (!valid) {
        alert(mensajeAlerta);
    }

    return valid;
}

// Función para mostrar la alerta
function mostrarAlerta(mensaje) {
    const alerta = document.getElementById('alerta');
    alerta.innerHTML = mensaje;
    alerta.style.display = 'block';
}
// Función para validar si algún empleado tiene un proceso sin horas registradas
function validarHorasRegistradas() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let valid = true;
    let mensajeAlerta = '';

    filasEmpleados.forEach(fila => {
        if (fila.style.display !== 'none') { // Solo validar empleados visibles
            const codigoEmp = fila.dataset.codigo_emp;
            const inasistencia = document.querySelector(`[name="inasistencia_${codigoEmp}"]`).checked;
            const deleteCheckbox = fila.querySelector('.delete-checkbox').checked;

            // Verificar si el empleado no tiene inasistencia ni está marcado para eliminar
            if (!inasistencia && !deleteCheckbox) {
                let tieneHorasRegistradas = false;
                let horasRegistradas = new Set();

                for (let i = 1; i <= 6; i++) {
                    const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);

                    // Verificar si el campo de inicio y fin no están deshabilitados y contienen valores
                    if (inicio && fin && !inicio.disabled && !fin.disabled) {
                        if (!inicio.value || !fin.value) {
                            mensajeAlerta += `El empleado con código ${codigoEmp} tiene campos de inicio o fin vacíos en el proceso ${i}.\n`;
                            valid = false;
                        } else {
                            tieneHorasRegistradas = true;
                            const horas = `${inicio.value}-${fin.value}`;
                            if (horasRegistradas.has(horas)) {
                                mensajeAlerta += `El empleado con código ${codigoEmp} tiene horas de inicio y fin idénticas en más de un proceso.\n`;
                                valid = false;
                            } else {
                                horasRegistradas.add(horas);
                            }
                        }
                    }
                }

                // Si no tiene horas registradas en ningún campo desbloqueado
                if (!tieneHorasRegistradas) {
                    mensajeAlerta += `El empleado con código ${codigoEmp} no tiene horas registradas en ningún proceso.\n`;
                    valid = false;
                }
            }
        }
    });

    // Si no es válido, mostramos el mensaje de alerta
    if (!valid) {
        alert(mensajeAlerta);
    }

    return valid;
}

function handleCheckboxChange(event) {
    const checkbox = event.target;
    const proceso = checkbox.dataset.proceso;
    const emp = checkbox.dataset.emp;
    const row = checkbox.closest('tr');
    const prevRow = getPreviousRow(row, proceso);

    const inicioInput = row.querySelector(`input[name="inicio_proceso${proceso}_${emp}"]`);
    const finInput = row.querySelector(`input[name="fin_proceso${proceso}_${emp}"]`);

    // Validar que los elementos de entrada existen
    if (!inicioInput || !finInput) {
        console.error(`No se encontraron los elementos de entrada para el proceso ${proceso} y el empleado ${emp}`);
        return;
    }

    if (checkbox.checked) {
        if (prevRow) {
            const prevInicio = prevRow.querySelector(`input[name="inicio_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`).value;
            const prevFin = prevRow.querySelector(`input[name="fin_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`).value;

            inicioInput.dataset.originalValue = inicioInput.value;
            finInput.dataset.originalValue = finInput.value;

            inicioInput.value = prevInicio;
            finInput.value = prevFin;

            calcularTotalHoras(emp, proceso);
        }
    } else {
        inicioInput.value = inicioInput.dataset.originalValue || '';
        finInput.value = finInput.dataset.originalValue || '';

        calcularTotalHoras(emp, proceso);
    }

    sumarHorasPorProceso();
}

function getPreviousRow(currentRow, proceso) {
    const deptoActual = currentRow.getAttribute('data-depto');
    let prevRow = currentRow.previousElementSibling;
    while (prevRow) {
        if (prevRow.getAttribute('data-depto') === deptoActual &&
            prevRow.querySelector(`input[name="inicio_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`)) {
            return prevRow;
        }
        prevRow = prevRow.previousElementSibling;
    }
    return null;
}

function filtrarEmpleados() {
    const deptoSeleccionado = document.getElementById('depto_select').value;
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let contador = 1;
    let totalEmpleados = 0;

    if (deptoSeleccionado === "") {
        document.getElementById('tabla_empleados').style.display = 'none';
        document.getElementById('total_empleados').style.display = 'none'; // Ocultar total_empleados
        return;
    }

    filasEmpleados.forEach(fila => {
        const deptoEmpleado = fila.getAttribute('data-depto');
        if (deptoSeleccionado === deptoEmpleado) {
            fila.style.display = "";
            fila.querySelector('.employee-number').textContent = contador++;
            totalEmpleados++;
        } else {
            fila.style.display = "none";
        }
    });

    document.getElementById('total_empleados').textContent = `Total de Empleados: ${totalEmpleados}`;
    document.getElementById('total_empleados').style.display = 'block'; // Mostrar total_empleados
    document.getElementById('tabla_empleados').style.display = totalEmpleados > 0 ? 'block' : 'none';
    sumarHorasPorProceso();
}

function toggleInputs(codigoEmp) {
    const inasistencia = document.querySelector(`[name="inasistencia_${codigoEmp}"]`).checked;
    const inputs = document.querySelectorAll(`[name^="inicio_proceso"][name$="_${codigoEmp}"], [name^="fin_proceso"][name$="_${codigoEmp}"], [name="horas_extras_${codigoEmp}"]`);
    inputs.forEach(input => {
        input.disabled = inasistencia;
        if (inasistencia) input.value = '';
    });

    if (inasistencia) {
        document.querySelector(`[name="total_${codigoEmp}"]`).value = '0.00';
    }

    sumarHorasPorProceso();
}

function toggleProcesoInputs(procesoNum) {
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
    const inputs = document.querySelectorAll(`[name^="inicio_proceso${procesoNum}_"], [name^="fin_proceso${procesoNum}_"]`);
    inputs.forEach(input => {
        input.disabled = !procesoSelect.value;
        if (!procesoSelect.value) input.value = '';
    });

    // Recalcula las horas cada vez que se selecciona un proceso
    sumarHorasPorProceso();
}

function ajustarHoraFin(codigoEmp, procesoNum) {
    const inicioField = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const finField = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
    
    // Validar que los elementos de entrada existen
    if (!inicioField || !finField) {
        console.error(`No se encontraron los elementos de entrada para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
        return;
    }

    if (!inicioField.value) return;

    const ajustarHora = (horas, minutos) => {
        let nuevaHora = horas + 1;
        if (nuevaHora >= 24) nuevaHora -= 24;
        return `${nuevaHora.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}`;
    };

    const [inicioHoras, inicioMinutos] = inicioField.value.split(':').map(Number);

    // Validar que las horas y minutos son números válidos
    if (isNaN(inicioHoras) || isNaN(inicioMinutos)) {
        console.error(`Horas o minutos inválidos para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
        finField.value = '';
        return;
    }

    finField.value = ajustarHora(inicioHoras, inicioMinutos);
    calcularTotalHoras(codigoEmp, procesoNum);

    let horas = inicioHoras;
    let minutos = inicioMinutos;

    for (let i = procesoNum + 1; i <= 6; i++) {
        const siguienteInicioField = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
        const siguienteFinField = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);
        
        if (!siguienteInicioField || !siguienteFinField) continue;

        siguienteInicioField.value = ajustarHora(horas, minutos);
        [horas, minutos] = siguienteInicioField.value.split(':').map(Number);
        siguienteFinField.value = ajustarHora(horas, minutos);
    }
}

function calcularTotalHoras(codigoEmp, procesoNum) {
    const inicio = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`).value;
    const fin = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`).value;
    const totalField = document.querySelector(`[name="total_proceso${procesoNum}_${codigoEmp}"]`);

    // Validar que los elementos de entrada existen
    if (!inicio || !fin || !totalField) {
        console.error(`No se encontraron los elementos de entrada para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
        return;
    }

    if (inicio && fin) {
        const [inicioHoras, inicioMinutos] = inicio.split(':').map(Number);
        const [finHoras, finMinutos] = fin.split(':').map(Number);

        // Validar que las horas y minutos son números válidos
        if (isNaN(inicioHoras) || isNaN(inicioMinutos) || isNaN(finHoras) || isNaN(finMinutos)) {
            console.error(`Horas o minutos inválidos para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
            totalField.value = '';
            return;
        }

        const inicioDate = new Date(0, 0, 0, inicioHoras, inicioMinutos);
        const finDate = new Date(0, 0, 0, finHoras, finMinutos);

        let diff = (finDate - inicioDate) / (1000 * 60 * 60);
        if (diff < 0) diff += 24;

        totalField.value = diff.toFixed(2);
    } else {
        totalField.value = '';
    }

    let totalHoras = 0;
    for (let i = 1; i <= 6; i++) {
        const totalProceso = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`).value;
        if (totalProceso) totalHoras += parseFloat(totalProceso) || 0;
    }

    const horasExtrasField = document.querySelector(`[name="horas_extras_${codigoEmp}"]`);
    const horasExtras = parseFloat(horasExtrasField.value) || 0;
    totalHoras += horasExtras;

    horasExtrasField.value = horasExtras.toFixed(2);
    document.querySelector(`[name="total_${codigoEmp}"]`).value = totalHoras.toFixed(2);

    sumarHorasPorProceso();
}

function sumarHorasPorProceso() {
    const totalHorasPorProceso = Array(6).fill(0);

    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        let totalEmpleado = 0;

        for (let i = 1; i <= 6; i++) {
            const totalProceso = fila.querySelector(`[name="total_proceso${i}_${fila.dataset.codigo_emp}"]`);
            if (totalProceso && totalProceso.value) {
                totalHorasPorProceso[i - 1] += parseFloat(totalProceso.value) || 0;
                totalEmpleado += parseFloat(totalProceso.value) || 0;
            }
        }

        const totalEmpleadoField = fila.querySelector(`[name="total_${fila.dataset.codigo_emp}"]`);
        if (totalEmpleadoField) {
            totalEmpleadoField.value = totalEmpleado.toFixed(2);
        }
    });

    for (let i = 1; i <= 6; i++) {
        const totalProcesoField = document.querySelector(`#total_proceso${i}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = totalHorasPorProceso[i - 1].toFixed(2);
        }
    }
}

function restablecerFormulario() {
    const inputs = document.querySelectorAll('input[type="time"], input[type="number"], input[type="text"]');
    inputs.forEach(input => {
        if (input.type === 'time' || input.type === 'number') {
            input.value = '';
        }
        if (!input.name.startsWith('horas_extras_')) {
            input.disabled = true; // Bloquear los inputs por defecto excepto horas extras
        }
    });

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    sumarHorasPorProceso();
}