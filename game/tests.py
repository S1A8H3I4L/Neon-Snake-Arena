import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Player, Score


class GameFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Enter Name")

    def test_start_game_creates_player_and_redirects(self):
        resp = self.client.post(reverse("start_game"), {"name": "Sahil"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("play"))
        self.assertTrue(Player.objects.filter(name="Sahil").exists())

    def test_start_game_rejects_empty_name(self):
        resp = self.client.post(reverse("start_game"), {"name": "   "})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Please enter a name")
        self.assertFalse(Player.objects.exists())

    def test_play_page_requires_session(self):
        resp = self.client.get(reverse("play"))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("home"))

    def test_play_page_loads_after_starting(self):
        self.client.post(reverse("start_game"), {"name": "Rahul"})
        resp = self.client.get(reverse("play"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Rahul")

    def test_save_score_persists_to_db(self):
        self.client.post(reverse("start_game"), {"name": "Sahil"})
        resp = self.client.post(
            reverse("save_score"),
            data=json.dumps({"score": 10}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["score"], 10)

        player = Player.objects.get(name="Sahil")
        self.assertEqual(player.scores.count(), 1)
        self.assertEqual(player.best_score, 10)

    def test_save_score_without_session_fails(self):
        resp = self.client.post(
            reverse("save_score"),
            data=json.dumps({"score": 5}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()["ok"])

    def test_save_score_rejects_negative_score(self):
        self.client.post(reverse("start_game"), {"name": "Amit"})
        resp = self.client.post(
            reverse("save_score"),
            data=json.dumps({"score": -5}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_same_player_name_reuses_player_row(self):
        self.client.post(reverse("start_game"), {"name": "Sahil"})
        self.client.post(
            reverse("save_score"),
            data=json.dumps({"score": 10}),
            content_type="application/json",
        )

        client2 = Client()
        client2.post(reverse("start_game"), {"name": "Sahil"})
        client2.post(
            reverse("save_score"),
            data=json.dumps({"score": 15}),
            content_type="application/json",
        )

        self.assertEqual(Player.objects.filter(name="Sahil").count(), 1)
        player = Player.objects.get(name="Sahil")
        self.assertEqual(player.scores.count(), 2)
        self.assertEqual(player.best_score, 15)

    def test_leaderboard_shows_best_score_per_player_ranked(self):
        sahil = Player.objects.create(name="Sahil")
        rahul = Player.objects.create(name="Rahul")
        amit = Player.objects.create(name="Amit")
        Score.objects.create(player=sahil, value=10)
        Score.objects.create(player=rahul, value=15)
        Score.objects.create(player=rahul, value=5)
        Score.objects.create(player=amit, value=8)

        resp = self.client.get(reverse("leaderboard"))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()

        rahul_pos = content.find("Rahul")
        sahil_pos = content.find("Sahil")
        amit_pos = content.find("Amit")
        self.assertTrue(rahul_pos < sahil_pos < amit_pos)
        self.assertContains(resp, "15")
        self.assertContains(resp, "10")
        self.assertContains(resp, "8")

    def test_leaderboard_empty_state(self):
        resp = self.client.get(reverse("leaderboard"))
        self.assertContains(resp, "No scores yet")

    def test_full_flow_two_players(self):
        c1 = Client()
        c1.post(reverse("start_game"), {"name": "Sahil"})
        c1.post(reverse("save_score"), data=json.dumps({"score": 10}), content_type="application/json")

        c2 = Client()
        c2.post(reverse("start_game"), {"name": "Rahul"})
        c2.post(reverse("save_score"), data=json.dumps({"score": 15}), content_type="application/json")

        resp = self.client.get(reverse("leaderboard"))
        content = resp.content.decode()
        self.assertTrue(content.find("Rahul") < content.find("Sahil"))


class AdminRegistrationTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        User.objects.create_superuser("tester", "tester@example.com", "pw12345")
        self.client.login(username="tester", password="pw12345")

    def test_admin_index_lists_player_and_score(self):
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Players")
        self.assertContains(resp, "Scores")
        self.assertContains(resp, "Game Statistics")

    def test_admin_player_changelist(self):
        Player.objects.create(name="Sahil")
        resp = self.client.get("/admin/game/player/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Sahil")

    def test_admin_game_statistics_view(self):
        p = Player.objects.create(name="Sahil")
        Score.objects.create(player=p, value=10)
        resp = self.client.get("/admin/game/gamestatistics/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Total Players")
