from django.db import models
from django.db.models import Max, Count, Avg


class Player(models.Model):
    """A player is identified by name. Re-entering the same name on a
    later visit reuses the same Player row so score history accumulates
    instead of fragmenting into duplicate players."""
    name = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def best_score(self):
        return self.scores.aggregate(best=Max("value"))["best"] or 0

    @property
    def games_played(self):
        return self.scores.count()

    @property
    def average_score(self):
        avg = self.scores.aggregate(avg=Avg("value"))["avg"]
        return round(avg, 1) if avg is not None else 0


class Score(models.Model):
    """A single completed game's result. Kept separate from Player so
    we retain full score history, not just a best-score field."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="scores")
    value = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-value", "created_at"]

    def __str__(self):
        return f"{self.player.name}: {self.value}"
