import re
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

from django.shortcuts import redirect
from rest_framework_simplejwt.exceptions import InvalidToken


# middleware.py
class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            '/login/',
            '/register/',
            '/admin/',
            '/static/',
            '/api/auth/',
            '/api/login/',
        ]

    def __call__(self, request):
        path = request.path

        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return self.get_response(request)

        # Для /api/map/ используем сессионную аутентификацию
        if path == '/api/map/':
            return self.get_response(request)

        # Для API-эндпоинтов проверяем JWT
        if path.startswith('/api/'):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Token required'}, status=401)
            try:
                token = auth_header.split(' ')[1]
                JWTAuthentication().get_validated_token(token)
            except Exception:
                return JsonResponse({'error': 'Invalid token'}, status=401)

        return self.get_response(request)


class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request._body_copy = request.body
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method in ('PUT', 'PATCH') and 'users' in request.path:
            try:
                if hasattr(request, '_body_copy') and request._body_copy:
                    import json
                    data = json.loads(request._body_copy.decode('utf-8'))
                    if 'password_hash' in data:
                        return JsonResponse(
                            {"error": "Для изменения пароля используйте поля current_password и new_password"},
                            status=400
                        )
            except Exception as e:
                print(f"Middleware error: {str(e)}")
        return None


