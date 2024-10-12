document.addEventListener("DOMContentLoaded", function() {
  const rows = document.querySelectorAll('#tabla-cuentas tbody tr.cuenta-padre'); // Solo cuentas principales
  let rowsPerPage = parseInt(document.getElementById('records-per-page').value);
  let totalRows = rows.length;
  let totalPages = Math.ceil(totalRows / rowsPerPage);
  let currentPage = 1;

  function showPage(page) {
      const start = (page - 1) * rowsPerPage;
      const end = start + rowsPerPage;

      // Mostrar solo las cuentas principales
      rows.forEach((row, index) => {
          row.style.display = index >= start && index < end ? '' : 'none';

          // Ocultar las subcuentas cuando la cuenta principal no esté visible
          if (index < start || index >= end) {
              const cuentaId = row.getAttribute('data-cuenta-id');
              const subcuentas = document.querySelectorAll(`.subcuenta-${cuentaId}`);
              subcuentas.forEach(subcuenta => subcuenta.classList.add('d-none'));
          }
      });

      updatePagination();
  }

  function updatePagination() {
      const pagination = document.getElementById('pagination');
      pagination.innerHTML = `
          <li class="page-item">
              <a class="page-link" href="#" aria-label="Previous" id="prev-page">
                  <span aria-hidden="true">&laquo;</span>
              </a>
          </li>
      `;

      const maxPagesToShow = 5;
      const startPage = Math.max(currentPage - 2, 1);
      const endPage = Math.min(startPage + maxPagesToShow - 1, totalPages);

      if (startPage > 1) {
          pagination.innerHTML += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
          if (startPage > 2) {
              pagination.innerHTML += `<li class="page-item disabled"><a class="page-link" href="#">...</a></li>`;
          }
      }

      for (let i = startPage; i <= endPage; i++) {
          const activeClass = i === currentPage ? 'active' : '';
          pagination.innerHTML += `
              <li class="page-item ${activeClass}">
                  <a class="page-link" href="#" data-page="${i}">${i}</a>
              </li>
          `;
      }

      if (endPage < totalPages) {
          if (endPage < totalPages - 1) {
              pagination.innerHTML += `<li class="page-item disabled"><a class="page-link" href="#">...</a></li>`;
          }
          pagination.innerHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
      }

      pagination.innerHTML += `
          <li class="page-item">
              <a class="page-link" href="#" aria-label="Next" id="next-page">
                  <span aria-hidden="true">&raquo;</span>
              </a>
          </li>
      `;

      document.querySelector('#prev-page').addEventListener('click', function(e) {
          e.preventDefault();
          if (currentPage > 1) {
              currentPage--;
              showPage(currentPage);
          }
      });

      document.querySelector('#next-page').addEventListener('click', function(e) {
          e.preventDefault();
          if (currentPage < totalPages) {
              currentPage++;
              showPage(currentPage);
          }
      });

      document.querySelectorAll('.page-link[data-page]').forEach(link => {
          link.addEventListener('click', function(e) {
              e.preventDefault();
              currentPage = parseInt(e.target.getAttribute('data-page'));
              showPage(currentPage);
          });
      });
  }

  document.getElementById('records-per-page').addEventListener('input', function() {
      rowsPerPage = parseInt(this.value);
      totalPages = Math.ceil(totalRows / rowsPerPage);
      currentPage = 1;
      showPage(currentPage);
  });

  showPage(currentPage);
});
