from rest_framework import serializers
from .models import User, Event, Category, Reaction
from django.contrib.auth.hashers import make_password
from django.core.validators import ValidationError
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email уже занят")]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Имя пользователя уже существует")]
    )

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password_hash': {
                'error_messages': {
                    'blank': 'Пароль не может быть пустым',
                    'required': 'Пароль обязателен для заполнения'
                }
            }
        }

    def validate_password_hash(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        return value

    def create(self, validated_data):
        if 'password_hash' not in validated_data:
            raise serializers.ValidationError({"password_hash": "Обязательное поле"})

        validated_data['password_hash'] = make_password(validated_data['password_hash'])
        return super().create(validated_data)


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


class EventSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    start_date = serializers.DateTimeField(
        error_messages={
            'invalid': 'Некорректный формат даты начала'
        }
    )
    end_date = serializers.DateTimeField(
        error_messages={
            'invalid': 'Некорректный формат даты окончания'
        }
    )

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'blank': 'Название события обязательно для заполнения'
                }
            }
        }

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                "end_date": "Дата окончания не может быть раньше даты начала"
            })
        return data


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
        valid_reactions = ['like', 'dislike', 'interested']
        if value not in valid_reactions:
            raise serializers.ValidationError(
                f"Недопустимая реакция. Допустимые значения: {', '.join(valid_reactions)}"
            )
        return value