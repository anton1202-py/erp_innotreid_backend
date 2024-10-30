import requests
import json 

company_id = "99e41291-e70f-465b-b9c2-e98f0ac9c9f5"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMwOTE1NzcwLCJpYXQiOjE3MzAzMTA5NzAsImp0aSI6IjVmYjg1NjYwZTIxNzQ2MGZhMTUxNjUwMTk4NjdkZTYwIiwidXNlcl9pZCI6MX0.cgsTiHJEok9KLrsXwARcEcQ_lO3YXC995Fzuk5kA-Kg"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

with open("claster.json", 'r') as f :
    clasters = json.loads(f.read())

with open("warehouses.json", 'r') as f :
    wr = json.loads(f.read())

for claster_item in clasters:
    claster = claster_item["Кластер"]
    for item in claster_item["Что в него входит"]:
        region_name = item

        data = {
            "claster_to": claster,
            "region_name": region_name
        }

        print(requests.post(f"http://localhost:8000/api/claster/v1/{company_id}",json=data, headers=headers).text)

for wr_item in wr:
    claster = wr_item['Кластер']
    for item in wr_item["Склады"]:
        warehouse_id = item["id"]

        data = {
            "claster_to": claster,
            "warehouse_id": warehouse_id
        }

        print(requests.post(f"http://localhost:8000/api/claster/v1/warehouse/{company_id}", json=data, headers=headers).text)



