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
    const modal = document.getElementById('eventModal');
    const form = document.getElementById('eventForm');

    if (!modal || !form) return;

    map.events.add('click', function(e) {
        const coords = e.get('coords');
        document.getElementById('latitude').value = coords[0].toPrecision(8);
        document.getElementById('longitude').value = coords[1].toPrecision(8);
        modal.style.display = 'block';
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        createEvent(map);
        modal.style.display = 'none';
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        createEvent(map);
        modal.style.display = 'none';
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
        if (response.status === 401) {
            window.location.href = '/login/';
            throw new Error('Token expired or invalid');
        }
        if (!response.ok) throw new Error('Ошибка загрузки мероприятий');
        return response.json();
    })
    .then(events => {
        addEventsToMap(map, events);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('status').textContent = error.message;
    });
}

function createEvent(map) {
    const token = getJWTToken();
    if (!token) {
        window.location.href = '/login/';
        return;
    }

    const formData = new FormData(document.getElementById('eventForm'));
    const eventData = {
        title: formData.get('title'),
        description: formData.get('description'),
        datetime: formData.get('datetime'),
        latitude: formData.get('latitude'),
        longitude: formData.get('longitude'),
        category: formData.get('category')
    };

    fetch('/api/events/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(eventData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка создания мероприятия');
        return response.json();
    })
    .then(event => {
        addEventsToMap(map, [event]);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось создать мероприятие');
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
    // Очищаем старые метки, если они есть
    map.geoObjects.removeAll();

    // Проверяем, что events - массив
    if (!Array.isArray(events)) {
        console.error('Ожидался массив мероприятий, получено:', events);
        return;
    }

    // Создаем кластеризатор для группировки меток
    const clusterer = new ymaps.Clusterer({
        preset: 'islands#invertedRedClusterIcons',
        clusterDisableClickZoom: true,
        clusterHideIconOnBalloonOpen: false,
        geoObjectHideIconOnBalloonOpen: false
    });

    // Создаем массив для меток
    const placemarks = [];

    events.forEach(event => {
        try {
            // Проверяем наличие обязательных полей
            if (!event.latitude || !event.longitude) {
                console.warn('У мероприятия отсутствуют координаты:', event);
                return;
            }

            // Создаем содержимое балуна
            const balloonContent = `
                <div style="padding: 10px; max-width: 300px;">
                    <h3 style="margin-top: 0; color: #1e88e5;">${event.title || 'Без названия'}</h3>
                    <p>${event.description || 'Описание отсутствует'}</p>
                    <div style="margin-top: 10px;">
                        <small>
                            <strong>Дата:</strong> ${event.datetime ? new Date(event.datetime).toLocaleString() : 'Не указана'}<br>
                            <strong>Категория:</strong> ${event.category?.name || 'Не указана'}
                        </small>
                    </div>
                </div>
            `;

            // Создаем метку
            const placemark = new ymaps.Placemark(
                [event.latitude, event.longitude],
                {
                    balloonContent: balloonContent,
                    hintContent: event.title || 'Мероприятие',
                },
                {
                    preset: 'islands#redEventCircleIcon',
                    balloonCloseButton: true,
                    hideIconOnBalloonOpen: false
                }
            );

            // Добавляем обработчик клика
            placemark.events.add('click', function() {
                placemark.balloon.open();
            });

            placemarks.push(placemark);

        } catch (e) {
            console.error('Ошибка создания метки для мероприятия:', event, e);
        }
    });

    // Добавляем метки в кластеризатор
    if (placemarks.length > 0) {
        clusterer.add(placemarks);
        map.geoObjects.add(clusterer);

        // Автоматически подбираем оптимальный масштаб
        if (placemarks.length > 1) {
            map.setBounds(clusterer.getBounds(), {
                checkZoomRange: true,
                zoomMargin: 50
            });
        } else if (placemarks.length === 1) {
            map.setCenter([placemarks[0].geometry.getCoordinates()], 14);
        }
    } else {
        console.warn('Нет мероприятий для отображения');
        document.getElementById('status').textContent = 'Мероприятия не найдены';
    }
}

function initApplication(map) {

    loadEvents(map);
    initLogoutButton();
    initModal(map);
}

