document.addEventListener('DOMContentLoaded', function () {
    var editModal = document.getElementById('editAccountModal');
    var formDescripcion = editModal.querySelector('#edit-descripcion');
    var inputCodigo = editModal.querySelector('#edit-codigo');
    var inputEstado = editModal.querySelector('#edit-estado');  // Checkbox para estado
    var selectCategoria = editModal.querySelector('#edit-categoria');  // Combobox para categoría
    var estadoLabel = editModal.querySelector('#estado-label');  // Label para el estado dinámico
    var saveButton = editModal.querySelector('#saveChangesButton');
    var modalTitle = editModal.querySelector('.modal-title');

    // Función para cambiar el texto del estado
    function actualizarEstadoLabel() {
        if (inputEstado.checked) {
            estadoLabel.textContent = 'Cuenta activa';
        } else {
            estadoLabel.textContent = 'Cuenta no activa';
        }
    }
    // Cargar datos en el modal y configurar el comportamiento de edición/ver/añadir
    editModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget; // Botón que disparó el modal
        var codigo = button.getAttribute('data-codigo');
        var descripcion = button.getAttribute('data-descripcion');
        var estado = button.getAttribute('data-estado');  // Capturamos el estado (true/false)
        var categoria = button.getAttribute('data-categoria');  // Capturamos la categoría

        // Revisar si es el modo 'añadir'
        if (button.classList.contains('add')) {
            inputCodigo.value = '';  
            formDescripcion.value = '';  
            inputEstado.checked = false;  // Desmarcar el checkbox por defecto
            actualizarEstadoLabel();  // Actualizar el texto del estado
            selectCategoria.selectedIndex = -1;  // Dejar el select sin selección por defecto
            inputCodigo.removeAttribute('readonly');  
            formDescripcion.removeAttribute('readonly');  
            selectCategoria.removeAttribute('disabled');  // Habilitar la categoría para seleccionar
            inputEstado.removeAttribute('disabled');  // Habilitar el checkbox para estado
            saveButton.style.display = 'block';  
            modalTitle.textContent = 'Añadir nueva cuenta';  
        } 
        // Revisar si es el modo 'editar'
        else if (button.classList.contains('edit')) {
            inputCodigo.value = codigo;  
            formDescripcion.value = descripcion;  
            inputEstado.checked = (estado === 'true');  // Comparación con la cadena "true"
            actualizarEstadoLabel();  // Actualizar el texto del estado
            selectCategoria.value = categoria.toLowerCase();  // Seleccionar la categoría actual
            inputCodigo.setAttribute('readonly', true);  // El código no se puede editar
            formDescripcion.removeAttribute('readonly');  // Permitir edición de descripción
            selectCategoria.removeAttribute('disabled');  // Permitir selección de categoría
            inputEstado.removeAttribute('disabled');  // Permitir cambiar el estado
            saveButton.style.display = 'block';  // Mostrar el botón de guardar cambios
            modalTitle.textContent = 'Editar cuenta contable';  
        } 
        // Revisar si es el modo 'ver'
        else if (button.classList.contains('view')) {
            inputCodigo.value = codigo;  
            formDescripcion.value = descripcion;  
            inputEstado.checked = (estado === 'true');  // Comparación con la cadena "true"
            actualizarEstadoLabel();  // Actualizar el texto del estado
            selectCategoria.value = categoria.toLowerCase();  // Mostrar la categoría actual
            inputCodigo.setAttribute('readonly', true);  // No permitir edición del código
            formDescripcion.setAttribute('readonly', true);  // No permitir edición de descripción
            inputEstado.setAttribute('disabled', true);  // Deshabilitar checkbox de estado
            selectCategoria.setAttribute('disabled', true);  // Deshabilitar select de categoría
            saveButton.style.display = 'none';  // Ocultar el botón de guardar en modo ver
            modalTitle.textContent = 'Ver cuenta contable';  // Cambiar el título del modal
        }
    });

    // Evento para cambiar el texto dinámico cuando el checkbox cambia
    inputEstado.addEventListener('change', function () {
        actualizarEstadoLabel();
    });
});

  
  


document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.toggle-subcuentas').forEach(function(button) {
        button.addEventListener('click', function() {
            const cuentaId = this.getAttribute('data-cuenta-id');
            const subcuentas = document.querySelectorAll('.subcuenta-' + cuentaId);
            const isExpanded = !subcuentas[0].classList.contains('d-none'); // Verifica si ya están visibles

            if (isExpanded) {
                // Si ya están expandidas, colapsar todas las subcuentas y sub-subcuentas
                collapseSubcuentas(cuentaId);
                button.innerHTML = '<i class="fas fa-plus"></i>'; // Cambia a ícono de expandir
            } else {
                // Si están colapsadas, mostrar solo las subcuentas directas
                subcuentas.forEach(function(subcuenta) {
                    subcuenta.classList.remove('d-none');
                });
                button.innerHTML = '<i class="fas fa-minus"></i>'; // Cambia a ícono de colapsar
            }
        });
    });

    // Función para colapsar todas las subcuentas recursivamente
    function collapseSubcuentas(cuentaId) {
        const subcuentas = document.querySelectorAll('.subcuenta-' + cuentaId);
        subcuentas.forEach(function(subcuenta) {
            subcuenta.classList.add('d-none'); // Colapsar la subcuenta
            // Cambiar el ícono del botón de subcuentas a expandir
            const toggleButton = subcuenta.querySelector('.toggle-subcuentas');
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-plus"></i>';
            }
            // Colapsar también las subcuentas de esta subcuenta
            const nestedCuentaId = subcuenta.getAttribute('data-cuenta-id');
            collapseSubcuentas(nestedCuentaId); // Llamada recursiva para subcuentas anidadas
        });
    }
});






document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById('search-input');
  const tableRows = document.querySelectorAll('#tabla-cuerpo tr');

  searchInput.addEventListener('input', function() {
      const searchTerm = searchInput.value.toLowerCase();

      tableRows.forEach(function(row) {
          const codigo = row.querySelectorAll('td')[1].textContent.toLowerCase();
          const descripcion = row.querySelectorAll('td')[2].textContent.toLowerCase();
          
          // Verificamos si el término de búsqueda coincide con el código o la descripción
          if (codigo.includes(searchTerm) || descripcion.includes(searchTerm)) {
              row.style.display = ''; // Mostramos la fila
          } else {
              row.style.display = 'none'; // Ocultamos la fila
          }
      });
  });
});


  