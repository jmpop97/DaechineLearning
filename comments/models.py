from django.db import models
from users.models import CommonModel
from users.models import User
from articles.models import Article

# Create your models here.

# 이모티콘 모델
class Emoticon(CommonModel):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)                   # User 삭제시 이모티콘은 유지
    title = models.CharField("이모티콘 제목", max_length=50)
    # CommonModel의 db_status 상태로 수정 가능/불가능 여부 판단예정

    def __str__(self):
        return self.title

# 이모티콘 이미지 모델
class EmoticonImages(CommonModel):
    emoticon = models.ForeignKey(Emoticon, on_delete=models.CASCADE, related_name='images')     # 
    image = models.ImageField("이미지", upload_to='%Y/%m/', blank=True, default=None)           # 이미지 blank 여부/ upload to 설정 확인하기

    def __str__(self):
        return self.emoticon.title

# 이모티콘 구매자 테이블?
class UserBoughtEmoticon(CommonModel):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emoticon_list')
    emoticon = models.ForeignKey(Emoticon, on_delete=models.CASCADE, related_name='sold_emoticon')

    def __str__(self):
        return f'이모티콘: {self.emoticon}//사용자: {self.buyer}'

# 댓글 모델
class Comment(CommonModel):
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    music = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField("댓글 내용", blank=True)
    use_emoticon = models.ForeignKey(EmoticonImages, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.comment
