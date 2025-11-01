import requests
import cloudinary.uploader
from datetime import datetime
from utils.mogodbConnet import mongo
from django.conf import settings
from bson import ObjectId
from concurrent.futures import ThreadPoolExecutor
from notifications.services import NotificationsService

notification_service = NotificationsService()

class collection:
    def __init__(self):
        self.post_collection = mongo.get_collection('posts')
        self.censorship_collection = mongo.get_collection('censorships')
        self.user_collection = mongo.get_collection('users')
        self.notifications_collection = mongo.get_collection('notifications')
    def get_post_collection(self):
        return self.post_collection
    def get_censorship_collection(self):
        return self.censorship_collection
    def get_user_collection(self): 
        return self.user_collection

class CensorshipService(collection):
    def __init__(self):
        super().__init__()
        self.post_collection = self.get_post_collection()
        self.censorship_collection = self.get_censorship_collection()
        self.user_collection = self.get_user_collection()
   
    def create_post(self, data):
        user_id = data.get("user_id")
        text_content = (data.get("text") or " ").strip()
        media_file = data.get("media")

        # Upload media (nếu có) và xác định loại
        media_url = None
        media_type = None
        if media_file:
            up = cloudinary.uploader.upload(media_file, resource_type="auto")
            media_url = up.get("secure_url")
            media_type = up.get("resource_type")  # 'image' | 'video'
        try:
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"success": False, "error": "User not found."}
            post_data = {
            "user_id": user_id,
            "avatar":user["avatar"] or None,
            "first_name":user["first_name"],
            "last_name":user["last_name"],
            "text": text_content,
            "media": media_url,
            "is_video": bool(media_type == "video"),
            "flag": False,
            "status": "valid",
            "total_love": 0,
            "total_comment": 0,
            "created_at": datetime.now(),
        }
            self.post_collection.insert_one(post_data)
            return {"success": True, "message": "Post created successfully."}
        except Exception as e:
            return {"success": False, "message": "Error in censorship", "error": str(e)}



    def get_listpost(self, limit: int = 10, cursor: str = None):
        try:
            q = {"status": "valid"}

            if cursor:
                dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
                q["created_at"] = {"$lt": dt}
            cursor_q = (self.post_collection.find(q)
                        .sort([("created_at", -1), ("_id", -1)])
                        .limit(limit))

            datas = []
            last_created = None
            for d in cursor_q:
                d["_id"] = str(d["_id"])
                if "created_at" in d and isinstance(d["created_at"], datetime):
                    last_created = d["created_at"]
                    d["created_at"] = d["created_at"].isoformat()
                datas.append(d)

            next_cursor = last_created.isoformat().replace("+00:00", "Z") if last_created else None
            print("next_cursor", next_cursor)
            return {
                "success": True,
                "data": datas,
                "nextCursor": next_cursor
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def getPostValidByUser(self,user_id):
        try:
            cursor = self.post_collection.find({"status": "valid","user_id":user_id})
            datas = []
            for d in cursor:
                d['_id'] = str(d['_id'])
                datas.append(d)
            return {"success": True, "data": datas}
        except Exception as e:
            return {"success": False, "error": str(e)} 
    
    def deletePost(self,user_id,post_id):
        try:
            print(user_id)
            print(post_id)
            postData = self.post_collection.find_one({'_id':ObjectId(post_id),'user_id':user_id})
            if not postData:
                return {"success":False,"message":"không tìm thấy user hay bài đăng"}
            result = self.post_collection.delete_one({"_id": ObjectId(post_id), "user_id": user_id})
            if result.deleted_count > 0:
                return {"success": True, "message": "xoá bài thành công"}
            else:
                return {"success": False, "message": "Post not found or not owned by this user"}
            
        except Exception as e:
            return {"success": False, "error": str(e)} 
    def heartPost(self,user_id,post_id):
        try:
            postData = self.post_collection.find_one({'_id':ObjectId(post_id)})
            if not postData:
                return {"success":False,"message":"không tìm thấy bài đăng"}
            userData = self.user_collection.find_one({'_id':ObjectId(user_id)})
            if not userData:
                return {"success":False,"message":"không tìm thấy user"}
            if user_id in postData.get("list_user_heart",[]):
                self.post_collection.update_one({'_id':ObjectId(post_id)},{
                    "$inc":{"total_love":-1},
                    "$pull":{"list_user_heart":user_id}
                })
                dele = self.notifications_collection.delete_one({
                    "user_id": ObjectId(postData["user_id"]),
                    "actor.actor_id": user_id,
                    "type": "like",
                    "resource_type": "post",
                    "resource_id": ObjectId(post_id),
                })
                if dele.deleted_count > 0:
                    print("dele",dele)
                return {"success":True,"message":"bỏ thích thành công"}
            else:
                self.post_collection.update_one({'_id':ObjectId(post_id)},{
                    "$inc":{"total_love":1},
                    "$push":{"list_user_heart":user_id}
                })
                if user_id != postData["user_id"]:
                    notification_service.create_notification({
                            "user_id": postData["user_id"],
                            "actor_id": user_id,
                            "type": "like",
                            "resource_type": "post",
                            "resource_id": post_id,
                            "message": f"{userData['last_name']} {userData['first_name']} đã thích bài viết của bạn."
                        })
                return {"success":True,"message":"thích thành công"}
        except Exception as e:
            return {"success": False, "error": str(e)} 
    def getPostById(self,post_id):
        try:
            postData = self.post_collection.find_one({'_id':ObjectId(post_id)})
            if not postData:
                return {"success":False,"message":"không tìm thấy bài đăng"}
            postData['_id'] = str(postData['_id'])
            return {"success":True,"data":postData}
        except Exception as e:
            return {"success": False, "error": str(e)}
    def getPostAwaitingCensorship(self):
        try:
            postData = self.post_collection.find({"flag": True, "status": "awaiting"})
            datas = []
            for d in postData:
                d['_id'] = str(d['_id'])
                datas.append(d)
            return {"success": True, "data": datas}
        except Exception as e:
            return {"success": False, "error": str(e)}
    def getCensorshipbyPostId(self,post_id):
        try:
            postData = self.post_collection.find_one({'_id':ObjectId(post_id),'flag': True, 'status': 'awaiting'})
            if not postData:
                return {"success":False,"message":"không tìm thấy bài đăng"}
            postData['_id'] = str(postData['_id'])
            censorships = list(self.censorship_collection.find({'post_id':post_id}))
            for c in censorships:
                c['_id'] = str(c['_id'])
                c['post_id'] = str(c['post_id'])
            return {
                "success":True,
                "data":{
                    "text":postData.get("text"),
                    "censorships":censorships
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    def updateCensorshipStatus(self,post_id,status):
        try:
            if status not in ["valid","not valid"]:
                return {"success":False,"message":"trạng thái không hợp lệ"}
            postData = self.post_collection.find_one({'_id':ObjectId(post_id),'flag': True, 'status': 'awaiting'})
            if not postData:
                return {"success":False,"message":"không tìm thấy bài đăng"}
            if status == "valid":
                self.post_collection.update_one({'_id':ObjectId(post_id)},{'$set':{'status':status,'flag':False}})
                notification_service.create_notification({
                            "user_id": postData["user_id"],
                            "actor_id": None,
                            "type": "censorship",
                            "resource_type": "post",
                            "resource_id": post_id,
                            "message": f"Bài viết của bạn đã được duyệt và hiển thị trên trang chủ."
                        })
            else:
                self.post_collection.update_one({'_id':ObjectId(post_id)},{'$set':{'status':status}})
                notification_service.create_notification({
                            "user_id": postData["user_id"],
                            "actor_id": None,
                            "type": "censorship",
                            "resource_type": "post",
                            "resource_id": post_id,
                            "message": f"Bài viết của bạn không được duyệt vì vi phạm tiêu chuẩn cộng đồng."
                        })
            return {"success":True,"message":"cập nhật trạng thái thành công"}
        except Exception as e:
            return {"success": False, "error": str(e)}