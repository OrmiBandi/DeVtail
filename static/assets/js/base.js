const dropdowns = document.getElementsByClassName("dropdown");
var i;

for (i = 0; i < dropdowns.length; i++) {
    dropdowns[i].addEventListener('click', function () {
        var j;
        for (j = 0; j < dropdowns.length; j++) {
            if (dropdowns[j] !== this) {
                dropdowns[j].removeAttribute('open');
            }
        }
    });
}