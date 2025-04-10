from rest_framework import serializers
from .models import User, Event, Category, Reaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from django.core.validators import ValidationError
from rest_framework.validators import UniqueValidator


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'email': self.user.email
        })
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'avatar']

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
        error_messages={
            'blank': 'Пароль не может быть пустым',
        },
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'created_at', 'avatar']
        extra_kwargs = {
            'password_hash': {'write_only': True, 'required': False},
            'created_at': {'read_only': True},
        }

    def validate_password(self, value):
        if value and len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
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
    going_users = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['event_id', 'title', 'description', 'latitude', 'longitude',
              'datetime', 'category', 'creator', 'going_users']
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'blank': 'Название события обязательно для заполнения'
                }
            }
        }

    def get_going_users(self, obj):
        going_users = User.objects.filter(
            reactions__event=obj,
            reactions__type='going'
        ).distinct()
        return SimpleUserSerializer(going_users, many=True, context=self.context).data


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'error_messages': {
                    'does_not_exist': 'Пользователь не найден'
                }
            },
            'event': {
                'error_messages': {
                    'does_not_exist': 'Событие не найдено'
                }
            }
        }

    def validate_reaction_type(self, value):
        valid_reactions = ['going', 'not_going']
        if value not in valid_reactions:
            raise serializers.ValidationError(
                f"Недопустимая реакция. Допустимые значения: {', '.join(valid_reactions)}"
            )
        return value


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'avatar')