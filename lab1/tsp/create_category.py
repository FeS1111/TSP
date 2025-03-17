import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsp.settings')
django.setup()

from main.models import Category

def create_categories():
    categories = ['Концерты', 'Выставки', 'Спорт', 'Образование', 'Фестивали']
    for name in categories:
        Category.objects.get_or_create(name=name)
        print(f'Создана категория: {name}')

if __name__ == "__main__":
    create_categories()