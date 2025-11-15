# config/settings.py (النسخة النهائية الكاملة)

from pathlib import Path
import os
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-your-secret-key' # استخدم المفتاح الخاص بك
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================================
# == FIREBASE ADMIN SDK INITIALIZATION
# ==========================================================
try:
    FIREBASE_CREDS_PATH = os.path.join(BASE_DIR, 'firebase-credentials.json')
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDS_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'revealapp-8af3f.appspot.com' # تأكد من اسم الـ Bucket
        })
        print("Firebase Admin SDK Initialized successfully!")
    FIRESTORE_DB = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase Admin App: {e}")
    FIRESTORE_DB = None

# ==========================================================
# == PYREBASE CONFIG FOR AUTHENTICATION
# ==========================================================
PYREBASE_CONFIG = {
    "apiKey": "AIzaSyCSCPWbtxmXJzTwGwj4OZDba3r3JaCuAlU", # استخدم مفتاحك
    "authDomain": "revealapp-8af3f.firebaseapp.com",
    "projectId": "revealapp-8af3f",
    "storageBucket": "revealapp-8af3f.appspot.com",
    "messagingSenderId": "490797315957",
    "appId": "1:490797315957:web:1c88cd379ac1bc7274053c",
    "databaseURL": ""
}

# ==========================================================
# == LOGIN URL
# ==========================================================
LOGIN_URL = 'core:login'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR, # ✨✨✨ أضف هذا السطر ليتمكن Django من العثور على manifest.json ✨✨✨
]
