from urllib.parse import parse_qs
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser

    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Custom middleware that takes JWT token from query string and authenticates via SimpleJWT
    """

    def __init__(self, inner):
        self.inner = inner  #tells to call next application

    async def __call__(self, scope, receive, send):  #ASGI application callable interface
        print("JWTAuthMiddleware scope before auth:", scope)

        from django.contrib.auth.models import AnonymousUser 
        from rest_framework_simplejwt.tokens import AccessToken  

        query_string = parse_qs(scope['query_string'].decode()) #scope['query_string'] is byte string then converted to normal string
        token = query_string.get('token') #get token from query string

        if token:   
            try:
                access_token = AccessToken(token[0]) 
                user_id = access_token["user_id"]
                scope["user"] = await get_user(user_id)
            except Exception as e:
                print("JWTAuthMiddleware error:", e)
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)
