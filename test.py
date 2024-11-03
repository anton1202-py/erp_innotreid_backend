import os 
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.product.tasks import get_yandex_orders

print(len(get_yandex_orders("y0_AgAEA7qjt7KxAAwmdgAAAAELY-tgAACft8WA-URJh5WJkKCbUYyt3bxRug","2023-10-10",23746359,"")))