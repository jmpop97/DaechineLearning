from rest_framework import serializers
from articles.models import Article, Genre, Music, MusicGenreTable

# serializer는 전부 검색부분용 입니다. 
# 노래제목,가수, 해당 곡 앨범자켓 
class MusicSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    id = serializers.CharField()

    def get_name(self, obj):
        return obj.get('name')

    def get_artist(self, obj):
        artists = obj.get('artists', [])
        if artists:
            return artists[0].get('name')
        else:
            return None

    def get_album(self, obj):
        album = obj.get('album', {})
        return {
            'name': album.get('name'),
            'id': album.get('id'),
            'release_date': album.get('release_date'),
            'images': album.get('images'),
            'artist_name': album.get('artists', [{}])[0].get('name'),
        }


class ImageSerializer(serializers.Serializer):
    url = serializers.URLField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()


class ArtistSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    href = serializers.CharField()
    images = ImageSerializer(many=True, required=False, read_only=True)


class ArticleListSerializer (serializers.ModelSerializer):
    """ 게시글 직렬화 """
    user = serializers.SerializerMethodField()
    music_id = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()

    def get_genre(self, article):
        qs = MusicGenreTable.objects.filter(db_status=1, music=article)
        genre_name = []
        for a in qs:
            genre_name.append(a.genre)
        # qs = 게시글 장르 리스트
        serializer = GenreSerializer(instance=genre_name, many=True)
        return serializer.data
    def get_user(self, obj):
        return obj.user.username
    def get_music_id(self, obj):
        return obj.music_id.name
    
    class Meta:
        model = Article
        fields = "__all__"


class ArticleCreateSerializer (serializers.ModelSerializer):
    """ 생성, 수정 게시글 데이터 직렬화 """

    class Meta:
        model = Article
        fields = "__all__"


class ArticleDetailSerializer (serializers.ModelSerializer):
    """ 상세 게시글 직렬화 """

    class Meta:
        model = Article
        fields = '__all__'
        
# 장르
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

# music 데이터 받는용
class MusicGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = '__all__'
