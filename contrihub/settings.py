from decouple import config
import dj_database_url
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dfv22x*65_x&xp_x@v$s*&ieo()*@3!*499lxdfaqgk$(gbw3x')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'home.apps.HomeConfig',
    'user_profile.apps.UserProfileConfig',
    'project.apps.ProjectConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd Party Libraries
    'social_django',  # Social Media Login
    'crispy_forms',
]

MIDDLEWARE = [
    # Middleware used for deployment on Heroku (Put it at the top)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware to handle Login through Social Media Platform requests
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'contrihub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context Preprocessors for Social media login
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect'
            ],
        },
    },
]

WSGI_APPLICATION = 'contrihub.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)
DATABASES['default']['CONN_MAX_AGE'] = 500

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)

STATIC_URL = '/static/'
STATIC_ROOT = 'static'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',  # for Github authentication
    'django.contrib.auth.backends.ModelBackend',  # Default Django Authentication Backend
)

SOCIAL_AUTH_GITHUB_KEY = config('SOCIAL_AUTH_GITHUB_KEY', default="")
SOCIAL_AUTH_GITHUB_SECRET = config('SOCIAL_AUTH_GITHUB_SECRET', default="")
SOCIAL_AUTH_GITHUB_SCOPE = [
    'user:email',  # For Reading user's email
    # 'read:org',  # For Reading Organizations authenticated user is part of
]

LOGIN_URL = 'authorize'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Email Setup
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default="")
EMAIL_PORT = config('EMAIL_PORT', default="")
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default="")
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default="")
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)

AVAILABLE_PROJECTS = config('AVAILABLE_PROJECTS', default="ContriHUB-22",
                            cast=lambda v: [s.strip() for s in v.split(',')])
LABEL_MENTOR = config('LABEL_MENTOR', default="mentor")
LABEL_LEVEL = config('LABEL_LEVEL', default="level")
LABEL_POINTS = config('LABEL_POINTS', default="points")
LABEL_RESTRICTED = config('LABEL_RESTRICTED', default="restricted")
DEPENDABOT_LOGIN = config('DEPENDABOT_LOGIN', default="dependabot[bot]")

MAX_SIMULTANEOUS_ISSUE = config('MAX_SIMULTANEOUS_ISSUE', default=2, cast=int)

DAYS_PER_ISSUE_FREE = config('DAYS_PER_ISSUE_FREE', default=1, cast=int)
DAYS_PER_ISSUE_VERY_EASY = config('DAYS_PER_ISSUE_VERY_EASY', default=1, cast=int)
DAYS_PER_ISSUE_EASY = config('DAYS_PER_ISSUE_EASY', default=1, cast=int)
DAYS_PER_ISSUE_MEDIUM = config('DAYS_PER_ISSUE_MEDIUM', default=2, cast=int)
DAYS_PER_ISSUE_HARD = config('DAYS_PER_ISSUE_HARD', default=3, cast=int)

DEFAULT_FREE_POINTS = config('DEFAULT_FREE_POINTS', default=0, cast=int)
DEFAULT_VERY_EASY_POINTS = config('DEFAULT_VERY_EASY_POINTS', default=2, cast=int)
DEFAULT_EASY_POINTS = config('DEFAULT_EASY_POINTS', default=10, cast=int)
DEFAULT_MEDIUM_POINTS = config('DEFAULT_MEDIUM_POINTS', default=20, cast=int)
DEFAULT_HARD_POINTS = config('DEFAULT_HARD_POINTS', default=30, cast=int)
