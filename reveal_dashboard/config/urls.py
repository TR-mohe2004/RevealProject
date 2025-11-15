# config/urls.py (النسخة النهائية الكاملة والمعدلة لـ PWA)

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # رابط لوحة تحكم Django الافتراضية
    path('admin/', admin.site.urls),

    # ✨✨✨ رابط ملف المانيفست لجعل الموقع يعمل كتطبيق ✨✨✨
    path(
        'manifest.json', 
        TemplateView.as_view(template_name='manifest.json', content_type='application/json'), 
        name='manifest'
    ),

    # توجيه كل الروابط الأخرى إلى ملف urls الخاص بتطبيق core
    path('', include('core.urls')),
]
