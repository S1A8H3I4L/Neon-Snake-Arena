from django.contrib import admin
from django.db.models import Max, Count, Avg
from .models import Player, Score


class ScoreInline(admin.TabularInline):
    model = Score
    extra = 0
    readonly_fields = ("value", "created_at")
    can_delete = True
    ordering = ("-created_at",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "best_score_display", "games_played_display", "average_score_display", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    inlines = [ScoreInline]

    @admin.display(description="Best Score")
    def best_score_display(self, obj):
        return obj.best_score

    @admin.display(description="Games Played")
    def games_played_display(self, obj):
        return obj.games_played

    @admin.display(description="Average Score")
    def average_score_display(self, obj):
        return obj.average_score


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ("player", "value", "created_at")
    list_filter = ("created_at",)
    search_fields = ("player__name",)
    ordering = ("-value",)
    autocomplete_fields = ("player",)


# --- A lightweight "Game Statistics" view, surfaced via a proxy model so it
# shows up in the admin index alongside Players and Scores without needing
# a separate admin app. ---

class GameStatistics(Score):
    class Meta:
        proxy = True
        verbose_name = "Game Statistic"
        verbose_name_plural = "Game Statistics"


@admin.register(GameStatistics)
class GameStatisticsAdmin(admin.ModelAdmin):
    """Read-only aggregate dashboard: total games, total players, top
    score, and average score across the whole site."""
    change_list_template = "admin/game_statistics.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        stats = Score.objects.aggregate(
            total_games=Count("id"),
            top_score=Max("value"),
            average_score=Avg("value"),
        )
        extra_context = extra_context or {}
        extra_context["stats"] = {
            "total_players": Player.objects.count(),
            "total_games": stats["total_games"] or 0,
            "top_score": stats["top_score"] or 0,
            "average_score": round(stats["average_score"], 1) if stats["average_score"] else 0,
        }
        return super().changelist_view(request, extra_context=extra_context)
