
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views, controllers


urlpatterns = [
    #path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("", views.HomePage.as_view(), name="index"),
    path("following", views.FollowingPage.as_view(), name="following"),
    path("profile/<int:pk>", views.ProfileMain.as_view(), name="profile"),
    path("profile/<int:pk>/<str:type>/<int:limit>", views.ListUsers.as_view(), name="user_list"),
    path("profile/detail/<int:pk>", views.ProfileDetail.as_view(), name="profile_detail"),
    path("profile/detail/<int:pk>/update/about", controllers.update_profile_about, name="profile_about"),
    path("profile/detail/<int:pk>/update/avatar", views.upload_avatar, name="profile_avatar"),
    path("profile/follow/<int:pk>", controllers.switch_following_status, name="update_following"),
    path("profile/follow/<int:pk>/followers", controllers.get_followers_counts, name="get_followers_count"),
    path("posts/get/<str:scope>/<int:limit>", views.ListPosts.as_view(), name="posts"),
    path("posts/get/<int:pk>", views.ShowPost.as_view(), name="post"),
    path("posts/viewed/<int:pk>", controllers.mark_post_viewed, name="mark_post_viewed"),
    path("posts/create/", controllers.create_post, name="create_post"),
    path("posts/update/<int:pk>", controllers.update_post, name="update_post"),
    path("posts/reaction/<str:type>/<int:pk>", controllers.post_reaction, name="reaction"),
    path("comments/<int:post_pk>", views.ListComments.as_view(), name="comments"),
    path("comments/<int:post_pk>/create", controllers.create_comment, name="create_comment")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
