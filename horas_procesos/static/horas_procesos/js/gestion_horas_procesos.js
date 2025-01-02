document.addEventListener('DOMContentLoaded', () => {
    const now = new Date();
    document.getElementById('fecha').textContent = now.toLocaleDateString();
    document.getElementById('tabla_empleados').style.display = 'none';

    const guardarBtn = document.getElementById('guardar-btn');
    const procesoSelects = document.querySelectorAll('select[name^="proceso"]');
    const form = document.querySelector('form');
    const empleadosTbody = document.getElementById('empleados_tbody');
    const deptoSelect = document.getElementById('depto_select');

    // Función para verificar si algún proceso está seleccionado
    function verificarSeleccionProcesos() {
        guardarBtn.disabled = !Array.from(procesoSelects).some(select => select.value);
    }

    // Agregar evento change a todos los selectores de procesos
    procesoSelects.forEach(select => {
        select.addEventListener('change', verificarSeleccionProcesos);
    });

    // Verificar la selección de procesos al cargar la página
    verificarSeleccionProcesos();

    // Manejar cambios en la tabla de empleados
    empleadosTbody.addEventListener('change', (event) => {
        const target = event.target;
        if (target.classList.contains('copy-checkbox')) {
            handleCheckboxChange(event);
        } else if (target.classList.contains('delete-checkbox')) {
            handleDeleteCheckboxChange(event);
        } else if (target.name.startsWith('tipo_inasistencia_')) {
            const codigoEmp = target.name.split('_')[1];
            toggleInputs(codigoEmp);
        } else if (target.name.startsWith('horas_extras_')) {
            const codigoEmp = target.name.split('_')[2];
            if (target.value < 0) target.value = 0;
            calcularTotalHoras(codigoEmp, 0);
        }
    });

    // Manejar cambio de departamento
    deptoSelect.addEventListener('change', () => {
        restablecerFormulario();
        filtrarEmpleados();
    });

    // Manejar envío del formulario
    form.addEventListener('submit', (event) => {
        if (!validarHorasRegistradas() || !validarHorasInicioFinIguales()) {
            event.preventDefault(); // Evitar el envío del formulario si la validación falla
        } else {
            event.preventDefault(); // Evitar el envío del formulario por defecto
            const formData = new FormData(form);

            const inasistencias = Array.from(document.querySelectorAll('select[name^="tipo_inasistencia_"]'))
                .map(select => ({
                    codigoEmp: select.name.split('_')[1],
                    inasistencia: ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R'].includes(select.value)
                }))
                .filter(emp => emp.inasistencia);

            inasistencias.forEach(emp => {
                for (let i = 1; i <= 15; i++) {
                    const inicioField = document.querySelector(`[name="inicio_proceso${i}_${emp.codigoEmp}"]`);
                    const finField = document.querySelector(`[name="fin_proceso${i}_${emp.codigoEmp}"]`);
                    if (inicioField && finField) {
                        inicioField.value = '00:00:00';
                        finField.value = '00:00:00';
                    }
                }
            });

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const responseModal = new bootstrap.Modal(document.getElementById('responseModal'));
                const responseModalBody = document.getElementById('responseModalBody');
                responseModalBody.textContent = data.success ? 'Datos enviados correctamente.' : 'Error al enviar los datos: ' + data.message;
                responseModal.show();
            })
            .catch(error => {
                const responseModal = new bootstrap.Modal(document.getElementById('responseModal'));
                const responseModalBody = document.getElementById('responseModalBody');
                responseModalBody.textContent = 'Ocurrió un error al enviar los datos: ' + error.message;
                responseModal.show();
            });
        }
    });

    // Agregar evento change a todos los selectores de inasistencia
    document.querySelectorAll('select[name^="tipo_inasistencia_"]').forEach(select => {
        select.addEventListener('change', (event) => {
            const codigoEmp = event.target.name.split('_')[1];
            toggleInputs(codigoEmp);
        });
    });

    // Agregar evento para marcar el campo como modificado por el usuario
    document.querySelectorAll('input[name^="inicio_proceso"]').forEach(input => {
        input.addEventListener('input', function() {
            this.dataset.userModified = true;
        });
    });

    // Verificar los valores de tipo_inasistencia en el DOM
    document.querySelectorAll('select[name^="tipo_inasistencia_"]').forEach(select => {
        const codigoEmp = select.name.split('_')[1];
        console.log(`Empleado ${codigoEmp} - Tipo de inasistencia: ${select.value}`);
    });
});

