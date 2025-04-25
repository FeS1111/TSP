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


class RegisterTemplateView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

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

    def create(self, request, *args, **kwargs):
        try:
            # Для FormData
            data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'datetime': request.POST.get('datetime'),
                'latitude': request.POST.get('latitude'),
                'longitude': request.POST.get('longitude'),
                'category': request.POST.get('category'),
                'creator': request.user.id
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        def list(self, request):
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "data": serializer.data  # Явно возвращаем массив
            })

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
