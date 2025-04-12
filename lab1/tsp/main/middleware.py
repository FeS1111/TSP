import re
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            re.compile(url) for url in [
                r'^/api/login/$',
                r'^/api/register/$',
                r'^/api/events/$'
                r'^/api/token/refresh/$'

            ]
        ]
        self.jwt_authentication = JWTAuthentication()

    def __call__(self, request):
        if self._is_exempt(request.path) or request.method == 'OPTIONS':
            return self.get_response(request)

        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Требуется токен авторизации'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            validated_token = self.jwt_authentication.get_validated_token(token)
            user = self.jwt_authentication.get_user(validated_token)
            request.user = user
        except (InvalidToken, AuthenticationFailed) as e:
            return JsonResponse({'error': str(e)}, status=401)

        return self.get_response(request)

    def _is_exempt(self, path):
        return any(url.match(path) for url in self.exempt_paths)

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


