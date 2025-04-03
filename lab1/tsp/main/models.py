from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=256)
    created_at = models.DateField(auto_now_add=True)
    avatar = models.TextField(blank=True, null=True)

    def set_password(self, password):
        self.password_hash = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password_hash)

    def __str__(self):
        return self.username


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    datetime = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')

    def __str__(self):
        return self.title


class EventToCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='event_categories')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_categories')

    class Meta:
        unique_together = ('category', 'event')

    def __str__(self):
        return f"{self.event.title} -> {self.category.name}"


class Reaction(models.Model):
    REACTION_TYPES = [
        ('going', 'Going'),
        ('not_going', 'Not Going'),
    ]

    reaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reactions')
    type = models.CharField(max_length=10, choices=REACTION_TYPES)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.type})"
