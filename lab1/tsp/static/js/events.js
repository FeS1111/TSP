document.addEventListener('DOMContentLoaded', function() {
    const token = window.ACCESS_TOKEN;
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    // Инициализация карты
    ymaps.ready(function() {
        const map = new ymaps.Map('map', {
            center: [55.76, 37.64],
            zoom: 10
        });

        // Элементы управления
        const modal = document.getElementById('eventModal');
        const closeBtn = document.querySelector('.close-btn');

        // Функции управления модальным окном
        function showModal() {
            modal.style.display = 'block';
        }

        function hideModal() {
            modal.style.display = 'none';
        }

        // Обработчики событий
        closeBtn.addEventListener('click', hideModal);

        // Клик по карте - показываем модальное окно
        map.events.add('click', function(e) {
            const coords = e.get('coords');
            document.getElementById('latitude').value = coords[0].toPrecision(8);
            document.getElementById('longitude').value = coords[1].toPrecision(8);
            showModal();
        });

        // Обработчик кнопки выхода
        document.getElementById('logoutBtn').addEventListener('click', function() {
            fetch('/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            }).then(() => {
                window.location.href = '/login/';
            });
        });

        // Загрузка мероприятий на карту
        loadEvents(map, token);
    });

    async function loadEvents(map, token) {
        try {
            const response = await fetch('/api/events/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const events = await response.json();
                addEventsToMap(map, events);
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function addEventsToMap(map, events) {
        events.forEach(event => {
            const placemark = new ymaps.Placemark(
                [parseFloat(event.latitude), parseFloat(event.longitude)],
                {
                    hintContent: event.title,
                    balloonContent: event.description || 'Нет описания'
                }
            );
            map.geoObjects.add(placemark);
        });
    }
});