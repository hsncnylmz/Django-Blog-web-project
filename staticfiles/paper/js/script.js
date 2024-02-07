$(document).ready(function () {
    // Like ve Dislike işlemleri
    $(".like-form, .dislike-form").submit(function (e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function (data) {
                // Her iki durumu da güncelle
                $(".like-count").html(data.likes);
                $(".dislike-count").html(data.dislikes);
            },
            error: function (xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Makale Türü seçeneği değiştiğinde tetiklenecek fonksiyon
    function handlePaperTypeChange() {
        var paperTypeCheckbox = document.getElementById('id_paper_type');
        var priceField = document.getElementById('priceField');

        // Eğer makale ücretli ise, fiyat alanını göster, değilse gizle
        priceField.style.display = paperTypeCheckbox.checked && paperTypeCheckbox.value === 'paid' ? 'block' : 'none';
    }

    // İlk yüklenişte de kontrol et
    handlePaperTypeChange();

    // Makale Türü seçeneği değişikliklerini dinle
    document.getElementById('id_paper_type').addEventListener('change', handlePaperTypeChange);
});