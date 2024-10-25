document.addEventListener('DOMContentLoaded', (event) => {
    const now = new Date();
    const formattedDate = now.toLocaleDateString();
    document.getElementById('fecha_hora').textContent = formattedDate;

    // Inicializar Flatpickr en los campos de tiempo
    flatpickr(".timepicker", {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true
    });

    // Enumerar empleados al cargar la página
    filtrarEmpleados();

    // Sumar horas por proceso al cargar la página
    sumarHorasPorProceso();

    // Añadir eventos de cambio a los checkboxes para copiar horarios
    const checkboxes = document.querySelectorAll('.copy-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', (event) => {
            const proceso = event.target.dataset.proceso;
            const emp = event.target.dataset.emp;
            const row = event.target.closest('tr');
            const prevRow = row.previousElementSibling;

            const inicioInput = row.querySelector(`input[name="inicio_proceso${proceso}_${emp}"]`);
            const finInput = row.querySelector(`input[name="fin_proceso${proceso}_${emp}"]`);

            if (event.target.checked) {
                if (prevRow) {
                    const prevInicio = prevRow.querySelector(`input[name="inicio_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`).value;
                    const prevFin = prevRow.querySelector(`input[name="fin_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`).value;

                    inicioInput.dataset.originalValue = inicioInput.value;
                    finInput.dataset.originalValue = finInput.value;

                    inicioInput.value = prevInicio;
                    finInput.value = prevFin;

                    // Calcular horas después de copiar los valores
                    calcularTotalHoras(emp, proceso);
                }
            } else {
                inicioInput.value = inicioInput.dataset.originalValue || '';
                finInput.value = finInput.dataset.originalValue || '';

                // Calcular horas después de restaurar los valores originales
                calcularTotalHoras(emp, proceso);
            }

            // Sumar horas por proceso después de cambiar el checkbox
            sumarHorasPorProceso();
        });
    });
});

// Función para filtrar empleados por departamento y enumerarlos
function filtrarEmpleados() {
    // Obtener el departamento seleccionado
    const deptoSeleccionado = document.getElementById('depto_select').value;
    // Obtener todas las filas de empleados
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let contador = 1;
    let totalEmpleados = 0;

    // Iterar sobre cada fila de empleado
    filasEmpleados.forEach(fila => {
        // Obtener el departamento del empleado
        const deptoEmpleado = fila.getAttribute('data-depto');
        // Mostrar u ocultar la fila según el departamento seleccionado
        if (deptoSeleccionado === "" || deptoSeleccionado === deptoEmpleado) {
            fila.style.display = "";
            // Enumerar la fila visible
            fila.querySelector('.employee-number').textContent = contador++;
            totalEmpleados++;
        } else {
            fila.style.display = "none";
        }
    });

    // Actualizar el total de empleados visibles
    document.getElementById('total_empleados').textContent = `Total de Empleados: ${totalEmpleados}`;

    // Sumar horas por proceso después de filtrar empleados
    sumarHorasPorProceso();
}

// Función para habilitar/deshabilitar campos de tiempo y horas extras
function toggleInputs(codigoEmp) {
    const inasistencia = document.querySelector(`[name="inasistencia_${codigoEmp}"]`).checked;
    const inputs = document.querySelectorAll(`[name^="inicio_proceso"][name$="_${codigoEmp}"], [name^="fin_proceso"][name$="_${codigoEmp}"], [name="horas_extras_${codigoEmp}"]`);
    inputs.forEach(input => {
        input.disabled = inasistencia;
        if (inasistencia) {
            input.value = ''; // Limpiar el valor del campo si la inasistencia está activada
        }
    });

    if (inasistencia) {
        document.querySelector(`[name="total_${codigoEmp}"]`).value = '0.00';
    }

    // Sumar horas por proceso después de cambiar la asistencia
    sumarHorasPorProceso();
}

// Función para habilitar/deshabilitar campos de tiempo según el proceso seleccionado
function toggleProcesoInputs(procesoNum) {
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
    const inputs = document.querySelectorAll(`[name^="inicio_proceso${procesoNum}_"], [name^="fin_proceso${procesoNum}_"]`);
    inputs.forEach(input => {
        input.disabled = !procesoSelect.value;
        if (!procesoSelect.value) {
            input.value = ''; // Limpiar el valor del campo si el proceso no está seleccionado
        }
    });

    // Sumar horas por proceso después de cambiar el proceso seleccionado
    sumarHorasPorProceso();
}

// Función para ajustar la hora de fin automáticamente una hora después de la hora de inicio
function ajustarHoraFin(codigoEmp, procesoNum) {
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
    const inicioField = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const finField = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);

    // Verificar si el proceso está seleccionado
    if (procesoSelect && procesoSelect.value && inicioField.value) {
        const [inicioHoras, inicioMinutos] = inicioField.value.split(':').map(Number);
        let finHoras = inicioHoras + 1;
        if (finHoras >= 24) finHoras -= 24; // Ajuste si la hora de fin es después de la medianoche

        finField.value = `${finHoras.toString().padStart(2, '0')}:${inicioMinutos.toString().padStart(2, '0')}`;
        calcularTotalHoras(codigoEmp, procesoNum);

        // Ajustar la hora de inicio del siguiente proceso
        const siguienteProcesoNum = procesoNum + 1;
        const siguienteProcesoSelect = document.querySelector(`[name="proceso${siguienteProcesoNum}_header"]`);
        const siguienteInicioField = document.querySelector(`[name="inicio_proceso${siguienteProcesoNum}_${codigoEmp}"]`);
        if (siguienteProcesoSelect && siguienteProcesoSelect.value && siguienteInicioField) {
            siguienteInicioField.value = finField.value;
        }
    }
}

