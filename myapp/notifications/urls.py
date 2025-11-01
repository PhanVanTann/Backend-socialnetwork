from django.urls import path,include
from .views import *
urlpatterns = [
    path('', NotificationView.as_view(), name='notification'),
] 