let eventForm = null;
let eventModal = null;
let currentEvents = [];

function initYandexMap() {
    ymaps.ready(() => {
        console.log("YMaps ready!");

        // Создаем карту
        const map = new ymaps.Map('map', {
            center: [53.195873, 50.100193],
            zoom: 12,
            controls: ['zoomControl', 'typeSelector']
        });

        setTimeout(() => {
            map.setCenter([53.195873, 50.100193], 12, {
                checkZoomRange: true
            });
        }, 500);

        if (typeof initApplication === 'function') {
            initApplication(map);
        }
    });
}

function loadYandexMaps() {
    return new Promise((resolve, reject) => {
        if (typeof ymaps !== 'undefined') {
            console.log("API уже загружен");
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://api-maps.yandex.ru/2.1/?apikey=73768dcf-5edf-40ff-b1c9-d7a3fabadc62&lang=ru_RU';
        script.onload = () => {
            console.log("API Яндекс.Карт успешно загружен");
            resolve();
        };

        script.onerror = () => {
            console.error("Ошибка загрузки API Яндекс.Карт");
            reject();
        };
        document.head.appendChild(script);
    });
}

async function initializeApp() {
    console.log("Запуск initializeApp...");

    // Проверка авторизации
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    try {
        // Загрузка API
        await loadYandexMaps();

        // Создание карты с гарантированным центрированием
        initYandexMap();

    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('status').textContent = 'Ошибка загрузки карты';
    }
}

document.addEventListener('DOMContentLoaded', initializeApp);

function getJWTToken() {
    return localStorage.getItem('access_token');
}

function initModal(map) {
    eventModal = document.getElementById('eventModal');
    eventForm = document.getElementById('eventForm');
    const cancelBtn = document.querySelector('.close-btn');

    if (!eventModal || !eventForm || !cancelBtn) return;

    map.events.add('click', function(e) {
        const coords = e.get('coords');
        document.getElementById('latitude').value = coords[0].toFixed(6);
        document.getElementById('longitude').value = coords[1].toFixed(6);
        eventModal.style.display = 'block';
    });

    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();
        createEvent(map);
    });

    cancelBtn.addEventListener('click', function() {
        eventModal.style.display = 'none';
        eventForm.reset();
    });
}

function loadEvents(map) {
    const token = getJWTToken();
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    fetch('/api/events/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка загрузки мероприятий');
        return response.json();
    })
    .then(events => {
        currentEvents = events; // Сохраняем мероприятия
        addEventsToMap(map, events);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('status').textContent = error.message;
    });
}

function createEvent(map) {
    const token = getJWTToken();
    if (!token) return;

    const formData = {
        title: eventForm.querySelector('[name="title"]').value.trim(),
        description: eventForm.querySelector('[name="description"]').value.trim(),
        datetime: new Date(eventForm.querySelector('[name="datetime"]').value).toISOString(),
        latitude: parseFloat(eventForm.querySelector('#latitude').value),
        longitude: parseFloat(eventForm.querySelector('#longitude').value),
        category: parseInt(eventForm.querySelector('[name="category"]').value)
    };

    fetch('/api/events/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка создания мероприятия');
        return response.json();
    })
    .then(newEvent => {
        // Добавляем новое мероприятие к текущим
        currentEvents.push(newEvent);
        // Полностью перерисовываем карту с обновленным списком
        addEventsToMap(map, currentEvents);
        eventModal.style.display = 'none';
        eventForm.reset();
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert(`Ошибка: ${error.message}`);
    });
}

function initLogoutButton() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

function logout() {
    fetch('/logout/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'Content-Type': 'application/json'
        }
    }).catch(error => {
        console.error('Ошибка при выходе:', error);
    }).finally(() => {
        // 2. Очищаем клиентские данные
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        // 3. Перенаправляем на страницу входа с параметром, предотвращающим цикл
        window.location.href = '/login/?logout=true';
    });
}

function addEventsToMap(map, events) {
    if (!map || !map.geoObjects) return;

    // Сохраняем текущий вид карты
    const currentCenter = map.getCenter();
    const currentZoom = map.getZoom();

    // Очищаем старые метки
    map.geoObjects.removeAll();

    // Создаем кластеризатор
    const clusterer = new ymaps.Clusterer({
        preset: 'islands#invertedRedClusterIcons',
        clusterDisableClickZoom: true
    });

    // Создаем метки для всех мероприятий
    const placemarks = events.map(event => {
        return new ymaps.Placemark(
            [event.latitude, event.longitude],
            {
                balloonContent: `
                    <h3>${event.title || 'Без названия'}</h3>
                    <p>${event.description || 'Нет описания'}</p>
                    <small>${new Date(event.datetime).toLocaleString()}</small>
                `,
                hintContent: event.title || 'Мероприятие'
            },
            {
                preset: 'islands#redIcon',
                balloonCloseButton: true
            }
        );
    });

    // Добавляем все метки на карту
    if (placemarks.length > 0) {
        clusterer.add(placemarks);
        map.geoObjects.add(clusterer);
    }

    // Восстанавливаем позицию карты
    map.setCenter(currentCenter, currentZoom, { checkZoomRange: true });
}

function initApplication(map) {

    loadEvents(map);
    initLogoutButton();
    initModal(map);
}

