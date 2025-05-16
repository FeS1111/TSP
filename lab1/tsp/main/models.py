from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name



class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateField(auto_now_add=True)
    avatar = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='auth')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name='Создатель')

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

    @staticmethod
    def get_going_count(event_id):
        return Reaction.objects.filter(event_id=event_id, type='going').count()

    @staticmethod
    def get_going_users(event_id):
        return User.objects.filter(reactions__event_id=event_id, reactions__type='going')