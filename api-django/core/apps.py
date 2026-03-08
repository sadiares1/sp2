from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from .signals import connect_characteristics_signals

        connect_characteristics_signals()
