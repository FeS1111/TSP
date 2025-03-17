import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsp.settings')
django.setup()


from main.models import User, Category, Event, EventToCategory, Reaction


def get_user():
    users = User.objects.all()
    for user in users:
        print(f"ID: {user.user_id}, Имя: {user.username}, Email: {user.email}")
    print("-" * 40)


def get_category():
    categories = Category.objects.all()
    for category in categories:
        print(f"ID: {category.category_id}, Название: {category.name}")
    print("-" * 40)

def get_event_to_categories():
    print("Связи мероприятий и категорий:")
    event_to_categories = EventToCategory.objects.all()
    for link in event_to_categories:
        print(f"Мероприятие: {link.event.title}, Категория: {link.category.name}")
    print("-" * 40)

def get_reactions():
    print("Реакции:")
    reactions = Reaction.objects.all()
    for reaction in reactions:
        print(f"Пользователь: {reaction.user.username}, Мероприятие: {reaction.event.title}, Реакция: {reaction.type}")
    print("-" * 40)

def get_events():
    print("Мероприятия:")
    events = Event.objects.all()
    for event in events:
        print(f"ID: {event.event_id}, Название: {event.title}, Дата: {event.datetime}, Категория: {event.category.name}")
    print("-" * 40)

if __name__ == "__main__":
    get_user()
    get_category()
    get_event_to_categories()
    get_reactions()
    get_events()


