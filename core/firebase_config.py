import firebase_admin
from firebase_admin import credentials, firestore
import os
from django.conf import settings

# بناء المسار إلى ملف الاعتماد
# هذا يضمن أنه سيعمل بغض النظر عن مكان تشغيل المشروع
cred_path = os.path.join(settings.BASE_DIR, 'firebase-credentials.json')

# تهيئة Firebase Admin SDK
# يتم استخدام try-except لمنع إعادة تهيئة التطبيق في كل مرة يتم فيها تحديث الكود
try:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("Firebase App Initialized successfully!")
except ValueError:
    print("Firebase App already initialized.")

# إنشاء كائن للوصول إلى قاعدة بيانات Firestore
db = firestore.client()
