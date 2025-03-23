from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # User Views
    path('users/', views.UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/register/', views.UserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('users/me/', views.UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('users/<int:pk>/', views.UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-detail'),

    # DriverProfile Views
    path('driver-profiles/', views.DriverProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='driverprofile-list'),
    path('driver-profiles/nearby/', views.DriverProfileViewSet.as_view({'get': 'nearby'}), name='driverprofile-nearby'),
    path('driver-profiles/update-location/', views.DriverProfileViewSet.as_view({'post': 'update_location'}), name='driverprofile-update-location'),
    path('driver-profiles/radius-search/', views.DriverProfileViewSet.as_view({'get': 'radius_search'}), name='driverprofile-radius-search'),
    path('driver-profiles/<int:pk>/', views.DriverProfileViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='driverprofile-detail'),

    # Booking Views
    path('bookings/', views.BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='booking-list'),
    path('bookings/<int:pk>/', views.BookingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='booking-detail'),
    path('bookings/<int:pk>/accept/', views.BookingViewSet.as_view({'post': 'accept'}), name='booking-accept'),
    path('bookings/<int:pk>/start-trip/', views.BookingViewSet.as_view({'post': 'start_trip'}), name='booking-start-trip'),
    path('bookings/<int:pk>/complete-trip/', views.BookingViewSet.as_view({'post': 'complete_trip'}), name='booking-complete-trip'),

    # Trip Views
    path('trips/', views.TripViewSet.as_view({'get': 'list'}), name='trip-list'),
    path('trips/<int:pk>/', views.TripViewSet.as_view({'get': 'retrieve'}), name='trip-detail'),

    # Payment Views
    path('payments/', views.PaymentViewSet.as_view({'get': 'list'}), name='payment-list'),
    path('payments/<int:pk>/', views.PaymentViewSet.as_view({'get': 'retrieve'}), name='payment-detail'),
    path('payments/<int:pk>/process-payment/', views.PaymentViewSet.as_view({'post': 'process_payment'}), name='payment-process-payment'),

    # Review Views
    path('reviews/', views.ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='review-detail'),

    # Subscription Views
    path('subscriptions/', views.SubscriptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='subscription-list'),
    path('subscriptions/<int:pk>/', views.SubscriptionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='subscription-detail'),

    # Notification Views
    path('notifications/', views.NotificationViewSet.as_view({'get': 'list'}), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationViewSet.as_view({'get': 'retrieve'}), name='notification-detail'),
    path('notifications/<int:pk>/mark-as-read/', views.NotificationViewSet.as_view({'post': 'mark_as_read'}), name='notification-mark-as-read'),
    path('notifications/mark-all-as-read/', views.NotificationViewSet.as_view({'post': 'mark_all_as_read'}), name='notification-mark-all-as-read'),

    # Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Heatmap
    path('heatmap/', views.DriverHeatmapView.as_view(), name='driver_heatmap'),
]