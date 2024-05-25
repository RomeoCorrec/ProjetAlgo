"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', views.index, name='index'),
    path('', views.index, name='deconnexion'),
    path('create-account/', views.create_account, name='create_account'),
    path('login/', views.login_view, name='login'),
    path('main-page/', views.main_page, name='main_page'),
    path('main-page/<str:filter>/', views.main_page, name='main_page_filter'),
    path('profil_page/', views.profil_page, name='profil_page'),
    path('post/', views.post, name='post'),
    path('filter_posts/', views.filter_posts, name='filter_posts'),
    path('modify_profil_page/', views.modify_profil_page, name='modify_profil_page'),
    path('modify_profil/', views.modify_profil, name='modify_profil'),
    path('search-profil/', views.search_profil, name='search_profil'),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/', views.accept_friend_request, name='accept_friend_request'),
    path('private-message-list/', views.private_messages_list, name='private_message_list'),
    path('private-message/<str:friend_username>', views.private_messages_page, name='private_message_page'),
    path('send-private-message/', views.send_private_messages, name='send_private_messages'),
    path('visit-profil/<str:username>', views.visit_profil, name='visit_profil'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('like-post/', views.like_post, name='like_post'),
    path('delete-post/', views.delete_post, name='delete_post'),
    path('group-list/', views.group_list, name='group_list'),
    path('create-group/', views.create_group, name='create_group'),
    path('send-group-message/', views.send_group_messages, name='send_group_messages'),
    path('group-message/<str:group_name>', views.group_messages_page, name='group_messages_page'),
    path('accept-group-invitation/<str:group_name>', views.accept_group_invitation_model, name='accept_group_invitation'),
    path('reject-group-invitation/<str:group_name>', views.reject_group_invitation_model, name='reject_group_invitation'),
]

