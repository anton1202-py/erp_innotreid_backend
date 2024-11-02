import os
import django
# Django sozlamalarini o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.product.tasks import get_yandex_orders

# Kerakli headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer y0_AgAEA7qjt7KxAAwmdgAAAAELY-tgAACft8WA-URJh5WJkKCbUYyt3bxRug'
}

# get_yandex_orders chaqiruvini chop etish
print(len(get_yandex_orders("y0_AgAEA7qjt7KxAAwmdgAAAAELY-tgAACft8WA-URJh5WJkKCbUYyt3bxRug", "2024-10-05", 42494921, "")))
