from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from comments.serializers import CommentSerializer, CommentCreateSerializer,\
EmoticonSerializer, EmoticonImagesSerializer, EmoticonCreateSerializer
from comments.models import Comment, Emoticon, EmoticonImages, UserBoughtEmoticon


# Create your views here.

# music 댓글
class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 댓글 가져오기
    def get(self, request, article_id):
        comment = Comment.objects.filter(music=article_id, db_status=1)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 생성
    def post(self, request, article_id):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save(writer=request.user, music=article_id)
            serializer.save(writer=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 수정
    def put(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)
        if request.user == comment.writer:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    # 댓글 삭제
    def delete(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)

        # 작성자만 삭제 가능하게
        if request.user == comment.writer:
            comment.db_status = 2
            comment.save()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

# 이모티콘
class EmoticonView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # 이모티콘 전부 다 가져오기
    def get(self, request):
        emoticon = Emoticon.objects.filter(db_status=1)
        serializer = EmoticonSerializer(emoticon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 이모티콘 제작
    def post(self, request):
        if 'images' in request.data:
            serializer = EmoticonCreateSerializer(data=request.data, context={"images":request.data.getlist("images")})
        else:
            serializer = EmoticonCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 이모티콘 자세히 보기
class EmoticonDetailView(APIView):
    def get(self, request, emoticon_id):
        emoticon = get_object_or_404(Emoticon, id=emoticon_id, db_status=1)
        serializer = EmoticonSerializer(emoticon)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, emoticon_id):
        # 이모티콘 수정
        emoticon = get_object_or_404(Emoticon, id=emoticon_id)
        remove_ids = request.data['remove_images']
        ids_list = remove_ids.split(",")

        if request.user == emoticon.creator:
            if 'images' in request.data:
                serializer = EmoticonSerializer(emoticon, data=request.data, context={"images":request.data.getlist("images")})
            else:
                serializer = EmoticonSerializer(emoticon, data=request.data)

            if serializer.is_valid():
                serializer.save()
                # 제거할 이미지가 있으면 제거해주는 코드
                if ids_list[0] != '':
                    for id in ids_list:
                        k = EmoticonImages.objects.get(id=id)
                        k.db_status = 2
                        k.save()
                
                # 이미지 업로드시 생성, 이모티콘에 추가
                images_data = serializer.context.get('images', None)
                if images_data:
                    for image_data in images_data:
                        EmoticonImages.objects.create(emoticon=emoticon, image=image_data)

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, emoticon_id):
        emoticon = get_object_or_404(Emoticon, id=emoticon_id, db_status=1)

        # 작성자만 삭제 가능하게
        if request.user == emoticon.creator:
            emoticon.db_status = 2
            emoticon.save()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

# 이모티콘 이미지 다 가져오기
class EmoticonImagesView(APIView):
    def get(self, request):
        emoticon_images = EmoticonImages.objects.filter(db_status=1)
        serializer = EmoticonImagesSerializer(emoticon_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 유저가 가진 이모티콘 조회 / 선택
class UserBoughtEmoticonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        emoticon_list = UserBoughtEmoticon.objects.filter(buyer=user_id, db_status=1)
        emoticons = []
        for a in emoticon_list:
            emoticons.append(a.emoticon)
        serializer = EmoticonSerializer(emoticons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, user_id):
        try:
            emoticon = Emoticon.objects.get(id=int(request.data['emoticon']))
            user = request.user
            select = get_object_or_404(UserBoughtEmoticon, buyer=user, emoticon=emoticon)
            if select:
                select.db_status = 1
                select.save()
                return Response(status=status.HTTP_200_OK)
        except:
            emoticon = Emoticon.objects.get(id=int(request.data['emoticon']))
            user = request.user
            UserBoughtEmoticon.objects.create(buyer=user, emoticon=emoticon)
            return Response(status=status.HTTP_200_OK)
    
    def delete(self, request, user_id):
        select = get_object_or_404(UserBoughtEmoticon, buyer=user_id, emoticon=int(request.data['emoticon']))
        if request.user == select.buyer:
            select.db_status = 2
            select.save()
            return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

# 기본 이모티콘 저장
try:
    if Emoticon.objects.filter(title="기본"):
        pass
    else:
        base_emoticon = Emoticon(title='기본')
        base_emoticon.save()
        input_images = ["/base_emoticon/기본1.png", "/base_emoticon/기본2.jfif", "/base_emoticon/기본3.gif", "/base_emoticon/기본4.png", "/base_emoticon/기본5.png", "/base_emoticon/기본6.gif", "/base_emoticon/기본7.png", "/base_emoticon/기본8.png"]
        for a in input_images:
            temp = EmoticonImages(emoticon=base_emoticon, image=a)
            temp.save()
except:
    pass

# 기본 이모티콘 가져오기
class UserBaseEmoticonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        base_emoticon = get_object_or_404(Emoticon, title='기본')
        serializer = EmoticonSerializer(base_emoticon)
        return Response(serializer.data, status=status.HTTP_200_OK)

class testView(APIView):
    def post(self, request):
        return Response(status=status.HTTP_200_OK)
