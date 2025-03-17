import django
import os
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsp.settings')
django.setup()

from main.models import Event, Category, User

def create_events():
    categories = Category.objects.all()
    users = User.objects.all()

    if not categories or not users:
        print("Ошибка: Сначала создайте категории и пользователей.")
        return

    for i in range(1, 6):
        event = Event.objects.create(
            title=f'Мероприятие {i}',
            description=f'Описание мероприятия {i}',
            latitude =round(random.uniform(-99.99999999, 99.99999999), 8),
            longitude = round(random.uniform(-99.99999999, 99.99999999), 8),
            datetime=datetime.now() + timedelta(days=random.randint(1, 30)),
            category=random.choice(categories),
            creator=random.choice(users)
        )
        print(f'Создано мероприятие: {event.title}')

if __name__ == "__main__":
    events = Event.objects.all()
    events.delete()
    create_events()