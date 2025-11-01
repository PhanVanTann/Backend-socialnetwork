import jwt
from django.conf import settings
from django.http import JsonResponse
from utils.jwt import decode_token  

class Middleware:
    def __init__(self,get_response):
            self.get_response = get_response
            self.rules = [
            ("/auth/login/", None),
            ("/users/", ["POST"]),
            ("/auth/refresh-token/",None),
            ("/auth/googleLogin/",None),
            ("/auth/verifyEmail/",None),
        ]
              
            self.rules_admin = {
                 
            }
    def __call__(self,request, *args, **kwds):
        path = request.path
        print(path)
        for rule_path,allowed_methods in self.rules:
            if path ==rule_path : 
                if allowed_methods is None:
                    print(allowed_methods)
                    return self.get_response(request)
                if request.method in allowed_methods:
                     return self.get_response(request)
        token = request.COOKIES.get("access_token")
        print(token)
        if not token:
            return JsonResponse({"success": False, "message": "Thiếu token"}, status=401)
        decode = decode_token(token) 
        if decode.get('error'):
             return JsonResponse({"success": False, "message": decode['error']}, status=401)
        if not decode.get('role'):  
            return JsonResponse({"success": False, "message": "Khoong cos quyen"}, status=401)
        return self.get_response(request)