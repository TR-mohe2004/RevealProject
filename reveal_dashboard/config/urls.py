# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. رابط لوحة تحكم Django الافتراضية
    path('secure-admin/', admin.site.urls), # تم تغيير الرابط لأمان أفضل

    # 2. رابط ملف المانيفست (manifest.json) لـ PWA
    # هذا الرابط يخدم ملف manifest.json من مجلد القوالب الرئيسي
    path(
        'manifest.json', 
        TemplateView.as_view(
            template_name='manifest.json', 
            content_type='application/json'
        ), 
        name='manifest'
    ),

    # 3. توجيه كل الروابط الأخرى إلى ملف urls الخاص بتطبيق core
    path('', include('core.urls')),
]

# 4. إضافة هذا السطر لخدمة ملفات الوسائط (الصور المرفوعة) في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

