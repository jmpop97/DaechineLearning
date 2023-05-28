import pprint
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from users.models import User
from articles.models import Article , Music, Genre,\
MusicGenreTable
from rest_framework.permissions import IsAuthenticated,\
IsAuthenticatedOrReadOnly
import base64
import requests
from rest_framework.exceptions import ParseError
from articles.serializers import (
    ArticleListSerializer,
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    MusicSerializer,
    ArtistSerializer,
    GenreSerializer,
    MusicGetSerializer,
)
from django.http import JsonResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import my_settings
from apscheduler.schedulers.background import BackgroundScheduler

# 스케줄러 객체 생성
client_credentials_manager = SpotifyClientCredentials(
    client_id=my_settings.SPOTYPY_KEY["music_id"], client_secret=my_settings.SPOTYPY_KEY["music_pw"])
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
client_id = my_settings.SPOTYPY_KEY["music_id"]
client_pw = my_settings.SPOTYPY_KEY["music_pw"]
access_token = ""
scheduler = BackgroundScheduler()
# Create your views here.
# access_token 받아오는 class
class GetMusicAccessToken(APIView):
    def post(self, request, format=None):
        auth_url = 'https://accounts.spotify.com/api/token'

        message = f"{client_id}:{client_pw}"
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        header = {'Authorization': f"Basic {base64_message}"}
        data = {'grant_type': 'client_credentials'}
        res = requests.post(auth_url, headers=header, data=data)
        response_object = res.json()
        access_token = response_object['access_token']

        my_settings.SPOTYPY_KEY["bearer_token"] = access_token
        return Response({'access_token': access_token})

# access_token 받아오는 함수
def get_token():
    global access_token
    auth_url = 'https://accounts.spotify.com/api/token'
    message = f"{client_id}:{client_pw}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    header = {'Authorization': f"Basic {base64_message}"}
    data = {'grant_type': 'client_credentials'}
    res = requests.post(auth_url, headers=header, data=data)
    response_object = res.json()
    access_token = response_object['access_token']
# 자동시작함수 스케줄링사용
get_token()
scheduler.add_job(get_token, 'interval', minutes=59)
# 스케줄링 시작
scheduler.start()


class MusicGenreApiDetail(APIView):  # 음악장르 전체목록 조회
    def get(self, request):
        url = f"https://api.spotify.com/v1/recommendations/available-genre-seeds"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return JsonResponse(data, safe=False)

#음악검색api 사용해서 음악검색 class
class MusicSearchApiDetail(APIView):
    def post(self, request, format=None):
        query = request.data.get('query', None)  # 검색어는 필수로 작성해야 함.
        limit = request.data.get('limit', 10)  # 기본값은 10이라 하고 작성 가능하게 만들 예정
        # 앨범으로도 검색 가능한데 이건 트랙으로 해둬도 될 거 같습니다.
        search_type = request.data.get('type', 'track')

        if not access_token:
            get_token()

        if not query:
            raise ParseError('검색어를 입력해주세요')

        search_url = f'https://api.spotify.com/v1/search?q={query}&type={search_type}&limit={limit}'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            tracks = data.get('tracks', {}).get('items', [])
            artists = data.get('artists', {}).get('items', [])
            tracks_serializer = MusicSerializer(tracks, many=True)
            artists_serializer = ArtistSerializer(artists, many=True)
            return Response({
                'tracks': tracks_serializer.data,
                'artists': artists_serializer.data,
            })
        else:
            return Response({'message': '트랙을 불러 올 수 없습니다.'}, status=response.status_code)

class SaveMusic(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, format=None):
        user = request.data.get('user', None)
        name = request.data.get('name', None)
        artist = request.data.get('artist', None)
        album = request.data.get('album', None)
        music_id = request.data.get('music_id', None)
        images = request.data.get('images', None)
        # Music 모델에 데이터 저장
        music = Music.objects.create(user=User.objects.get(id=user), name=name, artist=artist, album=album, music_id=music_id, images=images)
        music.save()
        temp = Music.objects.get(id=music.pk, name=name, artist=artist, album=album, music_id=music_id, images=images)
        serializer = MusicGetSerializer(temp)

        return Response(serializer.data, status=status.HTTP_200_OK)
# music id로 검색
class MusicIdSearch(APIView):
    def post(self, request,):
        music_id = request.data.get('music_id', None)
        search_url = f'https://api.spotify.com/v1/tracks/{music_id}'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            preview_music = data['preview_url']
            return Response({'preview_url': preview_music})
        else:
            return Response({'message': '트랙을 찾을 수 없습니다.'}, status=response.status_code)

