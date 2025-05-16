from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import User, Category, Reaction, Event
from .serializers import UserSerializer, CategorySerializer, EventSerializer, ReactionSerializer, \
    CustomTokenObtainPairSerializer, UserRegistrationSerializer, IsAdminOrStaff, CanChangePassword, IsEventCreator
from django.shortcuts import render, redirect
from django.views import View
import json


class EventsTemplateView(LoginRequiredMixin, View):
    login_url = 'login'

    def create(self, request, *args, **kwargs):
        try:
            data = request.POST.dict()
            data['creator'] = request.user.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return JsonResponse(serializer.data, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        return render(request, 'events/events.html', {
            'categories': Category.objects.all(),
            'csrf_token': get_token(request)
        })


class LoginTemplateView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('map')
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Оставляем сессию для веб-интерфейса
            refresh = RefreshToken.for_user(user)

            # Возвращаем страницу с токеном
            return render(request, 'auth/login.html', {
                'access_token': str(refresh.access_token),
                'refresh_token': '/map'
            })
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid credentials'})


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Автоматически входим пользователя после регистрации
        user = authenticate(
            username=serializer.data['username'],
            password=request.data['password']
        )

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Пользователь успешно зарегистрирован!",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED, headers=headers)

        return Response(
            {"message": "Пользователь успешно зарегистрирован! Пожалуйста, войдите."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class RegisterTemplateView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('map')
        return render(request, 'auth/register.html')

    def post(self, request):
        return redirect('api-register')

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
    queryset = Event.objects.all().prefetch_related('reactions')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsEventCreator]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()

            data['creator'] = request.user.id

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        if event.creator != request.user:
            return Response(
                {"error": "Вы можете удалять только свои мероприятия"},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(event)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReactionApiView(viewsets.ModelViewSet):
    queryset = Reaction.objects.none()
    serializer_class = ReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        Reaction.objects.filter(
            user=self.request.user,
            event=serializer.validated_data['event']
        ).delete()
        serializer.save(user=self.request.user)

    def get_object(self):
        reaction = super().get_object()

        if reaction.user != self.request.user:
            raise PermissionDenied("Вы можете изменять только свои реакции")
        return reaction

    def create(self, request, *args, **kwargs):
        try:
            Reaction.objects.filter(
                user=request.user,
                event_id=request.data['event']
            ).delete()

            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def destroy(self, request, *args, **kwargs):
        reaction = self.get_object()
        if reaction.user != request.user:
            raise PermissionDenied("Вы можете удалять только свои реакции")
        reaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Успешный выход"}, status=200)
        except TokenError as e:
            return Response({"error": str(e)}, status=400)
class LogoutView(View):

    def post(self, request):
        logout(request)
        request.session.flush()
        return redirect('/login/')
