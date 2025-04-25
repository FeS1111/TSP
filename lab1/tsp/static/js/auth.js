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

async function register(username, email, password) {
    const response = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password })
    });

    if (response.ok) {
        const data = await response.json();
        alert(data.message || 'Registration successful!');
        window.location.href = '/map/';
    } else {
        const errorData = await response.json();
        alert(errorData.error || 'Registration failed');
    }
}

// Добавляем токен в заголовки всех API запросов
fetch('/api/protected/', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
});