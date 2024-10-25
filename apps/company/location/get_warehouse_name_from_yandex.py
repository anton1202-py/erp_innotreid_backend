from geopy.geocoders import Nominatim
import time

def get_location_info(latitude, longitude):
    time.sleep(2)
    # Geolokatsiya obyektini yaratish
    geolocator = Nominatim(user_agent="geoapiExercises")

    # Koordinatalarni geokodlash
    location = geolocator.reverse((latitude, longitude), exactly_one=True)

    if location:
        address = location.raw.get('address', {})
        # Viloyat yoki davlat nomini olish
        region = address.get('state', '')
        country = address.get('country', 'Davlat ma\'lumotlari topilmadi')
        return region
    else:
        return ""

