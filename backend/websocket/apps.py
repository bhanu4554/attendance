from django.apps import AppConfig


class WebsocketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'websocket'

    def ready(self):
        # Temporarily disabled - Redis not available
        # import websocket.signals
        import websocket.signals_disabled