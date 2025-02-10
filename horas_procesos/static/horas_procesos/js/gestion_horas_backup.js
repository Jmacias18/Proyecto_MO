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
        filtrarEmpleados();
        restablecerSelectores(); // Restablecer los selectores de proceso y producto
        // Mostrar el checkbox y la etiqueta cuando se seleccione un departamento
        if (deptoSelect.value) {
            copyAllCheckbox.style.display = 'inline-block';
            copyAllLabel.style.display = 'inline-block';
        } else {
            copyAllCheckbox.style.display = 'none';
            copyAllLabel.style.display = 'none';
        }
    });

    // Manejar envío del formulario
    /* form.addEventListener('submit', (event) => {
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
    }); */

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
    document.addEventListener('DOMContentLoaded', initGlobals);
    document.getElementById('depto_select').addEventListener('change', initGlobals);

    /* // Verificar los valores de tipo_inasistencia en el DOM
    document.querySelectorAll('select[name^="tipo_inasistencia_"]').forEach(select => {
        const codigoEmp = select.name.split('_')[1];
        console.log(`Empleado ${codigoEmp} - Tipo de inasistencia: ${select.value}`);
    }); */
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
/* function actualizarHoraComida(procesoNum, codigoEmp) {
    const checkbox = document.querySelector(`input[name="hora_comida_proceso${procesoNum}_${codigoEmp}"]`);
    const inicio = document.querySelector(`input[name="inicio_proceso${procesoNum}_${codigoEmp}"]`);
    const fin = document.querySelector(`input[name="fin_proceso${procesoNum}_${codigoEmp}"]`);
    const totalField = document.querySelector(`input[name="total_proceso${procesoNum}_${codigoEmp}"]`);

    if (!checkbox || !inicio || !fin || !totalField) {
        console.error(`No se encontraron los elementos de entrada para el proceso ${procesoNum} y el empleado ${codigoEmp}`);
        return;
    }

    let diff = 0;
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

        diff = (finDate - inicioDate) / (1000 * 60 * 60);
        if (diff < 0) diff += 24;

        // Restar 45 minutos si el checkbox de hora de comida está marcado
        if (checkbox.checked) {
            diff -= 0.75; // 45 minutos en horas
        }
    }

    totalField.value = diff.toFixed(2);

    // Calcular el total de horas para todos los procesos seleccionados
    requestAnimationFrame(() => {
        calcularTotalHoras(codigoEmp, procesoNum);
        sumarHorasPorProceso();
    });
}//yaaa doom */
let empleadosTbody;

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

    /* function prepararDatosParaEnvio() {
        const datos = {
            departamento: document.getElementById('depto_select').value,
            empleados: []
        };
        const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    
        // Array para registrar los recorridos
        const recorridos = [];
    
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
                            recorridos.push(`Procesando proceso ${i} para el empleado ${codigoEmp}`);
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
                recorridos.push(`Agregando datos del empleado ${codigoEmp}`);
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
    
        // Imprimir el array de recorridos en la consola
        console.log('Recorridos:prepararDatosParaEnvio', recorridos);
    }//yaaa */




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

    function validarHorasInicioFinIguales() {
        const filasEmpleados = Array.from(document.querySelectorAll('#empleados_tbody tr')).filter(fila => fila.style.display !== 'none');
        let valid = true;
        let mensajesAlerta = [];
        const recorridos = [];
    
        filasEmpleados.forEach(fila => {
            const codigoEmp = fila.dataset.codigo_emp;
            const tipoInasistenciaElement = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
            const tipoInasistencia = tipoInasistenciaElement ? tipoInasistenciaElement.value : '';
    
            if (['ASI', 'RT', 'NI'].includes(tipoInasistencia)) {
                let tieneProcesoSeleccionado = false;
                let totalHoras = 0;
    
                for (let i = 1; i <= 10; i++) {
                    const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
                    if (procesoSelect && procesoSelect.value) {
                        tieneProcesoSeleccionado = true;
                        break;
                    }
                }
    
                if (tieneProcesoSeleccionado) {
                    for (let i = 1; i <= 10; i++) {
                        const procesoSelect = document.querySelector(`[name="proceso${i}_header"]`);
                        if (procesoSelect && procesoSelect.value) {
                            const inicio = document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`);
                            const fin = document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`);
                            const total = document.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
    
                            if (inicio && fin && !inicio.disabled && !fin.disabled) {
                                if (inicio.value === fin.value && inicio.value) {
                                    mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene horas de inicio y fin iguales en el proceso ${i}.`);
                                    valid = false;
                                }
    
                                if (total && total.value) {
                                    totalHoras += parseFloat(total.value) || 0;
                                    recorridos.push(`Empleado ${codigoEmp} - Proceso ${i} - Total: ${total.value}`);
                                }
                            }
                        }
                    }
    
                    const horasExtrasField = document.querySelector(`[name="horas_extras_${codigoEmp}"]`);
                    const horasExtras = parseFloat(horasExtrasField.value) || 0;
                    totalHoras += horasExtras;
    
                    if (totalHoras === 12) {
                        totalHoras -= 0.75;
                    } else if (totalHoras === 8) {
                        totalHoras -= 0.5;
                    }
    
                    if (totalHoras > 12) {
                        totalHoras = 12;
                    }
    
                    if (totalHoras < 11.25) {
                        mensajesAlerta.push(`El empleado con código ${codigoEmp} tiene menos de 12 horas trabajadas.`);
                        valid = false;
                    }
                }
            }
        });
    
        if (!valid) {
            showAlert(mensajesAlerta.join('\n'), 'danger');
        }
    
        console.log('Recorridos: validarHorasInicioFinIguales', recorridos);
        return valid;
    }//yaaa doom
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
    const deptoSeleccionado = deptoSelect.value;
    const filasEmpleados = empleadosTbody.querySelectorAll('tr');
    let contador = 1;
    let totalEmpleados = 0;

    if (deptoSeleccionado === "") {
        tablaEmpleados.style.display = 'none';
        totalEmpleadosElement.style.display = 'none';
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

    totalEmpleadosElement.textContent = `Total de Empleados: ${totalEmpleados}`;
    totalEmpleadosElement.style.display = 'block';
    tablaEmpleados.style.display = totalEmpleados > 0 ? 'block' : 'none';
}//yaaa doom

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
} */
 
    function validarHorasRegistradas() {
        const filasEmpleados = Array.from(document.querySelectorAll('#empleados_tbody tr')).filter(fila => fila.style.display !== 'none');
        const deptoSeleccionado = document.getElementById('depto_select').value;
        let valid = true;
        let mensajeAlerta = '';
        const recorridos = [];
    
        filasEmpleados.forEach(fila => {
            const deptoEmpleado = fila.getAttribute('data-depto');
            const codigoEmp = fila.dataset.codigo_emp;
            const tipoInasistencia = document.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`).value;
            const inasistencia = ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R'].includes(tipoInasistencia);
    
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
                            } else {
                                tieneHorasRegistradas = true;
                                const horas = `${inicio.value}-${fin.value}`;
                                if (horasRegistradas.has(horas)) {
                                    mensajeAlerta += `El empleado con código ${codigoEmp} tiene horas de inicio y fin idénticas en más de un proceso.\n`;
                                    valid = false;
                                } else {
                                    horasRegistradas.add(horas);
                                    horarios.push({ inicio: inicio.value, fin: fin.value });
                                    recorridos.push(`Empleado ${codigoEmp} - Proceso ${i} - Inicio: ${inicio.value}, Fin: ${fin.value}`);
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
    
        console.log('Recorridos: validarHorasRegistradas', recorridos);
        return valid;
    }
/* function verificarHorasDuplicadas(codigoEmp) {
    let mensaje = '';
    const horasRegistradas = new Set();

    // Seleccionar todos los campos de inicio y fin de proceso para el empleado
    const inicioCampos = [];
    const finCampos = [];
    for (let i = 1; i <= 10; i++) {
        inicioCampos.push(document.querySelector(`[name="inicio_proceso${i}_${codigoEmp}"]`));
        finCampos.push(document.querySelector(`[name="fin_proceso${i}_${codigoEmp}"]`));
    }

    for (let i = 0; i < 10; i++) {
        const inicio = inicioCampos[i];
        const fin = finCampos[i];

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
}//yaaa doom */
/* function handleCheckboxChange(event) {
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
            const prevInicioInput = prevRow.querySelector(`input[name="inicio_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`);
            const prevFinInput = prevRow.querySelector(`input[name="fin_proceso${proceso}_${prevRow.dataset.codigo_emp}"]`);

            if (prevInicioInput && prevFinInput) {
                const prevInicio = prevInicioInput.value;
                const prevFin = prevFinInput.value;

                // Guardar los valores originales
                inicioInput.dataset.originalValue = inicioInput.value;
                finInput.dataset.originalValue = finInput.value;

                // Copiar los valores de la fila anterior
                inicioInput.value = prevInicio;
                finInput.value = prevFin;
            }
        } else {
            console.warn(`No se encontró una fila anterior con el proceso ${proceso} para el empleado ${emp}`);
        }
    } else {
        // Restaurar los valores originales
        inicioInput.value = inicioInput.dataset.originalValue || '';
        finInput.value = finInput.dataset.originalValue || '';
    }

    // Habilitar o deshabilitar los checkboxes de copiar y borrar
    checkbox.disabled = !desbloquear;

    // Calcular y sumar horas después de cualquier cambio
    requestAnimationFrame(() => {
        calcularTotalHoras(emp, proceso);
        sumarHorasPorProceso();
    });
}//yaaa doom
function getPreviousRowWithProceso(currentRow, proceso) {
    const deptoActual = currentRow.getAttribute('data-depto');
    let prevRow = currentRow.previousElementSibling;

    while (prevRow) {
        const codigoEmp = prevRow.dataset.codigo_emp;
        const prevInicioInput = prevRow.querySelector(`input[name="inicio_proceso${proceso}_${codigoEmp}"]`);
        const prevFinInput = prevRow.querySelector(`input[name="fin_proceso${proceso}_${codigoEmp}"]`);

        if (prevRow.getAttribute('data-depto') === deptoActual && prevRow.style.display !== 'none' && prevInicioInput && prevFinInput && prevInicioInput.value && prevFinInput.value) {
            return prevRow;
        }
        prevRow = prevRow.previousElementSibling;
    }

    return null;
}//yaaa doom */

function handleCopyAllCheckboxChange(event) {
    const checkbox = event.target;
    const deptoActual = document.getElementById('depto_select').value; // Obtener el departamento seleccionado
    if (!deptoActual) {
        console.error('No se pudo encontrar el departamento seleccionado.');
        return;
    }
    console.log(`Departamento seleccionado: ${deptoActual}`);
    
    const rows = document.querySelectorAll(`tr[data-depto="${deptoActual}"]`);
    console.log(`Número de filas encontradas: ${rows.length}`);
    
    let inicioValues = [];
    let finValues = [];

    // Guardar los valores de inicio y fin del primer empleado
    const firstRow = rows[0];
    const firstInicioInputs = firstRow.querySelectorAll(`input[name^="inicio_proceso"]`);
    const firstFinInputs = firstRow.querySelectorAll(`input[name^="fin_proceso"]`);
    firstInicioInputs.forEach((input, i) => {
        inicioValues[i] = input.value;
    });
    firstFinInputs.forEach((input, i) => {
        finValues[i] = input.value;
    });

    let index = 1;

    function processNextRow() {
        if (index >= rows.length) {
            return;
        }

        const row = rows[index];
        const codigoEmp = row.dataset.codigo_emp;
        const tipoInasistenciaSelect = row.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
        const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : null;

        if (tipoInasistencia === 'F' || tipoInasistencia === 'D') {
            console.log(`Empleado ${codigoEmp} tiene tipo de inasistencia ${tipoInasistencia}. No se desbloquearán los campos ni se asignarán horas.`);
        } else {
            const inicioInputs = row.querySelectorAll(`input[name^="inicio_proceso"]`);
            const finInputs = row.querySelectorAll(`input[name^="fin_proceso"]`);

            inicioInputs.forEach((inicioInput, i) => {
                const finInput = finInputs[i];
                const procesoSelect = document.querySelector(`[name="proceso${i + 1}_header"]`);

                if (procesoSelect && procesoSelect.value) {
                    // Habilitar los inputs antes de copiar los valores
                    inicioInput.disabled = false;
                    finInput.disabled = false;

                    // Copiar los valores de inicio y fin al resto de los empleados
                    inicioInput.value = inicioValues[i];
                    finInput.value = finValues[i];
                    console.log(`Copiando valores - Inicio: ${inicioValues[i]}, Fin: ${finValues[i]} para empleado ${codigoEmp}`);

                    // Llamar a las funciones de ajuste y cálculo si es necesario
                    ajustarHoraFin(codigoEmp, i + 1);
                    calcularTotalHoras(codigoEmp, i + 1);
                }
            });
        }

        index++;
        requestAnimationFrame(processNextRow);
    }

    requestAnimationFrame(processNextRow);
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
    checkbox.disabled = !desbloquear;

    // Calcular y sumar horas después de cualquier cambio
    requestAnimationFrame(() => {
        calcularTotalHoras(codigoEmp, procesoNum);
        sumarHorasPorProceso();
    });
}//yaaa doom
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

        if (deptoEmpleado === deptoSeleccionado && ['ASI', 'RT', 'NI'].includes(tipoInasistencia)) {
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
}
// Variables globales
let totalHorasGlobal = 0;
let totalHorasExtrasGlobal = 0;



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

    // Descontar tiempo de comida solo si el total de horas es exactamente 12 o 8
    if (totalHoras === 12) {
        totalHoras -= 0.75; // Descontar 45 minutos
    } else if (totalHoras === 8) {
        totalHoras -= 0.5; // Descontar 30 minutos
    }

    // Limitar el total de horas a 12
    if (totalHoras > 12) {
        totalHoras = 12;
    }

    document.querySelector(`[name="total_${codigoEmp}"]`).value = totalHoras.toFixed(2);

    // Llamar a sumarHorasPorProceso para actualizar los totales
    sumarHorasPorProceso();
}
function sumarHorasPorProceso() {
    const totalHorasPorProceso = Array(10).fill(0);
    const deptoSeleccionado = document.getElementById('depto_select').value;

    document.querySelectorAll('#empleados_tbody tr').forEach(fila => {
        const deptoEmpleado = fila.getAttribute('data-depto');
        const codigoEmp = fila.dataset.codigo_emp;
        const tipoInasistenciaSelect = fila.querySelector(`select[name="tipo_inasistencia_${codigoEmp}"]`);
        const tipoInasistencia = tipoInasistenciaSelect ? tipoInasistenciaSelect.value : '';

        if (deptoEmpleado === deptoSeleccionado && !['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R'].includes(tipoInasistencia)) {
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

/* function validarHorasTotales() {
    const filasEmpleados = document.querySelectorAll('#empleados_tbody tr');
    let mensajeAlerta = '';

    filasEmpleados.forEach(fila => {
        const codigoEmp = fila.dataset.codigo_emp;
        let totalHoras = 0;

        for (let i = 1; i <= 10; i++) {
            const totalProcesoField = fila.querySelector(`[name="total_proceso${i}_${codigoEmp}"]`);
            if (totalProcesoField && totalProcesoField.value) {
                totalHoras += parseFloat(totalProcesoField.value) || 0;
            }
        }

        const horasExtrasField = fila.querySelector(`[name="horas_extras_${codigoEmp}"]`);
        const horasExtras = parseFloat(horasExtrasField.value) || 0;
        totalHoras += horasExtras;

        if (totalHoras < 12) {
            mensajeAlerta += `El empleado con código ${codigoEmp} tiene menos de 12 horas registradas.\n`;
        }
    });

    if (mensajeAlerta) {
        showAlert(mensajeAlerta, 'danger');
        return false;
    }

    return true;
} */
