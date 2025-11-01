from django.urls import path,include
from .views import *
urlpatterns = [
    path('', UserView.as_view(), name='craete_user'),
    path('listuser/',UsersView.as_view(),name='users')

] 