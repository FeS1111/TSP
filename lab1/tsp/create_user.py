import argparse
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsp.settings')
django.setup()

from main.models import User
from django.utils import timezone

def create_user(username, email, password):
    user = User(
        username=username,
        email=email,
        password_hash='',
        created_at=timezone.now()
    )
    user.set_password(password)
    user.save()
    print(f"Пользователь {username} создан")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Создание нового пользователя")
    parser.add_argument('username', type=str, help='Имя пользователя')
    parser.add_argument('email', type=str, help='Email пользователя')
    parser.add_argument('password', type=str, help='Пароль пользователя')
    args = parser.parse_args()
    create_user(args.username, args.email, args.password)