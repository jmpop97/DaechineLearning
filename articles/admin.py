from django.contrib import admin
from articles.models import Article, Music, Genre, MusicGenreTable


# Register your models here.
# class ArticlesAdmin(admin.ModelAdmin):
#     list_display = ['id', 'content', 'created_at']


admin.site.register(Music)
admin.site.register(Genre)
admin.site.register(MusicGenreTable)
# Register your models here.


class ArticlesAdmin(admin.ModelAdmin):

    list_display = ["id", "title", "content", "music_id",]
    list_filter = ["title",]
    fieldsets = []

    search_fields = ["title", "content",]
    ordering = ["title"]
    filter_horizontal = []
    list_display_links = ["id", "title", "content", "music_id",]

admin.site.register(Article, ArticlesAdmin)

