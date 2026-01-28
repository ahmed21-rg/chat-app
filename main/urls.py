from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import chat_test, UserLoginView



urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    
    path("login/", views.UserLoginView.as_view()),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    
    #path( "", views.login_page, name="login_page"),

    path("me/", views.MeView.as_view()),
    path("messages/<user_id>/", views.MyInboxView.as_view()),
    path("rooms/<int:room_id>/messages/", views.GetMessageView.as_view()), # get messages in a room older 
    path("rooms/<int:room_id>/send/", views.SendMessageView.as_view()),    # send message to a room
    path("rooms/private/<int:user_id>/", views.GetOrCreatePrivateRoomView.as_view()),
    path("profile/<int:pk>/", views.UpdateProfileView.as_view()),
    path("search/<str:username>/", views.SearchUserView.as_view()),
    path("users/", views.SearchUserView.as_view()),
    path("groups/create/", views.CreateGroupView.as_view()),
    path("groups/", views.GroupListView.as_view()),
    path("groups/<int:room_id>/add-member/", views.AddGroupMemberView.as_view()),
    path("groups/<int:room_id>/remove-member/<int:user_id>/", views.RemoveGroupMemberView.as_view()),
    path("rooms/<int:room_id>/upload/", views.FileUploadView.as_view()),

    path("chat/", chat_test),
]   