from django.urls import path
from articles import views

urlpatterns = [
    path("music/api", views.MusicApiDetail.as_view(), name="music_api"),
    path("music/api/token", views.GetMusicAccessToken.as_view(),name="music_api_token"),
    path("music/api/search", views.MusicSearchApiDetail.as_view(),name="music_api_search"),
    path("music/api/genre", views.MusicGenreApiDetail.as_view(),name="music_api_genre"),
    path("music/api/music-id-search", views.MusicIdSearch.as_view(),name="music_api_id_search"),
    path("save_music", views.SaveMusic.as_view(),name="save_music"),
    # 메인 게시글 작성(POST), 불러오기(GET)
    path('', views.ArticleView.as_view(), name='article_main'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),  # 특정 게시글 불러와, 수정, 삭제(GET,PUT,DEL)
    path('genre/', views.GenreView.as_view(), name='genre'),                        # 장르 조회 / 생성
    path('genre/<int:genre_id>/', views.GenreView.as_view(), name='genre_update'),  # 장르 수정 / 삭제
    path('<int:article_id>/genre/', views.MusicGenreTableView.as_view(), name='article_genre'),  # 게시글 장르 조회 
    path('genre/restore/', views.GenreRestoreView.as_view(), name='genre_restore'), # 장르 복구
]
