from rest_framework import viewsets, generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, Category, Reaction, Event
from .serializers import UserSerializer, CategorySerializer, EventSerializer, ReactionSerializer, \
    CustomTokenObtainPairSerializer, UserRegistrationSerializer, IsAdminOrStaff, CanChangePassword, IsEventCreator
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.views.decorators.http import require_POST


@require_POST
@login_required
def create_event(request):
    try:
        Event.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            latitude=float(request.POST['latitude']),
            longitude=float(request.POST['longitude']),
            datetime=request.POST['datetime'],
            creator=request.user
        )
        messages.success(request, 'Мероприятие успешно создано!')
    except (KeyError, ValueError) as e:
        messages.error(request, f'Ошибка при создании мероприятия: {str(e)}')

    return redirect('main')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('main')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def main_view(request):
    events = Event.objects.all()
    # Преобразование координат в позиции на карте (примерные значения)
    for event in events:
        event.x_pos = (event.longitude + 180) / 3.6  # Примерное преобразование
        event.y_pos = (90 - event.latitude) / 1.8  # Примерное преобразование

    return render(request, 'main.html', {
        'events': events,
        'default_lat': 55.751244,
        'default_lng': 37.618423
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if 'username' in request.POST and form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')

        if 'new_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'profile.html', {
        'form': form,
        'password_form': password_form
    })


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Пользователь успешно зарегистрировался!"},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()

        if obj != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы можете просматривать только свой профиль")
        return obj

    def get_permissions(self):
        if self.action == 'retrieve' and self.request.method == 'GET':
            return [IsAuthenticated()]
        if self.action == 'update' and self.request.method == 'PUT':
            return [CanChangePassword()]
        return [IsAdminOrStaff()]

class CategoryApiView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class EventApiView(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsEventCreator]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReactionApiView(viewsets.ModelViewSet):
    queryset = Reaction.objects.none()
    serializer_class = ReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        reaction = super().get_object()

        if reaction.user != self.request.user:
            raise PermissionDenied("Вы можете изменять только свои реакции")
        return reaction

    def destroy(self, request, *args, **kwargs):
        reaction = self.get_object()
        if reaction.user != request.user:
            raise PermissionDenied("Вы можете удалять только свои реакции")
        reaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Успешный выход"}, status=200)
        except TokenError as e:
            return Response({"error": str(e)}, status=400)
