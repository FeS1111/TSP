from django.contrib import admin
from django.urls import path, include
from main.views import UserApiView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserApiView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]