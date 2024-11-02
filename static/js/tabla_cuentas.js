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

    // Validación en tiempo real
    inputCodigo.addEventListener('input', validarCodigoCuentaPadreYNivel);
    selectCuentaPadre.addEventListener('change', validarCodigoCuentaPadreYNivel);

    function validarCamposObligatorios() {
        let isValid = true;
        if (!selectCategoria.value) {
            mostrarError(selectCategoria, errorCategoria, 'Debe seleccionar una categoría.');
            isValid = false;
        } else {
            limpiarError(selectCategoria, errorCategoria);
        }

        if (!inputCodigo.value) {
            mostrarError(inputCodigo, errorCodigo, 'El código es obligatorio.');
            isValid = false;
        } else {
            limpiarError(inputCodigo, errorCodigo);
        }

        if (!formDescripcion.value) {
            mostrarError(formDescripcion, errorDescripcion, 'La descripción es obligatoria.');
            isValid = false;
        } else {
            limpiarError(formDescripcion, errorDescripcion);
        }

        return isValid;
    }

    function validarCodigoCuentaPadreYNivel() {
        let esValido = true;
        const cuentaPadreCodigo = selectCuentaPadre.options[selectCuentaPadre.selectedIndex]?.text.split(" - ")[0].trim();
        let longitudPermitida;

        // Validación de longitud según el nivel seleccionado
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
        } else {
            limpiarError(inputCodigo, errorCodigo);
        }

        // Validación de cuenta padre
        if (cuentaPadreCodigo && !inputCodigo.value.startsWith(cuentaPadreCodigo)) {
            mostrarError(inputCodigo, errorCodigo, 'El código ingresado no pertenece a la cuenta padre seleccionada.');
            esValido = false;
        } else {
            limpiarError(inputCodigo, errorCodigo);
        }

        return esValido;
    }

    function cargarDatosCuenta(button, editable) {
        inputCodigo.value = button.getAttribute('data-codigo');
        formDescripcion.value = button.getAttribute('data-descripcion');
        inputEstado.checked = button.getAttribute('data-estado') === 'true';

        const categoriaSeleccionada = button.getAttribute('data-categoria');
        if (categoriaSeleccionada) {
            Array.from(selectCategoria.options).forEach(option => {
                if (option.value.toLowerCase() === categoriaSeleccionada.toLowerCase()) {
                    option.selected = true;
                }
            });
        }

        cargarCuentasPorCategoria(categoriaSeleccionada, function () {
            const cuentaPadreId = button.getAttribute('data-cuenta-padre');
            if (cuentaPadreId) {
                selectCuentaPadre.value = cuentaPadreId;
            }
        });

        estadoLabel.textContent = inputEstado.checked ? 'Cuenta activa' : 'Cuenta no activa';

        if (!editable) deshabilitarCamposModal();
        else habilitarCamposModal();
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

    saveButton.addEventListener('click', function (e) {
        e.preventDefault();
        if (!validarCamposObligatorios() || !validarCodigoCuentaPadreYNivel()) return;

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

    function mostrarCuentaAgregada(codigo, descripcion) {
        document.getElementById('successMessage').textContent = 'La cuenta ha sido añadida correctamente.';
        document.getElementById('successCodigo').textContent = `Código: ${codigo}`;
        document.getElementById('successDescripcion').textContent = `Descripción: ${descripcion}`;
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
    document.getElementById('editAccountModal').addEventListener('hidden.bs.modal', function () {
        limpiarCamposModal();
    });
});
