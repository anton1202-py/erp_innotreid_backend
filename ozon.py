import requests
import json


url = 'https://api-seller.ozon.ru/v2/product/list'
url_info = 'https://api-seller.ozon.ru/v2/product/info'

headers = {
    'Client-Id': '48762',
    'Api-Key': '5b3b0e68-3f96-4772-9550-9951cb3d1678',
    'Content-Type': 'application/json'
}

params = {

}

data = {
    "product_id": 482172568
}
data_json = json.dumps(data)

response = requests.post(url, headers=headers, params=params)
response_info = requests.post(url_info, headers=headers, data=data_json)

print(response.json())
print()
print(response_info.json())
