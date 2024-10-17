from json import dumps
import calendar

import requests
from datetime import datetime, timedelta
from celery import shared_task
from django.db.models import F
from apps.marketplaceservice.models import Ozon, Wildberries, YandexMarket
from apps.product.models import Product, ProductSale, ProductOrder, ProductStock, Warehouse, WarehouseForStock
from config.celery import app
import time

date_from = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

wildberries_orders_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={date_from}T00:00:00'
wildberries_stocks_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom={date_from}T00:00:00'
ozon_sales_url = 'https://api-seller.ozon.ru/v1/analytics/data'
ozon_product_info_url = 'https://api-seller.ozon.ru/v2/product/info'
yandex_market_sales_url = 'https://api.partner.market.yandex.ru/reports/shows-sales/generate?format=CSV'
yandex_report_url = 'https://api.partner.market.yandex.ru/reports/info/{report_id}'

def get_warehouse_data( api_key):
    headers = {
        "Authorization": api_key
    }
    response = requests.get("https://supplies-api.wildberries.ru/api/v1/warehouses", headers=headers)
    return response.json()

def not_official_api_wildberries(nmId, api_key):
    
    response = requests.get(f"https://card.wb.ru/cards/detail?dest=-446085&regions=80,83,38,4,64,33,68,70,30,40,86,75,69,1,66,110,22,48,31,71,112,114&nm={nmId}")
    result = []
    if response.status_code == 200:
        products = response.json()['data']['products']
        for item in products:
            for item2 in item["sizes"]:
                for item3 in item2['stocks']:
                    result.append(item3)
    return result

