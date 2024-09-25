const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', () => {
      const filter = searchInput.value.toLowerCase();
      const rows = document.querySelectorAll('#tabla-cuerpo tr');

      rows.forEach(row => {
        const codigo = row.cells[0].textContent.toLowerCase();
        const descripcion = row.cells[1].textContent.toLowerCase();
        if (codigo.includes(filter) || descripcion.includes(filter)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });

// Obtener el modal
const modalElement = document.getElementById('myModal');
const modal = new bootstrap.Modal(modalElement);

// Agregar evento de clic a cada fila de la tabla
document.querySelectorAll("#tabla-cuerpo tr").forEach((row) => {
  row.addEventListener("click", function () {
    const codigo = this.cells[0].textContent; // Obtiene el código de la fila
    const descripcion = this.cells[1].textContent; // Obtiene la descripción de la fila

    // Actualiza los valores de los inputs del modal
    document.getElementById("modal-codigo").value = codigo;
    document.getElementById("modal-descripcion").value = descripcion;

    // Aplica la animación de entrada al mostrar el modal
    modalElement.classList.remove('animate__fadeOutUp');
    modalElement.classList.add('animate__fadeInDown');
    
    // Muestra el modal
    modal.show();
  });
});

// Configura el evento para cuando se cierre el modal
modalElement.addEventListener('hide.bs.modal', function () {
  // Cambia a la animación de salida
  modalElement.classList.remove('animate__fadeInDown');
  modalElement.classList.add('animate__fadeOutUp');
});

