from rest_framework import authentication, exceptions

from .models import ApiToken


class ApiTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed(
                "Invalid authorization header. Use: Token <token>"
            )

        token_key = parts[1]

        try:
            token = ApiToken.objects.select_related("user").get(key=token_key)
        except ApiToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")

        return token.user, token

    def authenticate_header(self, request):
        return self.keyword