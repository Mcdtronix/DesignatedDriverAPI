from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import User, DriverProfile, Booking, Trip, Payment, Review, Subscription, Notification
from .serializers import (UserSerializer, DriverProfileSerializer, BookingSerializer,TripSerializer, PaymentSerializer, ReviewSerializer,SubscriptionSerializer, NotificationSerializer)
from .utils import haversine_distance 
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import generate_driver_heatmap



# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, 'profile.html')
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverProfileViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearby available drivers"""
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius', 5)  # default 5km
        
        if not all([latitude, longitude]):
            return Response({"error": "Latitude and longitude are required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        user_latitude = float(latitude)
        user_longitude = float(longitude)
        
        available_drivers = DriverProfile.objects.filter(
            is_available=True,
            current_latitude__isnull=False,
            current_longitude__isnull=False
        )
        
        # Find drivers within radius using haversine distance
        nearby_drivers = []
        for driver in available_drivers:
            distance = haversine_distance(
                user_longitude, user_latitude,
                driver.current_longitude, driver.current_latitude
            )
            
            if distance <= float(radius):
                driver_data = self.get_serializer(driver).data
                driver_data['distance'] = round(distance, 2)
                nearby_drivers.append(driver_data)
                
        return Response(nearby_drivers)
    
    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update driver's current location"""
        user = request.user
        
        try:
            driver_profile = DriverProfile.objects.get(user=user)
        except DriverProfile.DoesNotExist:
            return Response({"error": "Driver profile not found"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not all([latitude, longitude]):
            return Response({"error": "Latitude and longitude are required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        driver_profile.current_latitude = float(latitude)
        driver_profile.current_longitude = float(longitude)
        driver_profile.last_location_update = timezone.now()
        driver_profile.save()
        
        return Response({"success": True})
    
    # 2. Add radius search functionality to DriverProfileViewSet

    @action(detail=False, methods=['get'])
    def radius_search(self, request):
        """Find drivers within a specified radius"""
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius', 5)  # default 5km
        
        if not all([latitude, longitude]):
            return Response({"error": "Latitude and longitude are required"}, 
                        status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user_lat = float(latitude)
            user_lng = float(longitude)
            radius_km = float(radius)
            
            # Get all drivers (we'll filter in Python)
            drivers = DriverProfile.objects.filter(
                is_available=True,
                current_latitude__isnull=False,
                current_longitude__isnull=False
            )
            
            # Filter and sort by distance
            drivers_with_distance = []
            for driver in drivers:
                distance = haversine_distance(
                    user_lng, user_lat,
                    driver.current_longitude, driver.current_latitude
                )
                
                if distance <= radius_km:
                    drivers_with_distance.append({
                        'driver': driver,
                        'distance': distance
                    })
            
            # Sort by distance
            drivers_with_distance.sort(key=lambda x: x['distance'])
            
            # Serialize and return
            result = []
            for item in drivers_with_distance:
                driver_data = self.get_serializer(item['driver']).data
                driver_data['distance'] = round(item['distance'], 2)
                result.append(driver_data)
                
            return Response(result)
            
        except ValueError:
            return Response({"error": "Invalid coordinates or radius"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        
class DriverHeatmapView(LoginRequiredMixin, TemplateView):
    template_name = 'api/heatmap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get city center (could be dynamic based on user location)
        city_lat = 37.7749  # Example: San Francisco
        city_lng = -122.4194
        
        context['heatmap'] = generate_driver_heatmap(city_lat, city_lng)
        return context

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_driver:
            return Booking.objects.filter(driver=user)
        return Booking.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'accepted'
        booking.save()
        
        # Create notification for user
        Notification.objects.create(
            user=booking.user,
            title="Booking Accepted",
            message=f"Your booking has been accepted by {booking.driver.get_full_name()}",
            related_booking=booking
        )
        
        return Response({"success": True})
    
    @action(detail=True, methods=['post'])
    def start_trip(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'in_progress'
        booking.save()
        
        # Create or update trip
        trip, created = Trip.objects.get_or_create(booking=booking)
        trip.start_time = timezone.now()
        trip.save()
        
        # Notify user
        Notification.objects.create(
            user=booking.user,
            title="Trip Started",
            message="Your trip has started",
            related_booking=booking
        )
        
        return Response({"success": True})
    
    @action(detail=True, methods=['post'])
    def complete_trip(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'completed'
        booking.save()
        
        # Update trip
        try:
            trip = Trip.objects.get(booking=booking)
            trip.end_time = timezone.now()
            
            # Calculate distance and fare (simplified)
            duration = (trip.end_time - trip.start_time).total_seconds() / 3600  # hours
            trip.distance = float(request.data.get('distance', 0))
            base_fare = 5.00
            distance_fare = trip.distance * 1.5  # $1.5 per km
            time_fare = duration * 10  # $10 per hour
            trip.total_fare = base_fare + distance_fare + time_fare
            trip.save()
            
            # Create payment record
            Payment.objects.create(
                trip=trip,
                amount=trip.total_fare,
                payment_method=request.data.get('payment_method', 'credit_card'),
                status='pending'
            )
            
            # Notify user
            Notification.objects.create(
                user=booking.user,
                title="Trip Completed",
                message=f"Your trip has been completed. Total fare: ${trip.total_fare}",
                related_booking=booking
            )
            
            return Response({"success": True, "total_fare": trip.total_fare})
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)
        
#####################################
    # 3. Add a function to calculate trip distance in BookingViewSet
# This will replace the GeoDjango distance calculations

def calculate_trip_distance(self, booking):
    """Calculate the distance for a trip using haversine formula"""
    from .utils import haversine_distance
    
    return haversine_distance(
        booking.pickup_longitude, booking.pickup_latitude,
        booking.destination_longitude, booking.destination_latitude
    )

# 4. Modify the complete_trip action to use the new distance calculation
@action(detail=True, methods=['post'])
def complete_trip(self, request, pk=None):
    booking = self.get_object()
    booking.status = 'completed'
    booking.save()
    
    # Update trip
    try:
        trip = Trip.objects.get(booking=booking)
        trip.end_time = timezone.now()
        
        # Calculate distance using haversine if not provided
        if request.data.get('distance'):
            trip.distance = float(request.data.get('distance'))
        else:
            trip.distance = self.calculate_trip_distance(booking)
        
        # Calculate duration in hours
        duration = (trip.end_time - trip.start_time).total_seconds() / 3600
        
        # Calculate fare
        base_fare = 5.00
        distance_fare = trip.distance * 1.5  # $1.5 per km
        time_fare = duration * 10  # $10 per hour
        trip.total_fare = base_fare + distance_fare + time_fare
        trip.save()
        
        # Create payment record
        Payment.objects.create(
            trip=trip,
            amount=trip.total_fare,
            payment_method=request.data.get('payment_method', 'credit_card'),
            status='pending'
        )
        
        # Notify user
        Notification.objects.create(
            user=booking.user,
            title="Trip Completed",
            message=f"Your trip has been completed. Total fare: ${trip.total_fare}",
            related_booking=booking
        )
        
        return Response({"success": True, "total_fare": trip.total_fare})
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_driver:
            return Trip.objects.filter(booking__driver=user)
        return Trip.objects.filter(booking__user=user)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_driver:
            return Payment.objects.filter(trip__booking__driver=user)
        return Payment.objects.filter(trip__booking__user=user)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        payment = self.get_object()
        
        # In a real app, integrate with payment gateway here
        payment.status = 'completed'
        payment.transaction_id = f"TX-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        payment.save()
        
        # Notify user
        Notification.objects.create(
            user=payment.trip.booking.user,
            title="Payment Successful",
            message=f"Your payment of ${payment.amount} was successful",
            related_booking=payment.trip.booking
        )
        
        return Response({"success": True})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_driver:
            return Review.objects.filter(driver=user)
        return Review.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"success": True})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user).update(is_read=True)
        return Response({"success": True})