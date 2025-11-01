from utils.mogodbConnet import mongo
from bson import ObjectId
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def to_oid(v):
    try:
        return ObjectId(v)
    except (TypeError):
        return v 

def user_group(uid: str) -> str:
    return f"user_{uid}"

class Collections:
    def __init__(self):
        self.notifications_collection = mongo.get_collection("notifications")
        self.user_collection = mongo.get_collection("users")

class NotificationsService(Collections):
    def __init__(self):
        super().__init__()

    def create_notification(self, data: dict):
        try:
            required = ["user_id", "actor_id", "type", "resource_type", "resource_id", "message"]
            miss = [k for k in required if k not in data]
            if miss:
                return {"success": False, "message": f"missing fields: {', '.join(miss)}"}
            user = self.user_collection.find_one({"_id": to_oid(data["user_id"])})
            if not user:
                return {"success": False, "message": "user_id not valid"}
            actor = self.user_collection.find_one({"_id": to_oid(data["actor_id"])})
            if not actor:
                return {"success": False, "message": "actor_id not valid"}
            doc = {
                "user_id": to_oid(data["user_id"]),
                 "actor":{ 
                    "actor_id": str(data["actor_id"]),
                    "name": f'{actor.get("first_name")} {actor.get("last_name")}',
                    "avatar": actor.get("avatar"),
                         },
                "type": data["type"],                  
                "resource_type": data["resource_type"], 
                "resource_id": to_oid(data["resource_id"]),
                "message": data["message"],
                "is_read": bool(data.get("is_read", False)),
                "created_at": datetime.utcnow(),
            }
            ins = self.notifications_collection.insert_one(doc)
            notif_id = str(ins.inserted_id)

            payload = {
                "id": notif_id,
                "user_id": str(data["user_id"]),
                "actor":{ 
                    "actor_id": str(data["actor_id"]),
                    "name": f'{actor.get("first_name")} {actor.get("last_name")}',
                    "avatar": actor.get("avatar"),
                         },
                "type": data["type"],
                "resource_type": data["resource_type"],
                "resource_id": str(data["resource_id"]),
                "message": data["message"],
                "is_read": False,
                "created_at": doc["created_at"].isoformat() + "Z",
            }
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    user_group(str(data["user_id"])),
                    {"type": "send_notification", "data": payload}
                )
            except Exception:
                import logging; logging.exception("WS push failed")

            return {"success": True, "notification_id": notif_id}

        except Exception as e:
            return {"success": False, "message": str(e)}
        
    def list_notifications(self, user_id: str):
        try:
            limit = 20
            cursor = self.notifications_collection.find(
                {"user_id": ObjectId(user_id)},
                sort=[("created_at", -1)],  
                limit=limit
            )
            items = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["user_id"] = str(doc["user_id"])
                doc["resource_id"] = str(doc["resource_id"])
                doc["created_at"] = doc["created_at"].isoformat() + "Z"
                items.append(doc)

            unread = self.notifications_collection.count_documents(
                {"user_id": ObjectId(user_id), "is_read": False}
            )
            print("unread", unread)
            return {
                "success": True,
                "data": {
                    "data": items,
                    "unread": unread
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def mark_as_read(self, user_id: str, notification_id: str):
        try:
            notif = self.notifications_collection.find_one(
                {"_id": ObjectId(notification_id), "user_id": ObjectId(user_id)}
            )
            if not notif:
                return {"success": False, "message": "notification not found"}
            if notif.get("is_read"):
                return {"success": True, "message": "already read"}

            self.notifications_collection.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"is_read": True}}
            )
            return {"success": True, "message": "marked as read"}
        except Exception as e:
            return {"success": False, "message": str(e)}