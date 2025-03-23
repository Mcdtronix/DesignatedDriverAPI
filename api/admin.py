from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DriverProfile, Booking, Trip, Payment, Review, Subscription, Notification


# Register your models here.
class DriverProfileInline(admin.StackedInline):
    model = DriverProfile
    can_delete = False
    verbose_name_plural = 'driver profile'

class UserAdmin(BaseUserAdmin):
    inlines = (DriverProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_driver', 'is_staff')
    list_filter = ('is_driver', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'profile_picture', 'is_driver')}),
    )

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'vehicle_make', 'vehicle_model', 'is_available', 'background_check_status')
    list_filter = ('is_available', 'background_check_status')
    search_fields = ('user__username', 'user__email', 'license_number', 'license_plate')
    readonly_fields = ('last_location_update',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'driver', 'scheduled_time', 'booking_time', 'status')
    list_filter = ('status', 'booking_time', 'scheduled_time')
    search_fields = ('user__username', 'driver__username', 'pickup_address', 'destination_address')
    date_hierarchy = 'booking_time'

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'start_time', 'end_time', 'distance', 'total_fare')
    list_filter = ('start_time', 'end_time')
    search_fields = ('booking__user__username', 'booking__driver__username')
    date_hierarchy = 'start_time'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'amount', 'payment_method', 'status', 'timestamp')
    list_filter = ('payment_method', 'status', 'timestamp')
    search_fields = ('transaction_id', 'trip__booking__user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'user', 'driver', 'rating', 'timestamp')
    list_filter = ('rating', 'timestamp')
    search_fields = ('user__username', 'driver__username', 'comment')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('plan', 'is_active', 'start_date', 'end_date')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'start_date'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

admin.site.register(User, UserAdmin)