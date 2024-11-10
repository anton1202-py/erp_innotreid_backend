import requests
import json 

company_id = "99e41291-e70f-465b-b9c2-e98f0ac9c9f5"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxODUyOTc3LCJpYXQiOjE3MzEyNDgxNzcsImp0aSI6ImY0YTAxNDVmYmY2MDQwYjNhZTMwZGJkOTdjN2FhZTkxIiwidXNlcl9pZCI6MX0.blw2wSjmynWqFAJUMan6vAWNpDgZ1a0X5y6-bCQ0yBw"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

MOSKVA_ZAPAD_CLUSTER = ['ГРИВНО_РФЦ', 'ДОМОДЕДОВО_РФЦ', 'ПЕТРОВСКОЕ_РФЦ', 'ХОРУГВИНО_РФЦ', 'СОФЬИНО_РФЦ']
MOSKVA_VOSTOK = ['ЖУКОВСКИЙ_РФЦ', 'НОГИНСК_РФЦ', 'ПУШКИНО_1_РФЦ', 'ПУШКИНО_2_РФЦ', 'ТВЕРЬ_РФЦ', 'ТВЕРЬ_ХАБ']
SANKT_PETERBURG = ['САНКТ_ПЕТЕРБУРГ_РФЦ', 'СПБ_БУГРЫ_РФЦ', 'СПБ_КОЛПИНО_РФЦ', 'СПБ_ШУШАРЫ_РФЦ']
DON = ['ВОРОНЕЖ_МРФЦ', 'ВОРОНЕЖ_2_РФЦ', 'ВОЛГОГРАД_МРФЦ', 'РОСТОВ_НА_ДОНУ_РФЦ']
UG = ['АДЫГЕЙСК_РФЦ', 'НЕВИННОМЫССК_РФЦ', 'НОВОРОССИЙСК_МРФЦ']
POVOLZHIE = ['КАЗАНЬ_РФЦ', 'НИЖНИЙ_НОВГОРОД_РФЦ', 'ОРЕНБУРГ_РФЦ', 'САМАРА_РФЦ']
URAL = ['ЕКАТЕРИНБУРГ_РФЦ']
SIBIR = ['КРАСНОЯРСК_МРФЦ', 'НОВОСИБИРСК_РФЦ', 'ОМСК_РФЦ']
KALININGRAD = ['КАЛИНИНГРАД_МРФЦ']
DALNIY_VASTOK = ['ХАБАРОВСК_2_РФЦ']
BELARUS = ['МИНСК_МПСЦ']
KAZAKHSTAN = ['АСТАНА_РФЦ', 'АЛМАТЫ_МРФЦ']

cluster_dict = {
    'Москва-Запад': MOSKVA_ZAPAD_CLUSTER,
    'Москва-Восток и Дальние регионы': MOSKVA_VOSTOK,
    'Санкт-Петербург и СЗО': SANKT_PETERBURG,
    'Дон': DON,
    'Юг': UG,
    'Поволжье': POVOLZHIE,
    'Урал': URAL,
    'Сибирь': SIBIR,
    'Калининград': KALININGRAD,
    'Дальний Восток': DALNIY_VASTOK,
    'Беларусь': BELARUS,
    'Казахстан': KAZAKHSTAN
}
CLUSTERS_NAME = ['Москва-Запад', 
                     'Москва-Восток и Дальние регионы', 
                     'Санкт-Петербург и СЗО', 
                     'Дон', 
                     'Юг',
                     'Поволжье',
                     'Урал',
                     'Сибирь',
                     'Калининград',
                     'Дальний Восток',
                     'Беларусь',
                     'Казахстан']


with open("ozon_warehouse.json", 'r') as f:
    clasters = json.loads(f.read())


for claster_item in clasters:
    claster = claster_item["classter_to"]
    for item in claster_item["warehouses"]:
        region_name = item

        data = {
            "claster_to": claster,
            "warehouse_name": region_name
        }

        print(requests.post(f"http://localhost:8000/api/claster/v1/ozon/{company_id}",json=data, headers=headers).text)

# for wr_item in wr:
#     claster = wr_item['classter_to']
#     for item in wr_item["warehouses"]:
#         warehouse_id = item

#         data = {
#             "claster_to": claster,
#             "warehouse_id": warehouse_id
#         }

#         print(requests.post(f"http://51.250.22.154:8000/api/claster/v1/warehouse/{company_id}", json=data, headers=headers).text)



