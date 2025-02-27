document.addEventListener('DOMContentLoaded', () => {
    const now = new Date();
    document.getElementById('fecha').value = now.toISOString().split('T')[0];
    document.getElementById('tabla_empleados').style.display = 'none';

    const guardarBtn = document.getElementById('guardar-btn');
    const procesoSelects = document.querySelectorAll('select[name^="proceso"]');
    const productoSelects = document.querySelectorAll('select[name^="producto"]');
    const form = document.querySelector('form');
    empleadosTbody = document.getElementById('empleados_tbody');
    deptoSelect = document.getElementById('depto_select');
    totalProcesosContainer = document.getElementById('total_procesos_container');
    deptoSelect = document.getElementById('depto_select');
    tablaEmpleados = document.getElementById('tabla_empleados');
    totalEmpleadosElement = document.getElementById('total_empleados');
    totalProcesoFields = document.querySelectorAll('[name^="total_proceso"]');
    const copyAllCheckbox = document.getElementById('copy-all-checkbox');
    const copyAllLabel = document.getElementById('copy-all-label');

    // Función para verificar si algún proceso está seleccionado
    function verificarSeleccionProcesos() {
        // Verificar si el proceso 1 está habilitado
        const proceso1 = document.querySelector('select[name="proceso1_header"]');
        const proceso1Seleccionado = !!proceso1.value;

        // Habilitar o deshabilitar el botón guardar basado en el resultado anterior
        guardarBtn.disabled = !proceso1Seleccionado;
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
            calcularTotalHoras('codigoEmp1', 1);
        }
    });

    // Función para restablecer los selectores de proceso y producto
    function restablecerSelectores() {
        procesoSelects.forEach(select => {
            select.selectedIndex = 0; // Restablecer al valor inicial
        });
        productoSelects.forEach(select => {
            select.selectedIndex = 0; // Restablecer al valor inicial
        });
    }

    // Manejar cambio de departamento
    deptoSelect.addEventListener('change', () => {
        restablecerFormulario();
        filtrarEmpleadosPorFecha(); // Llamar a la función para filtrar empleados por fecha y departamento
        restablecerSelectores(); // Restablecer los selectores de proceso y producto
    
        // Restablecer el checkbox de copiar todo
        const copyAllCheckbox = document.getElementById('copy-all-checkbox');
        copyAllCheckbox.checked = false; // Desmarcar el checkbox
        copyAllCheckbox.style.display = deptoSelect.value ? 'inline-block' : 'none'; // Mostrar u ocultar el checkbox y la etiqueta
    
        // Mostrar el checkbox y la etiqueta cuando se seleccione un departamento
        const copyAllLabel = document.getElementById('copy-all-label');
        if (deptoSelect.value) {
            copyAllCheckbox.style.display = 'inline-block';
            copyAllLabel.style.display = 'inline-block';
        } else {
            copyAllCheckbox.style.display = 'none';
            copyAllLabel.style.display = 'none';
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

    // Agregar evento change al campo de fecha
    document.getElementById('fecha').addEventListener('change', filtrarEmpleadosPorFecha);

    // Inicializar variables globales
    initGlobals();
    document.getElementById('depto_select').addEventListener('change', initGlobals);
});//yaaa COMENTADO UNA FUNCION 
// Variables globales para elementos del DOM
let deptoSeleccionado;
let filasEmpleados;
let totalProcesoFields;
let totalField;
let horasExtrasField;
let horaComidaCheckbox;
let recorridos = [];
let guardarBtn;
let procesoSelects;


// Función para inicializar las variables globales
function initGlobals() {
    deptoSeleccionado = document.getElementById('depto_select').value;
    filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    totalProcesoFields = document.querySelectorAll(`input[name^="total_proceso"]`);
}
function verificarSeleccionProcesos() {
    // Usar Array.prototype.some para verificar si alguno de los selectores tiene un valor seleccionado
    const algunoSeleccionado = Array.from(procesoSelects).some(select => !!select.value);

    // Habilitar o deshabilitar el botón guardar basado en el resultado anterior
    if (guardarBtn.disabled !== !algunoSeleccionado) {
        guardarBtn.disabled = !algunoSeleccionado;
    }
}//yaaa doom

let empleadosTbody;

function toggleInputs(codigoEmp) {
    guardarEstadoAnterior(codigoEmp); // Guardar el estado antes de realizar cambios


    const tipoInasistenciaElement = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
    if (!tipoInasistenciaElement) {
        console.error(`Elemento select[name="tipo_inasistencia_${codigoEmp}"] no encontrado`);
        return;
    }

    const tipoInasistencia = tipoInasistenciaElement.value;
    const inasistencia = ['F', 'D', 'V', 'INC', 'S', 'B','R'].includes(tipoInasistencia);
    const desbloquear = ['RT', 'NI', 'ASI','P'].includes(tipoInasistencia);

    const inputs = document.querySelectorAll(`[name^="inicio_proceso"][name$="_${codigoEmp}"], [name^="fin_proceso"][name$="_${codigoEmp}"], [name="horas_extras_${codigoEmp}"]`);
    const totalElement = document.querySelector(`[name="total_${codigoEmp}"]`);

    inputs.forEach(input => {
        const procesoNum = input.name.match(/\d+/)[0];
        const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
        if (procesoSelect && procesoSelect.value) {
            if (inasistencia) {
                input.value = '--:--';
                input.disabled = true;
            } else if (desbloquear) {
                input.disabled = false;
            }
        }
    });

    if (inasistencia && totalElement) {
        totalElement.value = '0.00';

        // Restablecer los totales de horas por proceso
        for (let i = 1; i <= 10; i++) {
            const totalProcesoField = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
            const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
            if (totalProcesoField && procesoSelect && procesoSelect.value) {
                totalProcesoField.value = '0.00';
            }
        }
    }

    // Habilitar o deshabilitar los checkboxes de copiar y borrar
    const copyCheckboxes = document.querySelectorAll(`.copy-checkbox[data-emp="${codigoEmp}"]`);
    const deleteCheckboxes = document.querySelectorAll(`.delete-checkbox[data-emp="${codigoEmp}"]`);
    copyCheckboxes.forEach(checkbox => {
        const procesoNum = checkbox.dataset.proceso;
        const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
        if (procesoSelect && procesoSelect.value) {
            checkbox.disabled = !desbloquear;
        }
    });
    deleteCheckboxes.forEach(checkbox => {
        const procesoNum = checkbox.dataset.proceso;
        const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
        if (procesoSelect && procesoSelect.value) {
            checkbox.disabled = !desbloquear;
        }
    });
}//yaaa doom

    




    function showAlert(message, type) {
        const alerta = document.getElementById('alerta');
        const alertaMensaje = alerta.querySelector('.alerta-mensaje');
        
        // Actualizar el contenido y las clases del elemento de alerta
        alertaMensaje.innerHTML = `
            ${message.replace(/\n/g, '<br>')} 
            <br>
            <button id="aceptar-btn" class="btn btn-primary">Aceptar</button>
            <button id="editar-btn" class="btn btn-secondary">Editar</button>
        `; // Reemplazar saltos de línea con <br> y agregar botones
        alerta.className = `alerta-centrada alert alert-${type}`;
        alerta.style.display = 'block';
    
        // Agregar eventos a los botones
        document.getElementById('aceptar-btn').addEventListener('click', () => {
            cerrarAlerta();
            enviarFormularioSinValidaciones(); // Enviar el formulario sin validaciones
        });
    
        document.getElementById('editar-btn').addEventListener('click', () => {
            cerrarAlerta();
            // Acción adicional para el botón Editar
        });
    }
    
    function cerrarAlerta() {
        const alerta = document.getElementById('alerta');
        alerta.style.display = 'none';
    }
    
    function enviarFormularioSinValidaciones() {
        const form = document.getElementById('horas-procesos-form');
        // Desactivar la validación del formulario
        form.onsubmit = null;
        form.submit(); // Enviar el formulario sin validaciones
    }

    function validartotalhoras() {
        const filasEmpleados = Array.from(document.querySelectorAll('#empleados_tbody tr')).filter(fila => fila.style.display !== 'none');
        let valid = true;
        let mensajesAlerta = [];
        const diasSemana = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
        
        // Obtener la fecha seleccionada en el input de tipo date
        const fechaInput = document.getElementById('fecha').value;
        const fechaSeleccionada = new Date(fechaInput + 'T00:00:00'); // Asegurarse de que se tome la fecha correctamente
        const diaActual = diasSemana[fechaSeleccionada.getUTCDay()];
        
        /* // Agregar console.log para verificar cómo se toma el día
        console.log(`Fecha seleccionada: ${fechaSeleccionada}`);
        console.log(`Día de la semana: ${diaActual}`); */
    
        filasEmpleados.forEach(fila => {
            const codigoEmp = fila.dataset.codigo_emp;
            const idTurno = fila.dataset.id_turno; // Obtener el id_turno del dataset
            const tipoInasistenciaElement = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
            const tipoInasistencia = tipoInasistenciaElement ? tipoInasistenciaElement.value : '';
    
            if (['ASI', 'RT', 'NI','P'].includes(tipoInasistencia)) {
                const totalField = document.querySelector(`input[name="total_${codigoEmp}"]`);
    
                if (totalField) {
                    const totalHoras = parseFloat(totalField.value) || 0;
    
                    // Validación para empleados con id_turno="100"
                    if (idTurno === "100") {
                        if (['lunes', 'martes', 'miércoles', 'jueves'].includes(diaActual)) {
                            if (totalHoras < 11.25) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 11.25 horas trabajadas.`);
                                valid = false;
                            } else if (totalHoras > 11.25) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 11.25 horas trabajadas.`);
                                valid = false;
                            }
                        } else if (['viernes', 'sábado'].includes(diaActual)) {
                            if (totalHoras < 7.50) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 7.50 horas trabajadas.`);
                                valid = false;
                            } else if (totalHoras > 7.50) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 7.50 horas trabajadas.`);
                                valid = false;
                            }
                        }
                    } else if (["4", "1009", "10"].includes(idTurno)) {
                        // Validación para empleados con id_turno="4", "1009", "10"
                        if (totalHoras < 8.25) {
                            mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 8.25 horas trabajadas.`);
                            valid = false;
                        } else if (totalHoras > 8.25) {
                            mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 8.25 horas trabajadas.`);
                            valid = false;
                        }
                    } else if (["1035", "1033", "1031", "1041", "1034", "1032"].includes(idTurno)) {
                        // Validación para empleados con id_turno="1035", "1033", "1031", "1041", "1034", "1032"
                        if (diaActual === 'lunes') {
                            if (totalHoras < 11.25) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 11.25 horas trabajadas.`);
                                valid = false;
                            } else if (totalHoras > 11.25) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 11.25 horas trabajadas.`);
                                valid = false;
                            }
                        } else {
                            if (totalHoras < 10.40) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 10.40 horas trabajadas.`);
                                valid = false;
                            } else if (totalHoras > 10.40) {
                                mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 10.40 horas trabajadas.`);
                                valid = false;
                            }
                        }
                    } else if (idTurno === "1044") {
                        // Validación para empleados con id_turno="1044"
                        if (totalHoras < 10.25) {
                            mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 10.25 horas trabajadas.`);
                            valid = false;
                        } else if (totalHoras > 10.25) {
                            mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 10.25 horas trabajadas.`);
                            valid = false;
                        }
                    } else {
                        // Validación para otros empleados
                        if (totalHoras < 11.25) {
                            mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 11.25 horas trabajadas.`);
                            valid = false;
                        } else if (totalHoras > 11.25) {
                            mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene más de 11.25 horas trabajadas.`);
                            valid = false;
                        }
                    }
                }
            }
        });
    
        if (!valid) {
            showAlert(mensajesAlerta.join('\n'), 'danger');
        }
    
        return valid;
    }
