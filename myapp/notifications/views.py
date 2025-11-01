from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .services import NotificationsService
notification_service = NotificationsService()

# Create your views here.
class NotificationView(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")
        if not user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)
        result = notification_service.list_notifications(user_id)
        return JsonResponse(result, status=200)
    def patch(self, request):
        notification_id = request.data.get("notification_id")
        user_id = request.data.get("user_id")
        if not notification_id and not user_id:
            return JsonResponse({"error": "notification_id and user_id is required"}, status=400)
        result = notification_service.mark_as_read(user_id,notification_id)
        return JsonResponse(result, status=200)
    