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