let totalProcesosContainer;


function restablecerFormulario() {
    const filasEmpleados = empleadosTbody.querySelectorAll('tr');

    filasEmpleados.forEach(fila => {
        let tieneDatos = false;

        // Verificar si hay datos en los campos de horas y procesos
        const inputs = fila.querySelectorAll('input[type="time"], input[type="number"], input[type="text"]');
        inputs.forEach(input => {
            if (input.value) {
                tieneDatos = true;
            }
        });

        if (tieneDatos) {
            // Limpiar y bloquear por defecto los campos de horas y procesos
            fila.querySelectorAll('input[type="time"], input[type="number"], input[type="text"]').forEach(input => {
                input.value = ''; // Limpiar el valor de los campos
                input.disabled = !input.name.startsWith('horas_extras_'); // Bloquear todos excepto horas extras
            });

            // Restablecer los checkboxes
            fila.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false; // Desmarcar todos los checkboxes
            });

            // Limpiar los campos de selección de procesos y productos
            fila.querySelectorAll('select[name^="proceso"], select[name^="producto"]').forEach(select => {
                select.selectedIndex = 0; // Restablecer el valor del selector al primer elemento
            });
        }
    });

    // Restablecer los totales de horas por proceso
    Array.from({ length: 10 }, (_, i) => i + 1).forEach(i => {
        const totalProcesoField = document.querySelector(`#total_proceso${i}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = '0.00'; // Restablecer los totales de horas a 0
        }
    });

    // Restablecer el resumen de asistencia
    const resumenAsistencia = document.getElementById('resumen-asistencia');
    if (resumenAsistencia) {
        const spans = resumenAsistencia.querySelectorAll('span');
        spans.forEach(span => {
            span.textContent = '0';
        });
        resumenAsistencia.style.display = 'block'; // Asegurarse de que el resumen de asistencia esté visible
    }
}//yaaa doom
let deptoSelect;
let tablaEmpleados;
let totalEmpleadosElement;

function filtrarEmpleados() {
    var departamento = document.getElementById('depto_select').value;
    
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/horas_procesos/gestion_horas_procesos/?departamento=' + departamento, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            
            var empleadosTbody = document.getElementById('empleados_tbody');
            if (empleadosTbody) {
                empleadosTbody.innerHTML = '';
                response.empleados.forEach(function (empleado, index) {
                    
                    var row = document.createElement('tr');
                    row.setAttribute('data-depto', empleado.id_departamento);
                    row.setAttribute('data-depto-descripcion', empleado.descripcion_departamento);
                    row.setAttribute('data-codigo_emp', empleado.codigo_emp);
                    row.setAttribute('data-id_turno', empleado.id_turno);
                    row.setAttribute('data-dias_descanso', empleado.dias_descanso.join(','));
                    row.setAttribute('data-es_descanso', empleado.es_descanso);

                    // Verifica que response.turnos esté definido y que tenga el formato esperado
                    var turno = response.turnos ? response.turnos.find(t => t.id === empleado.id_turno) : null;

                    row.innerHTML = `
                        <td class="employee-number">${index + 1}</td>
                        <td>${empleado.codigo_emp}</td>
                        <td>${empleado.nombre_emp}</td>
                        <td>${empleado.descripcion_departamento}</td>
                        <td>
                            <select class="form-select form-select-sm" name="tipo_inasistencia_${empleado.codigo_emp}" onchange="toggleInputs('${empleado.codigo_emp}'); actualizarResumenAsistencia(); applyColorClass(this);">
                                ${response.tipos_inasistencia.map(tipo => `
                                    <option value="${tipo.ID_Asis}" ${empleado.tipo_inasistencia == tipo.ID_Asis ? 'selected' : ''}>${tipo.Descripcion}</option>
                                `).join('')}
                            </select>
                        </td>
                        <td>
                            ${turno ? `
                                <div>Turno: ${turno.nombre}</div>
                                <div>Horario: ${turno.horario}</div>
                                <div>Descanso: ${turno.descanso}</div>
                            ` : 'No asignado'}
                        </td>
                        ${Array.from({ length: 10 }, (_, i) => `
                            <td>
                                <input type="checkbox" class="form-check-input comida-checkbox" data-proceso="${i + 1}" data-emp="${empleado.codigo_emp}" name="comida_proceso${i + 1}_${empleado.codigo_emp}" onchange="handleComidaCheckboxChange(event)">
                                <input type="hidden" name="comida_proceso${i + 1}_${empleado.codigo_emp}_hidden" value="off">
                                <label for="comida-checkbox">
                                    <img src="/static/icons/hora_comida.png" alt="Comida" style="width: 15px; height: 15px;">
                                </label>
                                <input type="time" class="form-control form-control-sm mb-2" name="inicio_proceso${i + 1}_${empleado.codigo_emp}" placeholder="Inicio" disabled step="60" onchange="ajustarHoraFin('${empleado.codigo_emp}', ${i + 1})">
                                <input type="time" class="form-control form-control-sm mb-2" name="fin_proceso${i + 1}_${empleado.codigo_emp}" placeholder="Fin" disabled step="60" onchange="calcularTotalHoras('${empleado.codigo_emp}', ${i + 1})">
                                <input type="text" class="form-control form-control-sm mb-2" name="total_proceso${i + 1}_${empleado.codigo_emp}" readonly>
                                <input type="checkbox" class="form-check-input delete-checkbox" data-proceso="${i + 1}" data-emp="${empleado.codigo_emp}" onchange="handleDeleteCheckboxChange(event)">
                                <label for="delete-checkbox">
                                    <img src="/static/icons/borrar.png" alt="Borrar Horas" style="width: 15px; height: 15px;">
                                </label>
                            </td>
                        `).join('')}
                        <td>
                            <input type="number" class="form-control form-control-sm mb-2" name="horas_extras_${empleado.codigo_emp}" step="0" onchange="calcularTotalHoras('${empleado.codigo_emp}')">
                        </td>
                        <td>
                            <input type="text" class="form-control form-control-sm input-large" name="total_${empleado.codigo_emp}" readonly>
                        </td>
                        <td>${empleado.codigo_emp}</td>
                    `;
                    empleadosTbody.appendChild(row);

                    // Aplicar color a los selectores de tipo de inasistencia
                    const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${empleado.codigo_emp}"]`);
                    if (tipoInasistenciaSelect) {
                        
                        applyColorClass(tipoInasistenciaSelect);
                    }
                });
                document.getElementById('tabla_empleados').style.display = 'block';
                actualizarResumenAsistencia(); // Llamar a la función para actualizar el resumen de asistencia

                // Actualizar el total de empleados
                var totalEmpleados = response.empleados.length;
                var totalEmpleadosElement = document.getElementById('total_empleados');
                totalEmpleadosElement.textContent = `Total de Empleados: ${totalEmpleados}`;
                totalEmpleadosElement.style.display = 'block';
            } else {
                console.error('No se encontró el cuerpo de la tabla de empleados.');
            }
        }
    };
    xhr.send();
}

