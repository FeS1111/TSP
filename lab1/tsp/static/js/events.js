let eventForm = null;
let eventModal = null;
let map;
let currentEvents = [];

function initYandexMap() {
    ymaps.ready(() => {
        console.log("YMaps ready!");
        map = new ymaps.Map('map', {
            center: [53.195873, 50.100193],
            zoom: 12,
            controls: ['zoomControl', 'typeSelector']
        });

        // Инициализация меток и балунов
        initEventBalloons(map);
        loadEvents(map);
        initLogoutButton();
        initModal(map);
    });
}

function initEventBalloons(map) {
    // Обработчик клика по метке
    map.geoObjects.events.add('click', function(e) {
        const placemark = e.get('target');
        const eventData = placemark.properties.get('eventData');

        if (eventData) {
            // Генерируем содержимое балуна
            const balloonContent = updateBalloonContent(eventData);
            console.log('Opening balloon for:', eventData); // Логирование

            // Открываем балун с кастомным содержимым
            placemark.balloon.open(
                balloonContent,
                {
                    closeButton: false,
                    panelMaxMapArea: 0 // Разрешить выход за пределы карты
                }
            );

            // Принудительно устанавливаем z-index
            setTimeout(() => {
                const balloonElement = document.querySelector('.ymaps-balloon');
                if (balloonElement) {
                    balloonElement.style.zIndex = '9999';
                }
            }, 50);
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
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 500) {
            throw new Error('Серверная ошибка. Проверьте логи сервера');
        }
        if (!response.ok) throw new Error('Ошибка загрузки мероприятий');
        return response.json();
    })
    .then(events => {
        currentEvents = events;
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
        // Закрываем модальное окно и очищаем форму
        eventModal.style.display = 'none';
        eventForm.reset();

        // Полностью перезагружаем мероприятия с сервера
        loadEvents(map);
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
    map.geoObjects.removeAll();
    currentEvents = events;

    events.forEach(event => {
        const placemark = new ymaps.Placemark(
            [event.latitude, event.longitude],
            {
                eventData: event,
                hintContent: event.title,
                balloonContent: updateBalloonContent(event)
            },
            {
                preset: 'islands#redIcon',
                balloonCloseButton: false,
                openBalloonOnClick: true
            }
        );

        map.geoObjects.add(placemark);
    });
}

function updateBalloonContent(event) {
    const currentUser = JSON.parse(localStorage.getItem('user'));
    const isCreator = currentUser && event.creator === currentUser.id;

    return `
        <div class="custom-balloon" style="
            min-width: 300px;
            padding: 20px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            position: relative;
            z-index: 9999;
        ">
            <!-- Кнопка закрытия балуна -->
            <div class="close-balloon" style="
                position: absolute;
                top: 10px;
                right: 10px;
                width: 24px;
                height: 24px;
                background: #fff;
                border-radius: 50%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                line-height: 1;
            ">
                ×
            </div>

            <h3 style="margin:0 0 12px 0; color: #2c3e50;">${event.title || 'Название мероприятия'}</h3>
            <p style="margin:0 0 10px 0; color: #7f8c8d;">${event.description || 'Описание отсутствует'}</p>
            <div style="margin-bottom: 15px; color: #95a5a6;">
                ${new Date(event.datetime).toLocaleString()}
            </div>

            <div style="border-top: 1px solid #ecf0f1; padding-top: 15px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-weight: bold; color: #27ae60;">Идут:</span>
                    <span style="margin:0 10px; color: #2c3e50;">${event.going_count || 0}</span>
                    <select style="
                        flex: 1;
                        padding: 8px;
                        border: 1px solid #bdc3c7;
                        border-radius: 4px;
                        background: #f9f9f9;
                    ">
                        ${(event.going_users || []).map(user => `
                            <option>${typeof user === 'object' ? user.username : user}</option>
                        `).join('')}
                    </select>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <button class="reaction-btn"
                            data-event-id="${event.event_id}"
                            data-type="going"
                            style="
                                padding: 10px;
                                background: ${event.user_reaction === 'going' ? '#1a7a4d' : '#27ae60'};
                                color: white;
                                border: none;
                                border-radius: 4px;
                                cursor: pointer;
                                transition: 0.3s;
                                opacity: ${event.user_reaction === 'going' ? '0.8' : '1'};
                            ">
                        ${event.user_reaction === 'going' ? '✔ Вы идёте' : 'Пойду'}
                    </button>
                    <button class="reaction-btn"
                            data-event-id="${event.event_id}"
                            data-type="not_going"
                            style="
                                padding: 10px;
                                background: ${event.user_reaction === 'not_going' ? '#a83227' : '#e74c3c'};
                                color: white;
                                border: none;
                                border-radius: 4px;
                                cursor: pointer;
                                transition: 0.3s;
                                opacity: ${event.user_reaction === 'not_going' ? '0.8' : '1'};
                            ">
                        ${event.user_reaction === 'not_going' ? '✖ Вы не идёте' : 'Не пойду'}
                    </button>
                </div>

                <!-- Кнопка удаления для создателя -->
                ${isCreator ? `
                <button class="delete-event-btn"
                        data-event-id="${event.event_id}"
                        style="
                            width: 100%;
                            padding: 10px;
                            background: #dc3545;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                            transition: 0.3s;
                        ">
                    Удалить мероприятие
                </button>
                ` : ''}
            </div>
        </div>
    `;
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('close-balloon')) {
        map.balloon.close();
    }
});

