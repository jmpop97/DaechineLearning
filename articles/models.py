from django.db import models
from users.models import CommonModel, User
# Create your models here.

class Music(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_id = models.CharField("MusicId", max_length=50)
    name = models.CharField("Name", max_length=50)
    artist = models.CharField("Artist",max_length=50)
    album = models.CharField("Album",max_length=50)
    images = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    music_id = models.ForeignKey(Music,on_delete=models.CASCADE,related_name="musicId")
    images = models.CharField(max_length=256)
    title = models.CharField("Title", max_length=50, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    music_search = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# 장르 모델
class Genre(CommonModel):
    # creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField("장르", max_length=50, unique=True)

    def __str__(self):
        return self.name

# 장르 - 게시글 테이블
class MusicGenreTable(CommonModel):
    music = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='genre_list')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='music_list')

    def __str__(self):
        return f'{self.music}//{self.genre}'
        
