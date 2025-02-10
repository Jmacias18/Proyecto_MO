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
document.addEventListener('DOMContentLoaded', function() {
    const guardarBtn = document.getElementById('guardar-btn');
    const form = document.getElementById('form-actualizar');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    guardarBtn.addEventListener('click', function(event) {
        event.preventDefault();

        if (!form.checkValidity()) {
            Swal.fire({
                icon: 'error',
                title: 'Formulario no válido',
                text: 'Por favor completa todos los campos requeridos.'
            });
            return;
        }

        Swal.fire({
            title: '¿Estás seguro?',
            text: "¿Deseas enviar el formulario?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, enviar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                const formData = new FormData(form);
                const jsonData = {};
                formData.forEach((value, key) => {
                    jsonData[key] = value;
                });

                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(jsonData)
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errData => {
                            throw new Error(errData.message || 'Error en el servidor');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Se envió correctamente.',
                            timer: 2000,
                            showConfirmButton: false
                        });
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
                        text: `Error al enviar el formulario: ${error.message}`
                    });
                });
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/horas_procesos/actualizar_horas_procesos/')) {
        const navbar = document.querySelector('.navbar-nav.ms-auto');
        const logoutButton = navbar.querySelector('form[action="/accounts/logout/"]').closest('li');
        const syncButton = document.createElement('li');
        syncButton.className = 'nav-item';
        syncButton.innerHTML = `
            <button id="sync-to-server-button" class="nav-link btn btn-link" style="padding: 0;">Sincronizar Procesos</button>
        `;
        navbar.insertBefore(syncButton, logoutButton);

        document.getElementById('sync-to-server-button').addEventListener('click', function(event) {
            event.preventDefault();  // Evitar el comportamiento predeterminado del botón
            fetch("{% url 'horas_procesos:sync_to_server' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error durante la sincronización.');
            });
        });
    }
    // Configurar todos los campos como solo lectura al cargar la página, excepto los campos de selección de departamento y filtrado por fecha
    document.querySelectorAll('input, select').forEach(input => {
        if (input.name !== 'departamento' && input.name !== 'fecha') {
            input.setAttribute('readonly', true);
            input.setAttribute('disabled', true);
        }
    });

    // Agregar evento al botón "Editar"
    document.getElementById('editar-btn').addEventListener('click', () => {
        document.querySelectorAll('input, select').forEach(input => {
            if (input.name !== 'departamento' && input.name !== 'fecha') {
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
            }
        });
        document.getElementById('guardar-btn').removeAttribute('disabled');
    });

   

    document.querySelectorAll('input[name^="horaentrada_"], input[name^="horasalida_"], input[name^="hrsextras_"], select[name^="proceso_"]').forEach(input => {
        input.setAttribute('data-original-value', input.value);
        input.addEventListener('change', (event) => {
            const id = event.target.name.split('_')[1];
            if (event.target.tagName.toLowerCase() === 'select') {
                actualizarProceso(id);
            } else {
                validarHoras(id);
                actualizarHoras(id);
            }
            actualizarTotalHoras();
        });
    });

    // Agregar evento change a los checkboxes de inasistencia
    document.querySelectorAll('input[name^="inasistencia_"]').forEach(input => {
        input.addEventListener('change', (event) => {
            const id = event.target.name.split('_')[1];
            const codigoEmp = document.querySelector(`tr[data-id="${id}"]`).dataset.codigoEmp;
            toggleInasistencia(id, codigoEmp);

            // Mostrar el modal de confirmación cuando se marca una inasistencia
            const mensaje = `Se marcará la inasistencia para el empleado ${codigoEmp}. ¿Deseas continuar?`;
            document.getElementById('confirmMessage').textContent = mensaje;
            const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
            confirmModal.show();

            document.getElementById('confirmSubmit').addEventListener('click', () => {
                document.getElementById('form-actualizar').submit();
            });
        });
    });

    document.getElementById('guardar-btn').addEventListener('click', (event) => {
        let valid = true;
        document.querySelectorAll('input[name^="horaentrada_"], input[name^="horasalida_"]').forEach(input => {
            const id = input.name.split('_')[1];
            const inasistencia = document.querySelector(`input[name="inasistencia_${id}"]`).checked;
            if (!inasistencia && !validarHoras(id)) {
                valid = false;
            }
        });

        if (!valid) {
            showAlert('Corrige los errores antes de guardar.', 'danger');
            return;
        }

        const { cambios, borrados } = contarCambiosYBorrados();
        const mensaje = `Se realizaron ${cambios} cambios y se eliminarán ${borrados} registros. ¿Deseas continuar?`;
        document.getElementById('confirmMessage').textContent = mensaje;
        const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
        confirmModal.show();

        document.getElementById('confirmSubmit').addEventListener('click', () => {
            // Asegurarse de que todos los procesos tengan el valor de TotalHrs antes de enviar el formulario
            document.querySelectorAll('input[name^="totalhrs_"]').forEach(input => {
                const codigoEmp = input.name.split('_')[1];
                const totalHrs = document.querySelector(`input[name="totalhrs_${codigoEmp}"]`).value;
                document.querySelectorAll(`tr[data-codigo-emp="${codigoEmp}"] input[name^="totalhrs_"]`).forEach(procesoInput => {
                    procesoInput.value = totalHrs;
                });
            });

            document.querySelectorAll('input[type="time"]').forEach(input => {
                if (input.value === '') {
                    input.value = '00:00:00.0000000';
                }
            });

            document.getElementById('form-actualizar').submit();
        });
    });

    // Llamar a actualizarTotalHoras al cargar la página
    actualizarTotalHoras();
});

