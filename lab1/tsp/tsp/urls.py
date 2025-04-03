from django.contrib import admin
from django.urls import path, include
from main.views import UserApiView, CategoryApiView, EventApiView, ReactionApiView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserApiView)
router.register(r'cat', CategoryApiView)
router.register(r'events', EventApiView)
router.register(r'react', ReactionApiView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]