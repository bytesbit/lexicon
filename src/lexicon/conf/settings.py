import os
import pathlib
from datetime import timedelta

import environ
from configurations import Configuration

env = environ.Env()

# Base directory of lexicon project
BASE_DIR = pathlib.Path(__file__).parent.resolve()
BASE_ROOT_DIR = (BASE_DIR / ".." / ".." / "..").resolve()

DJANGO_CONFIGURATION = os.environ.get("DJANGO_CONFIGURATION", "Development")
DJANGO_ENV = str(DJANGO_CONFIGURATION).lower()
DEFAULT_CLIENT_HOSTS = "localhost,127.0.0.1,0.0.0.0"
VALID_ENVIRONMENTS = (
    "production",
    "staging",
    "development",
)


#######################
# Helper functions   #
#####################


def load_env(environment):
    environment = str(environment).lower()
    if environment not in VALID_ENVIRONMENTS:
        raise Exception(f"Invalid environment value : {environment}")

    valid_env_filenames = [f"{environment}.env", f".env.{environment}"]
    env_file_path = None
    for env_filename in valid_env_filenames:
        env_file_path = os.path.join(BASE_ROOT_DIR, env_filename)
        try:
            os.stat(env_file_path)
            print(f'Loading "{env_file_path}" environment variable file')
            break
        except os.error:
            env_file_path = None
            pass

    if env_file_path is None:
        raise Exception(
            f"Not found any valid environment file, tried loading" f" {valid_env_filenames}"
        )

    env.read_env(env_file_path)


def get_list(text):
    return [item.strip() for item in text.split(",")]


#################################################
# Django configuration setup and declarations  #
###############################################

load_env(DJANGO_ENV)


