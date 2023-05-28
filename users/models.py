# step 1 : 유저모델 구현하기 (유저에게 필요한 정보를 가져오기)

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models



class CommonModel(models.Model):
    db_status_choice = [
        (1, 'active'),
        (2, 'delete'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    db_status = models.PositiveIntegerField(
        choices=db_status_choice, default=1)

    class Meta:
        abstract = True
        # class Meta 를 선언함으로써, 다른 모델들이 상속 받을수 있는 모델이 됨

# custom user model 사용 시 UserManager 클래스와 create_user, create_superuser 함수가 정의되어 있어야 함


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    # python manage.py createsuperuser 사용 시 해당 함수가 사용됨

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            username=username,
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    # User Email (Required)
    email = models.EmailField("email", max_length=256, unique=True)
    # User Username
    username = models.CharField("username", max_length=20, unique=True)
    # User Password (Required)
    password = models.CharField("Password", max_length=256)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email',]

    objects = UserManager()  # Necessary when creating custom user

    def __str__(self):
        return f"{self.username}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


from articles.views import Article
class UserActiveArticle(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_active_list')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='user_active_list')
    # article = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='music_active_list')
    listen_rate = models.DecimalField(max_digits=9,decimal_places=8)

