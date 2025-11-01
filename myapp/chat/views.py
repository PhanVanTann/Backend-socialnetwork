from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
from .services import ChatService, MessageService
chatservice = ChatService()
messageService = MessageService()
# Create your views here.
class ChatView(APIView):
    def post(self,request):
        user_id1 = request.data.get('user_id1')
        user_id2 = request.data.get('user_id2')
        result = chatservice.create_roomchat(user_id1,user_id2)
        return JsonResponse(result,status = 201)
class MessageView(APIView):
    def post(self,request):
        room_id =request.data.get('room_id')
        send_id = request.data.get('send_id')
        receiver_id = request.data.get('receiver_id')
        text = request.data.get('text')
        media  = request.FILES.get('media') 
        result = messageService.create_message(room_id,send_id,receiver_id,text,media)
        return JsonResponse(result,status=201)
    def get(self,request):
        room_id = request.GET.get('room_id')
        user_id = request.GET.get('user_id')
        result = messageService.get_history_chat_byuser(room_id,user_id)
        return JsonResponse(result,status = 200)
class HistoryChat(APIView):
    def get(self,request):
        room_id = request.GET.get('room_id')
        user_id = request.GET.get('user_id')
        result = messageService.get_history_chat_byreceiver(room_id,user_id)
        return JsonResponse(result,status = 200)