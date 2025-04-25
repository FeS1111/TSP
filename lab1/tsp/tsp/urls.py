from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from main.views import (
    UserApiView, CategoryApiView,
    EventApiView, ReactionApiView,
    UserRegistrationView, CustomTokenObtainPairView,
    LogoutView, EventsTemplateView,
    LoginTemplateView, RegisterTemplateView
)
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt


router = DefaultRouter()
router.register(r'users', UserApiView, basename='users')
router.register(r'categories', CategoryApiView, basename='categories')
router.register(r'events', EventApiView, basename='events')
router.register(r'reactions', ReactionApiView, basename='reactions')

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='api-login'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='api-register'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('register/', RegisterTemplateView.as_view(), name='register'),
    path('map/', EventsTemplateView.as_view(), name='map'),
    path('logout/', csrf_exempt(LogoutView.as_view()), name='logout'),

]