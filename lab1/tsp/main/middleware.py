from django.http import JsonResponse

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