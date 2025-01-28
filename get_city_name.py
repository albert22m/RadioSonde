from geopy.geocoders import Nominatim

def get_city_name(lat, lon):
    geolocator = Nominatim(user_agent="SkewTdiagram")
    location = geolocator.reverse((lat, lon), exactly_one=True)

    if location and location.raw.get('address'):
        address = location.raw['address']

        city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
        country = address.get('country_code').upper()

        if city:
            city_name = city.lower().strip()  # Make sure to strip any extra spaces

            if "town of" in city_name:
                city_name = city_name.replace("town of", "").strip()
                return f'{city_name.upper()}, {country}'
            
            if "village of" in city_name:
                city_name = city_name.replace("village of", "").strip()
                return f'{city_name.upper()}, {country}'

            return f'{city_name.upper()}, {country}'
        
    return 'Unknown Location'
