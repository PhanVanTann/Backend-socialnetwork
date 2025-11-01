
from django.urls import path,include
from .views import *
urlpatterns = [
    path('verifyEmail/', EmailView.as_view(), name='verify_email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('googleLogin/', GoogleLoginView.as_view(), name='google_login'),
    path('refresh-token/',AuthView.as_view(),name="refresh-token" )

] 