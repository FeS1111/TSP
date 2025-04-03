from django.shortcuts import render
from rest_framework import viewsets

from .models import User, Category, Reaction, Event
from .serializers import UserSerializer, CategorySerializer, EventSerializer, ReactionSerializer


class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

