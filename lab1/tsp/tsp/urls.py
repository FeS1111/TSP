from django.contrib import admin
from django.urls import path, include
from main.views import UserApiView, CategoryApiView, EventApiView, ReactionApiView, UserRegistrationView, CustomTokenObtainPairView,LogoutView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users', UserApiView)
router.register(r'categories', CategoryApiView)
router.register(r'events', EventApiView)
router.register(r'reactions', ReactionApiView)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]