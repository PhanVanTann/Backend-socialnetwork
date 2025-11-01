from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .services import CensorshipService
censorship_service = CensorshipService()
# Create your views here.
class CensorshipView(APIView):
    
    def post(self, request):
        data={
            "user_id" : request.data.get('user_id'),
            "text"    : request.data.get('text'),
            "media"   : request.FILES.get('media'), 
        }
        
        result = censorship_service.create_post(data)
        print("Image Censorship Result:", result)
        if result['success']:
            return JsonResponse(result, status=201)
        else:
            return JsonResponse({"error": result['error']}, status=500)
    
    def get(self,request):
        limit = int(request.GET.get("limit", 10))
        cursor = request.GET.get("cursor", None) 
        result  = censorship_service.get_listpost(limit,cursor)
        return JsonResponse(result, status=200)
    def delete(self,request):
        post_id = request.GET.get('post_id')
        user_id = request.GET.get('user_id')
        result = censorship_service.deletePost(user_id,post_id)
        return JsonResponse(result,status = 200)
    
class MyPostValid(APIView):
    def get(self,request):
        user_id = request.GET.get("user_id")
        result = censorship_service.getPostValidByUser(user_id)
        return JsonResponse(result, status=200) 
class HeartView(APIView):
    def post(self,request):
        user_id = request.data.get("user_id")
        post_id = request.data.get("post_id")
        result = censorship_service.heartPost(user_id,post_id)
        return JsonResponse(result,status=200)

class getPostById(APIView):
    def get(self,request):
        post_id = request.GET.get("post_id")
        result = censorship_service.getPostById(post_id)
        return JsonResponse(result,status=200)

class getPostAwaitingCensorship(APIView):
    def get(self,request):
        result  = censorship_service.getPostAwaitingCensorship()
        return JsonResponse(result, status=200)
class getCensorshipbyPostId(APIView):
    def get(self,request):
        post_id = request.GET.get("post_id")
        result  = censorship_service.getCensorshipbyPostId(post_id)
        return JsonResponse(result, status=200)
    def patch(self,request):
        post_id = request.data.get("post_id")
        status = request.data.get("status")
        result  = censorship_service.updateCensorshipStatus(post_id,status)
        return JsonResponse(result, status=200)