$remember_checkbox = document.querySelector('.remember-checkbox');
console.log($remember_checkbox);
$remember_checkbox.addEventListener('click', function () {
    if ($remember_checkbox.checked) {
        console.log('checked');
        $email = document.querySelector('.email').value;
        if ($email) {
            localStorage.setItem('email', $email);
        }
    } else {
        console.log('unchecked');
        $email = document.querySelector('.email').value;
        localStorage.removeItem('email');
    }
});

if (localStorage.getItem('email')) {
    console.log('email');
    $email = document.querySelector('.email');
    $email.value = localStorage.getItem('email');
    $remember_checkbox.checked = true;
}