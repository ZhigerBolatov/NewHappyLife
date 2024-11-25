//const backEndUrl = 'https://happylifes.org:8000/';
const backEndUrl = 'http://127.0.0.1:8000/';

async function fetchData(url, method, body) {
    let response = null;
    if (body !== null) {
        response = await fetch(backEndUrl + url, {
            method: method,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body:JSON.stringify(body)
        });
    } else {
        response = await fetch(backEndUrl + url, {
            method: method,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
    }
    const data = await response.json();
    return {data: data, status: response.status}
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : '';
};

function getFullMonth() {
    const start = new Date();
    const end = new Date(start);
    end.setMonth(start.getMonth() + 1);

    let range = [];

    while (start <= end) {
        const next = new Date(start);
        start.setDate(start.getDate() + 1);

        const dayObj = {
            date: next.getDate(),
            month: next.getMonth() + 1,
            year: next.getFullYear(),
            weekday: next.toLocaleString('en-US', { weekday: 'short' })
        };
        range.push(dayObj);
    }

    return range;
}

function getTimeSlots(start_time, end_time) {
    const timeSlots = [];
    const start = new Date(`1970-01-01T${start_time}`);
    const end = new Date(`1970-01-01T${end_time}`);

    let currentTime = start;
    while (currentTime < end) {
        const hours = String(currentTime.getHours()).padStart(2, '0');
        const minutes = String(currentTime.getMinutes()).padStart(2, '0');
        timeSlots.push(`${hours}:${minutes}`);

        currentTime.setMinutes(currentTime.getMinutes() + 30);
    }

    return timeSlots;
}

function isTimePassed(timeStr) {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    const [hours, minutes] = timeStr.split(':').map(Number);
    const inputTime = hours * 60 + minutes;
    return currentTime >= inputTime;
}

function isTimeBooked(bookings, date) {
    for (let booking of bookings) {
        let datetime = booking.datetime;
        let time = `${date.getHours()}:${date.getMinutes()}`;
        if (datetime.date == date.getDate() && datetime.month == date.getMonth() + 1 && datetime.time == time) {
            return true
        }
    }
    return false;
}

async function follow_newsletter() {
    const newsletter_email_input = document.getElementById('newsletter_email_input');
    const newsletter_follow_button = document.getElementById('newsletter_follow_button');
    const newsletter_error_text = document.getElementById('newsletter_error_text');
    newsletter_error_text.innerHTML = '';
    const body = {
        email: newsletter_email_input.value
    }
    const newsletters = await fetchData('newsletters', 'POST', body);
    if (newsletters.status == 200) {
        newsletter_email_input.disabled = 'disabled';
        newsletter_email_input.style.color = 'gray';
        newsletter_follow_button.disabled = 'disabled';
        newsletter_follow_button.classList.remove('btn-primary');
        newsletter_follow_button.classList.add('btn-success');
        newsletter_follow_button.innerHTML = 'Followed!';
    } else {
        newsletter_email_input.style.border = '2px solid red';
        newsletter_email_input.style.color = 'red';
        const error_message = document.createElement('p');
        newsletter_error_text.innerHTML = newsletters.data.detail;
    }
}

function newsletter_init() {
    const newsletter_input = document.getElementById('newsletter_email_input');
    const newsletter_follow_button = document.getElementById('newsletter_follow_button');
    const newsletter_error_text = document.getElementById('newsletter_error_text');
    newsletter_input.addEventListener('input', function() {
        let email = String(this.value).toLowerCase();
        let re = /\S+@\S+\.\S+/;
        let is_valid = re.test(email);
        if (!is_valid) {
            this.style.border = '2px solid red';
            this.style.color = 'red';
            newsletter_follow_button.disabled = 'disabled';
        } else {
            this.style.border = null;
            this.style.color = 'black';
            newsletter_follow_button.disabled = '';
        }
    });
}
