async function login(username, password) {
    const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        window.location.href = '/api/map/';
    } else {
        alert('Login failed');
    }
}

// Добавляем токен в заголовки всех API запросов
fetch('/api/protected/', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
});