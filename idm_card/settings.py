import django
import email.utils

import kombu
import os
import six
from django.urls import reverse
from django.utils.functional import lazy

DEBUG = os.environ.get('DJANGO_DEBUG')

USE_TZ = True
TIME_ZONE = 'Europe/London'


ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split() if not DEBUG else ['*']

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY and DEBUG:
    SECRET_KEY = 'very secret key'

if 'DJANGO_ADMINS' in os.environ:
    ADMINS = [email.utils.parseaddr(addr.strip()) for addr in os.environ['DJANGO_ADMINS'].split(',')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + (
            'postgresql' if django.VERSION >= (1, 9) else 'postgresql_psycopg2'),
        'NAME': os.environ.get('DATABASE_NAME', 'idm_card'),
    },
}

INSTALLED_APPS = [
    'idm_brand',
    'idm_broker.apps.IDMBrokerConfig',
    'idm_card',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'oidc_auth',
    'reversion',
    'rest_framework',
]
try:
    __import__('django_extensions')
except ImportError:
    pass
else:
    INSTALLED_APPS.append('django_extensions')

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'oidc_auth.auth.OpenIDConnectBackend',
    'django.contrib.auth.backends.ModelBackend',
]


OIDC_AUTH = {
    'DEFAULT_PROVIDER': {
        'issuer': os.environ.get('OIDC_ISSUER', 'http://localhost:8001/'),
        'authorization_endpoint': os.environ.get('OIDC_AUTHORIZATION_ENDPOINT', 'http://localhost:8001/openid/authorize'),
        'token_endpoint': os.environ.get('OIDC_TOKEN_ENDPOINT', 'http://localhost:8001/openid/token'),
        'userinfo_endpoint': os.environ.get('OIDC_USERINFO_ENDPOINT', 'http://localhost:8001/openid/userinfo'),
        'jwks_uri': os.environ.get('OIDC_JWKS_URI', 'http://localhost:8001/openid/jwks'),
        'client_id': os.environ.get('OIDC_CLIENT_ID', ''),
        'client_secret': os.environ.get('OIDC_CLIENT_SECRET', ''),
        'signing_alg': os.environ.get('OIDC_SIGNING_ALG', 'RS256')
    },
    'SCOPES': os.environ.get('OIDC_SCOPES', 'identity').split(),
    'PROCESS_USERINFO': 'idm_card.auth.process_userinfo',
}

LOGIN_URL = 'oidc-login'
LOGOUT_URL = 'logout'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'idm_card.context_processors.idm_card',
            ),
        },
    },
]

IDM_CORE_URL = os.environ.get('IDM_CORE_URL', 'http://localhost:8000/')
IDM_AUTH_URL = os.environ.get('IDM_AUTH_URL', 'http://localhost:8001/')

# AMQP
BROKER_ENABLED = bool(os.environ.get('BROKER_ENABLED'))
BROKER_TRANSPORT = os.environ.get('BROKER_TRANSPORT', 'amqp')
BROKER_HOSTNAME= os.environ.get('BROKER_HOSTNAME', 'localhost')
BROKER_SSL = os.environ.get('BROKER_SSL', 'yes').lower() not in ('no', '0', 'off', 'false')
BROKER_VHOST= os.environ.get('BROKER_VHOST', '/')
BROKER_USERNAME = os.environ.get('BROKER_USERNAME', 'guest')
BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', 'guest')
BROKER_PREFIX = os.environ.get('BROKER_PREFIX', 'idm.core.')

ROOT_URLCONF = 'idm_card.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT')

MEDIA_ROOT = os.environ.get('DJANGO_MEDIA_ROOT')

LOGIN_REDIRECT_URL = '/account/profile/'
LOGIN_URL = 'oidc-login'
LOGOUT_URL = 'logout'


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')

IDM_CORE_URL = os.environ.get('IDM_CORE_URL', 'http://localhost:8000/')
IDM_CORE_API_URL = os.environ.get('IDM_CORE_API_URL', 'http://localhost:8000/api/')

SESSION_COOKIE_NAME = 'idm-card-sessionid'

# The SOCIAL_AUTH_SAML_ENABLED_IDPS setting mentioned in the docs (http://psa.matiasaguirre.net/docs/backends/saml.html)
# is replaced by idm_auth.saml.models.IDP, and you can add more with fixtures, the admin, or the load_saml_metadata
# management command.

for key in os.environ:
    if key.startswith('SOCIAL_AUTH_'):
        locals()[key] = os.environ[key]

EMAIL_HOST = os.environ.get('SMTP_SERVER')
EMAIL_HOST_USER = os.environ.get('SMTP_USER')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_USE_TLS = True

EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

IDM_APPLICATION_ID = '4ff517c5-532f-42ee-afb1-a5d3da2f61d5'

CLIENT_PRINCIPAL_NAME = os.environ.get('CLIENT_PRINCIPAL_NAME')


AUTH_USER_MODEL = 'idm_card.User'


IDM_BROKER = {
    'CONSUMERS': [{
        'queues': [kombu.Queue('idm.card.person',
                               exchange=kombu.Exchange('idm.core.person', type='topic', passive=True),
                               routing_key='#')],
        'tasks': ['idm_card.tasks.process_person_update'],
    }],
}
