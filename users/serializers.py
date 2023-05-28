from rest_framework import serializers
from users.models import User, UserActiveArticle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# 토큰 정보 커스터마이징
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        
        return token
#
class UserActiveArticleViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActiveArticle
        fields = ("listen_rate","article",)