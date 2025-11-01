"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from user_auth import urls as auth_urls
from users import urls as user_urls
from post import urls as post_urls
from chat import urls as chat_urls
from friend import urls as friend_urls
from comments import urls as comment_urls
from notifications import urls as notification_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(auth_urls.urlpatterns)), 
    path('users/', include(user_urls.urlpatterns)),
    path('post/', include(post_urls.urlpatterns)),
    path('chat/',include(chat_urls.urlpatterns)),
    path('friend/',include(friend_urls.urlpatterns)),
    path('comment/',include(comment_urls.urlpatterns)),
    path('notifications/',include(notification_urls.urlpatterns)),
]
