from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .services import userService


class UserView(APIView):
    

    def post(self, request,*args, **kwargs): 
        user_data = request.data
        if not user_data:
            return JsonResponse({"error":"no data"},status=400)
        user_infor = userService.create_user(user_data)
        if not user_infor:
            return JsonResponse({"error": "Failed to create user."}, status=400)      
        return JsonResponse(user_infor, status=201)
    def get(self,request):
        user_id = request.GET.get("user_id")
        result = userService.getUserById(user_id)
        return JsonResponse(result,status=200)
    def patch(self,request):
        user_id = request.GET.get("user_id")
        data = {   
                "first_name":request.data.get('first_name'),
                "last_name":request.data.get('last_name'),
                "introduce":request.data.get('introduce')
        }
        if request.FILES.get('avatar'):
            data['avatar'] = request.FILES.get('avatar') 
        result = userService.upDateUser(user_id,data)
        return JsonResponse(result,status=200)
class UsersView(APIView):
    def get(self, request,*args, **kwargs):
        user_id = request.GET.get("user_id")
        result = userService.getListUser(user_id)
        return JsonResponse(result,status=200)