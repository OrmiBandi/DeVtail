const $holiday_p1 = document.querySelector('.holiday_p_1');
const $holiday_p2 = document.querySelector('.holiday_p_2');
const $holiday_p3 = document.querySelector('.holiday_p_3');
// 목표 날짜 설정
// const countDownDate = new Date("Mar 31, 2024 23:59:59").getTime();
const year = $holiday_p1.dataset.holiday.split(' ')[0].replace('년', '');
const month = $holiday_p1.dataset.holiday.split(' ')[1].replace('월', '');
const day = $holiday_p1.dataset.holiday.split(' ')[2].replace('일', '');
const countDownDate = new Date(year, month, day).getTime();
let interval;
// 1초마다 업데이트되는 함수
function countdownFunction(dest_date) {
    const updateCountdown = () => {
        const now = new Date().getTime();
        const distance = dest_date - now;
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update the DOM elements with the countdown values
        const $day_span = document.querySelector('.day');
        $day_span.style.setProperty('--value', days);

        const $hour_span = document.querySelector('.hour');
        $hour_span.style.setProperty('--value', hours);

        const $min_span = document.querySelector('.min');
        $min_span.style.setProperty('--value', minutes);

        const $sec_span = document.querySelector('.sec');
        $sec_span.style.setProperty('--value', seconds);
    };
    // Call the updateCountdown function every second
    clearInterval(interval);
    interval = setInterval(updateCountdown, 1000);
}

countdownFunction(countDownDate);

const $holiday_btn1 = document.querySelector('.holiday_btn_1');
const $holiday_btn2 = document.querySelector('.holiday_btn_2');
const $holiday_btn3 = document.querySelector('.holiday_btn_3');
const $holiday_title = document.querySelector('.holiday_title');
const holiday_name1 = $holiday_p1.dataset.name;
const holiday_name2 = $holiday_p2.dataset.name;
const holiday_name3 = $holiday_p3.dataset.name;

const buttons = [$holiday_btn1, $holiday_btn2, $holiday_btn3];
const paragraphs = [$holiday_p1, $holiday_p2, $holiday_p3];
const holiday_names = [holiday_name1, holiday_name2, holiday_name3];

buttons.forEach((button, index) => {
    button.addEventListener('click', () => {
        paragraphs.forEach((paragraph, idx) => {
            if (index === idx) {
                paragraph.classList.add('font-semibold');
                const year = paragraph.dataset.holiday.split(' ')[0].replace('년', '');
                const month = paragraph.dataset.holiday.split(' ')[1].replace('월', '');
                const day = paragraph.dataset.holiday.split(' ')[2].replace('일', '');
                const countDownDate = new Date(year, month, day).getTime();
                countdownFunction(countDownDate);
                $holiday_title.textContent = holiday_names[index];
            } else {
                paragraph.classList.remove('font-semibold');
            }
        });
    });
});