function verificarSeleccionProcesos() {
    // Usar Array.prototype.some para verificar si alguno de los selectores tiene un valor seleccionado
    const algunoSeleccionado = Array.from(procesoSelects).some(select => select.value);

    // Habilitar o deshabilitar el botón guardar basado en el resultado anterior
    guardarBtn.disabled = !algunoSeleccionado;
}
function toggleInputs(codigoEmp) {
    const tipoInasistenciaElement = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
    if (!tipoInasistenciaElement) {
        console.error(`Elemento select[name="tipo_inasistencia_${codigoEmp}"] no encontrado`);
        return;
    }

    const tipoInasistencia = tipoInasistenciaElement.value;
    const inasistencia = ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R'].includes(tipoInasistencia);
    const desbloquear = ['RT', 'NI', 'ASI'].includes(tipoInasistencia);

    const inputs = document.querySelectorAll(`[name^="inicio_proceso"][name$="_${codigoEmp}"], [name^="fin_proceso"][name$="_${codigoEmp}"], [name="horas_extras_${codigoEmp}"]`);
    const totalElement = document.querySelector(`[name="total_${codigoEmp}"]`);

    inputs.forEach(input => {
        const procesoSelect = document.querySelector(`[name="proceso${input.name.match(/\d+/)[0]}_header"]`);
        if (inasistencia) {
            input.value = '--:--';
            input.disabled = true;
        } else if (desbloquear && procesoSelect && procesoSelect.value) {
            input.disabled = false;
        }
    });

    if (inasistencia && totalElement) {
        totalElement.value = '0.00';

        // Restablecer los totales de horas por proceso
        for (let i = 1; i <= 15; i++) {
            const totalProcesoField = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
            if (totalProcesoField) {
                totalProcesoField.value = '0.00';
            }
        }
    }

    // Habilitar o deshabilitar los checkboxes de copiar y borrar
    const copyCheckboxes = document.querySelectorAll(`.copy-checkbox[data-emp="${codigoEmp}"]`);
    const deleteCheckboxes = document.querySelectorAll(`.delete-checkbox[data-emp="${codigoEmp}"]`);
    copyCheckboxes.forEach(checkbox => checkbox.disabled = !desbloquear);
    deleteCheckboxes.forEach(checkbox => checkbox.disabled = !desbloquear);

    sumarHorasPorProceso();
}
/* function filtrarDescanso() {
    // Seleccionar automáticamente "DESCANSO" si es día de descanso
    let empleados = document.querySelectorAll('tr[data-codigo_emp]');
    const deptoSeleccionado = document.getElementById('depto_select').value;
    empleados = Array.from(empleados);
    empleados = empleados.filter(empleado => empleado.getAttribute('data-depto') === deptoSeleccionado);
  
    empleados.forEach(empleado => {
        const codigoEmp = empleado.getAttribute('data-codigo_emp');
        const esDescanso = empleado.getAttribute('data-es_descanso') === 'true';
        if (esDescanso) {
            const tipoInasistenciaElement = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
            if (tipoInasistenciaElement) {
                tipoInasistenciaElement.value = 'D';
                toggleInputs(codigoEmp);
            }
        }
    });
} */

    function prepararDatosParaEnvio() {
        const datos = {
            departamento: document.getElementById('depto_select').value,
            empleados: []
        };
        const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    
        filasEmpleados.forEach(fila => {
            if (fila.style.display !== 'none') { // Solo procesar empleados visibles
                const codigoEmp = fila.dataset.codigo_emp;
                const procesos = [];
    
                for (let i = 1; i <= 15; i++) {
                    const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
                    const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);
                    const total = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
    
                    if (procesoSelect && procesoSelect.value && !inicio.disabled && !fin.disabled) {
                        if (inicio.value && fin.value) {
                            procesos.push({
                                procesoId: procesoSelect.value,
                                inicio: inicio.value,
                                fin: fin.value,
                                total: total.value
                            });
                        }
                    }
                }
    
                const horasExtras = document.querySelector(`[name="horas_extras_${codigoEmp}"]`).value || 0;
                const totalHoras = document.querySelector(`[name="total_${codigoEmp}"]`).value || 0;
                const tipoInasistencia = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`).value;
    
                datos.empleados.push({
                    codigoEmp: codigoEmp,
                    procesos: procesos,
                    horasExtras: horasExtras,
                    totalHoras: totalHoras,
                    tipoInasistencia: tipoInasistencia
                });
            }
        });
    
        // Enviar datos al servidor
        fetch('/horas_procesos/gestion_horas_procesos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            console.log("Estado de la respuesta:", response.status);  // Verificar el estado de la respuesta
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Respuesta del servidor:", data);  // Verificar la respuesta del servidor
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: 'Se envió correctamente.',
                    timer: 2000,
                    showConfirmButton: false
                });
    
                // Recargar la página después de 2 segundos
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: `Error al enviar el formulario: ${data.error}`
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: `Error al enviar el formulario: ${error}`
            });
        });
    }




function showAlert(message, type) {
    const alerta = document.getElementById('alerta');
    alerta.querySelector('.alerta-mensaje').innerHTML = message.replace(/\n/g, '<br>'); // Reemplazar saltos de línea con <br>
    alerta.className = `alerta-centrada alert alert-${type}`;
    alerta.style.display = 'block';
}
function cerrarAlerta() {
    const alerta = document.getElementById('alerta');
    alerta.style.display = 'none';
}
function validarHorasInicioFinIguales() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let valid = true;
    let mensajesAlerta = [];

    filasEmpleados.forEach(fila => {
        if (fila.style.display !== 'none') { // Solo validar empleados visibles
            const codigoEmp = fila.dataset.codigo_emp;

            for (let i = 1; i <= 15; i++) {
                const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);

                if (inicio && fin && inicio.value === fin.value && inicio.value) {
                    mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene horas de inicio y fin iguales en el proceso ${i}.`);
                    valid = false;
                }
            }
        }
    });

    if (!valid) {
        showAlert(mensajesAlerta.join('\n'), 'danger');
    }

    return valid;
}
function restablecerFormulario() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');

    filasEmpleados.forEach(fila => {
        // Limpiar y bloquear por defecto los campos de horas y procesos
        fila.querySelectorAll('input[type="time"], input[type="number"], input[type="text"]').forEach(input => {
            input.value = ''; // Limpiar el valor de los campos
            input.disabled = !input.name.startsWith('horas_extras_'); // Bloquear todos excepto horas extras
        });

        // Restablecer los checkboxes
        fila.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false; // Desmarcar todos los checkboxes
        });

        // Limpiar los campos de selección de procesos
        fila.querySelectorAll('select[name^="proceso"]').forEach(select => {
            select.selectedIndex = 0; // Restablecer el valor del selector al primer elemento
        });
    });

    // Restablecer los totales de horas por proceso
    Array.from({ length: 15 }, (_, i) => i + 1).forEach(i => {
        const totalProcesoField = document.querySelector(`#total_proceso${i}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = '0.00'; // Restablecer los totales de horas a 0
        }
    });
}
function filtrarEmpleados() {
    const deptoSeleccionado = document.getElementById('depto_select').value;
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let contador = 1;
    let totalEmpleados = 0;

    if (deptoSeleccionado === "") {
        document.getElementById('tabla_empleados').style.display = 'none';
        document.getElementById('total_empleados').style.display = 'none';
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
    document.getElementById('total_empleados').style.display = 'block';
    document.getElementById('tabla_empleados').style.display = totalEmpleados > 0 ? 'block' : 'none';
}
/* function validarHorasInicioFinIguales() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let valid = true;
    let mensajeAlerta = '';

    filasEmpleados.forEach(fila => {
        if (fila.style.display !== 'none') { // Solo validar empleados visibles
            const codigoEmp = fila.dataset.codigo_emp;

            for (let i = 1; i <= 15; i++) {
                const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`).value;
                const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`).value;

                if (inicio && fin && inicio === fin) {
                    mensajeAlerta += `El empleado con código ${codigoEmp} tiene horas de inicio y fin iguales en el proceso ${i}.\n`;
                    valid = false;
                }
            }
        }
    });

    if (!valid) {
        showAlert(mensajeAlerta, 'danger');
    }

    return valid;
}
 */
function validarHorasRegistradas() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    const deptoSeleccionado = document.getElementById('depto_select').value;
    let valid = true;
    let mensajeAlerta = '';

    filasEmpleados.forEach(fila => {
        const deptoEmpleado = fila.getAttribute('data-depto');
        const codigoEmp = fila.dataset.codigo_emp;
        const tipoInasistencia = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`).value;
        const inasistencia = ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R'].includes(tipoInasistencia);

        if (deptoEmpleado === deptoSeleccionado && !inasistencia) {
            let tieneHorasRegistradas = false;
            const horasRegistradas = new Set();
            const horarios = [];

            for (let i = 1; i <= 15; i++) {
                const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);

                if (procesoSelect && procesoSelect.value) {
                    const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);

                    // Verificar si los campos de inicio y fin no están deshabilitados y contienen valores
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
                                horarios.push({ inicio: inicio.value, fin: fin.value });
                            }
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
        } else if (['NI', 'RT', 'ASI'].includes(tipoInasistencia)) {
            // No deshabilitar los campos ni poner las horas en 00:00:00 para "NUEVO INGRESO (NI)" o "RETARDO (RT)"
            for (let i = 1; i <= 15; i++) {
                const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);
                if (inicio && fin) {
                    inicio.disabled = false;
                    fin.disabled = false;
                }
            }
        }
    });

    // Si no es válido, mostrar el mensaje de alerta
    if (!valid) {
        showAlert(mensajeAlerta, 'danger');
    }

    return valid;
}



