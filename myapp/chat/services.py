from utils.mogodbConnet import mongo
from bson import ObjectId
from datetime import datetime
import cloudinary.uploader
from notifications.services import NotificationsService
notification_service = NotificationsService()
class collection:
    def __init__(self):
        self.roomchat_conlection = mongo.get_collection('roomchats')
        self.user_collection = mongo.get_collection('users')
        self.message_collection = mongo.get_collection('messages')
    def get_roomchat_conletion(self):
        return self.roomchat_conlection
    def get_user_collection(self): 
        return self.user_collection
    def get_message_colletion(self):
        return self.message_collection
class ChatService(collection):
    def __init__(self):
        super().__init__()
        self.roomchat_conllection = self.get_roomchat_conletion()
        self.user_collection = self.get_user_collection()
    def create_roomchat(self,user_id1,user_id2):
        user1 = self.user_collection.find_one({'_id':ObjectId(user_id1)})
        user2 = self.user_collection.find_one({'_id':ObjectId(user_id2)})
        if not user1 and not user2:
            return {"success":False,"message":"user_id not valid" }
        members = sorted([ObjectId(user_id1), ObjectId(user_id2)], key=lambda x: str(x))
        try:
            room_data = self.roomchat_conllection.find_one({
                "members": {
                    "$all": members
                }
            })
            if not room_data:
                room = self.roomchat_conllection.insert_one({'members':members, "created_at": datetime.now(),}) 
                room_id = str(room.inserted_id)
                return {"success":True,"room_id":room_id}
            return {"success":True,"room_id":str(room_data['_id'])}
        except Exception as e:
            return{"success":False,"message":str(e)}
        
class MessageService(collection):
    def __init__(self):
        super().__init__()
        self.message_colletion = self.get_message_colletion()
        self.user_collection = self.get_user_collection()
    def create_message(self,room_id,send_id,receiver_id,text,media):
        media_url = None
        if media:
            media_file = media 
            upload_result = cloudinary.uploader.upload(media_file,resource_type="auto")
            media_url = upload_result.get("secure_url")
        
        message_doc = {
            "room_id": ObjectId(room_id),
            "send_id": ObjectId(send_id),
            "receiver_id": ObjectId(receiver_id),
            "text": text,
            "media": media_url,
            "status":False,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        userData = self.user_collection.find_one({'_id':ObjectId(send_id)})
        self.message_collection.insert_one(message_doc)
        notification_service.create_notification({
                        "user_id": receiver_id,
                        "actor_id": send_id,
                        "type": "message",
                        "resource_type": "message",
                        "resource_id": room_id,
                        "message": f"{userData['last_name']} {userData['first_name']} đã gửi cho bạn một tin nhắn."
                    })
        return {"success": True, "message": "Message created"}
    def get_history_chat_byuser(self,room_id,user_id):
        try:
            mess = self.message_collection.find({"room_id":ObjectId(room_id),"send_id":ObjectId(user_id)},{"room_id":1,"send_id":1,"receiver_id":1,"text":1,"media":1,"created_at":1}) 
            mess_lis = [
                {
                    "room_id":str(mes.get("room_id")),
                    "send_id":str(mes.get("send_id")),
                    "receiver_id":str(mes.get("receiver_id")),
                    "text":mes.get("text"),
                    "media":mes.get("media"),
                    "created_at":mes.get("created_at")
                } 
                for mes in mess
            ]
            return {"success":True,"data":mess_lis}
        except Exception as e:
            print(e)
    def get_history_chat_byreceiver(self,room_id,user_id):
        try:
            mess = self.message_collection.find({"room_id":ObjectId(room_id),"receiver_id":ObjectId(user_id)},{"room_id":1,"send_id":1,"receiver_id":1,"text":1,"media":1,"created_at":1}) 
            mess_lis = [
                {
                    "room_id":str(mes.get("room_id")),
                    "send_id":str(mes.get("send_id")),
                    "receiver_id":str(mes.get("receiver_id")),
                    "text":mes.get("text"),
                    "media":mes.get("media"),
                    "created_at":mes.get("created_at")
                } 
                for mes in mess
            ]
            return {"success":True,"data":mess_lis}
        except Exception as e:
            print(e)

        
