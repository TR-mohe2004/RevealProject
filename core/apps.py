from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    # هذه الدالة تعمل مرة واحدة عند بدء تشغيل التطبيق
    def ready(self):
        # استيراد ملف تهيئة Firebase لضمان تشغيله
        import core.firebase_config
