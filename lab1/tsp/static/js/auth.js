// static/js/auth.js
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const response = await fetch('/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        // Сохраняем токен в localStorage и sessionStorage
        localStorage.setItem('access_token', data.access);
        sessionStorage.setItem('access_token', data.access);
        
        // Перенаправляем с токеном
        window.location.href = '/api/events/';
    } else {
        alert('Ошибка авторизации');
    }
});
