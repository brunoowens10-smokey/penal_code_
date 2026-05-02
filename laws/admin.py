from django.contrib import admin
from .models import Article, Chapter, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("number", "name_en")
    search_fields = ("number", "name_en", "name_fr", "name_rw")
    ordering = ("id",)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("number", "name_en", "title")
    list_filter = ("title",)
    search_fields = ("number", "name_en", "name_fr", "name_rw", "title__name_en")
    ordering = ("title_id", "id")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("number", "title_en", "chapter")
    list_filter = ("chapter__title", "chapter")
    search_fields = (
        "number",
        "title_en",
        "content_en",
        "content_fr",
        "content_rw",
        "chapter__name_en",
        "chapter__title__name_en",
    )
    ordering = ("chapter_id", "id")
