from rest_framework import permissions, serializers
from .models import User, Event, Category, Reaction
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from django.core.validators import ValidationError
from rest_framework.validators import UniqueValidator


class LoginFormSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class IsEventCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user

class IsEventCreatorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.is_staff)

class CanChangePassword(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'update' and request.method == 'PUT':
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            'refresh': data['refresh'],
            'access': data['access']
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            raise serializers.ValidationError(
                "Некорректный формат email. Используйте форматы: text@text.ru или text@text.com")
        if not value.endswith(('.ru', '.com')):
            raise serializers.ValidationError("Допустимы только домены .ru и .com")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать не менее 8 символов")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            avatar=validated_data.get('avatar')
        )


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email уже занят")],
        required=False
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Имя пользователя уже существует")],
        required=False
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        error_messages={
            'blank': 'Пароль не может быть пустым',
        },
        style={'input_type': 'password'}
    )
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password',
            'created_at', 'avatar', 'current_password', 'new_password'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
        }

    def validate_password(self, value):
        if value and len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        return value

    def validate(self, data):
        if 'new_password' in data and data['new_password']:
            if not data.get('current_password'):
                raise serializers.ValidationError(
                    {"current_password": "Текущий пароль обязателен для изменения пароля"}
                )

            if not self.instance.check_password(data['current_password']):
                raise serializers.ValidationError(
                    {"current_password": "Неверный текущий пароль"}
                )

            if len(data['new_password']) < 8:
                raise serializers.ValidationError(
                    {"new_password": "Пароль должен содержать минимум 8 символов"}
                )

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)
        current_password = validated_data.pop('current_password', None)

        if new_password:
            instance.set_password(new_password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
        ret.pop('current_password', None)
        ret.pop('new_password', None)
        return ret


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        error_messages={
            'blank': 'Название категории не может быть пустым',
            'max_length': 'Название категории не должно превышать 100 символов'
        }
    )

    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):

        if self.instance and self.instance.name == value:
            return value

        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('Категория с таким названием уже существует')
        return value


class EventSerializer(serializers.ModelSerializer):
    going_count = serializers.SerializerMethodField()
    going_users = serializers.SerializerMethodField()

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['event_id', 'title', 'description', 'latitude', 'longitude',
              'datetime', 'category', 'creator', 'going_users', 'going_count', 'user_reaction']
        read_only_fields = ['creator']
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'blank': 'Название события обязательно для заполнения'
                }
            }
        }

    def get_user_reaction(self, obj):
        user = self.context['request'].user
        reaction = obj.reactions.filter(user=user).first()
        return reaction.type if reaction else None
    def get_going_count(self, obj):
        return obj.reactions.filter(type='going').count()

    def get_going_users(self, obj):
        return [reaction.user.username for reaction in obj.reactions.filter(type='going')]

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')
        read_only_fields = ['id', 'username', 'avatar']

class ReactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        required=False
    )

    class Meta:
        model = Reaction
        fields = ['reaction_id', 'user', 'event', 'type']
        read_only_fields = ['user', 'reaction_id', 'event']
        extra_kwargs = {
            'type': {
                'required': True,
                'error_messages': {
                    'invalid_choice': 'Допустимые значения: going, not_going'
                }
            }
        }

    def validate(self, data):
        if self.instance is None and 'event' not in data:
            raise serializers.ValidationError({"event": "Это поле обязательно при создании реакции"})

        if self.instance and data['type'] == self.instance.type:
            raise serializers.ValidationError("Реакция уже существует")

        if self.instance and 'event' in data:
            if data['event'] != self.instance.event:
                raise serializers.ValidationError({"event": "Нельзя изменять мероприятие для существующей реакции"})

        if self.instance is None and Reaction.objects.filter(
                user=data.get('user', self.context['request'].user),
                event=data['event']
        ).exists():
            raise serializers.ValidationError({"error": "Вы уже оставили реакцию на это мероприятие"})

        return data



