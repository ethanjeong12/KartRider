import json
import jwt

from django.test import (
    TestCase,
    Client,
)
from unittest.mock import (
    patch,
    MagicMock
)
from config.settings import (
    SECRET_KEY,
    ALGORITHM
)
from .models import User
from rank.models import GameUser

class SocialLoginTest(TestCase):
    def setUp(self):
        User.objects.create(
            email           = 'test@test.com',
            kakao_id        = 'test',
            picture         = 'http://k.kakaocdn.net/dn/5w8QS/btqCrOP9kx6/XcCLekEj4OrEbCncK7CLiK/img_640x640.jpg'
        )
    def tearDown(self):
        User.objects.filter(email='test@test.com').delete()

    @patch('user.views.requests')
    def test_login_pass(self, mocked_request):

        class MockedResponse:
            def json(self):
                return {
                    'kakao_account' : {
                        'email' : 'test@test.com'
                    },
                    'properties' : {
                        'nickname'      : 'test',
                        'profile_image' : 'http://k.kakaocdn.net/dn/5w8QS/btqCrOP9kx6/XcCLekEj4OrEbCncK7CLiK/img_640x640.jpg'
                    }
                }

        mocked_request.get = MagicMock(return_value = MockedResponse())

        kakao_id = MockedResponse().json()['properties']['nickname']
        kakao_picture = MockedResponse().json()['properties']['profile_image']
        kakao_email = MockedResponse().json()['kakao_account']['email']

        client  = Client()
        headers = {
            'HTTP_Authorization'    : '',
            'content_type'          : 'application/json'
        }
        response = client.post('/user/login', **headers)
        token = response.json()['access_token']

        self.assertEqual(response.json(), {
            'access_token'  : token,
            'nickname'      : kakao_id,
            'profile_image' : kakao_picture,
            'email'         : kakao_email
        })
        self.assertEqual(response.status_code, 200)

    @patch('user.views.requests')
    def test_login_fail(self, mocked_request):

        class MockedResponse:
            def json(self):
                return {
                    'account' : {
                        'email' : 'test@test.com'
                    },
                    'properties' : {
                        'nickname'  : 'test',
                        'image'     : 'http://k.kakaocdn.net/dn/5w8QS/btqCrOP9kx6/XcCLekEj4OrEbCncK7CLiK/img_640x640.jpg'
                    }
                }

        mocked_request.get = MagicMock(return_value = MockedResponse())

        client  = Client()
        headers = {
            'HTTP_Authorization'    : '',
            'content_type'          : 'application/json'
        }
        response = client.post('/user/login', **headers)

        self.assertEqual(response.json(),{
            'Message' : 'INVALID_KEYS'
        })
        self.assertEqual(response.status_code, 400)

class ConnectGameuserTest(TestCase):
    def setUp(self):
        GameUser.objects.create(
            access_id='100',
            nickname='test100'
        )
        User.objects.create(
            email           = 'ihavegameuser@test.com',
            picture         = 'google.com',
            game_user_id    = GameUser.objects.get(access_id='100').id
        )
        GameUser.objects.create(
            access_id='101',
            nickname='test101'
        )
        User.objects.create(
            email = 'idonthavegameuser@test.com',
            picture= 'google.com'
        )
    def tearDown(self):
        GameUser.objects.get(access_id='100').delete()
        GameUser.objects.get(access_id='101').delete()
        User.objects.get(email='ihavegameuser@test.com').delete()
        User.objects.get(email='idonthavegameuser@test.com').delete()

    def test_connect_gameuser_pass(self):
        client = Client()

        user_mail = User.objects.get(email='idonthavegameuser@test.com').email
        token = jwt.encode({'email':user_mail}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')

        body = {'nickname' : 'test101'}
        headers = {
            'HTTP_Authorization' : token,
            'content_type' : 'application/json'
        }

        response = client.post('/user/connect-gameuser', json.dumps(body), **headers)
        self.assertEqual(response.status_code, 200)

    def test_connect_gameuser_fail(self):
        client = Client()

        user_mail = User.objects.get(email='ihavegameuser@test.com').email
        token = jwt.encode({'email':user_mail}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')

        body = {'nickname' : 'test101'}
        headers = {
            'HTTP_Authorization' : token,
            'content_type' : 'application/json'
        }

        response = client.post('/user/connect-gameuser', json.dumps(body), **headers)
        self.assertEqual(response.status_code, 400)

    def test_overlap_gameuser(self):
        client = Client()

        user_mail = User.objects.get(email='idonthavegameuser@test.com').email
        token = jwt.encode({'email':user_mail}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')

        body = {'nickname' : 'test100'}
        headers = {
            'HTTP_Authorization' : token,
            'content_type' : 'application/json'
        }

        response = client.post('/user/connect-gameuser', json.dumps(body), **headers)

        self.assertEqual(response.status_code, 400)

    def test_notfound_gameuser(self):
        client = Client()

        user_mail = User.objects.get(email='idonthavegameuser@test.com').email
        token = jwt.encode({'email':user_mail}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')

        body = {'nickname' : 'no_user'}
        headers = {
            'HTTP_Authorization' : token,
            'content_type' : 'application/json'
        }

        response = client.post('/user/connect-gameuser', json.dumps(body), **headers)
        self.assertEqual(response.status_code, 400)

