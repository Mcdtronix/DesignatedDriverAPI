# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import User, DriverProfile, Booking, Trip, Payment, Review, Notification

    # Create driver profile when a user is marked as a driver
@receiver(post_save, sender=User)
def create_driver_profile(sender, instance, created, **kwargs):
    if created and instance.is_driver:
        DriverProfile.objects.create(user=instance)

@receiver(post_save, sender=Booking)
def booking_notification(sender, instance, created, **kwargs):
    # Send notifications on booking status changes
    if created:
        # New booking notification to driver
        Notification.objects.create(
            user=instance.driver,
            title="New Booking Request",
            message=f"You have a new booking request from {instance.user.get_full_name()}",
            related_booking=instance
        )
        
        # Also send email notification
        if settings.EMAIL_HOST:
            send_mail(
                'New Booking Request',
                f'You have a new booking request from {instance.user.get_full_name()}',
                settings.DEFAULT_FROM_EMAIL,
                [instance.driver.email],
                fail_silently=True,
            )
    
    # Status change notification
    elif instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        new_status = instance.status
        
        # Notify user about status change
        if new_status != old_status:
            Notification.objects.create(
                user=instance.user,
                title=f"Booking {new_status.title()}",
                message=f"Your booking has been {new_status}",
                related_booking=instance
            )

@receiver(post_save, sender=Payment)
def payment_completed(sender, instance, **kwargs):
    # Actions to take when payment is completed
    if instance.status == 'completed' and instance.tracker.has_changed('status'):
        # Notify driver about payment
        Notification.objects.create(
            user=instance.trip.booking.driver,
            title="Payment Received",
            message=f"You've received payment of ${instance.amount} for trip #{instance.trip.id}",
            related_booking=instance.trip.booking
        )
        
        # Send receipt to user
        if settings.EMAIL_HOST:
            send_mail(
                'Payment Receipt',
                f'Thank you for your payment of ${instance.amount} for your trip on {instance.trip.end_time.strftime("%Y-%m-%d %H:%M")}',
                settings.DEFAULT_FROM_EMAIL,
                [instance.trip.booking.user.email],
                fail_silently=True,
            )

@receiver(post_save, sender=Review)
def review_notification(sender, instance, created, **kwargs):
    # Notify driver when they receive a review
    if created:
        Notification.objects.create(
            user=instance.driver,
            title="New Review",
            message=f"You've received a {instance.rating}-star review",
            related_booking=instance.trip.booking
        )