from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from dj_rest_auth.registration.views import VerifyEmailView

from users import views

urlpatterns = [
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # 일반 회원 회원가입
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # 유효한 이메일이 유저에게 전달
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', views.ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('active/',views.UserActiveArticleView.as_view(),name='active')
]
