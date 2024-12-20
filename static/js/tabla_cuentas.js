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
    var loadingSpinner = document.getElementById('loadingSpinner');

    // Variable para almacenar el nivel seleccionado
    let nivelSeleccionado = 2; // Nivel predeterminado de 3 dígitos


    let cuentaSeleccionada = null; // Código de cuenta seleccionada para "Dar de Baja"
    let nuevaAccionEstado = null;  // Estado que se aplicará a la cuenta ("true" o "false")


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

    // Escuchar cambios en los niveles de cuenta
    document.querySelectorAll('input[name="nivel-cuentas"]').forEach(function (radio) {
        radio.addEventListener('change', function () {
            nivelSeleccionado = parseInt(this.value);
            validarCodigoCuentaPadreYNivel(); // Validar en tiempo real al cambiar el nivel
        });
    });

    // Evento para cambiar el texto del estado al marcar/desmarcar el checkbox
    inputEstado.addEventListener('change', function () {
        estadoLabel.textContent = inputEstado.checked ? 'Cuenta activa' : 'Cuenta no activa';
    });

    // Mostrar/Ocultar spinner de carga
    function mostrarSpinner() {
        loadingSpinner.style.display = 'block';
    }

    function ocultarSpinner() {
        loadingSpinner.style.display = 'none';
    }

    // Cargar cuentas por categoría seleccionada
    function cargarCuentasPorCategoria(categoriaId, callback) {
        fetch('/cuentas/por_categoria', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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

    selectCategoria.addEventListener('change', function () {
        var categoriaSeleccionada = selectCategoria.value;
        if (categoriaSeleccionada) {
            cargarCuentasPorCategoria(categoriaSeleccionada);
        } else {
            selectCuentaPadre.innerHTML = '<option value="">Seleccione una cuenta padre</option>';
        }
        limpiarError(selectCategoria, errorCategoria);
    });
    document.querySelectorAll('.add, .edit, .view').forEach(function (button) {
        button.addEventListener('click', function () {
            limpiarErrores(); // Limpiar errores al abrir el modal
            if (button.classList.contains('add')) {
                modalTitle.textContent = 'Añadir cuenta';
                limpiarCamposModal();
                habilitarCamposModal();
                cuentaPadreContainer.style.display = 'block';
                saveButton.textContent = 'Añadir';
                saveButton.style.display = 'block';
                saveButton.setAttribute('data-action', 'add');
            } else if (button.classList.contains('edit')) {
                modalTitle.textContent = 'Editar cuenta';
                cargarDatosCuenta(button, true);
                habilitarCamposEdicion(); // Solo habilitar campos relevantes para edición
                cuentaPadreContainer.style.display = 'none';
                saveButton.textContent = 'Guardar cambios';
                saveButton.style.display = 'block';
                saveButton.setAttribute('data-action', 'edit');
            } else if (button.classList.contains('view')) {
                modalTitle.textContent = 'Ver cuenta';
                cargarDatosCuenta(button, false);
                deshabilitarCamposModal();
                cuentaPadreContainer.style.display = 'none';
                saveButton.style.display = 'none';
            }
            editModal.show();
        });
    });
    document.querySelectorAll('.delete').forEach(function (button) {
        button.addEventListener('click', function () {
            // Obtener datos del botón
            const codigo = button.getAttribute('data-codigo');
            const descripcion = button.getAttribute('data-descripcion');
            const estadoActual = button.getAttribute('data-estado') === 'true';

            // Definir la acción (dar de baja o reactivar)
            const nuevaAccion = estadoActual ? 'dar de baja' : 'reactivar';
            nuevaAccionEstado = estadoActual ? 'false' : 'true';

            // Actualizar el mensaje en el modal
            document.getElementById('deleteMessage').textContent = `¿Estás seguro de que deseas ${nuevaAccion} la cuenta "${descripcion}" (Código: ${codigo})?`;

            // Guardar los datos seleccionados para su uso al confirmar
            cuentaSeleccionada = codigo;
        });
    });

    document.getElementById('confirmDeleteButton').addEventListener('click', function () {
        mostrarSpinner();
        fetch('/cuentas/dar_baja', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: cuentaSeleccionada,
                estado: nuevaAccionEstado
            })
        })
        .then(response => response.json())
        .then(data => {
            ocultarSpinner();
            if (data.message) {
                // Cambiar el estado visual de la fila en la tabla
                const fila = document.querySelector(`tr[data-cuenta-id="${cuentaSeleccionada}"]`);
                if (fila) {
                    const botonDarBaja = fila.querySelector('.delete i'); // Ícono dentro del botón de "Dar de baja"
                    if (nuevaAccionEstado === 'false') {
                        fila.classList.add('cuenta-inactiva'); // Marcar como inactiva
                        botonDarBaja.textContent = 'thumb_up'; // Cambiar a ícono de "Reactivar"
                        botonDarBaja.parentElement.setAttribute('data-estado', 'false'); // Actualizar atributo
                        botonDarBaja.setAttribute('title', 'Reactivar');
                    } else {
                        fila.classList.remove('cuenta-inactiva'); // Reactivar
                        botonDarBaja.textContent = 'thumb_down'; // Cambiar a ícono de "Dar de baja"
                        botonDarBaja.parentElement.setAttribute('data-estado', 'true'); // Actualizar atributo
                        botonDarBaja.setAttribute('title', 'Dar de baja');
                    }
                }
    
                // Ocultar el modal de confirmación y mostrar el de éxito
                const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteAccountModal'));
                deleteModal.hide();
    
                document.getElementById('successMessage').textContent = data.message;
                successModal.show();
            } else if (data.error) {
                console.error('Error:', data.error);
            }
        })
        .catch(error => {
            console.error('Error al cambiar el estado de la cuenta:', error);
            ocultarSpinner();
        });
    });
    
    
    


    confirmDeleteButton.addEventListener('click', function () {
        if (cuentaSeleccionada && nuevaAccionEstado !== null) {
            cambiarEstadoCuenta(cuentaSeleccionada, nuevaAccionEstado);
        }
        deleteAccountModal.hide();
    });


    // Habilitar campos específicos para edición
    function habilitarCamposEdicion() {
        inputCodigo.setAttribute('readonly', true);
        selectCategoria.setAttribute('disabled', true);
        selectCuentaPadre.setAttribute('disabled', true);

        formDescripcion.removeAttribute('readonly');
        inputEstado.removeAttribute('disabled');
    }

    // Habilitar todos los campos para añadir
    function habilitarCamposModal() {
        inputCodigo.removeAttribute('readonly');
        formDescripcion.removeAttribute('readonly');
        selectCategoria.removeAttribute('disabled');
        selectCuentaPadre.removeAttribute('disabled');
        inputEstado.removeAttribute('disabled');
    }

    // Deshabilitar todos los campos
    function deshabilitarCamposModal() {
        inputCodigo.setAttribute('readonly', true);
        formDescripcion.setAttribute('readonly', true);
        selectCategoria.setAttribute('disabled', true);
        selectCuentaPadre.setAttribute('disabled', true);
        inputEstado.setAttribute('disabled', true);
    }
    // Validación en tiempo real
    inputCodigo.addEventListener('input', validarCodigoCuentaPadreYNivel);
    selectCuentaPadre.addEventListener('change', validarCodigoCuentaPadreYNivel);
    formDescripcion.addEventListener('input', function () {
        limpiarError(formDescripcion, errorDescripcion);
    });

    function validarCodigoCuentaPadreYNivel() {
        var cuentaPadreCodigo = selectCuentaPadre.options[selectCuentaPadre.selectedIndex].text.split(" - ")[0].trim();
        var longitudPermitida;
        let esValido = true;

        // Verificar que el código pertenece a la cuenta padre
        if (cuentaPadreCodigo && !inputCodigo.value.startsWith(cuentaPadreCodigo)) {
            mostrarError(inputCodigo, errorCodigo, 'El código ingresado no pertenece a la cuenta padre seleccionada.');
            esValido = false;
        } else {
            limpiarError(inputCodigo, errorCodigo);
        }

        // Verificar longitud según nivel seleccionado
        switch (nivelSeleccionado) {
            case 2:
                longitudPermitida = 3;
                break;
            case 3:
                longitudPermitida = 4;
                break;
            case 4:
                longitudPermitida = 5;
                break;
            default:
                longitudPermitida = 3;
        }

        if (inputCodigo.value.length !== longitudPermitida) {
            mostrarError(inputCodigo, errorCodigo, `El código debe tener ${longitudPermitida} dígitos para el nivel seleccionado.`);
            esValido = false;
        } else if (esValido) {
            limpiarError(inputCodigo, errorCodigo);
        }

        // Verificar si la descripción está vacía
        if (formDescripcion.value.trim() === '') {
            mostrarError(formDescripcion, errorDescripcion, 'La descripción es requerida.');
            esValido = false;
        } else {
            limpiarError(formDescripcion, errorDescripcion);
        }

        return esValido; // Retornar la validez de la validación
    }


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

        estadoLabel.textContent = inputEstado.checked ? 'Cuenta activa' : 'Cuenta no activa';
    }

    function limpiarCamposModal() {
        inputCodigo.value = '';
        formDescripcion.value = '';
        inputEstado.checked = false;
        selectCategoria.value = '';
        selectCuentaPadre.innerHTML = '<option value="">Seleccione una cuenta padre</option>';
        limpiarError(inputCodigo, errorCodigo);
        limpiarError(formDescripcion, errorDescripcion);
        limpiarError(selectCategoria, errorCategoria);
    }

    function habilitarCamposModal() {
        inputCodigo.removeAttribute('readonly');
        formDescripcion.removeAttribute('readonly');
        selectCategoria.removeAttribute('disabled');
        inputEstado.removeAttribute('disabled');
    }

    function deshabilitarCamposModal() {
        inputCodigo.setAttribute('readonly', true);
        formDescripcion.setAttribute('readonly', true);
        selectCategoria.setAttribute('disabled', true);
        inputEstado.setAttribute('disabled', true);
    }

    function mostrarError(campo, mensajeError, texto) {
        campo.classList.add('error-input');
        mensajeError.textContent = texto;
        mensajeError.style.display = 'block';
    }

    function limpiarError(campo, mensajeError) {
        campo.classList.remove('error-input');
        mensajeError.style.display = 'none';
    }

    // Validación para el editar
    function validarCamposEditar() {
        let esValido = true;

        // Validar descripción
        if (formDescripcion.value.trim() === '') {
            mostrarError(formDescripcion, errorDescripcion, 'La descripción es requerida.');
            esValido = false;
        } else {
            limpiarError(formDescripcion, errorDescripcion);
        }

        return esValido;
    }

    saveButton.addEventListener('click', function (e) {
        e.preventDefault();
        const action = saveButton.getAttribute('data-action');
        if (action === 'add') {
            if (!validarCodigoCuentaPadreYNivel()) return;
            guardarNuevaCuenta();
        } else if (action === 'edit') {
            if (!validarCamposEditar()) return;
            editarCuenta();
        }
    });

    function guardarNuevaCuenta() {
        mostrarSpinner();
        const codigo = inputCodigo.value;
        const descripcion = formDescripcion.value;
        const estado = inputEstado.checked ? 'true' : 'false';
        const categoria = selectCategoria.value;
        const cuentaPadre = selectCuentaPadre.value;

        fetch('/cuentas/añadir', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                descripcion: descripcion,
                estado: estado,
                categoria: categoria,
                cuenta_padre: cuentaPadre || null,
                nivel: nivelSeleccionado
            })
        })
            .then(response => response.json())
            .then(data => {
                ocultarSpinner();
                if (data.message) {
                    mostrarCuentaAgregada(codigo, descripcion); // Mensaje específico para añadir
                    editModal.hide();
                } else if (data.error) {
                    mostrarError(inputCodigo, errorCodigo, data.error);
                }
            })
            .catch(error => {
                console.error('Error al añadir la cuenta:', error);
                ocultarSpinner();
            });
    }

    function editarCuenta() {
        mostrarSpinner();
        const codigo = inputCodigo.value;
        const descripcion = formDescripcion.value;
        const estado = inputEstado.checked ? 'true' : 'false';

        fetch('/cuentas/editar', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                descripcion: descripcion,
                estado: estado
            })
        })
            .then(response => response.json())
            .then(data => {
                ocultarSpinner();
                if (data.message) {
                    mostrarCuentaActualizada(codigo, descripcion); // Mensaje específico para actualizar
                    editModal.hide();
                } else if (data.error) {
                    mostrarError(formDescripcion, errorDescripcion, data.error);
                }
            })
            .catch(error => {
                console.error('Error al editar la cuenta:', error);
                ocultarSpinner();
            });
    }

    function mostrarCuentaAgregada(codigo, descripcion) {
        document.getElementById('successMessage').textContent = 'La cuenta ha sido añadida correctamente.';
        document.getElementById('successCodigo').textContent = `Código: ${codigo}`;
        document.getElementById('successDescripcion').textContent = `Descripción: ${descripcion}`;
        successModal.show();
    }

    function mostrarCuentaActualizada(codigo, descripcion) {
        document.getElementById('successMessage').textContent = 'La cuenta ha sido actualizada correctamente.';
        document.getElementById('successCodigo').textContent = `Código: ${codigo}`;
        document.getElementById('successDescripcion').textContent = `Descripción: ${descripcion}`;
        successModal.show();
    }


    document.getElementById('successModal').addEventListener('hidden.bs.modal', function () {
        location.reload();
    });

    document.querySelectorAll('.toggle-subcuentas').forEach(function (button) {
        button.addEventListener('click', function () {
            const cuentaId = this.getAttribute('data-cuenta-id');
            const subcuentas = document.querySelectorAll(`.subcuenta[data-padre-id="${cuentaId}"]`);
            const isVisible = Array.from(subcuentas).some(subcuenta => !subcuenta.classList.contains('d-none'));

            subcuentas.forEach(subcuenta => {
                subcuenta.classList.toggle('d-none', isVisible); // Alternar visibilidad
            });

            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-plus', isVisible);
                icon.classList.toggle('fa-minus', !isVisible);
            }
        });
    });

    // Limpiar errores al cerrar el modal
    editModal.addEventListener('hidden.bs.modal', function () {
        limpiarCamposModal();
        limpiarError(inputCodigo, errorCodigo);
        limpiarError(formDescripcion, errorDescripcion);
        limpiarError(selectCategoria, errorCategoria);
    });

    function limpiarErrores() {
        limpiarError(inputCodigo, errorCodigo);
        limpiarError(formDescripcion, errorDescripcion);
        limpiarError(selectCategoria, errorCategoria);
    }

});


