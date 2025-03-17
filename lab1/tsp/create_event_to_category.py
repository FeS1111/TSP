import django
import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsp.settings')
django.setup()

from main.models import Event, Category, EventToCategory

def create_event_to_category():

    events = Event.objects.all()
    categories = Category.objects.all()

    if not events or not categories:
        print("Ошибка: Сначала создайте мероприятия и категории.")
        return

    for event in events:
        for _ in range(random.randint(1, 3)):
            category = random.choice(categories)
            EventToCategory.objects.get_or_create(event=event, category=category)
            print(f'Создана связь: {event.title} - {category.name}')

if __name__ == "__main__":
    create_event_to_category()