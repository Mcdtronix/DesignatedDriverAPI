import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import User, DriverProfile

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'location_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Update driver location in database
        if 'latitude' in data and 'longitude' in data:
            await self.update_driver_location(
                self.user_id, 
                data['latitude'], 
                data['longitude']
            )
        
        # Send location to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'latitude': data['latitude'],
                'longitude': data['longitude']
            }
        )
    
    # Receive message from room group
    async def location_update(self, event):
        latitude = event['latitude']
        longitude = event['longitude']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'latitude': latitude,
            'longitude': longitude
        }))
    
    @database_sync_to_async
    def update_driver_location(self, user_id, latitude, longitude):
        try:
            driver_profile = DriverProfile.objects.get(user_id=user_id)
            driver_profile.current_latitude = float(latitude)
            driver_profile.current_longitude = float(longitude)
            driver_profile.save()
        except DriverProfile.DoesNotExist:
            pass