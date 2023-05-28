from django.urls import path
from comments import views


urlpatterns = [
    path('<int:article_id>/comment/', views.CommentView.as_view(), name="comment_view"),                    # 게시글 댓글 가져오기, 생성
    path('<int:article_id>/comment/<int:comment_id>/', views.CommentView.as_view(), name="comment_view"),   # 댓글 수정, 삭제
    path('emoticon/', views.EmoticonView.as_view(), name="emoticon"),                                       # 이모티콘 전부 다 가져오기
    path('emoticon/images/', views.EmoticonImagesView.as_view(), name="emoticon_images"),                   # 이모티콘 이미지 전부 다 가져오기
    path('emoticon/detail/<int:emoticon_id>/', views.EmoticonDetailView.as_view(), name="emoticon_detail"), # 이모티콘 자세히 보기 / 수정
    path('emoticon/<int:user_id>/', views.UserBoughtEmoticonView.as_view(), name="user_emoticon"),          # 유저가 가진 이모티콘 가져오기
    path('emoticon/<int:user_id>/base/', views.UserBaseEmoticonView.as_view(), name="user_base_emoticon"),  # 기본 이모티콘 가져오기
    path('test/', views.testView.as_view(), name="test"),  # test
]
