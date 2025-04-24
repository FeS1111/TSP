// Главная функция инициализации
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем загрузился ли API Яндекс.Карт
    if (typeof ymaps === 'undefined') {
        console.error('API Яндекс.Карт не загружен!');
        alert('Не удалось загрузить карты. Пожалуйста, обновите страницу.');
        return;
    }

    // Инициализируем карту после загрузки API
    ymaps.ready(initApplication);
});

function initApplication() {
    try {
        // 1. Создаем карту
        const map = createMap();
        
        // 2. Инициализируем модальное окно
        initModal(map);
        
        // 3. Загружаем мероприятия
        loadEvents(map);
        
        // 4. Настраиваем кнопку выхода
        initLogoutButton();
        
    } catch (error) {
        console.error('Ошибка инициализации:', error);
        alert('Произошла ошибка при загрузке карты');
    }
}

// Создание карты
function createMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) throw new Error('Элемент карты не найден!');
    
    const map = new ymaps.Map('map', {
        center: [55.751574, 37.573856], // Москва
        zoom: 10,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']
    });
    
    // Настройка элементов управления
    map.controls.add('zoomControl', { float: 'right' });
    map.controls.add('typeSelector', { float: 'left' });
    
    console.log('Карта успешно создана');
    return map;
}

// Инициализация модального окна
function initModal(map) {
    const modal = document.getElementById('eventModal');
    const closeBtn = document.querySelector('.close-btn');
    const form = document.getElementById('eventForm');
    
    if (!modal || !closeBtn || !form) {
        console.warn('Не найдены элементы модального окна');
        return;
    }
    
    // Закрытие по кнопке
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    
    // Клик по карте - открытие модалки
    map.events.add('click', function(e) {
        const coords = e.get('coords');
        document.getElementById('latitude').value = coords[0].toPrecision(8);
        document.getElementById('longitude').value = coords[1].toPrecision(8);
        modal.style.display = 'block';
    });
    
    // Отправка формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        createEvent(map);
        modal.style.display = 'none';
    });
}

// Загрузка мероприятий
function loadEvents(map) {
    fetch('/api/events/', {
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка загрузки мероприятий');
        return response.json();
    })
    .then(events => {
        addEventsToMap(map, events);
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

// Добавление мероприятий на карту
function addEventsToMap(map, events) {
    events.forEach(event => {
        try {
            const placemark = new ymaps.Placemark(
                [event.latitude, event.longitude],
                {
                    hintContent: event.title,
                    balloonContent: `
                        <h3>${event.title}</h3>
                        <p>${event.description || 'Нет описания'}</p>
                        <small>${new Date(event.datetime).toLocaleString()}</small>
                    `,
                },
                {
                    preset: 'islands#redIcon'
                }
            );
            map.geoObjects.add(placemark);
        } catch (e) {
            console.error('Ошибка добавления метки:', e);
        }
    });
}

// Создание нового мероприятия
function createEvent(map) {
    const formData = new FormData(document.getElementById('eventForm'));
    
    fetch('/api/events/', {
        method: 'POST',
        body: formData,
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка создания мероприятия');
        return response.json();
    })
    .then(event => {
        // Добавляем новое мероприятие на карту
        addEventsToMap(map, [event]);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось создать мероприятие');
    });
}

// Кнопка выхода
function initLogoutButton() {
    document.getElementById('logoutBtn').addEventListener('click', function() {
        fetch('/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(() => {
            window.location.href = '/login/';
        })
        .catch(error => {
            console.error('Ошибка выхода:', error);
        });
    });
}

// Вспомогательная функция для получения cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}