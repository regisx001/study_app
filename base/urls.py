from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),

    path("profile/<str:id>", views.profilePage, name="user-profile"),

    path("", views.home, name="home"),
    path("room/<int:id>", views.room, name="room"),


    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<int:id>", views.updateRoom, name="update-room"),
    path("delete-room/<int:id>", views.deleteRoom, name="delete-room"),


    path("delete-message/<int:id>", views.deleteMessage, name="delete-message"),


    path("update-user/", views.updateUser, name="update-user"),

    path("activity/", views.activityPage, name="activity"),
    path("topics/", views.topicsPage, name="topics"),
]
