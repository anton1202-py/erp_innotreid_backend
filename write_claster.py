from datetime import datetime
import requests

def get_paid_orders(url, headers, date_from, status="delivering"):
    
    # data = {
    #     "dir": "asc",
    #     "filter": {
    #         "status": status,
    #         "since": date_from,
    #         "to": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    #     },
    #     "limit": 1000,  
    #     "offset": 0,
    #     "warehouse_type": "ALL",
    #     "with": {
    #         "analytics_data": True,
    #         "financial_data": True
    #     }
    # }

    data = {
    "limit": 1000,
    "offset": 0,
    "warehouse_type": "ALL"
    }

    results = []
    response = requests.post(url, headers=headers, json=data)
    # print(response.text)
    # print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
    
    while "result" in response.json().keys() and response.json()["result"]["rows"]:
        results += response.json().get('result', [])['rows']
        data['offset'] += 1000
        # print(response.json().get("result")[0]["order_id"])
        response = requests.post(url, headers=headers, json=data)
        # print("data added")
        
    
    return results

FBO_URL = "https://api-seller.ozon.ru/v2/posting/fbo/list"
FBS_URL = "https://api-seller.ozon.ru/v2/posting/fbs/list"

headers = {
            'Client-Id': "48762",
            'Api-Key': "5b3b0e68-3f96-4772-9550-9951cb3d1678",
            'Content-Type': 'application/json'
        }

results = get_paid_orders("https://api-seller.ozon.ru/v2/analytics/stock_on_warehouses", headers, date_from="2024-01-01T15:37:04.694146Z")
# print(len(results1))
# results2 = get_paid_orders(FBS_URL, headers, date_from="2024-01-01T15:37:04.694146Z")
# print(len(results2))

# results3 = get_paid_orders(FBO_URL, headers, date_from="2024-01-01T15:37:04.694146Z",status="awaiting_packaging")
# print(len(results3))
# results4 = get_paid_orders(FBS_URL, headers, date_from="2024-01-01T15:37:04.694146Z",status="awaiting_packaging")
# print(len(results4))
# results5 = get_paid_orders(FBO_URL, headers, date_from="2024-01-01T15:37:04.694146Z",status="awaiting_deliver")
# print(len(results5))
# results6 = get_paid_orders(FBS_URL, headers, date_from="2024-01-01T15:37:04.694146Z",status="awaiting_deliver")
# print(len(results6))
# results7 = get_paid_orders(FBO_URL, headers, date_from="2024-01-01T15:37:04.694146Z",status="delivered")
# print(len(results7))
# results8 = get_paid_orders(FBS_URL, headers, date_from="2024-01-01T15:37:04.694146Z",status="delivered")
# print(len(results8))
# print("success get data")

# results = results1 + results2 + results3 + results4 + results5 + results6 + results8 + results7
print(len(results))

dc = {"warehouse": 0}

for item in results:
    dc[item["warehouse_name"]] = 0

str1 = ""

for str_item in dc.keys():
    str1 += f"{str_item}\n"

with open("warehouse2_ozon.txt", "w") as f:
    f.write(str1)


