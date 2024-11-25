document.addEventListener('DOMContentLoaded', function() {
    function actualizarHoras(idHrspro, codigoEmp) {
        const horaEntrada = document.querySelector(`input[name="horaentrada_${idHrspro}"]`).value;
        const horaSalida = document.querySelector(`input[name="horasalida_${idHrspro}"]`);
        const siguienteProceso = document.querySelector(`input[name="horaentrada_${parseInt(idHrspro) + 1}"]`);

        if (horaEntrada) {
            const [hours, minutes] = horaEntrada.split(':');
            const nuevaHoraSalida = new Date();
            nuevaHoraSalida.setHours(parseInt(hours) + 1);
            nuevaHoraSalida.setMinutes(parseInt(minutes));
            const formattedHoraSalida = nuevaHoraSalida.toTimeString().split(' ')[0].substring(0, 5);
            horaSalida.value = formattedHoraSalida;

            if (siguienteProceso) {
                siguienteProceso.value = formattedHoraSalida;
            }
        }

        calcularHoras(idHrspro);
        calcularTotalHorasEmpleado(codigoEmp);
        calcularTotalHorasGeneral();
    }

    function calcularHoras(idHrspro) {
        const horaEntrada = document.querySelector(`input[name="horaentrada_${idHrspro}"]`).value;
        const horaSalida = document.querySelector(`input[name="horasalida_${idHrspro}"]`).value;
        const hrs = document.querySelector(`input[name="hrs_${idHrspro}"]`);

        if (horaEntrada && horaSalida) {
            const [hoursEntrada, minutesEntrada] = horaEntrada.split(':');
            const [hoursSalida, minutesSalida] = horaSalida.split(':');
            const entrada = new Date();
            const salida = new Date();
            entrada.setHours(parseInt(hoursEntrada));
            entrada.setMinutes(parseInt(minutesEntrada));
            salida.setHours(parseInt(hoursSalida));
            salida.setMinutes(parseInt(minutesSalida));

            const diff = (salida - entrada) / (1000 * 60 * 60);
            hrs.value = diff.toFixed(2);
        }
    }

    function calcularTotalHorasEmpleado(codigoEmp) {
        let totalHoras = 0;
        const procesos = document.querySelectorAll(`input[name^="hrs_"][name$="_${codigoEmp}"]`);
        procesos.forEach(proceso => {
            totalHoras += parseFloat(proceso.value) || 0;
        });
        document.querySelector(`input[name="total_${codigoEmp}"]`).value = totalHoras.toFixed(2);
    }

    function calcularTotalHorasGeneral() {
        let totalHorasGeneral = 0;
        const totalHorasEmpleados = document.querySelectorAll('input[name^="total_"]');
        totalHorasEmpleados.forEach(total => {
            totalHorasGeneral += parseFloat(total.value) || 0;
        });
        document.getElementById('total_proceso').innerText = totalHorasGeneral.toFixed(2);
    }

    function eliminarProceso(idHrspro) {
        fetch(`/horas_procesos/eliminar_proceso/${idHrspro}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al eliminar el proceso.');
            }
        });
    }

    function actualizarProceso(idHrspro) {
        console.log(`Actualizando proceso con id: ${idHrspro}`);
        const horaEntrada = document.querySelector(`input[name="horaentrada_${idHrspro}"]`).value;
        const horaSalida = document.querySelector(`input[name="horasalida_${idHrspro}"]`).value;
        const hrs = document.querySelector(`input[name="hrs_${idHrspro}"]`).value;
        const totalhrs = document.querySelector(`input[name="totalhrs_${idHrspro}"]`).value;
        const hrsextras = document.querySelector(`input[name="hrsextras_${idHrspro}"]`).value;
        const inasistencia = document.querySelector(`input[name="inasistencia_${idHrspro}"]`).checked ? 0 : 1;

        fetch(`/horas_procesos/actualizar_proceso/${idHrspro}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                horaentrada: horaEntrada,
                horasalida: horaSalida,
                hrs: hrs,
                totalhrs: totalhrs,
                hrsextras: hrsextras,
                inasistencia: inasistencia
            })
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al actualizar el proceso.');
            }
        });
    }

    // Expose functions to the global scope
    window.actualizarHoras = actualizarHoras;
    window.eliminarProceso = eliminarProceso;
    window.actualizarProceso = actualizarProceso;
});