function filtrarEmpleadosPorFecha() {
    var fecha = document.getElementById('fecha').value;
    var departamento = document.getElementById('depto_select').value;

    if (!fecha) {
        console.error('La fecha no está seleccionada.');
        return;
    }

    if (!departamento) {
        console.error('El departamento no está seleccionado.');
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', `/horas_procesos/gestion_horas_procesos/?fecha=${fecha}&departamento=${departamento}`, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            
            var empleadosTbody = document.getElementById('empleados_tbody');
            if (empleadosTbody) {
                empleadosTbody.innerHTML = '';
                response.empleados.forEach(function (empleado, index) {
                    
                    var row = document.createElement('tr');
                    row.setAttribute('data-depto', empleado.id_departamento);
                    row.setAttribute('data-depto-descripcion', empleado.descripcion_departamento);
                    row.setAttribute('data-codigo_emp', empleado.codigo_emp);
                    row.setAttribute('data-id_turno', empleado.id_turno);
                    row.setAttribute('data-dias_descanso', empleado.dias_descanso.join(','));
                    row.setAttribute('data-es_descanso', empleado.es_descanso);

                    // Verifica que response.turnos esté definido y que tenga el formato esperado
                    var turno = response.turnos ? response.turnos.find(t => t.id === empleado.id_turno) : null;

                    row.innerHTML = `
                        <td class="employee-number">${index + 1}</td>
                        <td>${empleado.codigo_emp}</td>
                        <td>${empleado.nombre_emp}</td>
                        <td>${empleado.descripcion_departamento}</td>
                        <td>
                            <select class="form-select form-select-sm" name="tipo_inasistencia_${empleado.codigo_emp}" onchange="toggleInputs('${empleado.codigo_emp}'); actualizarResumenAsistencia(); applyColorClass(this);">
                                ${response.tipos_inasistencia.map(tipo => `
                                    <option value="${tipo.ID_Asis}" ${empleado.tipo_inasistencia == tipo.ID_Asis ? 'selected' : ''}>${tipo.Descripcion}</option>
                                `).join('')}
                            </select>
                        </td>
                        <td>
                            ${turno ? `
                                <div>Turno: ${turno.nombre}</div>
                                <div>Horario: ${turno.horario}</div>
                                <div>Descanso: ${turno.descanso}</div>
                            ` : 'No asignado'}
                        </td>
                        ${Array.from({ length: 10 }, (_, i) => `
                            <td>
                                <input type="checkbox" class="form-check-input comida-checkbox" data-proceso="${i + 1}" data-emp="${empleado.codigo_emp}" name="comida_proceso${i + 1}_${empleado.codigo_emp}" onchange="handleComidaCheckboxChange(event)">
                                <input type="hidden" name="comida_proceso${i + 1}_${empleado.codigo_emp}_hidden" value="off">
                                <label for="comida-checkbox">
                                    <img src="/static/icons/hora_comida.png" alt="Comida" style="width: 15px; height: 15px;">
                                </label>
                                <input type="time" class="form-control form-control-sm mb-2" name="inicio_proceso${i + 1}_${empleado.codigo_emp}" placeholder="Inicio" disabled step="60" onchange="ajustarHoraFin('${empleado.codigo_emp}', ${i + 1})">
                                <input type="time" class="form-control form-control-sm mb-2" name="fin_proceso${i + 1}_${empleado.codigo_emp}" placeholder="Fin" disabled step="60" onchange="calcularTotalHoras('${empleado.codigo_emp}', ${i + 1})">
                                <input type="text" class="form-control form-control-sm mb-2" name="total_proceso${i + 1}_${empleado.codigo_emp}" readonly>
                                <input type="checkbox" class="form-check-input delete-checkbox" data-proceso="${i + 1}" data-emp="${empleado.codigo_emp}" onchange="handleDeleteCheckboxChange(event)">
                                <label for="delete-checkbox">
                                    <img src="/static/icons/borrar.png" alt="Borrar Horas" style="width: 15px; height: 15px;">
                                </label>
                            </td>
                        `).join('')}
                        <td>
                            <input type="number" class="form-control form-control-sm mb-2" name="horas_extras_${empleado.codigo_emp}" step="0" onchange="calcularTotalHoras('${empleado.codigo_emp}')">
                        </td>
                        <td>
                            <input type="text" class="form-control form-control-sm input-large" name="total_${empleado.codigo_emp}" readonly>
                        </td>
                        <td>${empleado.codigo_emp}</td>
                    `;
                    empleadosTbody.appendChild(row);

                    // Aplicar color a los selectores de tipo de inasistencia
                    const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${empleado.codigo_emp}"]`);
                    if (tipoInasistenciaSelect) {
                        
                        applyColorClass(tipoInasistenciaSelect);
                    }
                });
                document.getElementById('tabla_empleados').style.display = 'block';
                actualizarResumenAsistencia(); // Llamar a la función para actualizar el resumen de asistencia

                // Actualizar el total de empleados
                var totalEmpleados = response.empleados.length;
                var totalEmpleadosElement = document.getElementById('total_empleados');
                totalEmpleadosElement.textContent = `Total de Empleados: ${totalEmpleados}`;
                totalEmpleadosElement.style.display = 'block';
            } else {
                console.error('No se encontró el cuerpo de la tabla de empleados.');
            }
        }
    };
    xhr.send();
}
    function validarHorasRegistradas() {
        const filasEmpleados = Array.from(document.querySelectorAll('#empleados_tbody tr')).filter(fila => fila.style.display !== 'none');
        const deptoSeleccionado = document.getElementById('depto_select').value;
        let valid = true;
        let mensajeAlerta = '';

        filasEmpleados.forEach(fila => {
            const deptoEmpleado = fila.getAttribute('data-depto');
            const codigoEmp = fila.dataset.codigo_emp;
            const tipoInasistencia = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`).value;
            const inasistencia = ['F', 'D', 'V', 'INC', 'S', 'B','R'].includes(tipoInasistencia);

            if (deptoEmpleado === deptoSeleccionado && !inasistencia) {
                let tieneHorasRegistradas = false;
                const horasRegistradas = new Set();
                const horarios = [];

                for (let i = 1; i <= 10; i++) {
                    const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);

                    if (procesoSelect && procesoSelect.value) {
                        const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                        const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);

                        if (inicio && fin && !inicio.disabled && !fin.disabled) {
                            if (!inicio.value || !fin.value) {
                                mensajeAlerta += `El empleado con código ${codigoEmp} tiene campos de inicio o fin vacíos en el proceso ${i}.\n`;
                                valid = false;
                            } else if (inicio.value === fin.value) {
                                mensajeAlerta += `El empleado con código ${codigoEmp} tiene la misma hora de inicio y fin en el proceso ${i}.\n`;
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

                horarios.sort((a, b) => a.inicio.localeCompare(b.inicio));
                for (let i = 0; i < horarios.length - 1; i++) {
                    if (horarios[i].fin > horarios[i + 1].inicio) {
                        mensajeAlerta += `El empleado con código ${codigoEmp} tiene horas solapadas entre los procesos.\n`;
                        valid = false;
                        break;
                    }
                }

                if (!tieneHorasRegistradas) {
                    mensajeAlerta += `El empleado con código ${codigoEmp} no tiene horas registradas en ningún proceso.\n`;
                    valid = false;
                }
            }
        });

        if (!valid) {
            showAlert(mensajeAlerta, 'danger');
        }

        return valid;
    }
    function handleCopyAllCheckboxChange(event) {
        const checkbox = event.target;
        const deptoActual = document.getElementById('depto_select').value; // Obtener el departamento seleccionado
        if (!deptoActual) {
            console.error('No se pudo encontrar el departamento seleccionado.');
            return;
        }
    
        const rows = document.querySelectorAll(`tr[data-depto="${deptoActual}"]`);
    
        let inicioValues = [];
        let finValues = [];
        let foundValidRow = false;
    
        // Buscar la primera fila con horas válidas
        for (let i = 1; i <= 10; i++) {
            for (let row of rows) {
                const codigoEmp = row.dataset.codigo_emp;
                const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
                const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : null;
    
                if (['ASI', 'RT', 'NI', 'P'].includes(tipoInasistencia)) {
                    const inicioInput = row.querySelector(`input[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const finInput = row.querySelector(`input[name="fin_proceso${i}_${codigoEmp}"]`);
                    const deleteCheckbox = row.querySelector(`.delete-checkbox[data-proceso="${i}"][data-emp="${codigoEmp}"]`);
    
                    if (inicioInput.value && finInput.value && (!deleteCheckbox || !deleteCheckbox.checked)) {
                        inicioValues[i - 1] = inicioInput.value;
                        finValues[i - 1] = finInput.value;
                        foundValidRow = true;
                        break;
                    }
                }
            }
        }
    
        if (!foundValidRow) {
            console.error('No se encontraron filas con horas válidas para copiar.');
            return;
        }
    
        // Procesar cada proceso individualmente
        for (let i = 1; i <= 10; i++) {
            const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
            if (!procesoSelect || !procesoSelect.value) {
                continue; // Saltar si el proceso no está seleccionado
            }
    
            let index = 0;
    
            function processNextRow() {
                if (index >= rows.length) {
                    return;
                }
    
                const row = rows[index];
                const codigoEmp = row.dataset.codigo_emp;
                const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
                const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : null;
    
                // Verificar si el checkbox delete-checkbox está marcado
                const deleteCheckbox = row.querySelector(`.delete-checkbox[data-proceso="${i}"][data-emp="${codigoEmp}"]`);
                if (deleteCheckbox && deleteCheckbox.checked) {
                    // No hacer nada si el checkbox de borrar está marcado
                } else if (tipoInasistencia === 'F' || tipoInasistencia === 'D') {
                    // No hacer nada si el tipo de inasistencia es 'F' o 'D'
                } else if (['ASI', 'RT', 'NI', 'P'].includes(tipoInasistencia)) {
                    const inicioInput = row.querySelector(`input[name="inicio_proceso${i}_${codigoEmp}"]`);
                    const finInput = row.querySelector(`input[name="fin_proceso${i}_${codigoEmp}"]`);
    
                    if (inicioInput && finInput && (!deleteCheckbox || !deleteCheckbox.checked)) {
                        // Habilitar los inputs antes de copiar los valores
                        inicioInput.disabled = false;
                        finInput.disabled = false;
    
                        // Copiar los valores de inicio y fin solo si están vacíos
                        if (!inicioInput.value && !finInput.value) {
                            if (inicioValues[i - 1] && finValues[i - 1]) {
                                inicioInput.value = inicioValues[i - 1];
                                finInput.value = finValues[i - 1];
    
                                // Llamar a las funciones de ajuste y cálculo si es necesario
                                ajustarHoraFin(codigoEmp, i);
                                calcularTotalHoras(codigoEmp, i);
                            } else {
                                console.log(`No se copian valores vacíos para el proceso ${i} del empleado ${codigoEmp}`);
                            }
                        }
                    }
                }
    
                index++;
                requestAnimationFrame(processNextRow);
            }
    
            requestAnimationFrame(processNextRow);
        }
    }
    function handleDeleteCheckboxChange(event) {
        const checkbox = event.target;
        const row = checkbox.closest('tr');
        const procesoNum = checkbox.dataset.proceso; // Obtener el número del proceso del dataset del checkbox
        const codigoEmp = checkbox.dataset.emp; // Obtener el código del empleado del dataset del checkbox
    
        guardarEstadoAnterior(codigoEmp); // Guardar el estado antes de realizar cambios
    
        const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
        const isDescanso = tipoInasistenciaSelect.value === 'D' || tipoInasistenciaSelect.value === 'F';
        const desbloquear = ['RT', 'NI', 'ASI','P'].includes(tipoInasistenciaSelect.value);
    
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
    
        // Verificar si el proceso está seleccionado
        const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
        if (!procesoSelect || !procesoSelect.value) {
            console.error(`El proceso ${procesoNum} no está seleccionado para el empleado ${codigoEmp}`);
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
        checkbox.disabled = !desbloquear;
    
        // Calcular y sumar horas después de cualquier cambio
        requestAnimationFrame(() => {
            calcularTotalHoras(codigoEmp, procesoNum);
            sumarHorasPorProceso();
        });
    }
function toggleProcesoInputs(procesoNum) {
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
    const selectedValue = procesoSelect.value;
    const deptoSeleccionado = deptoSelect.value;

    if (!deptoSeleccionado) {
        console.error('No se pudo encontrar el departamento seleccionado.');
        return;
    }

    const filasEmpleados = empleadosTbody.querySelectorAll('tr');
    filasEmpleados.forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;
        const deptoEmpleado = fila.getAttribute('data-depto');
        const tipoInasistenciaSelect = fila.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
        const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : '';

        if (deptoEmpleado === deptoSeleccionado && ['ASI', 'RT', 'NI','P'].includes(tipoInasistencia)) {
            const inicioInput = fila.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
            const finInput = fila.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
            const copyCheckbox = fila.querySelector(`.copy-checkbox[data-proceso="${procesoNum}"]`);
            const deleteCheckbox = fila.querySelector(`.delete-checkbox[data-proceso="${procesoNum}"]`);

            if (inicioInput && finInput) {
                const isEnabled = !!selectedValue;
                inicioInput.disabled = !isEnabled;
                finInput.disabled = !isEnabled;
                if (!isEnabled) {
                    inicioInput.value = '';
                    finInput.value = '';
                }
            } else {
                console.error(`No se encontraron los elementos de entrada para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
            }

            // Habilitar o deshabilitar los checkboxes de copiar y borrar
            if (copyCheckbox) {
                copyCheckbox.disabled = !selectedValue;
            }
            if (deleteCheckbox) {
                deleteCheckbox.disabled = !selectedValue;
            }
        }
    });
}//yaaa doom

function ajustarHoraFin(codigoEmp, procesoNum) {
    const inicioField = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const finField = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
    const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);

    // Verificar si el proceso está seleccionado
    if (!procesoSelect || !procesoSelect.value) {
        console.error(`El proceso ${procesoNum} no está seleccionado para el empleado ${codigoEmp}`);
        return;
    }

    if (!inicioField.value || finField.value) return; // No ajustar si el finField ya tiene un valor

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
    saveCurrentState(); // Guardar el estado después de ajustar la hora
}

// Variables globales
let totalHorasGlobal = 0;
let totalHorasExtrasGlobal = 0;

function calcularTotalHoras(codigoEmp, procesoNum) {
    const inicio = document.querySelector(`[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const fin = document.querySelector(`[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
    const totalField = document.querySelector(`[name="total_proceso${procesoNum}_${codigoEmp}"]`);
    const idTurno = document.querySelector(`tr[data-codigo_emp="${codigoEmp}"]`).dataset.id_turno; // Obtener el id_turno del dataset
    const diasSemana = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
    
    // Obtener la fecha seleccionada en el input de tipo date
    const fechaInput = document.getElementById('fecha').value;
    const fechaSeleccionada = new Date(fechaInput + 'T00:00:00'); // Asegurarse de que se tome la fecha correctamente
    const diaActual = diasSemana[fechaSeleccionada.getUTCDay()];

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

        // Descontar tiempo de comida si el checkbox está marcado
        const comidaCheckbox = document.querySelector(`.comida-checkbox[data-proceso="${procesoNum}"][data-emp="${codigoEmp}"]`);
        if (comidaCheckbox && comidaCheckbox.checked) {
            if (idTurno === "100" && (diaActual === 'viernes' || diaActual === 'sábado')) {
                diff -= 0.5; // Descontar 30 minutos
            } else {
                diff -= 0.75; // Descontar 45 minutos
            }
        } else {
            console.log(`Checkbox de comida no marcado para empleado ${codigoEmp}, proceso ${procesoNum}`);
        }

        totalField.value = diff.toFixed(2);
    } else {
        totalField.value = '';
    }

    // Calcular el total de horas para todos los procesos seleccionados
    let totalHoras = 0;
    document.querySelectorAll(`[name^="total_proceso"][name$="_${codigoEmp}"]`).forEach(totalProcesoField => {
        if (totalProcesoField && totalProcesoField.value) {
            totalHoras += parseFloat(totalProcesoField.value) || 0;
        }
    });

    // Agregar horas extras
    const horasExtrasField = document.querySelector(`[name="horas_extras_${codigoEmp}"]`);
    const horasExtras = parseFloat(horasExtrasField.value) || 0;
    totalHoras += horasExtras;

    document.querySelector(`[name="total_${codigoEmp}"]`).value = totalHoras.toFixed(2);

    // Llamar a sumarHorasPorProceso para actualizar los totales
    sumarHorasPorProceso();
    saveCurrentState(); // Guardar el estado después de calcular las horas
}
function sumarHorasPorProceso() {
    const totalHorasPorProceso = Array(10).fill(0);
    const deptoSeleccionado = document.getElementById('depto_select').value;

    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        const deptoEmpleado = fila.getAttribute('data-depto');
        const codigoEmp = fila.dataset.codigo_emp;
        const tipoInasistenciaSelect = fila.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
        const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : '';

        if (deptoEmpleado === deptoSeleccionado && !['F', 'D', 'V', 'INC', 'S', 'B'].includes(tipoInasistencia)) {
            for (let i = 1; i <= 10; i++) {
                const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
                if (procesoSelect && procesoSelect.value) {
                    const totalProceso = fila.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
                    if (totalProceso && totalProceso.value && !totalProceso.disabled) {
                        const totalProcesoValue = parseFloat(totalProceso.value) || 0;
                        totalHorasPorProceso[i - 1] += totalProcesoValue;
                    }
                }
            }
        }
    });

    totalHorasPorProceso.forEach((total, i) => {
        const totalProcesoField = document.querySelector(`#total_proceso${i + 1}`);
        const procesoSelect = document.querySelector(`[name="proceso${i + 1}_header"]`);
        if (totalProcesoField && procesoSelect && procesoSelect.value) {
            totalProcesoField.textContent = total.toFixed(2);
        }
    });
}
function handleComidaCheckboxChange(event) {
    const checkbox = event.target;
    const codigoEmp = checkbox.dataset.emp;
    const procesoNum = checkbox.dataset.proceso; // Obtener el número del proceso del dataset del checkbox

    guardarEstadoAnterior(codigoEmp); // Guardar el estado antes de realizar cambios

    // Deshabilitar todos los checkboxes de comida del mismo empleado excepto el que se seleccionó
    document.querySelectorAll(`.comida-checkbox[data-emp="${codigoEmp}"]`).forEach(cb => {
        if (cb !== checkbox) {
            cb.disabled = checkbox.checked;
        }
    });

    // Actualizar el valor del campo oculto correspondiente
    const hiddenField = document.querySelector(`[name="comida_proceso${procesoNum}_${codigoEmp}_hidden"]`);
    if (hiddenField) {
        hiddenField.value = checkbox.checked ? 'on' : 'off';
    }

    // Calcular las horas para el empleado y proceso específicos
    calcularTotalHoras(codigoEmp, procesoNum);
}
function buscarEmpleado() {
    const input = document.getElementById('search');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('tabla_empleados');
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) { // Empieza en 1 para saltar el encabezado
        const tdNoEmp = tr[i].getElementsByTagName('td')[1];
        const tdNombre = tr[i].getElementsByTagName('td')[2];
        if (tdNoEmp || tdNombre) {
            const txtValueNoEmp = tdNoEmp.textContent || tdNoEmp.innerText;
            const txtValueNombre = tdNombre.textContent || tdNombre.innerText;
            if (txtValueNoEmp.toLowerCase().indexOf(filter) > -1 || txtValueNombre.toLowerCase().indexOf(filter) > -1) {
                tr[i].style.display = '';
            } else {
                tr[i].style.display = 'none';
            }
        }
    }
}
let stateStack = [];
const MAX_STACK_SIZE = 50; // Limitar el tamaño de stateStack


function guardarEstadoAnterior(codigoEmp) {
    const form = document.getElementById('horas-procesos-form');
    const inputs = form.querySelectorAll(`input[name*="_${codigoEmp}"]`);
    let currentState = {};
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            currentState[input.name] = input.checked;
        } else {
            currentState[input.name] = input.value;
        }
    });

    // Comparar el estado actual con el último estado guardado
    if (stateStack.length === 0 || JSON.stringify(currentState) !== JSON.stringify(stateStack[stateStack.length - 1])) {
        stateStack.push(JSON.parse(JSON.stringify(currentState))); // Deep copy to avoid reference issues
        if (stateStack.length > MAX_STACK_SIZE) {
            stateStack.shift(); // Eliminar el estado más antiguo si se supera el tamaño máximo
        }
        
    } else {
        console.log('No hay cambios, no se guarda el estado.');
    }
}