const validarHoras = (id) => {
    const entrada = document.querySelector(`input[name="horaentrada_${id}"]`).value;
    const salida = document.querySelector(`input[name="horasalida_${id}"]`).value;

    const inasistencia = document.querySelector(`input[name="inasistencia_${id}"]`).checked;
    if (inasistencia) {
        return true; // Saltar validación si está marcado como inasistencia
    }

    if (!entrada || !salida) {
        showAlert('Faltan datos de hora.', 'danger');
        return false;
    }

    const [horaEntrada, minutoEntrada] = entrada.split(':').map(Number);
    const [horaSalida, minutoSalida] = salida.split(':').map(Number);

    const inicio = new Date(0, 0, 0, horaEntrada, minutoEntrada);
    const fin = new Date(0, 0, 0, horaSalida, minutoSalida);
    let diferencia = (fin - inicio) / 1000 / 60 / 60;

    if (diferencia < 0) {
        diferencia += 24;
    }

    if (diferencia >= 14) {
        showAlert('La diferencia entre la hora de entrada y la hora de salida no puede ser igual o superior a 14 horas.', 'danger');
        document.querySelector(`input[name="horasalida_${id}"]`).value = '';
        return false;
    }

    if (entrada === salida) {
        showAlert('La hora de entrada y la hora de salida no pueden ser iguales.', 'danger');
        document.querySelector(`input[name="horasalida_${id}"]`).value = '';
        return false;
    }

    return true;
};
const actualizarTotalHoras = () => {
    try {
        const totalHorasPorEmpleado = {};
        const totalHorasPorProceso = {};

        // Sumar las horas de todos los procesos por empleado
        document.querySelectorAll('input[name^="hrs_"]').forEach(input => {
            const id = input.name.split('_')[1];
            const row = document.querySelector(`tr[data-id="${id}"]`);
            if (!row) {
                console.error(`Fila con data-id="${id}" no encontrada`);
                return;
            }
            const codigoEmp = row.dataset.codigoEmp;
            const proceso = document.querySelector(`select[name="proceso_${id}"]`).selectedOptions[0].textContent;
            const horas = parseFloat(input.value) || 0;

            if (!totalHorasPorEmpleado[codigoEmp]) {
                totalHorasPorEmpleado[codigoEmp] = 0;
            }

            if (!totalHorasPorProceso[proceso]) {
                totalHorasPorProceso[proceso] = 0;
            }

            totalHorasPorEmpleado[codigoEmp] += horas;
            totalHorasPorProceso[proceso] += horas;
        });

        // Asignar el valor de TotalHrs a todos los procesos del empleado
        document.querySelectorAll('input[name^="totalhrs_"]').forEach(input => {
            const id = input.name.split('_')[1];
            const codigoEmp = document.querySelector(`tr[data-id="${id}"]`).dataset.codigoEmp;
            input.value = totalHorasPorEmpleado[codigoEmp].toFixed(2);
        });

        // Mostrar el detalle de horas por proceso
        const detalleProcesos = Object.entries(totalHorasPorProceso)
            .map(([proceso, horas]) => `<td>${proceso}: ${horas.toFixed(2)} horas</td>`)
            .join('');
        document.getElementById('detalle_procesos_container').innerHTML = `<table><tr>${detalleProcesos}</tr></table>`;

        // Actualizar el total de horas de todos los empleados
        const total = Object.values(totalHorasPorEmpleado).reduce((sum, value) => sum + value, 0);
        document.getElementById('total_proceso').textContent = total.toFixed(2);

    } catch (error) {
        console.error("Error actualizando el total de horas:", error);
    }
};





const contarCambiosYBorrados = () => {
    let cambios = 0;
    let borrados = 0;

    document.querySelectorAll('input[name^="horaentrada_"], input[name^="horasalida_"], select[name^="proceso_"], input[name^="inasistencia_"]').forEach(input => {
        const originalValue = input.getAttribute('data-original-value');
        if (input.type === 'checkbox') {
            if (input.checked.toString() !== originalValue) {
                cambios++;
            }
        } else {
            if (input.value !== originalValue) {
                cambios++;
            }
        }
    });

    document.querySelectorAll('.eliminar-checkbox:checked').forEach(checkbox => {
        borrados++;
    });

    return { cambios, borrados };
};

const actualizarHoras = (id) => {
    try {
        const entrada = document.querySelector(`input[name="horaentrada_${id}"]`).value;
        const salida = document.querySelector(`input[name="horasalida_${id}"]`).value;

        if (!entrada || !salida) {
            console.warn(`Faltan datos de hora en el proceso ${id}.`);
            return;
        }

        const [horaEntrada, minutoEntrada] = entrada.split(':').map(Number);
        const [horaSalida, minutoSalida] = salida.split(':').map(Number);

        const inicio = new Date(0, 0, 0, horaEntrada, minutoEntrada);
        const fin = new Date(0, 0, 0, horaSalida, minutoSalida);
        let diferencia = (fin - inicio) / 1000 / 60 / 60;

        if (diferencia < 0) {
            diferencia += 24;
        }

        const hrsInput = document.querySelector(`input[name="hrs_${id}"]`);
        hrsInput.value = diferencia.toFixed(2);

        actualizarTotalHoras();
    } catch (error) {
        console.error(`Error actualizando horas para el proceso ${id}:`, error);
    }
};