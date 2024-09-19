from json import dumps
import calendar

import requests
from datetime import datetime, timedelta
from celery import shared_task
from django.db.models import F
from apps.marketplaceservice.models import Ozon, Wildberries, YandexMarket
from apps.product.models import Product, ProductSale, ProductOrder, ProductStock, Warehouse, WarehouseForStock
from config.celery import app

date_from = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

wildberries_orders_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={date_from}T00:00:00'
wildberries_stocks_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom={date_from}T00:00:00'
ozon_sales_url = 'https://api-seller.ozon.ru/v1/analytics/data'
ozon_product_info_url = 'https://api-seller.ozon.ru/v2/product/info'
yandex_market_sales_url = 'https://api.partner.market.yandex.ru/reports/shows-sales/generate?format=CSV'
yandex_report_url = 'https://api.partner.market.yandex.ru/reports/info/{report_id}'

@app.task
def update_wildberries_sales():

    for wildberries in Wildberries.objects.all():
        
        wb_api_key = wildberries.wb_api_key
        company = wildberries.company
        try:
            latest_product_sale = ProductSale.objects.filter(marketplace_type="wildberries").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            latest_product_sale = False
        if not latest_product_sale:
            latest_product_sale = (datetime.now()-timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%S')
        wildberries_sales_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/sales?dateFrom={latest_product_sale}'
        response = requests.get(wildberries_sales_url, headers={'Authorization': f'{wb_api_key}'})
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                
                warehouse, created = Warehouse.objects.get_or_create(
                    name = item['warehouseName'],
                    country_name = item['countryName'],
                    oblast_okrug_name = item['oblastOkrugName'],
                    region_name = item['regionName']
                )

                wildberries = wildberries
                warehouse = warehouse
                barcode = item["barcode"]

                product = Product.objects.filter(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
                if product.exists():
                    product = product.first()
                else:
                    product, _ = Product.objects.get_or_create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
                date = datetime.strptime(item['date'],"%Y-%m-%dT%H:%M:%S")
                product_sale, created_sale= ProductSale.objects.get_or_create(
                    product=product,
                    company=company,
                    date=date,
                    marketplace_type="wildberries",
                    warehouse=warehouse
                )
                
                
                
        else:
            return response.text
        return "Success"

@app.task
def update_wildberries_orders():
    for wildberries in Wildberries.objects.all():
        
        wb_api_key = wildberries.wb_api_key
        company = wildberries.company
        try:
            latest_product_sale = ProductOrder.objects.filter(marketplace_type="wildberries").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            latest_product_sale = False
        if not latest_product_sale:
            latest_product_sale = date_from
        wildberries_sales_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={latest_product_sale}'
        response = requests.get(wildberries_sales_url, headers={'Authorization': f'{wb_api_key}'})
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                
                warehouse, created = Warehouse.objects.get_or_create(
                    name = item['warehouseName'],
                    country_name = item['countryName'],
                    oblast_okrug_name = item['oblastOkrugName'],
                    region_name = item['regionName']
                )

                wildberries = wildberries
                warehouse = warehouse
                barcode = item['barcode']
                product = Product.objects.filter(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
                if product.exists():
                    product = product.first()
                else:
                    product, _ = Product.objects.get_or_create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
                date = datetime.strptime(item['date'],"%Y-%m-%dT%H:%M:%S")
                product_order, created_sale= ProductOrder.objects.get_or_create(
                    product=product,
                    company=company,
                    date=date,
                    marketplace_type="wildberries",
                    warehouse=warehouse
                )
                
        else:
            return response.text
        return "Success"

@app.task
def update_wildberries_stocks():
    
    for wildberries in Wildberries.objects.all():
        wb_api_key = wildberries.wb_api_key
        response = requests.get(wildberries_stocks_url, headers={'Authorization': f'Bearer {wb_api_key}'})

        for item in response.json():
            warehouse = item['warehouseName']
            quantity = item['quantity']
            company = wildberries.company
            date = datetime.strptime(item["lastChangeDate"],"%Y-%m-%dT%H:%M:%S")
            
            barcode = item['barcode']
            product = Product.objects.filter(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
            if product.exists():
                product = product.first()
            else:
                product, _ = Product.objects.get_or_create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
            warehouse_obj, created_w = WarehouseForStock.objects.get_or_create(name=warehouse, marketplace_type="wildberries")
            
            product_stock, created_s = ProductStock.objects.get_or_create(
                product=product,
                warehouse=warehouse_obj,
                marketplace_type = "wildberries",
                company=company,
                date=date
            )
            if created_s:
                product_stock.quantity = quantity
                product_stock.save()
            else:
                product_stock.quantity = quantity
                product_stock.save()
            
    return "Succes"
            
def get_paid_orders(url, headers, date_from, status="delivered",status_2="paid"):
    date = datetime.strptime(date_from,"%Y-%m-%dT%H:%M:%S.%fZ")
    data = {
        "dir": "asc",
        "filter": {
            "status": status,
            "financial_status": status_2,
            "since": date_from,
            "to": (date + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        },
        "limit": 1000,  
        "offset": 0,
        "with": {
            "analytics_data": True,
            "financial_data": True
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('result', [])
    else:
      
        return []

def get_barcode(vendor_code, api_key, client_id):
    body = {"offer_id": vendor_code}
    headers = {
        "Api-Key":api_key,
        "Client-Id": client_id,
        'Content-Type': 'application/json'
    }

    response = requests.post("https://api-seller.ozon.ru/v2/product/info",json=body, headers=headers)
    return response.json()["result"]["barcode"]

@app.task
def update_ozon_sales():
    
    FBO_URL = "https://api-seller.ozon.ru/v2/posting/fbo/list"
    FBS_URL = "https://api-seller.ozon.ru/v2/posting/fbs/list"
    
    for ozon in Ozon.objects.all():
        company = ozon.company
        api_token = ozon.api_token
        client_id = ozon.client_id
        headers = {
            'Client-Id': client_id,
            'Api-Key': api_token,
            'Content-Type': 'application/json'
        }

        try:
            date_from = ProductSale.objects.filter(marketplace_type="ozon").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            date_from = False
        if not date_from:
            date_from = (datetime.now()-timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        while datetime.strptime(date_from,'%Y-%m-%dT%H:%M:%S.%fZ') <= datetime.now():
            count1 = ProductSale.objects.filter(marketplace_type="ozon").count()
            fbo_orders = get_paid_orders(FBO_URL,headers,date_from)
            fbs_orders = get_paid_orders(FBS_URL,headers,date_from)
            results = fbo_orders + fbs_orders

            for item in results:
                try:
                    date = datetime.strptime(item['in_process_at'],"%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    date = datetime.strptime(item['in_process_at'],"%Y-%m-%dT%H:%M:%SZ")
                sku = item['products'][0]['offer_id']
                
                if "warehouse_name" in item["analytics_data"].keys():
                    warehouse_name = item["analytics_data"]['warehouse_name']
                else:
                    warehouse_name = ""
                oblast_okrug_name = item["analytics_data"]['region']
                region_name = item["analytics_data"]['city']
                barcode = get_barcode(vendor_code=sku, api_key=ozon.api_token,client_id=ozon.client_id)
                product = Product.objects.filter(barcode=barcode)
                if product.exists():
                    wildberries_product = product.filter(marketplace_type="wildberries")
                    if wildberries_product.exists():
                        vendor_code = wildberries_product.first().vendor_code
                        ozon_product = product.filter(marketplace_type='ozon')
                        if ozon_product.exists():
                            ozon_product.first().vendor_code = vendor_code
                            ozon_product.first().save()
                            product = ozon_product.first()
                    else:
                        product = product.first()
                else:
                    product, created_p = Product.objects.get_or_create(vendor_code=sku, marketplace_type="ozon", barcode=barcode)
                warehouse, created_w = Warehouse.objects.get_or_create(
                    name = warehouse_name,
                    country_name = "Russia",
                    oblast_okrug_name = oblast_okrug_name,
                    region_name = region_name
                )
                if not ProductSale.objects.filter(
                    product=product,
                    company=company,
                    date=date,
                    warehouse=warehouse,
                    marketplace_type = "ozon"
                ).exists():
                    product_sale = ProductSale.objects.get_or_create(
                        product=product,
                        company=company,
                        date=date,
                        warehouse=warehouse,
                        marketplace_type = "ozon"
                    )
            try:
                date_from1 = ProductSale.objects.filter(marketplace_type="ozon").latest('date').date
            except:
                date_from1 = (datetime.strptime(date_from,'%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(days=3))
            if date_from1 != datetime.strptime(date_from,'%Y-%m-%dT%H:%M:%S.%fZ'):
                date_from = date_from1.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                date_from = (date_from1 + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

@app.task
def update_ozon_orders():
    
    FBO_URL = "https://api-seller.ozon.ru/v2/posting/fbo/list"
    FBS_URL = "https://api-seller.ozon.ru/v2/posting/fbs/list"
    try:
        date_from = ProductOrder.objects.filter(marketplace_type="ozon").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        date_from = False
    if not date_from:
        date_from = (datetime.now()-timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    for ozon in Ozon.objects.all():
        company = ozon.company
        api_token = ozon.api_token
        client_id = ozon.client_id
        headers = {
            'Client-Id': client_id,
            'Api-Key': api_token,
            'Content-Type': 'application/json'
        }

        while datetime.strptime(date_from,'%Y-%m-%dT%H:%M:%S.%fZ') <= datetime.now():

            fbo_orders = get_paid_orders(FBO_URL,headers,date_from,"awaiting_packaging","")
            fbs_orders = get_paid_orders(FBS_URL,headers,date_from, "awaiting_deliver","")
            
            results = fbo_orders + fbs_orders 

            for item in results:
                
                date = item['in_process_at']
                sku = item['products'][0]['offer_id']
                
                if "warehouse_name" in item["analytics_data"].keys():
                    warehouse_name = item["analytics_data"]['warehouse_name']
                
                warehouse_name = ""
                oblast_okrug_name = item["analytics_data"]['region']
                region_name = item["analytics_data"]['city']

                barcode = get_barcode(vendor_code=sku, api_key=ozon.api_token,client_id=ozon.client_id)
                product = Product.objects.filter(barcode=barcode)
                if product.exists():
                    wildberries_product = product.filter(marketplace_type="wildberries")
                    if wildberries_product.exists():
                        vendor_code = wildberries_product.first().vendor_code
                        ozon_product = product.filter(marketplace_type='ozon')
                        if ozon_product.exists():
                            ozon_product.first().vendor_code = vendor_code
                            ozon_product.first().save()
                            product = ozon_product.first()
                    else:
                        product = product.first()
                else:
                    product, created_p = Product.objects.get_or_create(vendor_code=sku, marketplace_type="ozon", barcode=barcode)
                warehouse, created_w = Warehouse.objects.get_or_create(
                    name = warehouse_name,
                    country_name = "Russia",
                    oblast_okrug_name = oblast_okrug_name,
                    region_name = region_name
                )
                
                product_sale = ProductOrder.objects.get_or_create(
                    product=product,
                    company=company,
                    date=date,
                    warehouse=warehouse,
                    marketplace_type = "ozon"
                )
             
            try:
                date_from1 = ProductOrder.objects.filter(marketplace_type="ozon").latest('date').date
            except:
                date_from1 = (datetime.strptime(date_from,'%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(days=3))
            if date_from1 != datetime.strptime(date_from,'%Y-%m-%dT%H:%M:%S.%fZ'):
                date_from = date_from1.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                date_from = (date_from1 + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

@app.task
def update_ozon_stocks():
    
    for ozon in Ozon.objects.all():
        api_key = ozon.api_token
        client_id = ozon.client_id
        
        headers = {
            'Client-Id': client_id,
            'Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        url = "https://api-seller.ozon.ru/v2/analytics/stock_on_warehouses"
        data = {
        "limit": 1000,
        "offset": 0,
        "warehouse_type": "ALL"
        }
        response = requests.post(url, headers=headers, json=data)
        
        company = ozon.company
    
        if response.status_code == 200:
            results = response.json().get('result').get("rows",[])
        else:
            results = []

        for item in results:
            
            vendor_code = item['item_code']
            warehouse = item['warehouse_name']
            quantity = item['reserved_amount']
            
            date = datetime.now()
            barcode = get_barcode(vendor_code=vendor_code, api_key=ozon.api_token,client_id=ozon.client_id)
            product = Product.objects.filter(barcode=barcode)
            if product.exists():
                wildberries_product = product.filter(marketplace_type="wildberries")
                if wildberries_product.exists():
                    vendor_code = wildberries_product.first().vendor_code
                    ozon_product = product.filter(marketplace_type='ozon')
                    if ozon_product.exists():
                        ozon_product.first().vendor_code = vendor_code
                        ozon_product.first().save()
                        product = ozon_product.first()
                else:
                    product = product.first()
            else:
                product, created_p = Product.objects.get_or_create(vendor_code=vendor_code, marketplace_type="ozon", barcode=barcode)
            warehouse_obj, created_w = WarehouseForStock.objects.get_or_create(name=warehouse, marketplace_type="ozon")
            product_stock, created_s = ProductStock.objects.get_or_create(
                product=product,
                warehouse=warehouse_obj,
                marketplace_type = "ozon",
                company=company,
                date=date
            )
            if created_s:
                product_stock.quantity = quantity
                product_stock.save()
            else:
                product_stock.quantity = quantity
                product_stock.save()        
    return "Succes"

def get_yandex_orders(api_key, date_from, client_id, status="DELIVERED"):
    date_to = datetime.now().strftime("%d-%m-%Y")
    url = f"https://api.partner.market.yandex.ru/campaigns/{client_id}/orders?orderIds=&status={status}&substatus=&fromDate={date_from}&toDate={date_to}&supplierShipmentDateFrom=&supplierShipmentDateTo=&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&buyerType=&page=&pageSize="
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
                }
    
    difrence = (datetime.now() - datetime.strptime(date_from,"%d-%m-%Y")).days
    if difrence == 365:
        orders = []
        months = []
        year = datetime.now().year
        for month in range(1, 13):  
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, calendar.monthrange(year, month)[1])
            months.append((first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))   
            
        for date_from, date_to in months:
            
            url = f"https://api.partner.market.yandex.ru/campaigns/{client_id}/orders?orderIds=&status={status}&substatus=&fromDate={date_from}&toDate={date_to}&supplierShipmentDateFrom=&supplierShipmentDateTo=&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&buyerType=&page=&pageSize="
            response = requests.get(url, headers=headers).json()["orders"]
            orders += response
    
    else:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            orders = response.json()['orders']
            return orders
        else:
            
            return []
    return orders

def find_barcode(vendor_code, company_id, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(f"https://api.partner.market.yandex.ru/businesses/{company_id}/offer-mappings",headers=headers).json()
    result = []
    while "paging" in response["result"] and "nextPageToken" in response['result']["paging"]:
        result += response["result"]["offerMappings"]
        params = {"page_token": response['result']["paging"]['nextPageToken']}
        response = requests.post(f"https://api.partner.market.yandex.ru/businesses/{company_id}/offer-mappings",headers=headers, params=params).json()

    result += response["result"]["offerMappings"]
    for product in result:
        if product["offer"]["offerId"] == vendor_code:
            return product["offer"]["barcodes"][0]
        
@app.task
def update_yandex_market_sales():
    
    for yandex_market in YandexMarket.objects.all():
        
        api_key_bearer = yandex_market.api_key_bearer
        fby_campaign_id = yandex_market.fby_campaign_id
        fbs_campaign_id = yandex_market.fbs_campaign_id
        company = yandex_market.company
        
        date_from = ProductSale.objects.filter(marketplace_type="yandexmarket")

        if not (date_from or date_from.exists()):
            date_from = (datetime.now()-timedelta(days=365)).strftime("%d-%m-%Y")
        else:
            date_from =date_from.latest("date").date.strftime("%d-%m-%Y")

        results1 = get_yandex_orders(api_key_bearer, date_from,client_id=fby_campaign_id)
        results2 = get_yandex_orders(api_key_bearer, date_from,client_id=fbs_campaign_id)

        results = results1 + results2

        for item in results:
            
            buyer_total = item.get("buyerTotal",0)
            item_total = item.get("itemsTotal",0)

            if buyer_total == item_total:
                if "serviceName" in item["delivery"].keys():
                    warehouse_name = item["delivery"]['serviceName']
            
                warehouse_name = ""
                oblast_okrug_name = item["delivery"]['region']['parent']['name']
                region_name = item["delivery"]['region']['name']
                try:
                    country_name = item.get('delivery', {}).get('address', {}).get('country', "")
                except:
                    country_name = "Russia"

                warehouse, created_w = Warehouse.objects.get_or_create(
                    name = warehouse_name,
                    country_name = country_name,
                    oblast_okrug_name = oblast_okrug_name,
                    region_name = region_name
                )
                
                products = item["items"]
                date = datetime.strptime(item['updatedAt'],"%d-%m-%Y %H:%M:%S")
                
                for product in products:
                    
                    vendor_code = product["offerId"]
                    barcode = find_barcode(vendor_code=vendor_code,company_id=yandex_market.business_id,api_key=yandex_market.api_key_bearer)
                    product_obj = Product.objects.filter(barcode=barcode)
                    if product_obj.exists():
                        wildberries_product = product_obj.filter(marketplace_type="wildberries")
                        if product_obj.exists():
                            vendor_code = wildberries_product.first().vendor_code
                            yandex_market_p = Product.objects.filter(barcode=barcode, marketplace_type="yandexmarket")
                            if yandex_market_p.exists():
                                yandex_market_p.first().vendor_code = vendor_code
                                yandex_market.save()
                                product_obj = yandex_market_p.first()
                        else:
                            product_obj = product_obj.first()
                    else:
                        product_obj, created_p = Product.objects.get_or_create(vendor_code=vendor_code, barcode=barcode, marketplace_type="yandexmarket")
                    if ProductSale.objects.filter(
                        product=product_obj,
                        company=company,
                        date=date,
                        warehouse=warehouse,
                        marketplace_type="yandexmarket"
                    ).exists():
                        product_s = ProductSale.objects.get_or_create(
                            product=product_obj,
                            company=company,
                            date=date,
                            warehouse=warehouse,
                            marketplace_type="yandexmarket"
                        )

                    date = date + timedelta(seconds=1)
    return "succes"
                    
@app.task
def update_yandex_market_orders():
    
    for yandex_market in YandexMarket.objects.all():
        api_key_bearer = yandex_market.api_key_bearer
        fby_campaign_id = yandex_market.fby_campaign_id
        fbs_campaign_id = yandex_market.fbs_campaign_id
        company = yandex_market.company
        date_from = ProductOrder.objects.filter(marketplace_type="yandexmarket")

        if not (date_from or date_from.exists()):
            date_from = (datetime.now()-timedelta(days=365)).strftime("%d-%m-%Y")
        else:
            date_from =date_from.latest("date").date.strftime("%d-%m-%Y")

        results1 = get_yandex_orders(api_key_bearer, date_from,client_id=fby_campaign_id,status="PROCESSING")
        results2 = get_yandex_orders(api_key_bearer, date_from,client_id=fbs_campaign_id,status="PROCESSING")

        results = results1 + results2

        for item in results:
            buyer_total = item.get("buyerTotal",0)
            item_total = item.get("itemsTotal",0)

            if buyer_total == item_total:
                if "serviceName" in item["delivery"].keys():
                    warehouse_name = item["delivery"]['serviceName']
            
                warehouse_name = ""
                oblast_okrug_name = item["delivery"]['region']['parent']['name']
                region_name = item["delivery"]['region']['name']
                try:
                    country_name = item.get('delivery', {}).get('address', {}).get('country', "")
                except:
                    country_name = "Russia"

                warehouse, created_w = Warehouse.objects.get_or_create(
                    name = warehouse_name,
                    country_name = country_name,
                    oblast_okrug_name = oblast_okrug_name,
                    region_name = region_name
                )
                
                products = item["items"]
                date = datetime.strptime(item['updatedAt'],"%d-%m-%Y %H:%M:%S")
                
                for product in products:
                    vendor_code = product["offerId"]
                    barcode = find_barcode(vendor_code=vendor_code,company_id=yandex_market.business_id,api_key=yandex_market.api_key_bearer)
                    product_obj = Product.objects.filter(barcode=barcode)
                    if product_obj.exists():
                        wildberries_product = product_obj.filter(marketplace_type="wildberries")
                        if product_obj.exists():
                            vendor_code = wildberries_product.first().vendor_code
                            yandex_market_p = Product.objects.filter(barcode=barcode, marketplace_type="yandexmarket")
                            if yandex_market_p.exists():
                                yandex_market_p.first().vendor_code = vendor_code
                                yandex_market.save()
                                product_obj = yandex_market_p.first()
                        else:
                            product_obj = product_obj.first()
                    else:
                        product_obj, created_p = Product.objects.get_or_create(vendor_code=vendor_code, barcode=barcode, marketplace_type="yandexmarket")
                    product_s = ProductOrder.objects.get_or_create(
                        product=product_obj,
                        company=company,
                        date=date,
                        warehouse=warehouse,
                        marketplace_type="yandexmarket"
                    )

                    date = date + timedelta(seconds=1)
    return "succes"    

def get_warehouse_name(business_id,headers, warehouse_id):
    warehouse_by_busness_id_url = f"https://api.partner.market.yandex.ru/businesses/{business_id}/warehouses"               
    warehouse_url = f"https://api.partner.market.yandex.ru/warehouses"    

    get_warehouse_name_l = requests.get(warehouse_by_busness_id_url,headers=headers).json()["result"]["warehouses"]
    get_warehouse_name_l_2 = requests.get(warehouse_url,headers=headers).json()["result"]["warehouses"]
    results = get_warehouse_name_l + get_warehouse_name_l_2
    
    for item in results:
        if item["id"] == warehouse_id:
            return item['name']

@app.task
def update_yandex_stocks():
    
    for yandex in YandexMarket.objects.all():
        api_key = yandex.api_key_bearer
        fbs = yandex.fbs_campaign_id
        fby = yandex.fby_campaign_id
        business_id = yandex.business_id
        
        url = "https://api.partner.market.yandex.ru/campaigns/{campaignId}/offers/stocks"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
                }
        response1 = requests.post(url.format(campaignId=fbs), headers=headers)
        result1 = []
        response2 = requests.post(url.format(campaignId=fby), headers=headers)
        result2 = []
        
        while True:
            if response1.status_code == 200 and "paging" in response1.json()["result"].keys() and "nextPageToken" in response1.json()["result"]["paging"].keys():
                result1 += response1.json()["result"]["warehouses"]
                nextPageToken = response1.json()["result"]["paging"]["nextPageToken"]
                params = {"page_token": nextPageToken}
                response1 = requests.post(url.format(campaignId=fbs), headers=headers,params=params)
            else:
                break
        
        while True:
            if response2.status_code == 200 and "paging" in response2.json()["result"].keys() and "nextPageToken" in response2.json()["result"]["paging"].keys():
                result2 += response2.json()["result"]["warehouses"]
                nextPageToken = response2.json()["result"]["paging"]["nextPageToken"]
                params = {"page_token": nextPageToken}
                response2 = requests.post(url.format(campaignId=fby), headers=headers,params=params)
            else:
                break
        company = yandex.company
    
        results = result1 + result2
       
        for item in results:
            warehouse = get_warehouse_name(business_id,headers,item['warehouseId'])
            for offers in item['offers']:
                if "upatedAt" in offers.keys():
                    date = datetime.strptime(offers['updatedAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
                else:
                    date = datetime.now()
                vendor_code = offers["offerId"]
                count = 0
                for stock in offers['stocks']:
                    if stock and stock["type"] == "AVAILABLE":
                        count += stock["count"]
                quantity = count
            
                barcode = find_barcode(vendor_code=vendor_code,company_id=yandex.business_id,api_key=yandex.api_key_bearer)
                product = Product.objects.filter(barcode=barcode)
                if product.exists():
                    wildberries_product = product.filter(marketplace_type="wildberries")
                    if product.exists():
                        vendor_code = wildberries_product.first().vendor_code
                        yandex_p = Product.objects.filter(barcode=barcode, marketplace_type="yandexmarket")
                        if yandex_p.exists():
                            yandex_p.first().vendor_code = vendor_code
                            yandex.save()
                            product = yandex_p.first()
                        else:
                            product = product.first()
                    else:
                        product, created_p = Product.objects.get_or_create(vendor_code=vendor_code, barcode=barcode, marketplace_type="yandexmarket")
                warehouse_obj, created_w = WarehouseForStock.objects.get_or_create(name=warehouse, marketplace_type="yandexmarket")
                try:
                    product_stock, created_s = ProductStock.objects.get_or_create(
                        product=product,
                        warehouse=warehouse_obj,
                        marketplace_type = "yandexmarket",
                        company=company,
                        date=date
                    )
                    if created_s:
                        product_stock.quantity = quantity
                        product_stock.save()
                    else:
                        product_stock.quantity = quantity
                        product_stock.save()
                    
                except:
                    pass
                
                
    return "Succes"
