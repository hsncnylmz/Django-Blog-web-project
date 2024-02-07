// reaction.js

document.addEventListener("DOMContentLoaded", function () {
    const reactionButtons = document.querySelectorAll(".reaction-btn");

    reactionButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const reactionType = button.dataset.reactionType;
            const blogSlug = button.closest(".container").dataset.blogSlug;

            const formData = new FormData();
            formData.append("reaction_type", reactionType);
            formData.append("csrfmiddlewaretoken", getCSRFToken());

            // Send AJAX request
            fetch(`/blog/${blogSlug}/reaction/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
            .then(response => response.json())
            .then(data => updateReactionCounts(data.reaction_counts));
        });
    });

    function updateReactionCounts(counts) {
        // Update the reaction counts on the page
        document.getElementById('count-like').innerText = counts.like_count;
        document.getElementById('count-dislike').innerText = counts.dislike_count;
        document.getElementById('count-laugh').innerText = counts.laugh_count;
        document.getElementById('count-surprise').innerText = counts.surprise_count;
        document.getElementById('count-sad').innerText = counts.sad_count;
        // Diğer reaksiyon sayılarını da benzer şekilde güncelleyin
    }

    function getCSRFToken() {
        // Get the CSRF token from the cookie or wherever it's stored
        const name = "csrftoken=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(";");

        for (let i = 0; i < cookieArray.length; i++) {
            let cookie = cookieArray[i].trim();
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length, cookie.length);
            }
        }

        return "";
    }
});
