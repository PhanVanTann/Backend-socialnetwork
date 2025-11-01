# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from bson import ObjectId
from .services import MessageService  

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'    

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        send_id = data['send_id']
        receiver_id = data['receiver_id']
        message_text = data.get('text', '')
        media = None  

        service = MessageService()
        save_result = service.create_message(
            room_id=self.room_id,
            send_id=send_id,
            receiver_id=receiver_id,
            text=message_text,
            media=media
        )
        print("result",save_result)

        if save_result['success']:
          
            await self.channel_layer.group_send(
                self.room_group_name,
                {   'type': 'chat_message',
                    'send_id': send_id,
                    'receiver_id': receiver_id,
                    'text': message_text,     
                    'media': None
                }
            )
            

    async def chat_message(self, event):
     
        await self.send(text_data=json.dumps({
            'send_id': event['send_id'],
            'receiver_id': event['receiver_id'],
            'text': event['text'],
            'media': event['media']
            
        }))