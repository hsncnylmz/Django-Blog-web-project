$(document).ready(function () {
    // Sayfa yüklendiğinde like ve dislike sayılarını al ve güncelle
    updateLikeDislikeCounts();

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

                // Like ve dislike sayılarını oturumda sakla
                sessionStorage.setItem('like_count', data.likes);
                sessionStorage.setItem('dislike_count', data.dislikes);
            },
            error: function (xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    });
});

// Like ve dislike sayılarını güncelleyen fonksiyon
function updateLikeDislikeCounts() {
    var likeCount = sessionStorage.getItem('like_count');
    var dislikeCount = sessionStorage.getItem('dislike_count');

    // Eğer oturumda kaydedilmişse sayfa üzerinde güncelle
    if (likeCount !== null && dislikeCount !== null) {
        $(".like-count").html(likeCount);
        $(".dislike-count").html(dislikeCount);
    }
}