function saveCurrentState() {
    const form = document.getElementById('horas-procesos-form');
    const inputs = form.querySelectorAll('input[type="time"], input[type="checkbox"].comida-checkbox, input[type="checkbox"].delete-checkbox, input[type="text"]');
    let currentState = {};
    inputs.forEach(input => {
        if (input.id !== 'search') { // Excluir el campo de búsqueda
            if (input.type === 'checkbox') {
                currentState[input.name] = input.checked;
            } else {
                currentState[input.name] = input.value;
            }
        }
    });

    // Comparar el estado actual con el último estado guardado
    if (stateStack.length === 0 || JSON.stringify(currentState) !== JSON.stringify(stateStack[stateStack.length - 1])) {
        stateStack.push(JSON.parse(JSON.stringify(currentState))); // Deep copy to avoid reference issues
        if (stateStack.length > MAX_STACK_SIZE) {
            stateStack.shift(); // Eliminar el estado más antiguo si se supera el tamaño máximo
        }
        
    } else {
        console.log('No hay cambios, no se guarda el estado.');
    }
}

function restorePreviousState() {
    if (stateStack.length > 0) {
        
        const previousState = stateStack.pop();
        const form = document.getElementById('horas-procesos-form');
        const inputs = form.querySelectorAll('input[type="time"], input[type="checkbox"].comida-checkbox, input[type="checkbox"].delete-checkbox, input[type="text"]');
        
        inputs.forEach(input => {
            if (input.id !== 'search' && previousState.hasOwnProperty(input.name)) { // Excluir el campo de búsqueda
                const deleteCheckbox = form.querySelector(`input[type="checkbox"].delete-checkbox[data-proceso="${input.dataset.proceso}"][data-emp="${input.dataset.emp}"]`);
                if (deleteCheckbox && deleteCheckbox.checked) {
                    // No restaurar el estado si el checkbox de borrar está marcado
                    
                } else {
                    if (input.type === 'checkbox') {
                        input.checked = previousState[input.name];
                    } else {
                        input.value = previousState[input.name];
                    }
                }
            }
        });

        // Rehabilitar los campos deshabilitados por los checkboxes de borrar
        const deleteCheckboxes = form.querySelectorAll('input[type="checkbox"].delete-checkbox');
        deleteCheckboxes.forEach(checkbox => {
            const row = checkbox.closest('tr');
            const procesoNum = checkbox.dataset.proceso;
            const codigoEmp = checkbox.dataset.emp;
            const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
            const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : '';

            if (!['F', 'D', 'V', 'INC', 'S', 'B'].includes(tipoInasistencia)) {
                const inputs = row.querySelectorAll(`input[name="inicio_proceso${procesoNum}_${codigoEmp}"], input[name="fin_proceso${procesoNum}_${codigoEmp}"], input[name="total_proceso${procesoNum}_${codigoEmp}"]`);
                const procesoSelect = document.querySelector(`[name="proceso${procesoNum}_header"]`);
                if (procesoSelect && procesoSelect.value && !previousState[checkbox.name]) {
                    // Verificar si hay algún otro checkbox de borrar marcado
                    const otherDeleteCheckboxes = form.querySelectorAll(`input[type="checkbox"].delete-checkbox[data-emp="${codigoEmp}"]:checked`);
                    if (otherDeleteCheckboxes.length === 0) {
                        inputs.forEach(input => {
                            input.disabled = false;
                        });
                    }
                }
            }
        });

        // Recalcular los totales después de restaurar el estado
        console.log('Recalculando totales...');
        recalcularTotales();
    } else {
        console.log('No hay estados anteriores para restaurar.');
    }
}
function recalcularTotales() {
   
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    const totalHorasPorProceso = Array(10).fill(0);

    filasEmpleados.forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;

        for (let i = 1; i <= 10; i++) {
            const totalProceso = fila.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
            if (totalProceso && totalProceso.value && !totalProceso.disabled) {
                const totalProcesoValue = parseFloat(totalProceso.value) || 0;
                totalHorasPorProceso[i - 1] += totalProcesoValue;
                console.log(`Sumando ${totalProcesoValue} horas al proceso ${i} para el empleado ${codigoEmp}`);
            }
        }
    });

    totalHorasPorProceso.forEach((total, i) => {
        const totalProcesoField = document.querySelector(`#total_proceso${i + 1}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = total.toFixed(2);
            
        }
    });
}

function deshacerCambio() {
    
    restorePreviousState();
}

document.addEventListener('DOMContentLoaded', function() {
    
    saveCurrentState();
    const form = document.getElementById('horas-procesos-form');
    const inputs = form.querySelectorAll('input[type="time"], input[type="checkbox"].comida-checkbox, input[type="checkbox"].delete-checkbox');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            saveCurrentState();
        });
    });
});

function recalcularTotales() {
    
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    const totalHorasPorProceso = Array(10).fill(0);

    filasEmpleados.forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;

        for (let i = 1; i <= 10; i++) {
            const totalProceso = fila.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
            if (totalProceso && totalProceso.value && !totalProceso.disabled) {
                const totalProcesoValue = parseFloat(totalProceso.value) || 0;
                totalHorasPorProceso[i - 1] += totalProcesoValue;
                
            }
        }
    });

    totalHorasPorProceso.forEach((total, i) => {
        const totalProcesoField = document.querySelector(`#total_proceso${i + 1}`);
        if (totalProcesoField) {
            totalProcesoField.textContent = total.toFixed(2);
            
        }
    });
}

