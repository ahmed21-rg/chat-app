from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import ChatRoom, Message, User

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Create a unique group per user
        self.user_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket connected for {self.user.username}")

    async def disconnect(self, close_code):

        if hasattr(self, "user_group_name"): # Check if user_group_name attribute exists before discarding group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Receive a message from frontend and broadcast to room members
        """
        data = json.loads(text_data) # Parse JSON data from frontend 
        room_id = data.get("room_id")
        
        message_id = data.get("message_id")#

        if not room_id or not message_id:
            return

        payload = await self.get_message_payload(message_id)
        room_name, members = await self.get_room_info(room_id)

        for member in members:
            await self.channel_layer.group_send(
                f'user_{member.id}',  # Send to the specific user's group 
                {
                    "type": "chat_message",
                    "payload": payload,
                    "room_id": room_id,
                    "room_name": room_name,
                    "is_group": len(members) > 2,
                }
            )

            if member.id != payload["sender_id"]:
                await self.channel_layer.group_send(
                    f'user_{member.id}',
                    {
                        "type": "notification",
                        "room_id": room_id,
                        "room_name": room_name,
                        "sender_username": payload["sender_username"],
                        "message": payload["message"],
                    }
                )


    async def chat_message(self, event):
        """
        Receive message from group_send and send to WebSocket
        """
        print("chat_message event:", event)
        
        payload = event["payload"] # Get message payload from event

       # if payload["sender_id"] == self.user.id:   
          #  return          # Avoid sending message back to sender

        await self.send(text_data=json.dumps({
            **event["payload"],
            "room_id": event["room_id"],
            "room_name": event["room_name"],
            "is_group": event["is_group"]
        }))      #Send event data as JSON to frontend


    async def notification(self, event):
        """
        Send notification to WebSocket
        """
        await self.send(text_data=json.dumps({
            "type": "notification",
            "room_id": event["room_id"],
            "room_name": event["room_name"],
            "sender_username": event["sender_username"],
            "message": event["message"],
        }))    #Send notification data as JSON to frontend

    @database_sync_to_async
    def save_message(self, room_id, sender_id, message, image_url=None, document_url=None):
        room = ChatRoom.objects.get(id=room_id)
        sender = User.objects.get(id=sender_id)
        return Message.objects.create(room=room, sender=sender, message=message, image=image_url, document=document_url)

    @database_sync_to_async
    def get_room_info(self, room_id):
        room = ChatRoom.objects.get(id=room_id)
        members = [m.user for m in room.members.all()]
        room_name = room.group_name if room.is_group else " & ".join([m.username for m in members])
        return room_name, members

    @database_sync_to_async
    def get_message(self, message_id):
        return Message.objects.get(id=message_id)
    
    @database_sync_to_async
    def get_message_sender_id(self,message_id):
        from .models import Message
        return Message.objects.select_related("sender").get(id=message_id).sender.id

    @database_sync_to_async
    def get_message_payload(self, message_id):  
        
        message = Message.objects.select_related("room", "sender").get(id=message_id)
        
        return{
            "id": message.id,
            "room_id": message.room.id,
            "sender_id": message.sender.id,
            "sender_username": message.sender.username,
            "message": message.message,
            "image_url": message.image.url if message.image else None,
            "document_url": message.document.url if message.document else None,
            "created_at": message.created_at.isoformat(),
        }    #Return message payload as a dictionary 