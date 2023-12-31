import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async  # Import database_sync_to_async
from chat.models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Set up the WebSocket connection
        self.roomGroupName = "group_chat_gfg"
        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()

         # Fetch previous messages from the database
        previous_messages = await self.get_previous_messages()
        for message in previous_messages:
            await self.send_message_to_chat(message)

    async def disconnect(self, close_code):
        # Remove the connection from the group when disconnecting
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_layer 
        )

    async def receive(self, text_data):
        # Receive and process incoming messages from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        
        # Save the message to the database
        await self.save_message(username, message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "message": message,
                "username": username,
            })

    async def sendMessage(self, event):
        # Send messages to the WebSocket
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({"message": message, "username": username}))

    async def send_message_to_chat(self, message):
        await self.send(text_data=json.dumps({
            'message': message['message'],
            'username': message['username']
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        # Save the message to the database using the ChatMessage model
        ChatMessage.objects.create(
            room=self.roomGroupName,
            username=username,
            message=message
        )
    @database_sync_to_async
    def get_previous_messages(self):
        # Retrieve previous messages from the database
        messages = ChatMessage.objects.filter(room=self.roomGroupName).order_by('timestamp')[:50]
        return [{'username': message.username, 'message': message.message} for message in messages]