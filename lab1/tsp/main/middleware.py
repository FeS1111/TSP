import re
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

from django.shortcuts import redirect
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        exempt_paths = ['/login/', '/register/', '/static/', '/admin/', '/api/login/', '/api/register/']

        if any(request.path.startswith(p) for p in exempt_paths):
            return self.get_response(request)

        if request.path == '/login/' and request.method == 'POST':
            return self.get_response(request)

        if not request.session.get('access_token'):
            # Не добавляем next=/ для корневого URL
            if request.path == '/':
                return redirect('/login/')
            return redirect(f'/login/?next={request.path}')

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