// Verifica si hay horas de inicio y fin idénticas en más de un proceso
function verificarHorasDuplicadas(codigoEmp) {
    let mensaje = '';
    const horasRegistradas = new Set();

    // Seleccionar todos los campos de inicio y fin de proceso para el empleado
    for (let i = 1; i <= 15; i++) {
        const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
        const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);

        if (inicio && fin && !inicio.disabled && !fin.disabled && inicio.value && fin.value) {
            const horas = `${inicio.value}-${fin.value}`;
            if (horasRegistradas.has(horas)) {
                mensaje += `El empleado con código ${codigoEmp} tiene horas de inicio y fin idénticas en más de un proceso.\n`;
            } else {
                horasRegistradas.add(horas);
            }
        }
    }

    return mensaje;
}
function handleCheckboxChange(event) {
    const checkbox = event.target;
    const proceso = checkbox.dataset.proceso;
    const emp = checkbox.dataset.emp;
    const row = checkbox.closest('tr');
    const prevRow = getPreviousRowWithProceso(row, proceso);

    // Obtener los elementos de entrada de inicio y fin
    const inicioInput = row.querySelector(`input[name="inicio_proceso${proceso}_${emp}"]`);
    const finInput = row.querySelector(`input[name="fin_proceso${proceso}_${emp}"]`);
    const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${emp}"]`);
    const isDescanso = tipoInasistenciaSelect.value === 'D' || tipoInasistenciaSelect.value === 'F';
    const desbloquear = ['RT', 'NI', 'ASI'].includes(tipoInasistenciaSelect.value);

    // Validar que los elementos de entrada existen
    if (!inicioInput || !finInput) {
        console.error(`No se encontraron los elementos de entrada para el proceso ${proceso} y el empleado ${emp}`);
        return;
    }

    if (checkbox.checked && !isDescanso) {
        if (prevRow) {
            const prevInicio = prevRow.querySelector(`input[name="inicio_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`).value;
            const prevFin = prevRow.querySelector(`input[name="fin_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`).value;

            // Guardar los valores originales
            inicioInput.dataset.originalValue = inicioInput.value;
            finInput.dataset.originalValue = finInput.value;

            // Copiar los valores de la fila anterior
            inicioInput.value = prevInicio;
            finInput.value = prevFin;
        } else {
            console.warn(`No se encontró una fila anterior con el proceso ${proceso} para el empleado ${emp}`);
        }
    } else {
        // Restaurar los valores originales
        inicioInput.value = inicioInput.dataset.originalValue || '';
        finInput.value = finInput.dataset.originalValue || '';
    }

    // Habilitar o deshabilitar los checkboxes de copiar y borrar
    if (desbloquear) {
        checkbox.disabled = false;
    } else {
        checkbox.disabled = true;
    }

    // Calcular y sumar horas después de cualquier cambio
    calcularTotalHoras(emp, proceso);
    sumarHorasPorProceso();
}

