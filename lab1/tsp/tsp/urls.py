from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from main.views import UserApiView, CategoryApiView, EventApiView, ReactionApiView, UserRegistrationView, CustomTokenObtainPairView,LogoutView
from rest_framework.routers import DefaultRouter
from main.views import EventsTemplateView, LoginTemplateView, RegisterTemplateView
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register(r'users', UserApiView)
router.register(r'categories', CategoryApiView)
router.register(r'events', EventApiView)
router.register(r'reactions', ReactionApiView, basename='reaction')

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='api-login'),
    path('api/register/', UserRegistrationView.as_view(), name='api-register'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('register/', RegisterTemplateView.as_view(), name='register'),
    path('api/map/', EventsTemplateView.as_view(), name='map'),
    path('logout/', csrf_exempt(LogoutView.as_view()), name='logout')
]
