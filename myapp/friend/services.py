from utils.mogodbConnet import mongo
from bson import ObjectId
from datetime import datetime
from notifications.services import NotificationsService

notification_service = NotificationsService()

class collection:
    def __init__(self):
        self.friend_collection = mongo.get_collection('friend')
        self.user_collection = mongo.get_collection('users')
    def get_friend_collection(self):
        return self.friend_collection
    def get_user_collection(self): 
        return self.user_collection

class FriendService(collection):
    def __init__(self):
        super().__init__()
        self.friend_collection=self.get_friend_collection()
        self.user_collection = self.get_user_collection()
    
    def create_friend(self,follower_id,followee_id):
        try:
            if follower_id == followee_id:
                return {"success": False, "message": "Không thể follow chính mình"}
            user = self.user_collection.find_one({'_id': ObjectId(follower_id)})
            followee = self.user_collection.find_one({'_id': ObjectId(followee_id)})
            if not user and not followee:
                return {"success":False,"message":"user không tồn tại"}
            exists = self.friend_collection.find_one({
                'follower_id': follower_id,
                'followee_id': followee_id
            })

            if exists:
                
                self.friend_collection.delete_one({
                    'follower_id': follower_id,
                    'followee_id': followee_id
                })
                return {"success": True, "message": "Đã unfollow", "is_friend": False}
            else:
                
                self.friend_collection.insert_one({
                    'follower_id': follower_id,
                    'followee_id': followee_id,
                    'created_at': datetime.now()
                })
                
            
                is_friend = self.friend_collection.find_one({
                    'follower_id': followee_id,
                    'followee_id': follower_id
                }) is not None
                if is_friend:
                    notification_service.create_notification({
                            "user_id": followee_id,
                            "actor_id": follower_id,
                            "type": "friend",
                            "resource_type": "user",
                            "resource_id": follower_id,
                            "message": f"Bạn và {user['last_name']} {user['first_name']} đã trở thành bạn bè."
                    })
                else:
                    notification_service.create_notification({
                            "user_id": followee_id,
                            "actor_id": follower_id,
                            "type": "follow",
                            "resource_type": "user",
                            "resource_id": follower_id,
                            "message": f"{user['last_name']} {user['first_name']} đã theo dõi bạn."
                    })
                return {
                    "success": True,
                    "message": "Follow thành công",
                    "is_friend": is_friend
                }
        except Exception as e:
            return{"success":False,"message":str(e)}
    def get_flowersbyuserid(self, user_id,my_id ,follower):
        try:
           
            print("user_id",user_id)
            print("my_id",my_id)
            user_data = self.user_collection.find_one({'_id': ObjectId(user_id)})
            if not user_data:
                return {"success": False, "message": "user không tồn tại"}

            if not follower:  
                flowers = list(self.friend_collection.find({"follower_id": user_id}))
                if not flowers:
                    return {"success": True, "message": "bạn chưa theo dõi ngừoi nào", "flowers": None}
                flowers_id = [item['followee_id'] for item in flowers]
            else: 
                flowers = list(self.friend_collection.find({"followee_id": user_id}))
                if not flowers:
                    return {"success": True, "message": "bạn chưa có người theo dõi nào", "flowers": None}
                flowers_id = [item['follower_id'] for item in flowers]

        
            flowers_infor = list(
                self.user_collection.find(
                    {"_id": {"$in": [ObjectId(fid) for fid in flowers_id]}},
                    {"first_name": 1, "last_name": 1, "avatar": 1}
                )
            )

            flowers_data = []
            for u in flowers_infor:
                other_id = str(u["_id"])
                me_follow = self.friend_collection.find_one({
                    "follower_id": my_id,
                    "followee_id": other_id
                })
                other_follow = self.friend_collection.find_one({
                    "follower_id": other_id,
                    "followee_id": my_id
                })
               
                if  me_follow and  other_follow:
                    result = True
                else :
                    result = False
                print(result,"shshhs")
                flowers_data.append({
                    "id": other_id,
                    "first_name": u["first_name"],
                    "last_name": u["last_name"],
                    "avatar": u["avatar"],
                    "is_friend": result
                })

            return {"success": True, "flowers": flowers_data}
        except Exception as e:
            return {"success": False, "message": str(e)}
    def getlistfriend(self, user_id: str):
        """
        Danh sách bạn bè (mutual follow):
        - followees: những người user_id đang follow
        - followers: những người đang follow user_id
        - friends = giao (mutual) followees ∩ followers
        """
        try:
          
            followees_cursor = self.friend_collection.find(
                {'follower_id': user_id},
                {'_id': 0, 'followee_id': 1}
            )
            followees = {doc['followee_id'] for doc in followees_cursor}

         
            followers_cursor = self.friend_collection.find(
                {'followee_id': user_id},
                {'_id': 0, 'follower_id': 1}
            )
            followers = {doc['follower_id'] for doc in followers_cursor}

     
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
    
    def isFriend(self, user_id, follower_id):
        try:
            user = self.user_collection.find_one(              
                    {"_id": ObjectId(user_id)},                   
            )
            follower = self.user_collection.find_one(              
                    {"_id": ObjectId(follower_id)}                
            )
            print(user,follower)
            if not user and not follower:               
                return {"success":False,"message":"not user"}
            me_follow = self.friend_collection.find_one({
                    "follower_id": user_id,
                    "followee_id": follower_id
                })
            other_follow = self.friend_collection.find_one({
                    "follower_id": follower_id,
                    "followee_id": user_id
                })
            if  me_follow and other_follow:
                result = "friend"
            elif me_follow and not other_follow:
                result = "follower"
            elif other_follow and not me_follow:
                result = "following"
            else :
                result ="nofollow"
            if result:
                return {
                    "success": True,
                    "is_friend": result,
                  
                }
            return{
                "success": False,
                "error":"không có trường hợp này"
               
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
                
            
    
        
   

