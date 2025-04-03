from django.contrib import admin
from .models import Category, User, Event, EventToCategory, Reaction

admin.site.register(Category)
admin.site.register(User)
admin.site.register(Event)
admin.site.register(EventToCategory)
admin.site.register(Reaction)
