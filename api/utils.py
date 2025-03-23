# utils.py
import requests
import pytz
import uuid
import logging
from django.conf import settings
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
import folium
from folium import plugins

logger = logging.getLogger(__name__)

def generate_unique_reference():
    """Generate a unique reference for bookings, payments, etc."""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4().hex)[:8]
    return f"{timestamp}-{unique_id}"

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of earth in kilometers
    return c * r

def geocode_address(address):
    """Convert address to latitude and longitude using Google Maps API"""
    if not settings.GOOGLE_MAPS_API_KEY:
        logger.warning("Google Maps API key not configured")
        return None, None
        
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": settings.GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            logger.error(f"Geocoding error: {data['status']}")
            return None, None
            
    except Exception as e:
        logger.exception(f"Geocoding exception: {str(e)}")
        return None, None

def calculate_fare(distance_km, duration_minutes, base_fare=5.0):
    """Calculate the fare for a trip"""
    distance_rate = 1.5  # $1.5 per km
    time_rate = 0.25  # $0.25 per minute
    
    distance_cost = distance_km * distance_rate
    time_cost = duration_minutes * time_rate
    
    total_fare = base_fare + distance_cost + time_cost
    return round(total_fare, 2)

def send_push_notification(user_id, title, message, data=None):
    """Send push notification to user's device(s)"""
    # This is a placeholder - integrate with FCM or other push notification service
    from .models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        # Get user's device tokens from your database
        # device_tokens = UserDevice.objects.filter(user=user).values_list('token', flat=True)
        
        # Example FCM integration (commented out)
        # if settings.FCM_SERVER_KEY:
        #     headers = {
        #         'Content-Type': 'application/json',
        #         'Authorization': f'key={settings.FCM_SERVER_KEY}',
        #     }
        #     
        #     payload = {
        #         'notification': {
        #             'title': title,
        #             'body': message,
        #         },
        #         'data': data or {},
        #         'registration_ids': list(device_tokens),
        #     }
        #     
        #     response = requests.post(
        #         'https://fcm.googleapis.com/fcm/send',
        #         headers=headers,
        #         json=payload
        #     )
        #     
        #     return response.status_code == 200
        
        logger.info(f"Push notification to user {user_id}: {title} - {message}")
        return True
        
    except Exception as e:
        logger.exception(f"Push notification error: {str(e)}")
        return False
    
# 5. Create a map utility function using Folium (add to utils.py)
def generate_trip_map(pickup_lat, pickup_lng, dest_lat, dest_lng, driver_lat=None, driver_lng=None):
    """
    Generate an HTML map showing the trip route and current locations
    
    Args:
        pickup_lat, pickup_lng: Pickup coordinates
        dest_lat, dest_lng: Destination coordinates
        driver_lat, driver_lng: Optional current driver location
        
    Returns:
        HTML string with the rendered map
    """

    
    # Create map centered between pickup and destination
    center_lat = (pickup_lat + dest_lat) / 2
    center_lng = (pickup_lng + dest_lng) / 2
    trip_map = folium.Map(location=[center_lat, center_lng], zoom_start=12)
    
    # Add pickup marker
    folium.Marker(
        [pickup_lat, pickup_lng],
        popup='Pickup',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(trip_map)
    
    # Add destination marker
    folium.Marker(
        [dest_lat, dest_lng],
        popup='Destination',
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(trip_map)
    
    # Add driver marker if provided
    if driver_lat and driver_lng:
        folium.Marker(
            [driver_lat, driver_lng],
            popup='Driver',
            icon=folium.Icon(color='blue', icon='car', prefix='fa')
        ).add_to(trip_map)
        
    # Add a line for the route
    folium.PolyLine(
        [(pickup_lat, pickup_lng), (dest_lat, dest_lng)],
        color='blue',
        weight=5,
        opacity=0.7
    ).add_to(trip_map)
    
    # Return HTML
    return trip_map._repr_html_()

    # 5. Add a utility function to get nearest drivers (for quick lookup)
# Add this to utils.py

def find_nearest_drivers(user_lat, user_lng, max_distance=10, limit=5):
    """
    Find the nearest available drivers within max_distance (km)
    
    Args:
        user_lat, user_lng: User location coordinates
        max_distance: Maximum distance in km (default 10)
        limit: Maximum number of drivers to return (default 5)
        
    Returns:
        List of driver profiles with distance
    """
    from .models import DriverProfile
    
    available_drivers = DriverProfile.objects.filter(
        is_available=True,
        current_latitude__isnull=False,
        current_longitude__isnull=False
    )
    
    drivers_with_distance = []
    
    for driver in available_drivers:
        distance = haversine_distance(
            user_lng, user_lat,
            driver.current_longitude, driver.current_latitude
        )
        
        if distance <= max_distance:
            drivers_with_distance.append({
                'driver': driver,
                'distance': distance
            })
    
    # Sort by distance
    drivers_with_distance.sort(key=lambda x: x['distance'])
    
    # Limit the results
    return drivers_with_distance[:limit]


# 6. Add a new feature to generate heatmap of driver activity (optional)
# Add this to utils.py

def generate_driver_heatmap(city_center_lat, city_center_lng, zoom=12):
    """
    Generate a heatmap of driver locations
    
    Args:
        city_center_lat, city_center_lng: Center coordinates for the map
        zoom: Initial zoom level
        
    Returns:
        HTML string with rendered heatmap
    """
    import folium
    from folium.plugins import HeatMap
    from .models import DriverProfile
    
    # Create base map
    m = folium.Map([city_center_lat, city_center_lng], zoom_start=zoom)
    
    # Get active driver locations
    drivers = DriverProfile.objects.filter(
        is_available=True,
        current_latitude__isnull=False,
        current_longitude__isnull=False
    )
    
    # Create heatmap data
    heat_data = []
    for driver in drivers:
        heat_data.append([driver.current_latitude, driver.current_longitude])
    
    # Add heatmap layer
    HeatMap(heat_data).add_to(m)
    
    return m._repr_html_()
