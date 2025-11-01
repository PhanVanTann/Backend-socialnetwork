from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .services import FriendService
friendService = FriendService()
# Create your views here.
class FriendView(APIView):
    def post(self,request):
        follower_id = request.data.get('follower_id')
        followee_id = request.data.get('followee_id')
        result = friendService.create_friend(follower_id,followee_id)
        return JsonResponse(result,status = 201)
    def get(self,request):
        user_id = request.GET.get('user_id') 
        my_id = request.GET.get('my_id')
        follower =False
        if request.GET.get('follower'):
            follower = request.GET.get('follower')
        
        result = friendService.get_flowersbyuserid(user_id,my_id,follower)
        return JsonResponse(result,status = 200)

class ListFriendView(APIView):
    def get(self,request):
        user_id = request.GET.get('user_id')  
        result = friendService.getlistfriend(user_id)
        return JsonResponse(result,status = 200)
    
class IsFriendView(APIView):
    def get(self,request):
        user_id = request.GET.get('user_id') 
        follower_id = request.GET.get('follower_id')
        
        result = friendService.isFriend(user_id,follower_id)
        return JsonResponse(result,status = 200)