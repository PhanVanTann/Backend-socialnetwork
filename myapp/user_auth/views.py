from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .services import emailService
from utils.jwt import decode_token
from .services import LoginService, UserLogoutService, GoogoleService,AuthServicer
from utils.jwt import create_cookie
from django.http import HttpResponseRedirect
import json
# Create your views here.
authServicer = AuthServicer()
class EmailView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        try:
            decoded_data = decode_token(token)
            if isinstance(decoded_data, dict) and decoded_data.get("error"):
                return JsonResponse({"error": f"Invalid token: {decoded_data['error']}"}, status=401)
            email = decoded_data.get('email')
            if not email:
                return JsonResponse({"error": "email not in token"}, status=400)

            email_service = emailService()
            user = email_service.verify_email_token(email)

            if user["success"]:
                return HttpResponseRedirect("https://socialnetwork-su0z.onrender.com/login?isVerified=true")
            else:
                return JsonResponse({"success":False,"error": "unverified Email"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        login_service = LoginService()
        login_response = login_service.login(email, password)

        if login_response['success']: 
            access_token = login_response["access_token"]
            refresh_token = login_response["refresh_token"]
         
            response = JsonResponse({
                "success": True,
                "message": "Login successful",
                "user_id": login_response['user_id'],
                "access_token":access_token, 
                "role": login_response['role'],
            }, status=200)
            response.set_cookie("access_token", access_token, httponly=True, max_age=3600)
            response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=7*24*3600)
            return response
        else:
            return JsonResponse({"error": login_response['message']}, status=401)
class UserLogoutView(APIView):
    userLogoutService = UserLogoutService()
    def post(self, request):
        access_token = request.COOKIES.get('access_token')
        print(access_token)
        if not access_token:
            return JsonResponse({"error": "Access token is required"}, status=400) 
        try:
            decoded_data = decode_token(access_token)
            print(decoded_data)
            if isinstance(decoded_data, dict) and decoded_data.get("error"):
                return JsonResponse({"error": f"Invalid token: {decoded_data['error']}"}, status=401)

            user_id = decoded_data.get('user_id')
            if not user_id:
                return JsonResponse({"error": "User ID not found in token"}, status=400)
 
            self.userLogoutService.logout(user_id) 
            response = JsonResponse({"success": True, "message": "Logout successful"}, status=200)
            response.delete_cookie('refresh_token')
            response.delete_cookie("access_token")
            return response
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class GoogleLoginView(APIView):
    def post(self, request):
        idtoken_str = request.data.get('idtoken')
        if not idtoken_str:
            return JsonResponse({"error": " token is required"}, status=400)

        google_service = GoogoleService()
        response = google_service.create_user(idtoken_str)
        
        if response['success']:
            access_token = response["access_token"]
            refresh_token = response["refresh_token"]
         
            response = JsonResponse({
                "success": True,
                "message": "Login successful",
                "user_id": response['user_id'],
                "access_token":access_token, 
                "role": response['role'],
            }, status=200)
            response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="None", max_age=3600)
            response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="None", max_age=7*24*3600)
            return response
        
        return JsonResponse({"error": "Invalid request"}, status=400)   
class AuthView(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh_token")
        result = authServicer.refreshToken(refresh_token)
        print(result,"jjhhh")
        response = JsonResponse({
                "success": True,
                "message":result['message']     
            }, status=200)
        
        response.set_cookie("access_token", result['new_accessToken'], httponly=True, secure=False, samesite="Lax",max_age=3600)
        return response