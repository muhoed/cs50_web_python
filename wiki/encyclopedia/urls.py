from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("article/<str:entry>/", views.show_entry, name="show_entry"),
    path("search/", views.search_result, name="search"),
    path("create/", views.create_page, name="create"),
    path("edit/<str:entry>", views.edit_page, name="edit"),
    path("random/", views.show_random, name="rand")
]
