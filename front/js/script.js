const backEndUrl = 'https://happylifes.org:8000/';
//const backEndUrl = 'http://127.0.0.1:8000/';

async function fetchData(url, method, body, content_type = 'application/json') {
    let response = null;
    let headers = {};
    if (content_type == 'multipart/form-data') {
        headers = {
            'X-CSRFToken': getCookie('csrftoken')
        };
    } else {
        headers = {
            'Content-Type': content_type,
            'X-CSRFToken': getCookie('csrftoken')
        };
        if (body !== null) {
            body = JSON.stringify(body);
        }
    }
    if (body !== null) {
        response = await fetch(backEndUrl + url, {
            method: method,
            credentials: 'include',
            headers: headers,
            body: body
        });
    } else {
        response = await fetch(backEndUrl + url, {
            method: method,
            credentials: 'include',
            headers: headers
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
            date: String(next.getDate()).padStart(2, '0'),
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
        let time = `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
        if (datetime.date == date.getDate() && datetime.month == date.getMonth() + 1 && datetime.time == time && booking.status != 'Rejected') {
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

function validate_email(email){
    var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
    return reg.test(email);
}

async function load_auth_route() {
    let flag = false;
    const is_authenticated_response = await fetchData('auth', 'GET', null);
    if (is_authenticated_response.status == 200) {
        flag = is_authenticated_response.data.is_authenticated;
    }
    const user_link = document.getElementById('user_link');
    if (flag) {
        const li1 = document.createElement('li');
        const a1 = document.createElement('a');
        a1.classList.add('dropdown-item')
        a1.href = 'cabinet.html';
        a1.innerHTML = 'Cabinet';
        li1.appendChild(a1);
        user_link.appendChild(li1);

        const li2 = document.createElement('li');
        const a2 = document.createElement('a');
        a2.classList.add('dropdown-item')
        a2.innerHTML = 'Log Out';
        a2.onclick = logout;
        li2.appendChild(a2);
        user_link.appendChild(li2);

        user_link.dataset.is_authenticated = 'true';


        const cabinet_nav = document.getElementById('cabinet_nav');
        if (cabinet_nav != null) {
            let cabinet_routing = null;
            if (is_authenticated_response.data.role == 'PT') {
                cabinet_routing = [
                    {href: 'cabinet.html', text: 'Profile'},
                    {href: 'patient_history.html', text: 'History'},
                    {href: 'patient_appointments.html', text: 'Appointments'},
                ];
            } else if (is_authenticated_response.data.role == 'DC') {
                cabinet_routing = [
                    {href: 'cabinet.html', text: 'Profile'},
                    {href: 'doctor_history.html', text: 'History'},
                    {href: 'doctor_appointments.html', text: 'Appointments'},
                    {href: 'doctor_schedule.html', text: 'Schedule'},
                    {href: 'doctors_assistant.html', text: 'Assistant'},
                    {href: 'doctor_statistics.html', text: 'Statistics'},
                ];
            } else if (is_authenticated_response.data.role == 'AD') {
                cabinet_routing = [
                    {href: 'cabinet.html', text: 'Profile'},
                    {href: 'admin_appointments.html', text: 'Appointments'},
                    {href: 'doctor_register.html', text: 'Register Doctor'},
                    {href: 'admin_schedule.html', text: 'Schedules'},
                    {href: 'admin_statistics.html', text: 'Statistics'},
                ];
            }
            for (let route of cabinet_routing) {
                let li = document.createElement('li');
                li.classList.add('nav-item');
                let a = document.createElement('a');
                a.classList.add('nav-link');
                let current_url = window.location.pathname.split( '/' ).pop();
                if (current_url == route.href) {
                    a.classList.add('active');
                }
                a.href = route.href;
                a.innerHTML = route.text;

                li.appendChild(a);
                cabinet_nav.appendChild(li);
            }
        }
    } else {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.classList.add('dropdown-item')
        a.href = 'login.html';
        a.innerHTML = 'Log In';
        li.appendChild(a);
        user_link.appendChild(li);
        user_link.dataset.is_authenticated = 'false';
    }
    return is_authenticated_response.data.role;
}

async function logout() {
    const log_out_response = await fetchData('log_out', 'POST', null);
    if (log_out_response.status == 200) {
        window.location.reload();
    }
}

async function check_authentication() {
    const is_authenticated_response = await fetchData('auth', 'GET', null);
    if (is_authenticated_response.status == 200) {
        return is_authenticated_response.data.is_authenticated;
    }
    return false;
}

async function log_out() {
    await logout();
    window.location.href = 'index.html';
}
