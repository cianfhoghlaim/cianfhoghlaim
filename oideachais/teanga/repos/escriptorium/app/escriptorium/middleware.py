from django.shortcuts import render
from django.urls import resolve
from rest_framework.authtoken.models import Token


class AccountExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # allow access to the logout view even if the account is expired
        current_url = resolve(request.path_info).url_name
        if current_url == 'logout':
            return self.get_response(request)

        # check if the user is authenticated via session or token
        token_key = request.META.get('HTTP_AUTHORIZATION')
        token = None

        # if a token is provided fetch the associated user
        if token_key:
            try:
                token_key = token_key.split('Token ')[1]
                token = Token.objects.get(key=token_key)
                request.user = token.user
            except (Token.DoesNotExist, IndexError):
                pass  # token is invalid or doesn't exist

        # skip check for unlogged users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # check if the user's account has expired
        user = request.user
        if user.is_account_expired():
            try:
                if token:
                    token.delete()

            except Token.DoesNotExist:
                pass
            return render(request, 'users/account_expired.html', status=403)

        return self.get_response(request)
