from django.db import models
from rank.models import GameUser

class User(models.Model):

    kakao_id  = models.CharField(max_length = 50, null = True)
    email     = models.EmailField(max_length = 200)
    picture   = models.URLField()
    game_user = models.OneToOneField(GameUser, on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.kakao_id
