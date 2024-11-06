

// Función para validar si algún empleado tiene un proceso sin horas registradas y evitar horas solapadas y duplicación de procesos
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
                let horarios = [];
                let procesosRegistrados = new Set();

                for (let i = 1; i <= 6; i++) {
                    const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);
                    const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);

                    // Verificar si el campo de inicio y fin no están deshabilitados y contienen valores
                    if (inicio && fin && procesoSelect && !inicio.disabled && !fin.disabled) {
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
                                horarios.push({ inicio: inicio.value, fin: fin.value });
                            }

                            // Verificar si el proceso está duplicado
                            const procesoValue = procesoSelect.value;
                            if (procesosRegistrados.has(procesoValue)) {
                                mensajeAlerta += `El empleado con código ${codigoEmp} tiene el proceso ${procesoValue} duplicado en diferentes campos de proceso.\n`;
                                valid = false;
                            } else {
                                procesosRegistrados.add(procesoValue);
                            }
                        }
                    }
                }

                // Verificar si hay horas solapadas
                horarios.sort((a, b) => a.inicio.localeCompare(b.inicio));
                for (let i = 0; i < horarios.length - 1; i++) {
                    if (horarios[i].fin > horarios[i + 1].inicio) {
                        mensajeAlerta += `El empleado con código ${codigoEmp} tiene horas solapadas entre los procesos.\n`;
                        valid = false;
                        break;
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

// Función para mostrar la alerta
function mostrarAlerta(mensaje) {
    const alerta = document.getElementById('alerta');
    alerta.innerHTML = mensaje;
    alerta.style.display = 'block';
}


// Función para manejar el cambio de los checkboxes de eliminación
function handleDeleteCheckboxChange(event) {
    const checkbox = event.target;
    const row = checkbox.closest('tr');
    const procesoNum = checkbox.dataset.proceso; // Obtener el número del proceso del dataset del checkbox
    const codigoEmp = checkbox.dataset.emp; // Obtener el código del empleado del dataset del checkbox

    // Validar que los datos del dataset existen
    if (!procesoNum || !codigoEmp) {
        console.error('Datos del dataset faltantes en el checkbox.');
        return;
    }

    // Seleccionar solo los campos de entrada correspondientes al proceso y empleado específicos
    const inputs = row.querySelectorAll(`input[name="inicio_proceso${procesoNum}_${codigoEmp}"], input[name="fin_proceso${procesoNum}_${codigoEmp}"], input[name="total_proceso${procesoNum}_${codigoEmp}"]`);

    if (checkbox.checked) {
        // Deshabilitar los campos de entrada correspondientes
        inputs.forEach(input => {
            input.disabled = true;
            input.value = ''; // Limpiar el valor del campo
        });
    } else {
        // Habilitar los campos de entrada correspondientes
        inputs.forEach(input => {
            input.disabled = false;
        });
    }
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

function toggleProcesoInputs(procesoNum) {
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
    const inputs = document.querySelectorAll(`[name^="inicio_proceso${procesoNum}_"], [name^="fin_proceso${procesoNum}_"]`);
    inputs.forEach(input => {
        input.disabled = !procesoSelect.value;
        if (!procesoSelect.value) input.value = '';
    });

    // Recalcula las horas cada vez que se selecciona un proceso
    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;
        if (procesoSelect.value) {
            calcularTotalHoras(codigoEmp, procesoNum);
        }
    });

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

        // Calcular las horas para el siguiente proceso
        calcularTotalHoras(codigoEmp, i);
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
        const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
        if (procesoSelect && procesoSelect.value) {
            const totalProceso = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`).value;
            if (totalProceso) totalHoras += parseFloat(totalProceso) || 0;
        }
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
            const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
            if (procesoSelect && procesoSelect.value) {
                const totalProceso = fila.querySelector(`[name="total_proceso${i}_${fila.dataset.codigo_emp}"]`);
                if (totalProceso && totalProceso.value) {
                    totalHorasPorProceso[i - 1] += parseFloat(totalProceso.value) || 0;
                    totalEmpleado += parseFloat(totalProceso.value) || 0;
                }
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

    // Restablecer los totales de horas por proceso
    for (let i = 1; i <= 6; i++) {
        const totalProcesoField = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
        if (totalProcesoField) {
            totalProcesoField.value = '0.00';
        }
    }

    sumarHorasPorProceso();
}
function restablecerFormulario() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');

    filasEmpleados.forEach(fila => {
        // Limpiar los campos de horas, procesos y horas extras
        const inputs = fila.querySelectorAll('input[type="time"], input[type="number"], input[type="text"]');
        inputs.forEach(input => {
            input.value = ''; // Limpiar el valor de los campos de tiempo y número
            input.disabled = true; // Bloquear los inputs por defecto
        });

        // Restablecer los checkboxes
        const checkboxes = fila.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false; // Desmarcar todos los checkboxes
        });

        // Limpiar los campos de selección de procesos
        const selects = fila.querySelectorAll('select[name^="proceso"]');
        selects.forEach(select => {
            select.selectedIndex = 0; // Restablecer el valor del selector al primer elemento
            const procesoNum = select.name.match(/\d+/)[0]; // Obtener el número del proceso
            const inputsProceso = fila.querySelectorAll(`[name="inicio_proceso${procesoNum}_${fila.dataset.codigo_emp}"], [name="fin_proceso${procesoNum}_${fila.dataset.codigo_emp}"]`);
            inputsProceso.forEach(input => {
                input.disabled = true; // Deshabilitar los campos de entrada asociados
                input.value = ''; // Limpiar el valor de los campos de hora de inicio y fin
            });
        });
    });

    // Restablecer los totales de horas por proceso
    for (let i = 1; i <= 6; i++) {
        const totalProcesoField = document.querySelector(`#total_proceso${i}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = '0.00'; // Restablecer los totales de horas a 0
        }
    }

    // Mostrar la tabla de empleados si hay empleados en el nuevo departamento
    filtrarEmpleados();
}