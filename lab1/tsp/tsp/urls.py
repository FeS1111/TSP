from django.contrib import admin
from django.urls import path, include
from main.views import UserApiView, CategoryApiView, EventApiView, ReactionApiView, UserRegistrationView, CustomTokenObtainPairView,LogoutView
from rest_framework.routers import DefaultRouter
from main.views import login_view, logout_view, register_view, main_view, profile_view, create_event


router = DefaultRouter()
router.register(r'users', UserApiView)
router.register(r'categories', CategoryApiView)
router.register(r'events', EventApiView)
router.register(r'reactions', ReactionApiView, basename='reaction')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', main_view, name='main'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('create-event/', create_event, name='create_event'),
]
