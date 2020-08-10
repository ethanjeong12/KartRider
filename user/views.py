import jwt
import json
import requests

from django.views import View
from django.http import (
    JsonResponse,
    HttpResponse
)

from config.settings import (
    SECRET_KEY,
    ALGORITHM
)

from .models import User
from rank.models import GameUser
from .utils import login_decorator

KAKAO_API = 'https://kapi.kakao.com/v2/user/me'

class SocialLoginView(View):
    def post(self, request):
        try:
            kakao_token         = request.headers['Authorization']
            req_kakao_profile   = requests.get(KAKAO_API,headers = {
                'Authorization' : f'Bearer {kakao_token}'
            })
            profile         = req_kakao_profile.json()
            kakao_email     = profile['kakao_account']['email']
            kakao_id        = profile['properties']['nickname']
            kakao_picture   = profile['properties']['profile_image']

            if User.objects.filter(email = kakao_email).exists():
                token = jwt.encode({'email' : kakao_email}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')
                return JsonResponse({
                    'access_token'      : token,
                    'nickname'          : kakao_id,
                    'profile_image'     : kakao_picture,
                    'email'             : kakao_email
                }, status=200)

            User(
                email           = kakao_email,
                kakao_id        = kakao_id,
                picture         = kakao_picture,
            ).save()

            token = jwt.encode({'email' : kakao_email}, SECRET_KEY, algorithm=ALGORITHM)
            token = token.decode('utf-8')

            return JsonResponse({
                'access_token'      : token,
                'nickname'          : kakao_id,
                'profile_image'     : kakao_picture,
                'email'             : kakao_email
            }, status=200)

        except KeyError:
                return JsonResponse({'Message' : 'INVALID_KEYS'}, status=400)

    @login_decorator
    def get(self, request):
        return JsonResponse({
            'email'         : request.userinfo.email,
            'nickname'      : request.userinfo.kakao_id,
            'profile_image' : request.userinfo.picture
        }, status = 200)

class ConnectGameuserView(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        try:
            if request.userinfo.game_user_id:
                return JsonResponse({'Message' : '이미 등록된 게임유저가 존재합니다.'}, status=400)
            elif GameUser.objects.filter(nickname=data['nickname']).exists():
                gameuser = GameUser.objects.get(nickname=data['nickname'])
                if User.objects.filter(game_user=gameuser).exists():
                    return JsonResponse({'Message' : '이미 등록된 게임유저'}, status=400)
                user = User.objects.get(id=request.userinfo.id)
                user.game_user = GameUser.objects.get(nickname=data['nickname'])
                user.save()

                return HttpResponse(status=200)
            return JsonResponse({'Message' : '게임유저가 존재하지 않습니다.'}, status=400)

        except KeyError:
            return JsonResponse({'Message' : 'INVALID_KEYS'}, status=400)
