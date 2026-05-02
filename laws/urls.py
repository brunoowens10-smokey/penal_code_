from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("title/<int:title_id>/", views.title_detail, name="title_detail"),
    path("chapter/<int:chapter_id>/", views.chapter_detail, name="chapter_detail"),
    path("article/<int:article_id>/", views.article_detail, name="article_detail"),
    path("search/", views.search, name="search"),
    path("assistant/", views.assistant, name="assistant"),
    path("language/", views.set_language, name="set_language"),
]
