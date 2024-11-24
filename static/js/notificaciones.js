document.addEventListener('DOMContentLoaded', function () {
    cargarNotificaciones();

    // Función para cargar todas las notificaciones
    function cargarNotificaciones() {
        fetch('/notificaciones')
            .then(response => response.json())
            .then(data => {
                const notificaciones = data.notificaciones || [];
                const tablaNotificaciones = document.getElementById('notification-table-body');
                const contador = document.getElementById('notification-count');

                // Calcular la cantidad de notificaciones no leídas primero
                const totalNoLeidas = notificaciones.filter(n => !n.leido).length;
                contador.textContent = totalNoLeidas;
                contador.style.display = 'inline-block'; // Mantener siempre visible

                // Resetear la tabla de notificaciones
                tablaNotificaciones.innerHTML = '';

                if (notificaciones.length === 0) {
                    // Mostrar mensaje de "No hay notificaciones nuevas"
                    const fila = document.createElement('tr');
                    fila.className = 'no-notifications';
                    fila.innerHTML = `
                        <td colspan="2" class="text-center">No hay notificaciones nuevas</td>
                    `;
                    tablaNotificaciones.appendChild(fila);
                } else {
                    // Mostrar cada notificación como fila en la tabla
                    notificaciones.forEach((notificacion, index) => {
                        const fila = document.createElement('tr');
                        fila.className = 'notification-item';

                        // Columna de mensaje
                        const celdaMensaje = document.createElement('td');
                        celdaMensaje.textContent = notificacion.mensaje;
                        fila.appendChild(celdaMensaje);

                        // Columna de acción
                        const celdaAccion = document.createElement('td');
                        const botonEliminar = document.createElement('i');
                        botonEliminar.className = 'material-icons close-icon';
                        botonEliminar.textContent = 'close';
                        botonEliminar.style.cursor = 'pointer';
                        botonEliminar.addEventListener('click', (event) => eliminarNotificacion(notificacion.id, event));
                        celdaAccion.appendChild(botonEliminar);
                        fila.appendChild(celdaAccion);

                        tablaNotificaciones.appendChild(fila);
                    });
                }
            })
            .catch(error => console.error('Error al cargar notificaciones:', error));
    }

    // Función para eliminar una notificación
    function eliminarNotificacion(notificacionId, event) {
        event.stopPropagation(); // Evita el cierre del dropdown

        // Eliminar la fila correspondiente de la interfaz
        const notificacionItem = event.target.closest('tr');
        if (notificacionItem) {
            notificacionItem.remove();
        }

        // Actualizar el contador
        const contador = document.getElementById('notification-count');
        let nuevoContador = Math.max(parseInt(contador.textContent) - 1, 0);
        contador.textContent = nuevoContador;
        contador.style.display = 'inline-block'; // Siempre visible, incluso con "0"

        // Si ya no hay notificaciones visibles, mostrar mensaje de "No hay notificaciones nuevas"
        const tablaNotificaciones = document.getElementById('notification-table-body');
        if (!tablaNotificaciones.querySelector('tr')) {
            const fila = document.createElement('tr');
            fila.className = 'no-notifications';
            fila.innerHTML = `
                <td colspan="2" class="text-center">No hay notificaciones nuevas</td>
            `;
            tablaNotificaciones.appendChild(fila);
        }

        // Hacer la solicitud al servidor para eliminar la notificación
        fetch('/notificaciones/eliminar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: notificacionId })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Error al eliminar la notificación:', data.error);
            }
        })
        .catch(error => console.error('Error al eliminar notificación:', error));
    }

    // Función para marcar todas las notificaciones como leídas
    document.getElementById('mark-as-read').addEventListener('click', function () {
        fetch('/notificaciones/marcar_leidas', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarNotificaciones(); // Recargar las notificaciones si se marcan como leídas
            }
        })
        .catch(error => console.error('Error al marcar notificaciones como leídas:', error));
    });
});
