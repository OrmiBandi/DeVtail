const dropdowns = document.getElementsByClassName("dropdown");
var i;
const $html = document.querySelector('html');
const theme = localStorage.getItem('theme');
const $theme_btn = document.querySelector('.theme_btn');

if (theme === 'dark') {
    $html.setAttribute('data-theme', 'dark');
    $theme_btn.setAttribute('value', 'light');
} else {
    $html.setAttribute('data-theme', 'light');
    $theme_btn.setAttribute('value', 'dark');
}

for (i = 0; i < dropdowns.length; i++) {
    dropdowns[i].addEventListener('click', function () {
        var j;
        for (j = 0; j < dropdowns.length; j++) {
            if (dropdowns[j] !== this) {
                dropdowns[j].removeAttribute('open');
            }
        }
    });

$theme_btn.addEventListener('click', () => {
    const current_theme = localStorage.getItem('theme');
    if (current_theme === 'dark') {
        localStorage.setItem('theme', 'light');
    } else {
        localStorage.setItem('theme', 'dark');
    }
});
