from django.apps import AppConfig


class UgcAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ugc_app'

    def ready(self):
        import ugc_app.signals