function handleDeleteEvent(eventId) {
    const token = getJWTToken();
    if (!token) return;

    if (!confirm('Вы уверены, что хотите удалить мероприятие?')) return;

    fetch(`/api/events/${eventId}/`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    })
    .then(response => {
        if (response.status === 204) {
            // Обновляем список мероприятий
            currentEvents = currentEvents.filter(e => e.event_id != eventId);
            loadEvents(map);
            map.balloon.close();
            alert('Мероприятие успешно удалено!');
        } else if (response.status === 403) {
            throw new Error('Недостаточно прав для удаления');
        } else {
            throw new Error('Ошибка удаления');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert(`Ошибка: ${error.message}`);
    });
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('delete-event-btn')) {
        const eventId = e.target.dataset.eventId;
        handleDeleteEvent(eventId);
    }
});

function setupReactionHandlers(map) {
    map.geoObjects.events.add('balloonopen', function(e) {
        const balloonContent = e.get('target').properties.get('balloonContent');
        setTimeout(() => {
            const balloonElement = document.querySelector('.ymaps-balloon');
            if (balloonElement) {
                balloonElement.addEventListener('click', (e) => {
                    if (e.target.classList.contains('reaction-btn')) {
                        const eventId = e.target.getAttribute('data-event-id');
                        const reactionType = e.target.getAttribute('data-type');
                        handleReaction(eventId, reactionType);
                    }
                });
            }
        }, 100);
    });
}

function handleReaction(eventId, reactionType) {
    const token = getJWTToken();
    if (!token) return;

    // 1. Находим текущее событие в массиве currentEvents
    const currentEvent = currentEvents.find(e => e.event_id == eventId);
    if (!currentEvent) {
        alert('Событие не найдено');
        return;
    }

    // 2. Проверяем текущую реакцию через найденный currentEvent
    if (currentEvent.user_reaction === reactionType) {
        if (!confirm("Вы уже выбрали эту реакцию. Хотите отменить её?")) return;
    }

    fetch('/api/reactions/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            event: parseInt(eventId),
            type: reactionType
        })
    })
    .then(response => {
        if (response.status === 400) {
            return response.json().then(err => { throw new Error(err.error); });
        }
        if (!response.ok) throw new Error('Ошибка сохранения реакции');
        return response.json();
    })
    .then(data => {
        // 3. Обновляем реакцию в найденном объекте события
        currentEvent.user_reaction = reactionType;
        loadEvents(map);

        // Обновляем балун
        const balloon = map.balloon;
        if (balloon.isOpen()) {
            balloon.close();
            setTimeout(() => {
                balloon.open(balloon.getData().geoObject);
            }, 300);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert(`Ошибка: ${error.message}`);
    });
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('reaction-btn')) {
        const eventId = e.target.dataset.eventId;
        const type = e.target.dataset.type;
        handleReaction(eventId, type);
    }
});

function initApplication(map) {
    // Инициализация карты
    loadEvents(map);
    initLogoutButton();
    initModal(map);

    // Вешаем глобальный обработчик на карту
    map.events.add('click', function(e) {
        // Закрываем все балуны перед открытием нового
        map.balloon.close();

        // Ищем событие по координатам
        const clickedEvent = currentEvents.find(event =>
            Math.abs(event.latitude - e.get('coords')[0]) < 0.0001 &&
            Math.abs(event.longitude - e.get('coords')[1]) < 0.0001
        );

        if (clickedEvent) {
            // Генерируем контент
            const balloonContent = updateBalloonContent(clickedEvent);
            console.log('Balloon Content:', balloonContent); // Логирование

            // Открываем балун
            map.balloon.open(
                e.get('coords'),
                {
                    content: balloonContent,
                    zIndex: 9999
                },
                {
                    closeButton: false
                }
            );

            // Вешаем обработчики на кнопки внутри балуна
            setTimeout(() => {
                document.querySelectorAll('.reaction-btn').forEach(btn => {
                    btn.onclick = (e) => {
                        const eventId = e.target.dataset.eventId;
                        const type = e.target.dataset.type;
                        handleReaction(eventId, type);
                    };
                });
            }, 100);
        }
    });
}

