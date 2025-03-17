import django
import os
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsp.settings')
django.setup()

from main.models import Reaction, Event, User

def create_reactions():

    users = User.objects.all()
    events = Event.objects.all()

    if not users or not events:
        print("Ошибка: Сначала создайте пользователей и мероприятия.")
        return

    for user in users:
        for event in random.sample(list(events), k=random.randint(1, 5)):
            reaction_type = random.choice(['going', 'not_going'])
            Reaction.objects.get_or_create(user=user, event=event, type=reaction_type)
            print(f'Создана реакция: {user.username} - {event.title} - {reaction_type}')

if __name__ == "__main__":
    create_reactions()