function getPreviousRowWithProceso(currentRow, proceso) {
    const deptoActual = currentRow.getAttribute('data-depto');
    let prevRow = currentRow.previousElementSibling;

    while (prevRow) {
        const codigoEmp = prevRow.dataset.codigo_emp;
        const prevInicioInput = prevRow.querySelector(`input[name="inicio_proceso${proceso}_${codigoEmp}"]`);
        const prevFinInput = prevRow.querySelector(`input[name="fin_proceso${proceso}_${codigoEmp}"]`);

        if (prevRow.getAttribute('data-depto') === deptoActual && prevInicioInput && prevFinInput && prevInicioInput.value && prevFinInput.value) {
            return prevRow;
        }
        prevRow = prevRow.previousElementSibling;
    }
    return null;
}
function handleDeleteCheckboxChange(event) {
    const checkbox = event.target;
    const row = checkbox.closest('tr');
    const procesoNum = checkbox.dataset.proceso; // Obtener el número del proceso del dataset del checkbox
    const codigoEmp = checkbox.dataset.emp; // Obtener el código del empleado del dataset del checkbox
    const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
    const isDescanso = tipoInasistenciaSelect.value === 'D' || tipoInasistenciaSelect.value === 'F';
    const desbloquear = ['RT', 'NI', 'ASI'].includes(tipoInasistenciaSelect.value);

    // Validar que los datos del dataset existen
    if (!procesoNum || !codigoEmp) {
        console.error('Datos del dataset faltantes en el checkbox.');
        return;
    }

    // Seleccionar solo los campos de entrada correspondientes al proceso y empleado específicos
    const inputs = row.querySelectorAll(`input[name="inicio_proceso${procesoNum}_${codigoEmp}"], input[name="fin_proceso${procesoNum}_${codigoEmp}"], input[name="total_proceso${procesoNum}_${codigoEmp}"]`);

    // Validar que los inputs existen
    if (inputs.length === 0) {
        console.error('No se encontraron los elementos de entrada correspondientes.');
        return;
    }

    if (checkbox.checked && !isDescanso) {
        // Deshabilitar los campos de entrada correspondientes y limpiar sus valores
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

    // Habilitar o deshabilitar los checkboxes de copiar y borrar
    if (desbloquear) {
        checkbox.disabled = false;
    } else {
        checkbox.disabled = true;
    }

    // Calcular y sumar horas después de cualquier cambio
    calcularTotalHoras(codigoEmp, procesoNum);
    sumarHorasPorProceso();
}
function toggleProcesoInputs(procesoNum) {
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
    const selectedValue = procesoSelect.value;

    // Seleccionar todos los selectores de proceso
    const allSelects = [];
    for (let i = 1; i <= 15; i++) {
        const select = document.querySelector(`[name="proceso${i}_header"]`);
        if (select) {
            allSelects.push(select);
        }
    }

    // Deshabilitar la opción seleccionada en todos los selectores de proceso posteriores
    allSelects.forEach((otherSelect, index) => {
        if (index + 1 !== procesoNum) {
            const options = otherSelect.querySelectorAll('option');
            options.forEach(option => {
                if (option.value === selectedValue) {
                    option.disabled = true;
                } else {
                    // Verificar si la opción está seleccionada en algún proceso anterior
                    let isSelectedInPrevious = false;
                    allSelects.forEach((previousSelect, prevIndex) => {
                        if (prevIndex + 1 !== index + 1 && previousSelect.value === option.value) {
                            isSelectedInPrevious = true;
                        }
                    });
                    option.disabled = isSelectedInPrevious;
                }
            });
        }
    });

    // Habilitar o deshabilitar los campos de entrada correspondientes al proceso seleccionado
    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;
        const tipoInasistenciaSelect = fila.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
        const isDescanso = tipoInasistenciaSelect.value === 'D' || tipoInasistenciaSelect.value === 'F';
        const desbloquear = ['RT', 'NI', 'ASI'].includes(tipoInasistenciaSelect.value);
        const inicioInput = fila.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
        const finInput = fila.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
        const copyCheckbox = fila.querySelector(`.copy-checkbox[data-proceso="${procesoNum}"]`);
        const deleteCheckbox = fila.querySelector(`.delete-checkbox[data-proceso="${procesoNum}"]`);

        if (selectedValue && !isDescanso) {
            if (inicioInput && finInput) {
                inicioInput.disabled = false;
                finInput.disabled = false;
            } else {
                console.error(`No se encontraron los elementos de entrada para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
            }
        } else {
            if (inicioInput && finInput) {
                inicioInput.disabled = true;
                finInput.disabled = true;
                inicioInput.value = '';
                finInput.value = '';
            }
        }

        // Habilitar o deshabilitar los checkboxes de copiar y borrar
        if (copyCheckbox) copyCheckbox.disabled = !desbloquear;
        if (deleteCheckbox) deleteCheckbox.disabled = !desbloquear;
    });

    // Recalcula las horas cada vez que se selecciona un proceso
    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;
        if (procesoSelect.value && fila.style.display !== 'none') { // Solo procesar empleados visibles
            calcularTotalHoras(codigoEmp, procesoNum);
        }
    });

    sumarHorasPorProceso();
}

function ajustarHoraFin(codigoEmp, procesoNum) {
    const inicioField = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const finField = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);

    // Verificar si el proceso está seleccionado
    if (!procesoSelect || !procesoSelect.value) {
        console.error(`El proceso ${procesoNum} no está seleccionado para el empleado ${codigoEmp}`);
        return;
    }

    // Obtener la hora de fin del proceso anterior
    if (procesoNum > 1) {
        const finAnteriorField = document.querySelector(`[name="fin_proceso${procesoNum - 1}_${codigoEmp}"]`);
        if (finAnteriorField && finAnteriorField.value && !inicioField.dataset.userModified) {
            inicioField.value = finAnteriorField.value;
        }
    }

    if (!inicioField.value) return;

    // Función auxiliar para ajustar la hora
    const ajustarHora = (horas, minutos) => {
        let nuevaHora = horas + 1;
        if (nuevaHora >= 24) nuevaHora -= 24;
        return `${nuevaHora.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}`;
    };

    const [inicioHoras, inicioMinutos] = inicioField.value.split(':').map(Number);

    if (isNaN(inicioHoras) || isNaN(inicioMinutos)) {
        console.error(`Horas o minutos inválidos para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
        finField.value = '';
        return;
    }

    finField.value = ajustarHora(inicioHoras, inicioMinutos);
    calcularTotalHoras(codigoEmp, procesoNum);

    let horas = inicioHoras;
    let minutos = inicioMinutos;

    // Ajustar las horas de los procesos siguientes
    for (let i = procesoNum + 1; i <= 15; i++) {
        const siguienteInicioField = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
        const siguienteFinField = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);
        const siguienteProcesoSelect = document.querySelector(`[name="proceso${i}_header"]`);

        // Verificar si el siguiente proceso está seleccionado
        if (!siguienteInicioField || !siguienteFinField || !siguienteProcesoSelect || !siguienteProcesoSelect.value) continue;

        if (!siguienteInicioField.dataset.userModified) {
            siguienteInicioField.value = ajustarHora(horas, minutos);
        }
        [horas, minutos] = siguienteInicioField.value.split(':').map(Number);
        siguienteFinField.value = ajustarHora(horas, minutos);

        calcularTotalHoras(codigoEmp, i);
    }
}


function calcularTotalHoras(codigoEmp, procesoNum) {
    const inicio = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const fin = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
    const totalField = document.querySelector(`[name="total_proceso${procesoNum}_${codigoEmp}"]`);

    // Validar que los elementos de entrada existen
    if (!inicio || !fin || !totalField) {
        console.error(`No se encontraron los elementos de entrada para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
        return;
    }

    if (inicio.value && fin.value) {
        const [inicioHoras, inicioMinutos] = inicio.value.split(':').map(Number);
        const [finHoras, finMinutos] = fin.value.split(':').map(Number);

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

    // Calcular el total de horas para todos los procesos
    let totalHoras = 0;
    for (let i = 1; i <= 15; i++) {
        const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
        if (procesoSelect && procesoSelect.value) {
            const totalProcesoField = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
            if (totalProcesoField && totalProcesoField.value) {
                totalHoras += parseFloat(totalProcesoField.value) || 0;
            }
        }
    }

    // Agregar horas extras
    const horasExtrasField = document.querySelector(`[name="horas_extras_${codigoEmp}"]`);
    const horasExtras = parseFloat(horasExtrasField.value) || 0;
    totalHoras += horasExtras;

    horasExtrasField.value = horasExtras.toFixed(2);
    document.querySelector(`[name="total_${codigoEmp}"]`).value = totalHoras.toFixed(2);

    sumarHorasPorProceso();
}
function sumarHorasPorProceso() {
    const totalHorasPorProceso = Array(15).fill(0);

    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        let totalEmpleado = 0;
        const codigoEmp = fila.dataset.codigo_emp;

        for (let i = 1; i <= 15; i++) {
            const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
            if (procesoSelect && procesoSelect.value) {
                const totalProceso = fila.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
                if (totalProceso && totalProceso.value) {
                    const totalProcesoValue = parseFloat(totalProceso.value) || 0;
                    totalHorasPorProceso[i - 1] += totalProcesoValue;
                    totalEmpleado += totalProcesoValue;
                }
            }
        }

        const totalEmpleadoField = fila.querySelector(`[name="total_${codigoEmp}"]`);
        if (totalEmpleadoField) {
            totalEmpleadoField.value = totalEmpleado.toFixed(2);
        }
    });

    totalHorasPorProceso.forEach((total, i) => {
        const totalProcesoField = document.querySelector(`#total_proceso${i + 1}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = total.toFixed(2);
        }
    });
}
