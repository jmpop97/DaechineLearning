from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from my_settings import EMAIL
from users.models import User,UserActiveArticle
from articles.models import MusicGenreTable
import speech_recognition as sr
import math
from users.serializers import UserActiveArticleViewSerializer
from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_framework import permissions
from datetime import datetime, timedelta

# 이메일 인증 확인 view
class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # A React Router Route will handle the failure scenario
        return HttpResponseRedirect('/') # 인증성공

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                # A React Router Route will handle the failure scenario
                return HttpResponseRedirect('/') # 인증실패
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs
    
class SoundAI(APIView):
    def post(self, request):
        audios=request.data['blob']
        Recognizer = sr.Recognizer()  # 인스턴스 생성
        mic = sr.AudioFile(audios)
        with mic as source:  # 안녕~이라고 말하면
            audio = Recognizer.listen(source)
        try:
            data = Recognizer.recognize_google(audio, language="ko")
        except:
            data=""
        return Response({"message":data}, status=status.HTTP_200_OK)

class UserActiveArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = UserActiveArticleViewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#유사한 사람
def update_data():
    today=datetime.today()
    str_today=today.strftime("%Y-%m-%d")
    yesterday = datetime.today() - timedelta(1)
    str_yesterday=yesterday.strftime("%Y-%m-%d")
    users=UserActiveArticle.objects.filter(listen_rate__gt=0.1,created_at__range=[str_yesterday,str_today]).values_list("user")
    users=list(set(users))
    user_genre={1: {'acoustic': 0.1, 'afrobeat': 10, 'alt-rock': 10}, 3: {'acoustic': 12, 'afrobeat': 13, 'alt-rock': 11}}
    for user in users:
        datas=UserActiveArticle.objects.filter(user=user[0],listen_rate__gt=0.1,created_at__range=["2023-05-26","2023-05-27"]).order_by("user")

        genre_dic=user_genre.get(user[0],{})
        #기존 데이터 0.9배
        for genre in genre_dic:
            genre_dic[genre]*=0.9

        #추가데이터
        for data in datas:
            genres=MusicGenreTable.objects.filter(music=data.article)
            for genre in genres:
                genre_dic[genre.genre.name]=genre_dic.get(genre.genre.name,0)+1
                pass
        if genre_dic!={}:
            user_genre[user[0]]=genre_dic

def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

def make_similar_user(user_genre,limit_n):
    users=combinations(user_genre, 2)  # 조합
    point_dic={}
    #취향벡터의 길이
    user_len_dic={}
    for user_name in user_genre:
        user_len_dic[user_name]=0
        for n in user_genre[user_name].values():
            user_len_dic[user_name]+=n*n
        user_len_dic[user_name]=math.sqrt(user_len_dic[user_name])
    #유사정도 측정
    for user_1,user_2 in users:
        point_dic[(user_1,user_2)]=0
        if user_1 < user_2:
            small_genre=user_genre[user_1]
        else:
            small_genre=user_genre[user_2]

        for genre_love in small_genre:

            point_dic[(user_1,user_2)]+=user_genre[user_1].get(genre_love,0)*user_genre[user_2].get(genre_love,0)\
                                    /user_len_dic[user_1]/user_len_dic[user_2]
    #최대인사람 5명 뽑기
    similar_users={}
    sorted_dict = sorted(point_dic.items(), key = lambda item: item[1],reverse= True)

    for user_name in user_genre:
        similar_users[user_name]=[]

    for (user1,user2),similar_rate in sorted_dict:
        if len(similar_users[user1])<limit_n:
            similar_users[user1]+=[user2]
        if len(similar_users[user2])<limit_n:
            similar_users[user2]+=[user1]
    #similar_users 유사한 사람