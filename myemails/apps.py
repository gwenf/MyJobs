from django.apps import AppConfig


class MyEmailsConfig(AppConfig):
    def ready(self):
        import myemails.signals
