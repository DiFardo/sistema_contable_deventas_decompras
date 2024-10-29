document.addEventListener('DOMContentLoaded', function () {
    var editModal = new bootstrap.Modal(document.getElementById('editAccountModal'));
    var successModal = new bootstrap.Modal(document.getElementById('successModal'));
    var formDescripcion = document.getElementById('edit-descripcion');
    var inputCodigo = document.getElementById('edit-codigo');
    var inputEstado = document.getElementById('edit-estado');
    var selectCategoria = document.getElementById('edit-categoria');
    var selectCuentaPadre = document.getElementById('edit-cuenta-padre');
    var estadoLabel = document.getElementById('estado-label');
    var saveButton = document.getElementById('saveChangesButton');
    var modalTitle = document.querySelector('.modal-title');
    var cuentaPadreContainer = document.querySelector('.cuenta-padre-container');
    var loadingSpinner = document.getElementById('loadingSpinner'); // Obtener el elemento del spinner

    // Crear mensajes de error para los campos
    var errorCodigo = document.createElement('div');
    errorCodigo.classList.add('error-message');
    errorCodigo.style.color = 'red'; 
    errorCodigo.style.marginTop = '5px';
    inputCodigo.parentNode.appendChild(errorCodigo);

    var errorDescripcion = document.createElement('div');
    errorDescripcion.classList.add('error-message');
    errorDescripcion.style.color = 'red';
    errorDescripcion.style.marginTop = '5px';
    formDescripcion.parentNode.appendChild(errorDescripcion);

    var errorCategoria = document.createElement('div');
    errorCategoria.classList.add('error-message');
    errorCategoria.style.color = 'red';
    errorCategoria.style.marginTop = '5px';
    selectCategoria.parentNode.appendChild(errorCategoria);

    // Función para cambiar el texto del estado
    function actualizarEstadoLabel() {
        estadoLabel.textContent = inputEstado.checked ? 'Cuenta activa' : 'Cuenta no activa';
    }

    // Evento para cambiar el texto del estado al marcar/desmarcar el checkbox
    inputEstado.addEventListener('change', actualizarEstadoLabel);

    // Función para mostrar el spinner de carga
    function mostrarSpinner() {
        loadingSpinner.style.display = 'block';
    }

    // Función para ocultar el spinner de carga
    function ocultarSpinner() {
        loadingSpinner.style.display = 'none';
    }

    // Función para cargar las cuentas principales según la categoría seleccionada
    function cargarCuentasPorCategoria(categoriaId, callback) {
        fetch('/cuentas/por_categoria', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ categoria: categoriaId })
        })
        .then(response => response.json())
        .then(data => {
            selectCuentaPadre.innerHTML = '<option value="">Seleccione una cuenta padre</option>';
            data.forEach(cuenta => {
                var option = document.createElement('option');
                option.value = cuenta.id;
                option.textContent = `${cuenta.codigo} - ${cuenta.descripcion}`;
                selectCuentaPadre.appendChild(option);
            });
            if (callback) callback(); 
        })
        .catch(error => console.error('Error al cargar las cuentas por categoría:', error));
    }

    // Evento de cambio en el select de categoría para actualizar cuentas padre
    selectCategoria.addEventListener('change', function () {
        var categoriaSeleccionada = selectCategoria.value;
        if (categoriaSeleccionada) {
            cargarCuentasPorCategoria(categoriaSeleccionada);
        } else {
            selectCuentaPadre.innerHTML = '<option value="">Seleccione una cuenta padre</option>';
        }
        limpiarError(selectCategoria, errorCategoria);
    });

    // Evento para abrir el modal con el título correcto
    document.querySelectorAll('.add, .edit, .view').forEach(function (button) {
        button.addEventListener('click', function () {
            if (button.classList.contains('add')) {
                modalTitle.textContent = 'Añadir cuenta';
                limpiarCamposModal();
                habilitarCamposModal();
                cuentaPadreContainer.style.display = 'block';
                saveButton.style.display = 'block';
            } else if (button.classList.contains('edit')) {
                modalTitle.textContent = 'Editar cuenta';
                cargarDatosCuenta(button, true);
                habilitarCamposModal();
                cuentaPadreContainer.style.display = 'none';
                saveButton.style.display = 'block';
            } else if (button.classList.contains('view')) {
                modalTitle.textContent = 'Ver cuenta';
                cargarDatosCuenta(button, false);
                deshabilitarCamposModal();
                cuentaPadreContainer.style.display = 'none';
                saveButton.style.display = 'none';
            }
        });
    });

    // Función para cargar los datos de la cuenta en el modal
    function cargarDatosCuenta(button, editable) {
        inputCodigo.value = button.getAttribute('data-codigo');
        formDescripcion.value = button.getAttribute('data-descripcion');
        inputEstado.checked = button.getAttribute('data-estado') === 'true';

        var categoriaSeleccionada = button.getAttribute('data-categoria');
        if (categoriaSeleccionada) {
            for (let i = 0; i < selectCategoria.options.length; i++) {
                if (selectCategoria.options[i].value.toLowerCase() === categoriaSeleccionada.toLowerCase()) {
                    selectCategoria.selectedIndex = i;
                    break;
                }
            }
        }

        cargarCuentasPorCategoria(categoriaSeleccionada, function () {
            var cuentaPadreId = button.getAttribute('data-cuenta-padre');
            if (cuentaPadreId) {
                selectCuentaPadre.value = cuentaPadreId;
            }
        });

        if (!editable) {
            deshabilitarCamposModal();
        } else {
            habilitarCamposModal();
        }

        actualizarEstadoLabel();
    }

    // Función para limpiar los campos del modal
    function limpiarCamposModal() {
        inputCodigo.value = '';
        formDescripcion.value = '';
        inputEstado.checked = false;
        selectCategoria.value = '';
        selectCuentaPadre.innerHTML = '<option value="">Seleccione una cuenta padre</option>';
        actualizarEstadoLabel();
        limpiarError(inputCodigo, errorCodigo);
        limpiarError(formDescripcion, errorDescripcion);
        limpiarError(selectCategoria, errorCategoria);
    }

    // Función para habilitar los campos del modal
    function habilitarCamposModal() {
        inputCodigo.removeAttribute('readonly');
        formDescripcion.removeAttribute('readonly');
        selectCategoria.removeAttribute('disabled');
        inputEstado.removeAttribute('disabled');
    }

    // Función para deshabilitar los campos del modal
    function deshabilitarCamposModal() {
        inputCodigo.setAttribute('readonly', true);
        formDescripcion.setAttribute('readonly', true);
        selectCategoria.setAttribute('disabled', true);
        inputEstado.setAttribute('disabled', true);
    }

    // Función para validar si el código pertenece al rango de la cuenta padre
    function validarCodigoCuentaPadre(codigo, cuentaPadre) {
        if (cuentaPadre && !codigo.startsWith(cuentaPadre)) {
            return false;
        }
        return true;
    }

    // Función para mostrar un mensaje de error en un campo
    function mostrarError(campo, mensajeError, texto) {
        campo.classList.add('error-input');
        mensajeError.textContent = texto;
        mensajeError.style.display = 'block';
    }

    // Función para limpiar el mensaje de error de un campo
    function limpiarError(campo, mensajeError) {
        campo.classList.remove('error-input');
        mensajeError.style.display = 'none';
    }

    // Eventos para borrar mensajes de error en tiempo real al escribir
    inputCodigo.addEventListener('input', function () {
        var cuentaPadre = selectCuentaPadre.value;
        if (!inputCodigo.value.trim()) {
            mostrarError(inputCodigo, errorCodigo, 'Por favor, ingrese un código válido.');
        } else if (!validarCodigoCuentaPadre(inputCodigo.value, cuentaPadre)) {
            mostrarError(inputCodigo, errorCodigo, 'El código no pertenece al rango de la cuenta padre.');
        } else {
            limpiarError(inputCodigo, errorCodigo);
        }
    });

    formDescripcion.addEventListener('input', function () {
        limpiarError(formDescripcion, errorDescripcion);
    });

    selectCategoria.addEventListener('change', function () {
        limpiarError(selectCategoria, errorCategoria);
    });

    // Evento para enviar el formulario de añadir cuenta
    saveButton.addEventListener('click', function (e) {
        e.preventDefault();

        // Verificar si los campos son válidos antes de enviar
        if (!validarCampos()) {
            return;
        }

        // Mostrar el spinner de carga
        mostrarSpinner();

        var codigo = inputCodigo.value;
        var descripcion = formDescripcion.value;
        var estado = inputEstado.checked ? 'true' : 'false';
        var categoria = selectCategoria.value;
        var cuentaPadre = selectCuentaPadre.value;

        fetch('/cuentas/añadir', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                codigo: codigo,
                descripcion: descripcion,
                estado: estado,
                categoria: categoria,
                cuenta_padre: cuentaPadre || null
            })
        })
        .then(response => response.json())
        .then(data => {
            // Ocultar el spinner de carga
            ocultarSpinner();

            if (data.message) {
                mostrarCuentaAgregada(codigo, descripcion);
                editModal.hide(); 
                successModal.show(); 
            } else if (data.error) {
                mostrarError(inputCodigo, errorCodigo, data.error); 
            }
        })
        .catch(error => {
            console.error('Error al añadir la cuenta:', error);
            ocultarSpinner(); 
        });
    });

    // Mostrar mensaje de éxito al agregar una cuenta
    function mostrarCuentaAgregada(codigo, descripcion) {
        document.getElementById('successMessage').textContent = 'La cuenta ha sido añadida correctamente.';
        document.getElementById('successCodigo').textContent = `Código: ${codigo}`;
        document.getElementById('successDescripcion').textContent = `Descripción: ${descripcion}`;
    }

    // Evento para cerrar el modal de éxito y recargar la página
    document.getElementById('successModal').addEventListener('hidden.bs.modal', function () {
        location.reload(); 
    });

    // Evento para expandir o contraer subcuentas
    document.querySelectorAll('.toggle-subcuentas').forEach(function (button) {
        button.addEventListener('click', function () {
            const cuentaId = this.getAttribute('data-cuenta-id');
            const subcuentas = document.querySelectorAll('.subcuenta-' + cuentaId);
            const isExpanded = !subcuentas[0].classList.contains('d-none');

            if (isExpanded) {
                collapseSubcuentas(cuentaId);
                button.innerHTML = '<i class="fas fa-plus"></i>';
            } else {
                subcuentas.forEach(function (subcuenta) {
                    subcuenta.classList.remove('d-none');
                });
                button.innerHTML = '<i class="fas fa-minus"></i>';
            }
        });
    });

    // Función para colapsar todas las subcuentas recursivamente
    function collapseSubcuentas(cuentaId) {
        const subcuentas = document.querySelectorAll('.subcuenta-' + cuentaId);
        subcuentas.forEach(function (subcuenta) {
            subcuenta.classList.add('d-none');
            const nestedCuentaId = subcuenta.getAttribute('data-cuenta-id');
            collapseSubcuentas(nestedCuentaId);
        });
    }

    // Función para validar campos vacíos y rango del código
    function validarCampos() {
        var esValido = true;

        if (!inputCodigo.value.trim()) {
            mostrarError(inputCodigo, errorCodigo, 'Por favor, ingrese un código válido.');
            esValido = false;
        } else if (!validarCodigoCuentaPadre(inputCodigo.value, selectCuentaPadre.value)) {
            mostrarError(inputCodigo, errorCodigo, 'El código no pertenece al rango de la cuenta padre.');
            esValido = false;
        } else {
            limpiarError(inputCodigo, errorCodigo);
        }

        if (!formDescripcion.value.trim()) {
            mostrarError(formDescripcion, errorDescripcion, 'Por favor, ingrese una descripción válida.');
            esValido = false;
        } else {
            limpiarError(formDescripcion, errorDescripcion);
        }

        if (!selectCategoria.value) {
            mostrarError(selectCategoria, errorCategoria, 'Por favor, seleccione una categoría.');
            esValido = false;
        } else {
            limpiarError(selectCategoria, errorCategoria);
        }

        return esValido;
    }
});
