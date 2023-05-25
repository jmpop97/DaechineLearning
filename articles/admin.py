from django.contrib import admin
from .models import Article, Genre, MusicGenreTable

# Register your models here.
# class ArticlesAdmin(admin.ModelAdmin):
#     list_display = ['id', 'content', 'created_at']


admin.site.register(Article)
admin.site.register(Genre)
admin.site.register(MusicGenreTable)
