from geopy.geocoders import Nominatim

def get_city_name(lat, lon):
    geolocator = Nominatim(user_agent="SkewTdiagram")
    location = geolocator.reverse((lat, lon), exactly_one=True)

    if location and location.raw.get('address'):
        address = location.raw['address']

        city = address.get('city')
        if city:
            return city
        
        locality = address.get('town') or address.get('village') or address.get('county')
        if locality:
            locality_name = locality.lower()
            if "town of" in locality_name:
                return locality_name.replace("town of", "").strip()
            if "village of" in locality_name:
                return locality_name.replace("village of", "").strip()
            return locality
        
    return 'Unknown City'