class BaseConfiguration(Configuration):
    ENV = DJANGO_ENV
    BASE_DIR = BASE_DIR
    BASE_ROOT_DIR = BASE_ROOT_DIR

    SECRET_KEY = env("SECRET_KEY")

    CRYPTOGRAPHY_KEY = env(
        "CRYPTOGRAPHY_KEY",
        default=SECRET_KEY,
    )

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = env.bool("DEBUG", default=True)

    ALLOWED_HOSTS = get_list(env("ALLOWED_HOSTS", default=DEFAULT_CLIENT_HOSTS))

    INSTALLED_APPS = [
        # django contrib apps
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.gis",
        # Third party apps
        "rest_framework",
        "corsheaders",
        # Lexicon apps
        "lexicon",
        "lexicon.video",
    ]

    DEFAULT_TIMEZONE = env("DEFAULT_TIMEZONE", default="Asia/Kolkata")

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "lexicon.middleware.current_user.CurrentUserMiddleware",
    ]

    ORIGINAL_BACKEND = "django.contrib.gis.db.backends.postgis"
    ROOT_URLCONF = "lexicon.conf.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "lexicon.conf.wsgi.application"

    # Database

    DATABASES = {
        "default": env.db(
            engine="django.db.backends.postgresql"
        ),  # require `DATABASE_URL` in environment file
    }

    # Password validation

    AUTH_USER_MODEL = "lexicon.User"

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    # Internationalization
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    STATIC_BASE_DIR = env("STATIC_BASE_DIR", default=BASE_ROOT_DIR)
    STATIC_ROOT = os.path.join(STATIC_BASE_DIR, "static")
    STATIC_URL = "/static/"

    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_ROOT_DIR, "media")

    # Default primary key field type
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    # -------------------- DRF Settings ----------------------------------
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ),
        "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
        "NON_FIELD_ERRORS_KEY": "_generic_errors",
        # It's set as the number of requests per period, where the period should be
        # one of: ('s', 'sec', 'm', 'min', 'h', 'hour', 'd', 'day')
        "DEFAULT_THROTTLE_CLASSES": ["lexicon.api.throttle.BurstAnonRateThrottle"],
        "DEFAULT_THROTTLE_RATES": {
            "anon_burst": "60/min",
            "user_signup_fail": "6/min",
            "login_bad_attempt": "6/min",
        },
    }

    # ----------------- Cache settings --------------------------------------
    DJANGO_CACHE_REDIS_URL = env("DJANGO_CACHE_REDIS_URL", default="")
    if DJANGO_CACHE_REDIS_URL:
        print('Using "Redis" for Django Cache')
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": DJANGO_CACHE_REDIS_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
                "KEY_PREFIX": "lexicon",
            }
        }
    else:
        # by default django use in-memory as cache storage
        print('Using "In-Memory" for Django Cache')

    # ------------------- File Storage Settings-----------------------------
    FILE_UPLOAD_MAX_SIZE = env("FILE_UPLOAD_MAX_SIZE", default=1024 * 1024 * 10)  # 10 MB
    VIDEO_FILE_UPLOAD_MAX_SIZE = env(
        "VIDEO_FILE_UPLOAD_MAX_SIZE", default=1024 * 1024 * 400
    )  # 400 MB

    # --------------------- General settings----------------------------------
    API_ROOT_URL = env("API_ROOT_URL", default="http://127.0.0.1:8000")

    # ----------------- Authentication settings -----------------------------
    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(
            minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINS", default=5)
        ),
        "REFRESH_TOKEN_LIFETIME": timedelta(
            minutes=env.int("JWT_REFRESH_TOKEN_LIFETIME_MINS", default=60 * 24)  # 1 day
        ),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": False,
        "UPDATE_LAST_LOGIN": False,
        "ALGORITHM": "HS256",
        "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
        "VERIFYING_KEY": None,
        "AUDIENCE": None,
        "ISSUER": None,
        "JWK_URL": None,
        "LEEWAY": 0,
        "AUTH_HEADER_TYPES": ("Bearer",),
        "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "USER_AUTHENTICATION_RULE": (
            "rest_framework_simplejwt.authentication.default_user_authentication_rule"
        ),
        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
        "JTI_CLAIM": "jti",
        "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
        "SLIDING_TOKEN_LIFETIME": timedelta(
            minutes=env("JWT_SLIDING_TOKEN_LIFETIME_MINS", default=5)
        ),
        "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(
            minutes=env("JWT_SLIDING_TOKEN_REFRESH_LIFETIME_MINS", default=60 * 24)
        ),
    }

    # ----------------Celery settings--------------------------------------
    CELERY_BROKER_URL = env("CELERY_BROKER_URL")
    CELERY_ACCEPT_CONTENT = [
        "application/json",
        "application/x-python-serialize",
    ]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = "UTC"
    CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=None)
    CELERY_TASK_IGNORE_RESULT = env.bool("CELERY_TASK_IGNORE_RESULT", default=True)
    CELERY_RESULT_EXPIRES = env.int("CELERY_RESULT_EXPIRES_SECS", default=60 * 60)  # 1hour

    # ---------------- Logging settings -----------------------------------
    LOGS_DIR = env("LOGS_DIR", default=BASE_ROOT_DIR)
    LOG_FILE_NAME = os.path.join(LOGS_DIR, "./lexicon-backend.log")
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
            },
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[{server_time}] {message}",
                "style": "{",
            },
            "json": {
                "format": "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": LOG_FILE_NAME,
                "formatter": "json",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            },
            "django.server": {
                "handlers": ["django.server"],
                "level": "INFO",
                "propagate": False,
            },
            "django.utils.autoreload": {"propagate": False},
            "lexicon": {
                "handlers": ["console", "file"],
                "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
                "propagate": False,
            },
        },
    }

    # ------------------ Page Size & Pagination Setting -----------------
    DEFAULT_PAGINATION_PAGE_SIZE = env.int("DEFAULT_PAGINATION_PAGE_SIZE", default=150)
    DEFAULT_PAGINATION_MAX_PAGE_SIZE = env.int("DEFAULT_PAGINATION_MAX_PAGE_SIZE", default=150)

    # ------------------ Backend Admin Site Title and Header --------------------
    BACKEND_ADMIN_SITE_TITLE = env("BACKEND_ADMIN_SITE_TITLE", default="Lexicon Admin")
    BACKEND_ADMIN_SITE_HEADER = env("BACKEND_ADMIN_SITE_HEADER", default="Lexicon Backend")


class Development(BaseConfiguration):
    DEBUG = True


class Staging(BaseConfiguration):
    DEBUG = False


class Production(BaseConfiguration):
    DEBUG = False
