from django.contrib import admin
from django.urls import path, include  # تأكد من إضافة include

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- إضافة هنا ---
    # أي رابط يتم طلبه، قم بتوجيهه إلى ملف core/urls.py للبحث عن تطابق هناك.
    path('', include('core.urls', namespace='core')),
]
