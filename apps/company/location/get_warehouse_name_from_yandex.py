from geopy.geocoders import Nominatim
import time
import requests

proxies_list = [
    {"http": "http://proxy1.com:8080", "https": "http://proxy1.com:8080"},
    {"http": "http://proxy2.com:8080", "https": "http://proxy2.com:8080"},
    # Qo'shimcha proxylar qo'shishingiz mumkin
]

def get_location_info(latitude, longitude):
    time.sleep(15)
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
    except:
        return ""

    if location:
        address = location.raw.get('address', {})
        region = address.get('state', '')
        country = address.get('country', 'Davlat ma\'lumotlari topilmadi')
        return region
    else:
        return ""