document.addEventListener('DOMContentLoaded', function() {
    var viewProductLinks = document.querySelectorAll('.view-product');
    
    viewProductLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            var imageUrl = link.getAttribute('data-image-url');
            viewProduct(imageUrl);
        });
    });
});

function viewProduct(imageUrl) {
    // Establece la URL de la imagen en el modal
    document.getElementById('productModalImage').src = imageUrl;
    // Muestra el modal
    var myModal = new bootstrap.Modal(document.getElementById('productModal'), {
        keyboard: false
    });
    myModal.show();
}
