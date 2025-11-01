from django.urls import path,include
from .views import *
urlpatterns = [
    path('', FriendView.as_view(), name='craete_flower'),
    path('list/',ListFriendView.as_view(),name="list_friend"),
    path('isfriend/',IsFriendView.as_view(),name="isfriend")
] 