function deshacerCambio() {
    
    restorePreviousState();
}

document.addEventListener('DOMContentLoaded', function() {
    
    saveCurrentState();
    const form = document.getElementById('horas-procesos-form');
    const inputs = form.querySelectorAll('input[type="time"], input[type="checkbox"].comida-checkbox, input[type="checkbox"].delete-checkbox');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            saveCurrentState();
        });
    });
});

function applyColorClass(selectElement) {
    const value = selectElement.value;
   
    selectElement.classList.remove('falta', 'asistencia', 'permiso', 'descanso', 'retardo', 'vacaciones', 'suspension', 'baja', 'renuncia', 'nuevo_ingreso');
    
    switch (value) {
        case 'F':
            selectElement.classList.add('falta');
           
            break;
        case 'ASI':
            selectElement.classList.add('asistencia');
            
            break;
        case 'P':
            selectElement.classList.add('permiso');
            
            break;
        case 'D':
            selectElement.classList.add('descanso');
            
            break;
        case 'RT':
            selectElement.classList.add('retardo');
            
            break;
        case 'V':
            selectElement.classList.add('vacaciones');
    
            break;
        case 'S':
            selectElement.classList.add('suspension');
            
            break;
        case 'B':
            selectElement.classList.add('baja');
            
            break;
        case 'R':
            selectElement.classList.add('renuncia');
            
            break;
        case 'NI':
            selectElement.classList.add('nuevo_ingreso');
            
            break;
        case 'INC':
            selectElement.classList.add('incapacidad');
            
            break;
        default:
            
            break;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Documento cargado, aplicando colores a los selectores de tipo de inasistencia'); // Log para verificar que el DOM está cargado
    document.querySelectorAll('select[name^="tipo_inasistencia_"]').forEach(select => {
        applyColorClass(select);
        select.addEventListener('change', function() {
            console.log(`Cambio detectado en el selector: ${select.name}`); // Log para verificar el cambio en el selector
            applyColorClass(select);
        });
    });
});
function handleDeleteHeaderCheckboxChange(event) {
    const checkbox = event.target;
    const proceso = checkbox.getAttribute('data-proceso');
    const checkboxes = document.querySelectorAll(`.delete-checkbox[data-proceso="${proceso}"]`);
    let index = 0;

    function processNextCheckbox() {
        if (index >= checkboxes.length) {
            return;
        }

        const cb = checkboxes[index];
        const emp = cb.getAttribute('data-emp');
        const inicioInput = document.querySelector(`input[name="inicio_proceso${proceso}_${emp}"]`);
        const finInput = document.querySelector(`input[name="fin_proceso${proceso}_${emp}"]`);

        if (!inicioInput.value && !finInput.value && !inicioInput.disabled && !finInput.disabled) {
            cb.checked = checkbox.checked;
            // Crear un evento de cambio y dispararlo en el checkbox
            const changeEvent = new Event('change');
            cb.dispatchEvent(changeEvent);
        }

        index++;
        requestAnimationFrame(processNextCheckbox);
    }

    requestAnimationFrame(processNextCheckbox);
}