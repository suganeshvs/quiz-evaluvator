import os
from django.apps import AppConfig


class QuizAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz_app'

    def ready(self):
        # Auto-detect and download AI engine / models in background irrespective of the machine
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('DJANGO_SETTINGS_MODULE'):
            try:
                from quiz_app.services.ai_service import AIService
                AIService.ensure_ai_engine_ready(async_mode=True)
            except Exception as e:
                print(f"[AI ENGINE] Background readiness check deferred: {e}")
