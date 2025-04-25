document.addEventListener('DOMContentLoaded', function() {
    if (typeof ymaps === 'undefined') {
        console.error('API Яндекс.Карт не загружен!');
        alert('Не удалось загрузить карты. Пожалуйста, обновите страницу.');
        return;
    }

    ymaps.ready(initApplication);
});

function initApplication() {
    try {
        const map = createMap();

        initModal(map);
        loadEvents(map);
        initLogoutButton();

    } catch (error) {
        console.error('Ошибка инициализации:', error);
        alert('Произошла ошибка при загрузке карты');
    }
}

function createMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) throw new Error('Элемент карты не найден!');

    const map = new ymaps.Map('map', {
        center: [55.751574, 37.573856],
        zoom: 10,
        controls: ['zoomControl', 'typeSelector', 'fullscreenControl']
    });

    map.controls.add('zoomControl', { float: 'right' });
    map.controls.add('typeSelector', { float: 'left' });

    console.log('Карта успешно создана');
    return map;
}

function initModal(map) {
    const modal = document.getElementById('eventModal');
    const closeBtn = document.querySelector('.close-btn');
    const form = document.getElementById('eventForm');

    if (!modal || !closeBtn || !form) {
        console.warn('Не найдены элементы модального окна');
        return;
    }

    closeBtn.addEventListener('click', () => modal.style.display = 'none');

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
}

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
        addEventsToMap(map, [event]);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось создать мероприятие');
    });
}

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
