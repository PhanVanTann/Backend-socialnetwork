from django.shortcuts import render
from .service import CommentsService
from django.http import JsonResponse
from rest_framework.views import APIView

comment_service = CommentsService()
# Create your views here.
class CommentsView(APIView):
    def post(self,request):
        
        result = comment_service.create_comment(request.data)
        return JsonResponse(result,status = 201)
    def get(self,request):
        postId = request.GET.get('postId')
        print("postId",postId)
        result = comment_service.getAllCommentsFromPostID(postId)
        return JsonResponse(result,status = 200)