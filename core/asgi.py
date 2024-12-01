"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from main_app.consumers import OpenAIConsumer  # Import your WebSocket consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openai_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Add the WebSocket URL
            path("ws/chat/", OpenAIConsumer.as_asgi()),
        ])
    ),
})
