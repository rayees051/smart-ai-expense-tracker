// DARK MODE

function toggleDarkMode() {

    document.body.classList.toggle('dark-mode');

    if (document.body.classList.contains('dark-mode')) {

        localStorage.setItem('darkMode', 'enabled');

    } else {

        localStorage.setItem('darkMode', 'disabled');

    }

}


// LOAD DARK MODE ON REFRESH

window.onload = function () {

    if (localStorage.getItem('darkMode') === 'enabled') {

        document.body.classList.add('dark-mode');

    }

};


// DELETE CONFIRMATION

document.addEventListener('DOMContentLoaded', function () {

    const deleteButtons = document.querySelectorAll('.btn-danger');

    deleteButtons.forEach(function (button) {

        button.addEventListener('click', function (event) {

            const confirmDelete = confirm(
                'Are you sure you want to delete this expense?'
            );

            if (!confirmDelete) {

                event.preventDefault();

            }

        });

    });

});


// SIMPLE CARD ANIMATION

document.addEventListener('DOMContentLoaded', function () {

    const cards = document.querySelectorAll('.card');

    cards.forEach(function (card, index) {

        card.style.opacity = 0;

        setTimeout(() => {

            card.style.transition = '0.5s';
            card.style.opacity = 1;

        }, index * 150);

    });

});