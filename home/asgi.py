import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')

import django
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from main.middleware import JWTAuthMiddleware
import main.routing


django_asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(main.routing.websocket_urlpatterns)
    ),
})
