document.addEventListener("DOMContentLoaded", function () {
    var headings = document.querySelectorAll('.post h3');

    if (headings.length > 0) {
        var headingsList = document.getElementById('headings-list') || document.createElement('div');
        headingsList.id = 'headings-list';

        var ul = document.createElement('ul');
        var h3 = document.createElement('h3');
        h3.innerText = 'Başlıklar';
        headingsList.appendChild(h3);
        headingsList.appendChild(ul);

        headings.forEach(function (heading, index) {
            var headingId = 'heading-' + index;
            heading.setAttribute('id', headingId);

            var li = document.createElement('li');
            var link = document.createElement('a');
            link.href = '#' + headingId;
            link.innerText = heading.innerText;
            link.classList.add('heading-link');

            li.appendChild(link);
            ul.appendChild(li);
        });

        // Belirli div içine başlıkları ekleyin
        var HeadingsDiv = document.getElementById('headinglist');

        // Kontrol ekleyin
        if (HeadingsDiv !== null) {
            HeadingsDiv.appendChild(headingsList);
        } else {
            console.error("Headinglist div not found");
        }
    }
});
