const $todos = document.querySelector('#scheduledTodos');
const $todoElements = $todos.querySelectorAll('li');
const $countContainer = document.getElementById('todoCounting');
const $todoCountingName = document.getElementById('todoCountingName');
let interval;

const firstTodoElement = $todoElements[0];

if (firstTodoElement) {
  firstTodoElement.classList.add('font-semibold');
  changeTodoCount($countContainer, firstTodoElement);
}


$todoElements.forEach((todoElement) => {
  todoElement.addEventListener('click', () => {
    manageFontClass(todoElement);
    changeTodoCount($countContainer, todoElement);
  })
})


function changeTodoCount(countContainer, todoElement) {
  let data = todoElement.dataset
  $todoCountingName.textContent = data.todoTitle

  const countDownDate = new Date(data.todoDate).getTime();

  const updateCountdown = () => {
    const now = new Date().getTime();
    const distance = countDownDate - now;
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    $day_span = document.querySelector('.day');
    $day_span.style.setProperty('--value', days);

    $hour_span = document.querySelector('.hour');
    $hour_span.style.setProperty('--value', hours);

    $min_span = document.querySelector('.min');
    $min_span.style.setProperty('--value', minutes);

    $sec_span = document.querySelector('.sec');
    $sec_span.style.setProperty('--value', seconds);

    if (distance < 1) {
      clearInterval(interval);
      $day_span.style.setProperty('--value', '00');
      $hour_span.style.setProperty('--value', '00');
      $min_span.style.setProperty('--value', '00');
      $sec_span.style.setProperty('--value', '00');
    }
  };

  clearInterval(interval);
  updateCountdown();
  interval = setInterval(updateCountdown, 1000);
}

function manageFontClass(clickedElement) {
  $todoElements.forEach((element) => {
    if (element !== clickedElement) {
      element.classList.remove('font-semibold');
    }
  });
  clickedElement.classList.add('font-semibold');
}