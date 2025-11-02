from utils.mogodbConnet import mongo
from bson import ObjectId
import bcrypt
from datetime import datetime
import requests
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from google.oauth2 import id_token
from google.auth.transport import requests as grequests 
from django.conf import settings
from utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decode_token_notime,
    )
class collection:
    def __init__(self):
        self.user_collection = mongo.get_collection('users')
        self.session_collection = mongo.get_collection('sessions')
    def get_user_collection(self):
        return self.user_collection
    def get_session_collection(self):
        return self.session_collection
    
    def create_session(self,user_id,email,role):
        access_token = create_access_token(str(user_id),role)
        refresh_token = create_refresh_token(str(user_id),role)
        # Kiểm tra xem đã có session cho user chưa
        existing_session = self.session_collection.find_one({"user_id": str(user_id)})
        if existing_session:
            self.session_collection.update_one(
                {"user_id": str(user_id)},
                {
                    "$set": {
                        "Access_Token": access_token,
                        "Refresh_Token": refresh_token,
                        "Created_at": datetime.now()
                    }
                }
            )
        else:
            dataSession = {
                "user_id": str(user_id),
                "Access_Token": access_token,
                "Refresh_Token": refresh_token,
                "Created_at": datetime.now()
            } 
            self.user_collection.update_one(
                            {'email': email},
                            {'$set': {'is_active': True}}  
                        )
            self.session_collection.insert_one(dataSession)
        return {
            "Access_Token": access_token,
            "Refresh_Token": refresh_token
        } 

class emailService(collection):
    def __init__(self):
        super().__init__()
        self.user_collection = self.get_user_collection()

    def verify_email_token(self, email):
        try:
            user = self.user_collection.find_one({"email": email})
            if user and not user.get("is_verified", False):
                self.user_collection.update_one({"email": email}, {"$set": {"is_verified": True}})
                return {"success": True, "message": "Email verified successfully."}
            return {"success": False, "message": "Invalid or already verified email."}
        except Exception as e:
            print(f"Error verifying email: {e}")
            return {"success": False, "message": "Error verifying email."}

class LoginService(collection):
    def __init__(self):
        super().__init__()
        self.user_collection = self.get_user_collection()
        self.session_collection = self.get_session_collection()
 
    

    def login(self, email, password):
        try:
            user = self.user_collection.find_one({"email": email})
            if user.get("is_google_account", True) and not user.get("password"):
                return {"success": False, "message": "Please login with Google account."}
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                if not user.get("is_verified", False):
                    return {"success": False, "message": "Email not verified."}
                dataSession = self.create_session(user['_id'],email,user['role'])
                return {
                            "success": True,
                            "message": "login success",
                            "access_token": dataSession['Access_Token'],
                            "refresh_token":dataSession['Refresh_Token'],
                            "user_id": str(user['_id']),
                            "role": user['role']
                        } 
            return {"success": False, "message": "Invalid email or password."}
        except Exception as e:
            print(f"Error during login: {e}")
            return {"success": False, "message": "Error during login."}

class UserLogoutService(collection):
    def __init__(self):
        self.session_collection = mongo.get_collection('sessions')
        self.user_collection = mongo.get_collection('users')

    def logout(self, user_id):
        try:          
            result = self.session_collection.delete_one({"user_id": str(user_id)})
            if result.deleted_count > 0:
                const = self.user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False}}
                ) 
                print(const)
                return {"success": True, "message": "Logout successful."}
            
            return {"success": False, "message": "No active session found."}
        except Exception as e:
            print(f"Error during logout: {e}")
            return {"success": False, "message": "Error during logout."} 
class GoogoleService(collection):
    def __init__(self):
        super().__init__()
        self.user_collection = self.get_user_collection()

    def create_user(self, idtoken_str):
        try: 
            print(settings.GOOGLE_CLIENT_ID)
            print(idtoken_str)
            idinfo = id_token.verify_oauth2_token(idtoken_str, grequests.Request(),settings.GOOGLE_CLIENT_ID)
            print(idinfo)
            email = idinfo.get("email")
            first_name = idinfo.get("family_name")
            last_name = idinfo.get("given_name")
            picture = idinfo.get("picture")
            user_data = self.user_collection.find_one({"email": email})
            if user_data:
                if not user_data.get("is_verified", False):
                    return {"success": False, "message": "Email not verified."}
                dataSession = self.create_session(user_data['_id'], email, user_data['role'])
                if not user_data.get("is_google_account"):
                    self.user_collection.update_one(
                        {"email": email},
                        {"$set": {"is_google_account": True}}
                    )
                return {
                        "success": True,
                        "message": "Login successful.",
                        "access_token": dataSession['Access_Token'],
                        "refresh_token": dataSession['Refresh_Token'],
                        "user_id": str(user_data['_id']),
                        "role": user_data['role']
                    }
            else:
                request_data = { 
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": "user",
                    "introduce":None,
                    "avatar": picture,
                    "is_verified": True,
                    "is_google_account": True,
                    "is_google_account": True,
                    "created_at": datetime.now(),
                }
                respone = self.user_collection.insert_one(request_data)
                if not respone.acknowledged:
                    return {"success": False, "message": "Failed to create user."}
                dataSession = self.create_session(respone.inserted_id, email, "user")

            return {
                "success": True,
                "message": "User created successfully.",
                "access_token": dataSession['Access_Token'],
                "refresh_token": dataSession['Refresh_Token'],
                "user_id": str(respone.inserted_id),
                "role": "user"
            }
        except Exception as e:
            print(f"Error creating user: {e}")
            return {"success": False, "message": "Error creating user."}
class AuthServicer(collection):
    def refreshToken(self,refresh_token):
        try:
                decode_ref = decode_token(refresh_token)
                if decode_ref.get('error'):
                    return {"success":False,"message":decode_ref['error']}
                secction = self.session_collection.find_one({"user_id":decode_ref["user_id"],"Refresh_Token":refresh_token})
                if not secction:
                    return {"success":False,"message":"Khoong tìm thấy phiên đăng nhập"}
                new_access =create_access_token(decode_ref.get('user_id'),decode_ref.get('role'))
                self.session_collection.update_one({"user_id":decode_ref["user_id"],"Refresh_Token":refresh_token},{"$set":{"Access_Token":new_access,"Created_at":datetime.utcnow()}})
                return {"success":True,"message":"refresh token thành công!","new_accessToken":new_access}
        except Exception as e:
            print(e)