@app.task
def update_wildberries_sales():
    sales_to_create = []
    products_to_create = []
    
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
            warehouses = {}

            existing_sales = ProductSale.objects.filter(
                marketplace_type="wildberries",
                company=company,
                date__gte=latest_product_sale
            ).values_list('product_id', 'date', 'warehouse_id')

            existing_sales_set = {(sale[0], sale[1], sale[2]) for sale in existing_sales}
            
            for item in data:

                warehouse_key = (item['warehouseName'], item['countryName'], item['oblastOkrugName'], item['regionName'])
                if warehouse_key not in warehouses:
                    warehouse, created = Warehouse.objects.get_or_create(
                        name=item['warehouseName'],
                        country_name=item['countryName'],
                        oblast_okrug_name=item['oblastOkrugName'],
                        region_name=item['regionName']
                    )
                    warehouses[warehouse_key] = warehouse
                else:
                    warehouse = warehouses[warehouse_key]
                
                barcode = item["barcode"]
                product = Product.objects.filter(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries").first()
                if not product:
                    Product.objects.get_or_create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
                
                date = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S")

                if (product, date, warehouse) not in existing_sales_set:
                    sales_to_create.append(ProductSale(
                        product=product or Product.objects.get_or_create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")[0],
                        company=company,
                        date=date,
                        marketplace_type="wildberries",
                        warehouse=warehouse
                    ))

    Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
    ProductSale.objects.bulk_create(sales_to_create, ignore_conflicts=True)
    
    return "Success"

@app.task
def update_wildberries_orders():
    orders_to_create = []
    products_to_create = []

    for wildberries in Wildberries.objects.all():
        wb_api_key = wildberries.wb_api_key
        company = wildberries.company
        
        try:
            latest_product_order = ProductOrder.objects.filter(marketplace_type="wildberries").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S')
        except ProductOrder.DoesNotExist:
            latest_product_order = False
            
        if not latest_product_order:
            latest_product_order = date_from
            
        wildberries_orders_url = f'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={latest_product_order}'
        response = requests.get(wildberries_orders_url, headers={'Authorization': f'{wb_api_key}'})

        if response.status_code == 200:
            data = response.json()
            warehouses = {}
            
            existing_orders = ProductOrder.objects.filter(
                marketplace_type="wildberries",
                company=company,
                date__gte=latest_product_order
            ).values_list('product_id', 'date', 'warehouse_id')
            existing_orders_set = {(order[0], order[1], order[2]) for order in existing_orders}
            
            for item in data:

                warehouse_key = (item['warehouseName'], item['countryName'], item['oblastOkrugName'], item['regionName'])
                
                if warehouse_key not in warehouses:
                    warehouse, created = Warehouse.objects.get_or_create(
                        name=item['warehouseName'],
                        country_name=item['countryName'],
                        oblast_okrug_name=item['oblastOkrugName'],
                        region_name=item['regionName']
                    )
                    warehouses[warehouse_key] = warehouse
                else:
                    warehouse = warehouses[warehouse_key]
                
                barcode = item['barcode']
                product = Product.objects.filter(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries").first()

                if not product:
                    product = Product.objects.create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")
                    
                else:
                    Product(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")

                date = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S")
                
                
                if product and warehouse and (product.id, date, warehouse.id) not in existing_orders_set:
                    orders_to_create.append(ProductOrder(
                        product=product,
                        company=company,
                        date=date,
                        marketplace_type="wildberries",
                        warehouse=warehouse
                    ))
 
            ProductOrder.objects.bulk_create(orders_to_create, ignore_conflicts=True)

        return "Success"

@app.task
def update_wildberries_stocks():
    
    
    for wildberries in Wildberries.objects.all():
        wb_api_key = wildberries.wb_api_key
        response = requests.get(wildberries_stocks_url, headers={'Authorization': f'Bearer {wb_api_key}'})
        
        if response.status_code != 200:
            continue  
        
        warehouse_data = get_warehouse_data(wb_api_key)
        warehouses_cache = {}
    
        for warehouse_item in warehouse_data:
            warehouses_cache[warehouse_item['ID']] = warehouse_item['name']
        
        for item in response.json():
            
            products_to_create = []
            stocks_to_create = []
            
            company = wildberries.company
            date = datetime.now()
            barcode = item.get('barcode')
            if not barcode:
                continue  
            
            product = Product.objects.filter(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries").first()
            if not product:
                product = Product.objects.create(vendor_code=item['supplierArticle'], barcode=barcode, marketplace_type="wildberries")

            result_w = not_official_api_wildberries(api_key=wb_api_key, nmId=item['nmId'])
            for item_not_official in result_w:
                quantity = item_not_official['qty']
                warehouse_id = item_not_official['wh']
                warehouse_name = warehouses_cache.get(warehouse_id)

                if warehouse_name:
                    warehouse_obj, created_w = WarehouseForStock.objects.get_or_create(name=warehouse_name, marketplace_type="wildberries")
                    stocks_to_create.append(ProductStock(
                        product=product,
                        warehouse=warehouse_obj,
                        marketplace_type="wildberries",
                        company=company,
                        date=date,
                        quantity=quantity
                    ))

    if products_to_create:
        Product.objects.bulk_create(products_to_create, ignore_conflicts=True) 
    if stocks_to_create:
        ProductStock.objects.bulk_create(stocks_to_create, ignore_conflicts=True)

    return "Success"
            
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
    
    if response.status_code == 200:
        return response.json()["result"]["barcode"]
    return 0 

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

        date_from = ProductSale.objects.filter(marketplace_type="ozon").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if ProductSale.objects.filter(marketplace_type="ozon").exists() else (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        while datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S.%fZ') <= datetime.now():
            fbo_orders = get_paid_orders(FBO_URL, headers, date_from)
            fbs_orders = get_paid_orders(FBS_URL, headers, date_from)
            results = fbo_orders + fbs_orders
            
            products_to_create = []
            product_sales_to_create = []
            warehouses_cache = {}
        
            for item in results:
    
                try:
                    date = datetime.strptime(item['in_process_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    date = datetime.strptime(item['in_process_at'], "%Y-%m-%dT%H:%M:%SZ")
                
                sku = item['products'][0]['offer_id']
                warehouse_name = item["analytics_data"].get("warehouse_name", "")
                oblast_okrug_name = item["analytics_data"]['region']
                region_name = item["analytics_data"]['city']
                barcode = get_barcode(vendor_code=sku, api_key=api_token, client_id=client_id)

                if not barcode:
                    continue  
                
                if warehouse_name not in warehouses_cache:
                    warehouse_obj, created_w = Warehouse.objects.get_or_create(
                        name=warehouse_name,
                        country_name="Russia",
                        oblast_okrug_name=oblast_okrug_name,
                        region_name=region_name
                    )
                    warehouses_cache[warehouse_name] = warehouse_obj
                else:
                    warehouse_obj = warehouses_cache[warehouse_name]

                product = Product.objects.filter(barcode=barcode, marketplace_type="ozon")

                if not product.exists():
                    product = Product.objects.create(vendor_code=sku, marketplace_type="ozon", barcode=barcode)
                    
                else:
                    product_w = Product.objects.filter(barcode=barcode, marketplace_type="wildberries")
                    product = product.first()
                    if product_w.exists():
                        vendor_code = product_w.first().vendor_code
                        product.vendor_code = vendor_code
                        product.save()

                
                product_sales_to_create.append(ProductSale(
                    product=product,
                    company=company,
                    date=date,
                    warehouse=warehouse_obj,
                    marketplace_type="ozon"
                ))
                
 
            if product_sales_to_create:
                ProductSale.objects.bulk_create(product_sales_to_create, ignore_conflicts=True)

            
            date_from = (ProductSale.objects.filter(marketplace_type="ozon").latest('date').date + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return "Success"
        
@app.task
def update_ozon_orders():
    
    FBO_URL = "https://api-seller.ozon.ru/v2/posting/fbo/list"
    FBS_URL = "https://api-seller.ozon.ru/v2/posting/fbs/list"
    
    try:
        date_from = ProductOrder.objects.filter(marketplace_type="ozon").latest('date').date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    except ProductOrder.DoesNotExist:
        date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    for ozon in Ozon.objects.all():
        company = ozon.company
        api_token = ozon.api_token
        client_id = ozon.client_id
        headers = {
            'Client-Id': client_id,
            'Api-Key': api_token,
            'Content-Type': 'application/json'
        }

        while datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S.%fZ') <= datetime.now():
            fbo_orders = get_paid_orders(FBO_URL, headers, date_from, "awaiting_packaging", "")
            fbs_orders = get_paid_orders(FBS_URL, headers, date_from, "awaiting_deliver", "")
            results = fbo_orders + fbs_orders

            products_to_create = []
            orders_to_create = []
            warehouses_cache = {}

            for item in results:
                date = item['in_process_at']
                sku = item['products'][0]['offer_id']
                warehouse_name = item["analytics_data"].get('warehouse_name', "")
                oblast_okrug_name = item["analytics_data"]['region']
                region_name = item["analytics_data"]['city']

                barcode = get_barcode(vendor_code=sku, api_key=ozon.api_token, client_id=ozon.client_id)
                if not barcode:
                    continue

                if warehouse_name not in warehouses_cache:
                    warehouse, created_w = Warehouse.objects.get_or_create(
                        name=warehouse_name,
                        country_name="Russia",
                        oblast_okrug_name=oblast_okrug_name,
                        region_name=region_name
                    )
                    warehouses_cache[warehouse_name] = warehouse
                else:
                    warehouse = warehouses_cache[warehouse_name]

                product = Product.objects.filter(barcode=barcode)

                if product.exists():
                    wildberries_product = Product.objects.filter(barcode=barcode, marketplace_type="wildberries").first()
                    ozon_product = Product.objects.filter(barcode=barcode, marketplace_type='ozon').first()

                    if not ozon_product and not wildberries_product:
                        product = Product.objects.create(vendor_code=sku, marketplace_type="ozon", barcode=barcode)
                       
                    elif ozon_product and wildberries_product:
                        product_sale = ProductOrder.objects.filter(product=ozon_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon").first()
                        if not product_sale:
                            orders_to_create.append(ProductOrder(product=ozon_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon"))
                    elif ozon_product:
                        orders_to_create.append(ProductOrder(product=ozon_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon"))
                    elif wildberries_product:
                        orders_to_create.append(ProductOrder(product=wildberries_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon"))
                else:
                    product = Product(vendor_code=sku, marketplace_type="ozon", barcode=barcode)
                    products_to_create.append(product)

            if products_to_create:
                Product.objects.bulk_create(products_to_create, ignore_conflicts=True)

            if orders_to_create:
                ProductOrder.objects.bulk_create(orders_to_create, ignore_conflicts=True)

            try:
                date_from = (ProductOrder.objects.filter(marketplace_type="ozon").latest('date').date + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            except ProductOrder.DoesNotExist:
                date_from = (datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return "Success"

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
            results = response.json().get('result', {}).get("rows", [])
        else:
            results = []

        products_to_create = []
        stocks_to_create = []
        warehouses_cache = {}

        for item in results:
            vendor_code = item['item_code']
            warehouse_name = item['warehouse_name']
            quantity = item['reserved_amount']
            
            date = datetime.now()
            barcode = get_barcode(vendor_code=vendor_code, api_key=ozon.api_token, client_id=ozon.client_id)
            if not barcode:
                continue
            
            if warehouse_name not in warehouses_cache:
                warehouse, created_w = WarehouseForStock.objects.get_or_create(name=warehouse_name, marketplace_type="ozon")
                warehouses_cache[warehouse_name] = warehouse
            else:
                warehouse = warehouses_cache[warehouse_name]

            product = Product.objects.filter(barcode=barcode).first()

            if product:
                wildberries_product = Product.objects.filter(barcode=barcode, marketplace_type="wildberries").first()
                ozon_product = Product.objects.filter(barcode=barcode, marketplace_type='ozon').first()

                if not ozon_product and not wildberries_product:
                    product, _ = Product.objects.get_or_create(vendor_code=vendor_code, marketplace_type="ozon", barcode=barcode)
                    stocks_to_create.append(ProductStock(product=product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon", quantity=quantity))
                elif ozon_product and wildberries_product:
                    product_sale_w = ProductStock.objects.filter(product=wildberries_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon", quantity=quantity).first()
                    product_sale_o = ProductStock.objects.filter(product=ozon_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon", quantity=quantity).first()

                    if product_sale_w:
                        continue
                    elif product_sale_o:
                        product_sale_o.product = wildberries_product
                        product_sale_o.save()
                        continue
                    else:
                        stocks_to_create.append(ProductStock(product=wildberries_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon", quantity=quantity))
                elif ozon_product and not wildberries_product:
                    stocks_to_create.append(ProductStock(product=ozon_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon", quantity=quantity))
                elif wildberries_product and not ozon_product:
                    stocks_to_create.append(ProductStock(product=wildberries_product, company=company, date=date, warehouse=warehouse, marketplace_type="ozon", quantity=quantity))
            else:
                product, created_p = Product.objects.get_or_create(vendor_code=vendor_code, marketplace_type="ozon", barcode=barcode)
                stocks_to_create.append(ProductStock(product=product, warehouse=warehouse, marketplace_type="ozon", company=company, date=date, quantity=quantity))

        if products_to_create:
            Product.objects.bulk_create(products_to_create, ignore_conflicts=True)

        if stocks_to_create:
            ProductStock.objects.bulk_create(stocks_to_create, ignore_conflicts=True)

    return "Success"

def get_yandex_orders(api_key, date_from, client_id, status="DELIVERED"):
    if (datetime.strptime(date_from,"%Y-%m-%d") - datetime.now()).days > 30:
        date_to = (datetime.strptime(date_from,"%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
    else:
        date_to = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.partner.market.yandex.ru/campaigns/{client_id}/orders?orderIds=&status={status}&substatus=&fromDate={date_from}&toDate={date_to}&supplierShipmentDateFrom=&supplierShipmentDateTo=&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&buyerType=&page=&pageSize="
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
                }
    
    difrence = (datetime.now() - datetime.strptime(date_from,"%Y-%m-%d")).days
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
            response = requests.get(url, headers=headers)
            
            orders += response.json()["orders"]
            if "pagesCount" in response.json().keys():
                for i in range(2,response.json()["pagesCount"]+1):
                    url = f"https://api.partner.market.yandex.ru/campaigns/{client_id}/orders?orderIds=&status={status}&substatus=&fromDate={date_from}&toDate={date_to}&supplierShipmentDateFrom=&supplierShipmentDateTo=&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&buyerType=&page={i}&pageSize="
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        orders += response.json()["orders"]
    
    else:
        orders = []
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            orders += response.json()['orders']
            if "pagesCount" in response.json().keys():
                for i in range(2,response.json()["pagesCount"]+1):
                    url = f"https://api.partner.market.yandex.ru/campaigns/{client_id}/orders?orderIds=&status={status}&substatus=&fromDate={date_from}&toDate={date_to}&supplierShipmentDateFrom=&supplierShipmentDateTo=&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&buyerType=&page={i}&pageSize="
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        orders += response.json()["orders"]
            return orders
        else:
            
            return []
    return orders

def find_barcode(vendor_code, company_id, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    body = {
         
        "offerIds": [vendor_code]
    }
    params = {
        'limit': 10,  #
        'page_token': None
    }
    response = requests.post(f"https://api.partner.market.yandex.ru/businesses/{company_id}/offer-mappings",headers=headers,json=body,params=params)
    if response.status_code == 200:
        try:
            return response.json()["result"]['offerMappings'][0]["offer"]["barcodes"][0]
        except:
            return 0
    else: 
        return 0
        
@app.task
def update_yandex_market_sales():
    
    for yandex_market in YandexMarket.objects.all():
        
        api_key_bearer = yandex_market.api_key_bearer
        fby_campaign_id = yandex_market.fby_campaign_id
        fbs_campaign_id = yandex_market.fbs_campaign_id
        company = yandex_market.company
        
        date_from = ProductSale.objects.filter(marketplace_type="yandexmarket")

        if not date_from.exists():
            date_from = (datetime.now()-timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            date_from = date_from.latest("date").date.strftime("%Y-%m-%d")

        results1 = get_yandex_orders(api_key_bearer, date_from, client_id=fby_campaign_id)
        results2 = get_yandex_orders(api_key_bearer, date_from, client_id=fbs_campaign_id)
        
        results = results1 + results2

        products_to_create = []
        product_sales_to_create = []
        warehouses_cache = {}

        for item in results:
            
            buyer_total = item.get("buyerTotal", 0)
            item_total = item.get("itemsTotal", 0)

            if buyer_total == item_total:
                if "serviceName" in item["delivery"].keys():
                    warehouse_name = item["delivery"]['serviceName']
                else:
                    warehouse_name = ""
                
                oblast_okrug_name = item["delivery"]['region']['parent']['name']
                region_name = item["delivery"]['region']['name']
                
                try:
                    country_name = item.get('delivery', {}).get('address', {}).get('country', "")
                except:
                    country_name = "Russia"


                warehouse_key = f"{warehouse_name}-{country_name}-{oblast_okrug_name}-{region_name}"
                if warehouse_key not in warehouses_cache:
                    warehouse, created_w = Warehouse.objects.get_or_create(
                        name=warehouse_name,
                        country_name=country_name,
                        oblast_okrug_name=oblast_okrug_name,
                        region_name=region_name
                    )
                    warehouses_cache[warehouse_key] = warehouse
                else:
                    warehouse = warehouses_cache[warehouse_key]

                products = item["items"]
                date = datetime.strptime(item['updatedAt'], "%d-%m-%Y %H:%M:%S")
                
                for product in products:
                    
                    vendor_code = product["offerId"]
                    barcode = find_barcode(vendor_code=vendor_code, company_id=yandex_market.business_id, api_key=yandex_market.api_key_bearer)
                    
                    if not barcode:
                        continue
                    
                    product_qs = Product.objects.filter(barcode=barcode)
                    if product_qs.exists():
                        
                        wildberries_product = product_qs.filter(marketplace_type="wildberries").first()
                        yandexmarket_product = product_qs.filter(marketplace_type='yandexmarket').first()

                        if not yandexmarket_product and not wildberries_product:

                            new_product, _ = Product.objects.get_or_create(vendor_code=vendor_code, marketplace_type="yandexmarket", barcode=barcode)
                            
                            product_sales_to_create.append(
                                ProductSale(
                                    product=new_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse,
                                    marketplace_type="yandexmarket"
                                )
                            )
                        elif yandexmarket_product and wildberries_product:
                            product_sale_w = ProductSale.objects.filter(product=wildberries_product, company=company, date=date, warehouse=warehouse, marketplace_type="yandexmarket")
                            product_sale_y = ProductSale.objects.filter(product=yandexmarket_product, company=company, date=date, warehouse=warehouse, marketplace_type="yandexmarket")
                            
                            if not product_sale_w.exists() and not product_sale_y.exists():
                                product_sales_to_create.append(
                                    ProductSale(
                                        product=wildberries_product,
                                        company=company,
                                        date=date,
                                        warehouse=warehouse,
                                        marketplace_type="yandexmarket"
                                    )
                                )
                        elif yandexmarket_product and not wildberries_product:
                            product_sales_to_create.append(
                                ProductSale(
                                    product=yandexmarket_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse,
                                    marketplace_type="yandexmarket"
                                )
                            )
                        elif wildberries_product and not yandexmarket_product:
                            product_sales_to_create.append(
                                ProductSale(
                                    product=wildberries_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse,
                                    marketplace_type="yandexmarket"
                                )
                            )
                    else:
                        new_product, _ = Product.objects.get_or_create(vendor_code=vendor_code, barcode=barcode, marketplace_type="yandexmarket")
                        
                        product_sales_to_create.append(
                            ProductSale(
                                product=new_product,
                                company=company,
                                date=date,
                                warehouse=warehouse,
                                marketplace_type="yandexmarket"
                            )
                        )

                    date = date + timedelta(seconds=1)

        if products_to_create:
            Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
        
        if product_sales_to_create:
            ProductSale.objects.bulk_create(product_sales_to_create, ignore_conflicts=True)

    return "success"

@app.task
def update_yandex_market_orders():
    
    for yandex_market in YandexMarket.objects.all():
        api_key_bearer = yandex_market.api_key_bearer
        fby_campaign_id = yandex_market.fby_campaign_id
        fbs_campaign_id = yandex_market.fbs_campaign_id
        company = yandex_market.company
        date_from = ProductOrder.objects.filter(marketplace_type="yandexmarket")

        if not (date_from.exists()):
            date_from = (datetime.now()-timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            date_from = date_from.latest("date").date.strftime("%Y-%m-%d")

        results1 = get_yandex_orders(api_key_bearer, date_from, client_id=fby_campaign_id, status="PROCESSING")
        results2 = get_yandex_orders(api_key_bearer, date_from, client_id=fbs_campaign_id, status="PROCESSING")

        results = results1 + results2

        products_to_create = []
        product_orders_to_create = []
        warehouses_cache = {}

        for item in results:
            buyer_total = item.get("buyerTotal", 0)
            item_total = item.get("itemsTotal", 0)

            if buyer_total == item_total:
                if "serviceName" in item["delivery"].keys():
                    warehouse_name = item["delivery"]['serviceName']
                else:
                    warehouse_name = ""
                
                oblast_okrug_name = item["delivery"]['region']['parent']['name']
                region_name = item["delivery"]['region']['name']
                
                try:
                    country_name = item.get('delivery', {}).get('address', {}).get('country', "")
                except:
                    country_name = "Russia"

                warehouse_key = f"{warehouse_name}-{country_name}-{oblast_okrug_name}-{region_name}"
                if warehouse_key not in warehouses_cache:
                    warehouse, created_w = Warehouse.objects.get_or_create(
                        name=warehouse_name,
                        country_name=country_name,
                        oblast_okrug_name=oblast_okrug_name,
                        region_name=region_name
                    )
                    warehouses_cache[warehouse_key] = warehouse
                else:
                    warehouse = warehouses_cache[warehouse_key]

                products = item["items"]
                date = datetime.strptime(item['updatedAt'], "%d-%m-%Y %H:%M:%S")
                
                for product in products:
                    vendor_code = product["offerId"]
                    barcode = find_barcode(vendor_code=vendor_code, company_id=yandex_market.business_id, api_key=yandex_market.api_key_bearer)
                    if not barcode:
                        continue

                    product_qs = Product.objects.filter(barcode=barcode)
                    
                    if product_qs.exists():
                        wildberries_product = product_qs.filter(marketplace_type="wildberries").first()
                        yandexmarket_product = product_qs.filter(marketplace_type='yandexmarket').first()

                        if not yandexmarket_product and not wildberries_product:

                            new_product = Product(vendor_code=vendor_code, marketplace_type="yandexmarket", barcode=barcode)
                            products_to_create.append(new_product)
                            product_orders_to_create.append(
                                ProductOrder(
                                    product=new_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse,
                                    marketplace_type="yandexmarket"
                                )
                            )
                        elif yandexmarket_product and wildberries_product:
                            product_order_w = ProductOrder.objects.filter(product=wildberries_product, company=company, date=date, warehouse=warehouse, marketplace_type="yandexmarket")
                            product_order_y = ProductOrder.objects.filter(product=yandexmarket_product, company=company, date=date, warehouse=warehouse, marketplace_type="yandexmarket")
                            
                            if not product_order_w.exists() and not product_order_y.exists():
                                product_orders_to_create.append(
                                    ProductOrder(
                                        product=wildberries_product,
                                        company=company,
                                        date=date,
                                        warehouse=warehouse,
                                        marketplace_type="yandexmarket"
                                    )
                                )
                        elif yandexmarket_product and not wildberries_product:
                            product_orders_to_create.append(
                                ProductOrder(
                                    product=yandexmarket_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse,
                                    marketplace_type="yandexmarket"
                                )
                            )
                        elif wildberries_product and not yandexmarket_product:
                            product_orders_to_create.append(
                                ProductOrder(
                                    product=wildberries_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse,
                                    marketplace_type="yandexmarket"
                                )
                            )
                    else:
                        new_product = Product.objects.create(vendor_code=vendor_code, barcode=barcode, marketplace_type="yandexmarket")
                        
                        product_orders_to_create.append(
                            ProductOrder(
                                product=new_product,
                                company=company,
                                date=date,
                                warehouse=warehouse,
                                marketplace_type="yandexmarket"
                            )
                        )

                    date = date + timedelta(seconds=1)
        
        if product_orders_to_create:
            ProductOrder.objects.bulk_create(product_orders_to_create, ignore_conflicts=True)

    return "success"
    
def get_warehouse_name(business_id,headers, warehouse_id):
    warehouse_by_busness_id_url = f"https://api.partner.market.yandex.ru/businesses/{business_id}/warehouses"               
    warehouse_url = f"https://api.partner.market.yandex.ru/warehouses"    

    get_warehouse_name_l = requests.get(warehouse_by_busness_id_url,headers=headers)
    if get_warehouse_name_l.status_code == 200:
        get_warehouse_name_l = get_warehouse_name_l.json()["result"]["warehouses"]
    else:
        get_warehouse_name_l = []
    get_warehouse_name_l_2 = requests.get(warehouse_url,headers=headers)
    if get_warehouse_name_l_2.status_code == 200:
        get_warehouse_name_l_2 = get_warehouse_name_l_2.json()["result"]["warehouses"]
    else:
        get_warehouse_name_l = []
    results = get_warehouse_name_l + get_warehouse_name_l_2
    
    for item in results:
        if item["id"] == warehouse_id:
            return item['name']

@app.task
def update_yandex_stocks():
    for yandex in YandexMarket.objects.all():
        api_key = yandex.api_key_bearer
        fby = yandex.fby_campaign_id
        business_id = yandex.business_id

        url = "https://api.partner.market.yandex.ru/campaigns/{campaignId}/offers/stocks"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        result2 = []
        response2 = requests.post(url.format(campaignId=fby), headers=headers)

        while True:
            if response2.status_code == 200 and "paging" in response2.json()["result"].keys() and "nextPageToken" in response2.json()["result"]["paging"].keys():
                result2 += response2.json()["result"]["warehouses"]
                nextPageToken = response2.json()["result"]["paging"]["nextPageToken"]
                params = {"page_token": nextPageToken}
                response2 = requests.post(url.format(campaignId=fby), headers=headers, params=params)
            else:
                break

        company = yandex.company
        results = result2

        products_to_create = []
        product_stocks_to_create = []
        warehouses_cache = {}

        for item in results:
            warehouse = get_warehouse_name(business_id, headers, item['warehouseId'])
            if not warehouse:
                continue

            for offers in item['offers']:
                try:
                    date = datetime.strptime(offers.get('updatedAt', datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")), "%Y-%m-%dT%H:%M:%S.%f%z")
                except:
                    continue
                vendor_code = offers["offerId"]
                count = sum(stock["count"] for stock in offers['stocks'] if stock and stock["type"] == "AVAILABLE")

                barcode = find_barcode(vendor_code=vendor_code, company_id=yandex.business_id, api_key=yandex.api_key_bearer)
                if not barcode or not warehouse:
                    continue

                if warehouse not in warehouses_cache:
                    warehouses_cache[warehouse], _ = WarehouseForStock.objects.get_or_create(name=warehouse, marketplace_type="yandexmarket")
                
                warehouse_obj = warehouses_cache[warehouse]
                
                product_qs = Product.objects.filter(barcode=barcode)

                if product_qs.exists():
                    wildberries_product = product_qs.filter(marketplace_type="wildberries").first()
                    yandexmarket_product = product_qs.filter(marketplace_type='yandexmarket').first()

                    if not yandexmarket_product and not wildberries_product:

                        new_product = Product(vendor_code=vendor_code, marketplace_type="yandexmarket", barcode=barcode)
                        products_to_create.append(new_product)
                        product_stocks_to_create.append(
                            ProductStock(
                                product=new_product,
                                company=company,
                                date=date,
                                warehouse=warehouse_obj,
                                marketplace_type="yandexmarket",
                                quantity=count
                            )
                        )
                    elif yandexmarket_product and wildberries_product:
                        product_stock_wildberries = ProductStock.objects.filter(
                            product=wildberries_product,
                            company=company,
                            date=date,
                            warehouse=warehouse_obj,
                            marketplace_type="yandexmarket"
                        ).first()
                        
                        if not product_stock_wildberries:
                            product_stocks_to_create.append(
                                ProductStock(
                                    product=wildberries_product,
                                    company=company,
                                    date=date,
                                    warehouse=warehouse_obj,
                                    marketplace_type="yandexmarket",
                                    quantity=count
                                )
                            )
                    elif yandexmarket_product:
                        product_stocks_to_create.append(
                            ProductStock(
                                product=yandexmarket_product,
                                company=company,
                                date=date,
                                warehouse=warehouse_obj,
                                marketplace_type="yandexmarket",
                                quantity=count
                            )
                        )
                    elif wildberries_product:
                        product_stocks_to_create.append(
                            ProductStock(
                                product=wildberries_product,
                                company=company,
                                date=date,
                                warehouse=warehouse_obj,
                                marketplace_type="yandexmarket",
                                quantity=count
                            )
                        )
                else:
                    new_product = Product.objects.create(vendor_code=vendor_code, barcode=barcode, marketplace_type="yandexmarket")
                    
                    product_stocks_to_create.append(
                        ProductStock(
                            product=new_product,
                            company=company,
                            date=date,
                            warehouse=warehouse_obj,
                            marketplace_type="yandexmarket",
                            quantity=count
                        )
                    )


        if products_to_create:
            Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
        
        if product_stocks_to_create:
            ProductStock.objects.bulk_create(product_stocks_to_create, ignore_conflicts=True)

    return "Success"


@app.task
def synchronous_algorithm():
    
    update_wildberries_sales.delay()
    update_ozon_sales.delay()
    update_yandex_market_sales()
    time.sleep(180)
    update_wildberries_orders.delay()
    update_ozon_orders.delay()
    update_yandex_market_orders()
    time.sleep(180)
    # update_wildberries_stocks().delay()
    update_ozon_stocks.delay()
    update_yandex_stocks.delay()

    return True

    