# 음악 api2023년 리스트 인기도순으로 정렬
class MusicApiDetail(APIView):
    def get(self, request):
        track_info = []
        for i in range(0, 1000, 50):
            track_results = sp.search(
                q='year:2023', type='track', limit=50, offset=i)
            for idx, t in enumerate(sorted(track_results['tracks']['items'], key=lambda x: x['popularity'], reverse=True), start=i+1):
                try:
                    album_data = {
                        '장르': t['album']['seed_genres'],
                        'id': t['album']['id'],
                        'popularity': t['popularity'],
                        '앨범자켓': t['album']['images'],
                        '곡명': t['album']['name'],
                        '미리듣기': t['preview_url'],
                        '가수': [{
                            '스포티파이_url': a['external_urls']['spotify'],
                            '세부정보_구독이안돼서안보임': a['href'],
                            'id': a['id'],
                            '가수이름or팀이름': a['name'],
                            '직업?유형?': a['type'],
                            '스포티파이자체_주소?키값?': a['uri']} for a in t['album']['artists']],
                    }
                except KeyError:
                    album_data = {
                        'id': t['album']['id'],
                        'popularity': t['popularity'],
                        'rank': idx,
                        '장르': None,
                        '앨범자켓': t['album']['images'],
                        '곡명': t['album']['name'],
                        '미리듣기': t['preview_url'],
                        '가수': [{
                            '스포티파이_url': a['external_urls']['spotify'],
                            '세부정보_구독이안돼서안보임': a['href'],
                            'id': a['id'],
                            '가수이름or팀이름': a['name'],
                            '직업?유형?': a['type'],
                            '스포티파이자체_주소?키값?': a['uri']} for a in t['album']['artists']],
                    }
                result_data = {
                    'album': album_data,
                }
                track_info.append(result_data)
        return JsonResponse(track_info, safe=False)


class ArticleView(APIView):# serializer 수정? 꾸미기?
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'genre' in request.data:
            serializer = ArticleCreateSerializer(data=request.data, context={"genre":request.data.getlist("genre")})
        else:
            serializer = ArticleCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            article = Article.objects.get(id=serializer.data['id'])
            for a in request.data.getlist("genre"):
                genre_get = Genre.objects.get(id=int(a))
                MusicGenreTable.objects.create(music=article, genre=genre_get)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ArticleDetailView(APIView):
    def get(self, request, pk):
        article = get_object_or_404(Article, id=pk)
        serializer = ArticleListSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        article = get_object_or_404(Article, id=pk)
        serializer = ArticleCreateSerializer(article, data=request.data)
        if request.user == article.user:
            serializer = ArticleCreateSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        article = get_object_or_404(Article, id=pk)
        if request.user == article.user:
            article.delete()
            return Response("삭제되었습니다.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이없습니다.", status=status.HTTP_403_FORBIDDEN)

# 장르 생성 / 조회 / 수정 / 삭제
input_genre = ["acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal", "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop", "chicago-house", "children", "chill", "classical", "club", "comedy", "country", "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk", "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop", "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore", "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode", "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop", "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep", "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop", "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"]
for a in input_genre:
    try:
        temp = Genre(name=a)
        temp.save()
    except:
        pass

class GenreView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request):
        genre = Genre.objects.filter(db_status=1).order_by('name')
        serializer = GenreSerializer(genre, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 수정권한 등록한사람한테?
    def put(self, request, genre_id):
        genre = get_object_or_404(Genre, id=genre_id, db_status=1)
        if request.user == genre.creator:
            serializer = GenreSerializer(genre, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    # 장르 삭제
    def delete(self, request, genre_id):
        genre = get_object_or_404(Genre, id=genre_id, db_status=1)

        # 작성자만 삭제 가능하게
        if request.user == genre.creator:
            genre.db_status = 2
            genre.save()
            self.genre_delete_func(genre)
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

    # 장르 삭제시 게시글-장르 테이블 같이 삭제처리
    def genre_delete_func(self, genre):
        article_genre = MusicGenreTable.objects.filter(genre=genre)
        for a in article_genre:
            a.db_status = 2
            a.save()
    
    # 장르 복구시 게시글-장르 테이블 같이 복구 
    # 따로 프론트에서 구현해서 메소드 사용 or admin 페이지 커스텀해서 복구
    def genre_restore_func(genre):
        article_genre = MusicGenreTable.objects.filter(genre=genre)
        for a in article_genre:
            a.db_status = 1
            a.save()

# 게시글 장르 선택 / 조회
class MusicGenreTableView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, article_id):
        genre_list = MusicGenreTable.objects.filter(music=article_id, db_status=1).order_by('genre__name')
        genres = []
        for a in genre_list:
            genres.append(a.genre)
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        # 추가할 장르id를 리스트로 받아서?
        article = get_object_or_404(Article, id=article_id, db_status=1)
        select_genre = request.data['select_genre']
        if request.user == article.writer:
            for a in select_genre:
                add_genre = get_object_or_404(Genre, id=a, db_status=1)
                saved_genre = MusicGenreTable.objects.filter(music=article, genre=add_genre, db_status=1)
                if saved_genre:
                    pass
                else:
                    MusicGenreTable.objects.create(music=article, genre=add_genre)
            return Response({"message": "저장 완료했습니다!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        article = get_object_or_404(Article, id=article_id, db_status=1)
        del_genres = request.data['del_genres']
        if request.user == article.writer:
            for a in del_genres:
                del_genre = get_object_or_404(Genre, id=a, db_status=1)
                saved_genre = get_object_or_404(MusicGenreTable, music=article, genre=del_genre, db_status=1)
                if saved_genre:
                    saved_genre.db_status=2
                    saved_genre.save()
                else:
                    pass
            return Response({"message": "삭제 완료했습니다!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

# 장르 복구 / 게시글-장르 테이블 같이 복구
class GenreRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        restore_name = request.data['name']
        genre = get_object_or_404(Genre, name=restore_name, db_status=2)
        serializer = GenreSerializer(genre, data=request.data)
        if serializer.is_valid():
            serializer.save()
            restore_table = MusicGenreTable.objects.filter(genre=genre, db_status=2)
            for a in restore_table:
                a.db_status = 1
                a.save()
            return Response({"message": "복구 완료했습니다!"}, status=status.HTTP_200_OK)
        # else:
        #     return Response({'message':'수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
