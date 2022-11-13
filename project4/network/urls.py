
from django.urls import path

from . import views, controllers


urlpatterns = [
    #path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("", views.HomePage.as_view(), name="index"),
    path("profile/<int:pk>", views.ProfileMain.as_view(), name="profile"),
    path("profile/detail/<int:pk>", views.ProfileDetail.as_view(), name="profile_detail"),
    path("following", views.ListFollowing.as_view(), name="following"),
    path("following/<int:pk>/update/<str:action>", views.ModifyFollowing.as_view(), name="update_following"),
    path("posts/get/<str:scope>/<int:limit>", views.ListPosts.as_view(), name="posts"),
    path("posts/get/<int:pk>", views.ShowPost.as_view(), name="post"),
    path("posts/viewed/<int:pk>", controllers.mark_post_viewed, name="mark_post_viewed"),
    path("posts/create/", controllers.create_post, name="create_post"),
    path("posts/update/<int:pk>", controllers.update_post, name="update_post"),
    path("posts/delete/<int:pk>", views.DeletePost.as_view(), name="delete_post"),
    path("posts/reaction/<str:type>/<int:pk>", controllers.post_reaction, name="reaction"),
    path("comments/<int:post_pk>", views.ListComments.as_view(), name="comments"),
    path("comments/<int:post_pk>/<int:comment_pk>", views.CommentDetails.as_view(), name="comment"),
    path("comments/<int:post_pk>/create", controllers.create_comment, name="create_comment"),
    path("comments/<int:post_pk>/update/<int:comment_pk>", views.HomePage.as_view(), name="update_comment"),
    path("comments/<int:post_pk>/delete/<int:comment_pk>", views.HomePage.as_view(), name="delete_comment")
]
