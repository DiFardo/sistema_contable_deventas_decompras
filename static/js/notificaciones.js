document.addEventListener('DOMContentLoaded', function () {
    cargarNotificaciones();

    // Función para cargar todas las notificaciones
    function cargarNotificaciones() {
        fetch('/notificaciones')
            .then(response => response.json())
            .then(data => {
                const notificaciones = data.notificaciones;
                const listaNotificaciones = document.getElementById('notification-list');
                const contador = document.getElementById('notification-count');

                // Calcular la cantidad de notificaciones no leídas primero
                const totalNoLeidas = notificaciones.filter(n => !n.leido).length;
                contador.textContent = totalNoLeidas;
                contador.style.display = totalNoLeidas > 0 ? 'inline-block' : 'none';

                // Resetear la lista de notificaciones
                listaNotificaciones.innerHTML = '';

                if (notificaciones.length === 0) {
                    listaNotificaciones.innerHTML = '<li class="no-notifications">No hay notificaciones nuevas</li>';
                } else {
                    // Mostrar las notificaciones en la lista
                    notificaciones.forEach(notificacion => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <div class="notification-content">
                                <span>${notificacion.mensaje}</span>
                                <span class="material-icons delete-icon" onclick="eliminarNotificacion(${notificacion.id}, event)">close</span>
                            </div>
                        `;
                        li.classList.add('notification-item');
                        if (!notificacion.leido) {
                            li.classList.add('not-read');
                        }
                        listaNotificaciones.appendChild(li);
                    });
                }
            })
            .catch(error => console.error('Error al cargar notificaciones:', error));
    }

    // Función para eliminar una notificación
    window.eliminarNotificacion = function(notificacionId, event) {
        event.stopPropagation(); // Evita el cierre del dropdown

        // Eliminar la notificación de la interfaz inmediatamente
        const notificacionItem = event.target.closest('.notification-item');
        if (notificacionItem) {
            notificacionItem.remove();
        }

        // Actualizar el contador
        const contador = document.getElementById('notification-count');
        let nuevoContador = parseInt(contador.textContent);
        nuevoContador = Math.max(nuevoContador - 1, 0);
        contador.textContent = nuevoContador;
        contador.style.display = nuevoContador > 0 ? 'inline-block' : 'none';

        // Hacer la solicitud para eliminar la notificación en el servidor
        fetch('/notificaciones/eliminar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: notificacionId })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.message) {
                console.error('Error al eliminar la notificación:', data.error);
            }
        })
        .catch(error => console.error('Error al eliminar notificación:', error));
    };

    // Función para marcar las notificaciones como leídas
    document.getElementById('mark-as-read').addEventListener('click', function () {
        fetch('/notificaciones/marcar_leidas', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                cargarNotificaciones(); // Recargar las notificaciones si se marcan como leídas
            }
        })
        .catch(error => console.error('Error al marcar notificaciones como leídas:', error));
    });
});


function toggleConfigurator() {
    const configurator = document.getElementById('configurator');
    configurator.classList.toggle('open');
  }

  function changeSidebarColor(color) {
    // Lógica para cambiar el color del sidebar
    const sidebar = document.querySelector('.sidebar');
    sidebar.className = `sidebar bg-${color}`;
  }

  function setSidebarType(type) {
    // Lógica para cambiar el tipo de sidebar
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.remove('bg-dark', 'bg-transparent', 'bg-white');
    sidebar.classList.add(`bg-${type}`);
  }

  // Cerrar el configurador al hacer clic fuera de él
  document.addEventListener('click', function(event) {
    const configurator = document.getElementById('configurator');
    const button = document.querySelector('.open-configurator');

    if (!configurator.contains(event.target) && !button.contains(event.target) && configurator.classList.contains('open')) {
      configurator.classList.remove('open');
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
    const configuratorButton = document.querySelector('.open-configurator');
    const configPanel = document.querySelector('.config-panel');
    const closeButton = document.querySelector('.close-config-panel');

    // Función para abrir el panel
    function openConfigurator() {
        configPanel.classList.add('open');
        configuratorButton.style.display = 'none'; // Ocultar el botón
    }

    // Función para cerrar el panel
    function closeConfigurator() {
        configPanel.classList.remove('open');
        configuratorButton.style.display = 'flex'; // Mostrar el botón nuevamente
    }

    // Evento para abrir el configurador al hacer clic en el botón flotante
    configuratorButton.addEventListener('click', openConfigurator);

    // Evento para cerrar el panel al hacer clic en el botón de cierre
    closeButton.addEventListener('click', closeConfigurator);
});
