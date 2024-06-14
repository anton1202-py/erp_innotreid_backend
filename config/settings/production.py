from config.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Test',
        'USER': 'Test',
        "PASSWORD": "Test",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
