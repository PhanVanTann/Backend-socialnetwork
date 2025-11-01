from django.urls import path
from .views import *

urlpatterns = [
    path('roomchat/', ChatView.as_view(),name="chatroom"),
    path('message/',MessageView.as_view(),name="message"),
    path('historyreceiver/',HistoryChat.as_view(),name="historyreceiver")
]