// Función para calcular el total de horas entre la hora de entrada y la hora de salida
function calcularTotalHoras(codigoEmp, procesoNum) {
    const inicio = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`).value;
    const fin = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`).value;
    
    const totalField = document.querySelector(`[name="total_proceso${procesoNum}_${codigoEmp}"]`);

    if (inicio && fin) {
        const [inicioHoras, inicioMinutos] = inicio.split(':').map(Number);
        const [finHoras, finMinutos] = fin.split(':').map(Number);

        const inicioDate = new Date(0, 0, 0, inicioHoras, inicioMinutos);
        const finDate = new Date(0, 0, 0, finHoras, finMinutos);

        let diff = (finDate - inicioDate) / (1000 * 60 * 60); // Diferencia en horas
        if (diff < 0) {
            diff += 24; // Ajuste si la hora de fin es después de la medianoche
        }

        totalField.value = diff.toFixed(2);
    } else {
        totalField.value = '';
    }

    // Calcular el total de horas trabajadas en todos los procesos
    let totalHoras = 0;
    for (let i = 1; i <= 6; i++) {
        const totalProceso = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`).value;
        if (totalProceso) {
            totalHoras += parseFloat(totalProceso) || 0;
        }
    }

    // Incluir horas extras en el total de horas trabajadas
    const horasExtrasField = document.querySelector(`[name="horas_extras_${codigoEmp}"]`);
    const horasExtras = parseFloat(horasExtrasField.value) || 0;
    totalHoras += horasExtras;

    // Mostrar las horas extras en tiempo real
    horasExtrasField.value = horasExtras.toFixed(2);

    document.querySelector(`[name="total_${codigoEmp}"]`).value = totalHoras.toFixed(2);

    // Sumar horas por proceso después de calcular las horas
    sumarHorasPorProceso();
}

// Función para sumar las horas de cada proceso y mostrar el total al final de cada columna
function sumarHorasPorProceso() {
    const totalHorasPorProceso = Array(6).fill(0);

    // Iterar sobre cada fila de empleado
    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        for (let i = 1; i <= 6; i++) {
            const totalProceso = fila.querySelector(`[name="total_proceso${i}_${fila.dataset.codigo_emp}"]`);
            if (totalProceso && totalProceso.value) {
                totalHorasPorProceso[i - 1] += parseFloat(totalProceso.value) || 0;
            }
        }
    });

    // Mostrar el total de horas por proceso en la fila de resumen
    for (let i = 1; i <= 6; i++) {
        const totalProcesoField = document.querySelector(`#total_proceso${i}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = totalHorasPorProceso[i - 1].toFixed(2);
        }
    }
}

// Añadir eventos de cambio a los campos de horas extras para recalcular el total en tiempo real
document.querySelectorAll('[name^="horas_extras_"]').forEach(input => {
    input.addEventListener('input', () => {
        const codigoEmp = input.name.split('_')[2];
        if (input.value < 0) {
            input.value = 0; // No permitir valores negativos
        }
        calcularTotalHoras(codigoEmp, 0); // Llamar a la función con procesoNum 0 para recalcular el total
    });
});

// Función para validar el formulario antes de enviarlo
function validarFormulario() {
    const empleados = document.querySelectorAll('#empleados_tbody tr');
    for (const empleado of empleados) {
        const codigoEmp = empleado.querySelector('.employee-number').textContent;
        const inasistencia = document.querySelector(`[name="inasistencia_${codigoEmp}"]`).checked;

        if (!inasistencia) {
            let tieneHoras = false;
            const horasRegistradas = [];

            for (let i = 1; i <= 6; i++) {
                const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`).value;
                const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`).value;

                // Validar que los campos de tiempo no estén vacíos
                if (!inicio || !fin) {
                    alert(`El empleado ${codigoEmp} tiene un proceso ${i} con campos de tiempo vacíos.`);
                    return false;
                }

                // Validar que la hora de fin sea posterior a la hora de inicio
                const [inicioHoras, inicioMinutos] = inicio.split(':').map(Number);
                const [finHoras, finMinutos] = fin.split(':').map(Number);
                const inicioDate = new Date(0, 0, 0, inicioHoras, inicioMinutos);
                const finDate = new Date(0, 0, 0, finHoras, finMinutos);

                if (finDate <= inicioDate) {
                    alert(`El empleado ${codigoEmp} tiene un proceso ${i} con la hora de fin anterior o igual a la hora de inicio.`);
                    return false;
                }

                // Validar que las horas no se solapen con otros procesos
                for (const [regInicio, regFin] of horasRegistradas) {
                    if ((inicioDate < regFin && finDate > regInicio)) {
                        alert(`El empleado ${codigoEmp} tiene horas solapadas en el proceso ${i}.`);
                        return false;
                    }
                }

                horasRegistradas.push([inicioDate, finDate]);
                tieneHoras = true;
            }

            // Validar que al menos un proceso tenga horas registradas
            if (!tieneHoras) {
                alert(`El empleado ${codigoEmp} no tiene ninguna hora registrada en ningún proceso.`);
                return false;
            }

            // Validar que las horas extras sean un número positivo
            const horasExtrasField = document.querySelector(`[name="horas_extras_${codigoEmp}"]`);
            const horasExtras = parseFloat(horasExtrasField.value) || 0;
            if (horasExtras < 0) {
                alert(`El empleado ${codigoEmp} tiene horas extras negativas.`);
                return false;
            }
        }
    }
    return true;
}