function showFile(inputId, previewId) {
    const fileInput = document.getElementById(`id_${inputId}`);
    const preview = document.getElementById(previewId);

    const file = fileInput.files[0];

    if (file) {
        preview.style.display = 'block';

        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };

        reader.readAsDataURL(file);
    } else {
        preview.style.display = 'none';
    }
}


$(document).ready(function () {
    $('#id_birth_date').on('input', function () {
        // Kullanıcının girişini dinamik olarak kontrol edin
        let value = $(this).val();
        
        // Giriş değerini kontrol edin ve gerekirse ayraç ekleyin
        if (/^\d{0,2}\/?\d{0,2}\/?\d{0,4}$/.test(value)) {
            // Giriş sınırları içindeyse ve regex'e uyan bir formattaysa ayraç ekleyin
            if (value.length === 2 || value.length === 5) {
                $(this).val(value + '/');
            }
        } else {
            // Giriş sınırları dışında ise son karakteri silin
            $(this).val(value.slice(0, -1));
        }
    });
});