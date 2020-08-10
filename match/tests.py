import json

from django.test import (
    TestCase,
    Client,
)

class IndiTest(TestCase):

    def test_indi_match_success(self):
        client = Client()
        response = client.get("/match/indimatch/1141319922/7b9f0fd5377c38514dbb78ebe63ac6c3b81009d5a31dd569d1cff8f005aa881a",  content_type="application/json")

        self.assertEqual(response.status_code, 200)


    def test_indi_match_fail(self):
        client = Client()
        response = client.get("/match/indimatch/1234/7b9f0fd5377c38514dbb78ebe63ac6c3b81009d5a31dd569d1cff8f005aa881a",  content_type="application/json")

        self.assertEqual(response.status_code, 400)

class TeamTest(TestCase):

    def test_team_match_success(self):
        client = Client()
        response = client.get("/match/teammatch/956968149/effd66758144a29868663aa50e85d3d95c5bc0147d7fdb9802691c2087f3416e",  content_type="application/json")

        self.assertEqual(response.status_code, 200)


    def test_indi_match_fail(self):
        client = Client()
        response = client.get("/match/teammatch/1234/effd66758144a29868663aa50e85d3d95c5bc0147d7fdb9802691c2087f3416e",  content_type="application/json")

        self.assertEqual(response.status_code, 400)
