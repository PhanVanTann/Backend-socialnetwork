from django.urls import path,include
from .views import *
urlpatterns = [
    path('', CommentsView.as_view(), name='craete_comment'),
] 