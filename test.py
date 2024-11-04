# import os 
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
# django.setup()

# from apps.product.tasks import get_yandex_orders

# print(len(get_yandex_orders("y0_AgAEA7qjt7KxAAwmdgAAAAELY-tgAACft8WA-URJh5WJkKCbUYyt3bxRug","2023-10-10",23746359,"")))

import json
import requests

headers = {
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxMjY4NTEyLCJpYXQiOjE3MzA2NjM3MTIsImp0aSI6ImMwMGUzYjU5N2IwYzQ2ZmM4MWVhNjg1ZTBiMjJmYWMxIiwidXNlcl9pZCI6MX0.H_i_j2YJvuq1qOLlljHrES7FI6D2MOR3eq0aU0aYj7g",
    'Content-Type': 'application/json'
}

company_id = "4e53ff0d-1ba1-4c92-9362-eb98729b676d"

# with open("claster.json", 'r') as f :
#     data = json.loads(f.read())

# for item in data:
#     claster = item['Кластер']
#     for region in item['Что в него входит']:
        
#         data = {
#         "claster_to": claster,
#         "region_name": region
#         }

#         print(requests.post(f"http://51.250.22.154:8000/api/claster/v1/{company_id}", json=data,headers=headers).status_code)


with open("ozon_warehouse.json", 'r') as f :
    data = json.loads(f.read())

for item in data.keys():
    claster_to = item
    for item_warehouse in data[item]:
        warehouse_id = item_warehouse
        data1 = {
                "claster_to": claster_to,
                "warehouse_name": warehouse_id
                }
        print(requests.post(f"http://51.250.22.154:8000/api/claster/v1/ozon/{company_id}", json=data1,headers=headers).status_code)