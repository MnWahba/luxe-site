import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-luxebags-secret-key-change-in-production-xyz123abc'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'axes',
    'users',
    'products',
    'orders',
    'payments',
    'reviews',
    'coupons',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'luxe_bags_project.middleware.PermanentLanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'luxe_bags_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'orders.context_processors.cart_count',
                'products.context_processors.categories_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'luxe_bags_project.wsgi.application'

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

LANGUAGE_CODE = 'en'
LANGUAGES = [('en', 'English'), ('ar', 'العربية')]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ══════════════════════════════════════════════════
# EMAIL CONFIGURATION
# ══════════════════════════════════════════════════
# To enable REAL email (Gmail):
#   1. Rename email_config.EXAMPLE.py → email_config.py
#   2. Fill in your Gmail and App Password
#   3. Restart the server
#
import importlib.util as _ilu, os as _os
_ecfg = _os.path.join(BASE_DIR, 'email_config.py')
if _os.path.exists(_ecfg):
    import importlib as _imp
    _spec = _ilu.spec_from_file_location('email_config', _ecfg)
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    EMAIL_BACKEND    = getattr(_mod, 'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
    EMAIL_HOST       = getattr(_mod, 'EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT       = getattr(_mod, 'EMAIL_PORT', 587)
    EMAIL_USE_TLS    = getattr(_mod, 'EMAIL_USE_TLS', True)
    EMAIL_HOST_USER  = getattr(_mod, 'EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = getattr(_mod, 'EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = getattr(_mod, 'DEFAULT_FROM_EMAIL', 'Fancy فانسي <noreply@fancy-store.com>')
else:
    # Development default — emails print to CMD window
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'Fancy فانسي <noreply@fancy-store.com>'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'users.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

SESSION_COOKIE_AGE = 86400 * 7

PAYMOB_API_KEY = os.environ.get('PAYMOB_API_KEY', '')
PAYMOB_INTEGRATION_ID = os.environ.get('PAYMOB_INTEGRATION_ID', '')
FAWRY_MERCHANT_CODE = os.environ.get('FAWRY_MERCHANT_CODE', '')
FAWRY_SECURITY_KEY = os.environ.get('FAWRY_SECURITY_KEY', '')

STORE_NAME = 'Fancy | فانسي'
STORE_PHONE = '01212184205'
STORE_WHATSAPP = '01212184205'
STORE_INSTAPAY = '01205951559'
STORE_ORANGE_CASH = '01223184205'
STORE_FACEBOOK = 'https://facebook.com'

# ── Axes: disable lockout in first run / dev mode ──
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_TEMPLATE = 'users/locked_out.html'
AXES_RESET_ON_SUCCESS = True
AXES_NEVER_LOCKOUT_WHITELIST = True  # set False in production
AXES_IP_WHITELIST = ['127.0.0.1']
