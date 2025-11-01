from utils.mogodbConnet import mongo
import bcrypt
from django.http import JsonResponse 
from utils.sendemail import send_verify_email
from utils.jwt import create_email_token
from datetime import datetime
from bson import ObjectId
import cloudinary.uploader

class collectionUser:
    def __init__(self):
        self.collection_users = mongo.get_collection('users')
        self.collection_friends = mongo.get_collection('friend')

    def get_collection_user(self):
        return self.collection_users
   

class UserService(collectionUser):
    def __init__(self):
        super().__init__()
        self.user_collection = self.get_collection_user()

    ## Check if user exists
    def check_user_exists(self, email):
        user = self.user_collection.find_one({"email": email})
        if user:
            return {"success": True, "message": "User already exists."}
        return {"success": False, "message": "User does not exist."}
    
    
    ## Create user
    def create_user(self, user_data):
        try:
            request_data = { 
                "email": user_data.get("email"),
                "password": user_data.get("password"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "role": "user",
                "introduce":None,
                "avatar":"https://res.cloudinary.com/debzpay3s/image/upload/v1755841904/avatar-trang-3_qamssw.jpg",
                "is_verified": False,
                "is_google_account": False,
                "created_at": datetime.now(),
            }
            if self.check_user_exists(request_data['email'])['success']==True:
                return {"success":False,"error": "User already exists."}
            if request_data["password"]:
                hashed_password = bcrypt.hashpw(request_data["password"].encode('utf-8'), bcrypt.gensalt())
                request_data['password'] = hashed_password.decode('utf-8')
             # Create email verification token
            token_email = create_email_token(request_data['email'])
            if not token_email:
                return {"success": False, "error": "Failed to create email token."}
            send_email = send_verify_email(request_data['email'],token_email)
            print("send_email",send_email)
            if not send_email:              
                return {"success": False, "error": "Failed to send verification email."}
            result = self.user_collection.insert_one(request_data)
            if not result.acknowledged:
                return {"success": False, "error": "Failed to create user."}
            return {
                "success":True,
                "message": "User created successfully", 
                "user_id": str(result.inserted_id)
                }
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    def getUserById(self,user_id):
        try:
            userdata = self.collection_users.find_one({"_id":ObjectId(user_id)},{"_id":1,"email":1,"first_name":1,"last_name":1,"role":1,"avatar":1,"introduce":1})
            userdata["_id"] = str(userdata["_id"])
            return {
                "success":True,
                "data":userdata
            }
        except Exception as e:
            print(e)
    def getListUser(self, user_id: str):
        try:
            cursor = self.collection_users.find(
                {"role":"user"},
                {"_id": 1, "email": 1, "first_name": 1, "last_name": 1, "role": 1, "avatar": 1}
            )

            listUser = []
            for item in cursor:
                
                uid = str(item["_id"])

                isfollower = self.collection_friends.find_one({"follower_id": user_id, "followee_id": uid})
                isfollowing = self.collection_friends.find_one({"follower_id": uid, "followee_id": user_id})

                if isfollower and isfollowing:
                    status = "friend"
                elif isfollower and not isfollowing:
                    status = "follower"   
                elif not isfollower and isfollowing:
                    status = "following"  
                else:
                    status = "nofollow"

                user_obj = {
                    "_id": uid,
                    "email": item.get("email"),
                    "first_name": item.get("first_name"),
                    "last_name": item.get("last_name"),
                    "role": item.get("role"),
                    "avatar": item.get("avatar"),
                    "introduce":item.get("introduce"),
                    "is_friend": status
                }
                listUser.append(user_obj)

            return {
                "success": True,
                "data": listUser
            }
        except Exception as e:
            print("getListUser error:", e)
            return {"success": False, "message": "Internal error"}
        
    def upDateUser(self,user_id,data):
        try:
            userData = self.collection_users.find_one({'_id':ObjectId(user_id)})
            if not userData:
                return {"success":False,"message":"không có user"}
            avatar = userData['avatar']
            if data.get('avatar'):
                up = cloudinary.uploader.upload(data['avatar'], resource_type="image")
                avatar = up.get("secure_url")
          
            update = self.collection_users.update_one({"_id":ObjectId(user_id)},
                                                       {"$set": {
                                                            "first_name": data['first_name'],
                                                            "last_name": data['last_name'],
                                                            "introduce": data['introduce'],
                                                            "avatar": avatar
                                                        }})
            print(update)
            result = {
                "user_id":user_id,
                "first_name" :data['first_name'],
                "last_name":data['last_name'],
                "introduce":data['introduce'],
                "avatar":avatar
            }
            return {"success":True,"message":"update thanh công","data":result}
        except Exception as e:
            print(" error:", e)
            return {"success": False, "message": "Internal error"}
   
userService = UserService()