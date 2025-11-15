# config/settings.py (النسخة النهائية والمُحسَّنة)

from pathlib import Path
import os
import firebase_admin
from firebase_admin import credentials

# لا تقم بتهيئة firestore هنا، سيتم ذلك في views.py لتجنب المشاكل
# from firebase_admin import firestore

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-your-secret-key' # تذكر تغيير هذا عند النشر
DEBUG = True
ALLOWED_HOSTS = []

# --- التطبيقات المثبتة ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # أضف تطبيقك هنا
    'core.apps.CoreConfig',
]

# --- الوسائط (Middleware) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --- القوالب (Templates) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ✨ تعديل 1: أضفنا مجلد القوالب الرئيسي
        'DIRS': [BASE_DIR / 'templates'],
        # ✨ تعديل 2: أعدنا تفعيل البحث في التطبيقات (مهم جداً)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- قاعدة البيانات ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- مدققات كلمة المرور ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- إعدادات اللغة والوقت ---
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Tripoli'
USE_I18N = True
USE_TZ = True

# --- الملفات الثابتة (Static & Media) ---
STATIC_URL = 'static/'
# ✨ تعديل 3: أزلنا BASE_DIR من هنا لأنه لم يعد ضرورياً
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # تم التعديل لاستخدام pathlib ليكون متوافقاً

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- إعدادات Firebase ---
# ✨ تعديل 4: تم نقل منطق التهيئة إلى ملف views.py لتجنب إعادة التهيئة المتكررة
# التي تسبب خطأ "Firebase App already initialized"
FIREBASE_CREDS_PATH = os.path.join(BASE_DIR, 'firebase-credentials.json')
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDS_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'revealapp-8af3f.appspot.com'
        })
        print("Firebase Admin SDK Initialized successfully!")
    except Exception as e:
        print(f"CRITICAL: Error initializing Firebase Admin App: {e}")

# هذا الجزء سيبقى هنا لتستخدمه مكتبة pyrebase
PYREBASE_CONFIG = {
    "apiKey": "AIzaSyCSCPWbtxmXJzTwGwj4OZDba3r3JaCuAlU", # استخدم مفتاحك
    "authDomain": "revealapp-8af3f.firebaseapp.com",
    "projectId": "revealapp-8af3f",
    "storageBucket": "revealapp-8af3f.appspot.com",
    "messagingSenderId": "490797315957",
    "appId": "1:490797315957:web:1c88cd379ac1bc7274053c",
    "databaseURL": ""
}

# --- رابط تسجيل الدخول ---
LOGIN_URL = 'core:login'
