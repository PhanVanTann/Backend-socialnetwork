import json
from channels.generic.websocket import AsyncWebsocketConsumer

def user_group(user_id):
    return f"user_{user_id}"

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        error = self.scope.get("ws_auth_error")
        if error:
            await self.close(code=4401)
            return
        user = self.scope["user"]
        if getattr(user, "is_anonymous", True):
            await self.close(code=4401)
            return
        self.user_group_name = user_group(self.scope["user"].id)

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("Disconnected:", close_code)
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'data': event['data']
        }))
    
    async def push_notification(self,data: dict):
        try: 
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    'type': 'send_notification',
                    'data': data
                }
            )
        except Exception as e:
            print(f"Error pushing notification: {e}")