from rest_framework import serializers
from comments.models import Comment, Emoticon, EmoticonImages, UserBoughtEmoticon


# 댓글
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, comment):
        return comment.writer.username

    class Meta:
        model = Comment
        fields = "__all__"

# 댓글 생성
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('comment', 'use_emoticon', 'music')

# 이모티콘 이미지들
class EmoticonImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmoticonImages
        fields = ("id", "image", "db_status",)

# 이모티콘
class EmoticonSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, emoticon):
        qs = EmoticonImages.objects.filter(db_status=1, emoticon=emoticon)
        serializer = EmoticonImagesSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Emoticon
        fields = "__all__"

# 이모티콘 생성
class EmoticonCreateSerializer(serializers.ModelSerializer):
    images = EmoticonImagesSerializer(many=True, required=False)

    class Meta:
        model = Emoticon
        fields = "__all__"

    def create(self, validated_data):
        images_data = self.context.get('images', None)
        emoticon = super().create(validated_data)
        if images_data:
            for image_data in images_data:
                EmoticonImages.objects.create(emoticon=emoticon, image=image_data)
        return emoticon

# 유저가 가진 이모티콘
class UserBoughtEmoticonSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBoughtEmoticon
        fields = "__all__"

# 이모티콘 수정용 이미지
class EmoticonImagesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmoticonImages
        fields = ("id", "db_status",)

# 이모티콘 수정용
class EmoticonUpdateSerializer(serializers.ModelSerializer):
    images = EmoticonImagesUpdateSerializer(many=True, required=False)

    class Meta:
        model = Emoticon
        fields = "__all__"
