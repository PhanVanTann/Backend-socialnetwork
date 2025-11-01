from utils.mogodbConnet import mongo
from bson import ObjectId
from datetime import datetime
from notifications.services import NotificationsService

notification_service = NotificationsService()

class collection:
    def __init__(self):
        self.post_collection = mongo.get_collection('posts')
        self.user_collection = mongo.get_collection('users')
        self.comment_collection = mongo.get_collection('comments')
    def get_post_collection(self):
        return self.post_collection
    def get_comment_collection(self):
        return self.comment_collection
    def get_user_collection(self): 
        return self.user_collection
class CommentsService(collection):
    def __init__(self):
        super().__init__()
        self.post_collection = self.get_post_collection()
        self.user_collection = self.get_user_collection()
        self.comment_collection = self.get_comment_collection()
    def create_comment(self, data):
        try:     
            user_data = self.user_collection.find_one({'_id':ObjectId(data.get('user_id'))})
            if not user_data:
                return {"success":False,"message":"user khoong tồn tại"}
            post_id = data.get('post_id')
            post_data = self.post_collection.find_one({'_id':ObjectId(post_id)})
            if not post_data:
                return {"success":False,"message":"bài viết không tồn tại"}
            if not data.get('parent_id'):
                data['parent_id'] = None
            if not data.get('interact'):
                data['interact'] = 0
                
            comment = {
                        "user_id": data.get('user_id'),
                        "post_id":post_id,
                        "content":data.get('content'),
                        "created_at": datetime.utcnow(),    
                        "parent_id" : data.get('parent_id'),
                        "interact": data.get('interact'),
            }
            dataComent = self.comment_collection.insert_one(comment)    
                
            comment['_id'] = str(dataComent.inserted_id)
            self.post_collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"total_comment": 1}})      
            if data.get('parent_id'):
                parent_comment = self.comment_collection.find_one({'_id': ObjectId(data.get('parent_id'))})
                if parent_comment:
                    if data.get('user_id') !=  parent_comment["user_id"]:
                   
                      notification_service.create_notification({
                      "user_id": parent_comment["user_id"],
                        "actor_id": data.get('user_id'),
                        "type": "reply",
                        "resource_type": "comment",
                        "resource_id": str(parent_comment["_id"]),
                        "message": f"{user_data['last_name']} {user_data['first_name']} đã trả lời bình luận của bạn."
                    })
            print("postdata",post_data)
            if post_data["user_id"] != data.get('user_id'):
                notification_service.create_notification({
                        "user_id": post_data["user_id"],
                        "actor_id": data.get('user_id'),
                        "type": "comment",
                        "resource_type": "post",
                        "resource_id": post_id,
                        "message": f"{user_data['last_name']} {user_data['first_name']} đã bình luận về bài viết của bạn."
                    })
            print("comment",comment)           
            return {"success":True,"message":"bình luận thành công","data":comment}  
                                 
        except Exception as e:
            return{"success":False,"message":str(e)}
    def getAllCommentsFromPostID(self,postId):
        try:
            postData = self.post_collection.find_one({'_id':ObjectId(postId)})
            if not postData:
                return {"success":False,"message":"bài post không tồn tại"}
            data = list(self.comment_collection.find({'post_id': postId}))
            for c in data:
                c["_id"] = str(c["_id"])
            print ("ahuqwhe21312wq" ,data)
            return {"success":True,"data":data}
        except Exception as e:
            return{"success":False,"message":str(e)}
    
    def getlistfriend(self, user_id: str):
        """
        Danh sách bạn bè (mutual follow):
        - followees: những người user_id đang follow
        - followers: những người đang follow user_id
        - friends = giao (mutual) followees ∩ followers
        """
        try:
            # 1) Lấy những người mình đang follow
            followees_cursor = self.friend_collection.find(
                {'follower_id': user_id},
                {'_id': 0, 'followee_id': 1}
            )
            followees = {doc['followee_id'] for doc in followees_cursor}

            # 2) Lấy những người đang follow mình
            followers_cursor = self.friend_collection.find(
                {'followee_id': user_id},
                {'_id': 0, 'follower_id': 1}
            )
            followers = {doc['follower_id'] for doc in followers_cursor}

            # 3) Mutual = giao nhau
            mutual_ids = list(followees & followers)

            if not mutual_ids:
                return {"success": True, "data": []}

          
            users_cursor = self.user_collection.find(
                {"_id": {"$in": [ObjectId(uid) for uid in mutual_ids]}},
                {"first_name": 1, "last_name": 1, "avatar": 1}
            )
            friends = [
                {
                    "id": str(u["_id"]),
                    "first_name": u.get("first_name"),
                    "last_name": u.get("last_name"),
                    "avatar": u.get("avatar")
                }
                for u in users_cursor
            ]

            return {"success": True, "data": friends}
        except Exception as e:
            return {"success": False, "message": str(e)}
        
   

