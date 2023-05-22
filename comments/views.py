from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from comments.serializers import CommentSerializer, EmoticonSerializer, EmoticonImagesSerializer
from comments.models import Comment, Emoticon, EmoticonImages, UserBoughtEmoticon


# Create your views here.

# music 댓글
class CommentView(APIView):
    # 댓글 가져오기
    def get(self, request, article_id):
        comment = Comment.objects.filter(music=article_id, db_status=1)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 댓글 생성
    def post(self, request, article_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save(writer=request.user, music=article_id)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 댓글 수정
    def put(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)
        # if request.user == comment.writer:
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({'message':'수정 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    # 댓글 삭제
    def delete(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, db_status=1)

        # 작성자만 삭제 가능하게
        # if request.user == comment.writer:
        comment.db_status = 2
        comment.save()
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        # else:
        #     return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)



# 이모티콘 전부 다 가져오기
class EmoticonView(APIView):
    def get(self, request):
        emoticon = Emoticon.objects.all()
        serializer = EmoticonSerializer(emoticon, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 유저가 가진 이모티콘 가져오기
class UserBoughtEmoticonView(APIView):
    def get(self, request, user_id):
        emoticon_list = UserBoughtEmoticon.objects.filter(buyer=user_id)
        emoticons = []
        for a in emoticon_list:
            emoticons.append(a.emoticon)
        serializer = EmoticonSerializer(emoticons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
