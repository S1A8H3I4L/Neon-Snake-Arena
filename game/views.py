import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.db.models import Max

from .models import Player, Score

MAX_NAME_LENGTH = 40


def home(request):
    """Name-entry screen. Stores the chosen name in the session so the
    game and game-over pages know who is playing without trusting a
    client-supplied player id on every request."""
    return render(request, "game/home.html")


@require_POST
def start_game(request):
    name = request.POST.get("name", "").strip()
    if not name:
        return render(request, "game/home.html", {"error": "Please enter a name to play."})
    if len(name) > MAX_NAME_LENGTH:
        return render(request, "game/home.html", {"error": f"Name must be {MAX_NAME_LENGTH} characters or fewer."})

    player, _ = Player.objects.get_or_create(name=name)
    request.session["player_id"] = player.id
    request.session["player_name"] = player.name
    return redirect("play")


def play(request):
    """The game screen itself. Bounces back to name entry if no one is
    'logged in' for this session."""
    if not request.session.get("player_id"):
        return redirect("home")
    return render(request, "game/play.html", {"player_name": request.session.get("player_name")})


@require_POST
def save_score(request):
    """Receives the final score from the JS game over event and persists
    it against the session's player. Returns JSON so the frontend can
    show 'Saved Successfully' without a full page reload."""
    player_id = request.session.get("player_id")
    if not player_id:
        return JsonResponse({"ok": False, "error": "No active player session."}, status=400)

    try:
        payload = json.loads(request.body)
        score_value = int(payload.get("score", -1))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid score payload."}, status=400)

    if score_value < 0:
        return JsonResponse({"ok": False, "error": "Score must be zero or greater."}, status=400)

    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Player not found."}, status=404)

    score = Score.objects.create(player=player, value=score_value)

    is_new_best = score_value >= player.best_score  # best_score already includes this row, so check rank
    rank = Score.objects.filter(value__gt=score_value).count() + 1

    return JsonResponse({
        "ok": True,
        "score": score.value,
        "player": player.name,
        "rank": rank,
        "is_personal_best": score_value == player.best_score,
    })


def leaderboard(request):
    """Shows the top score per player (not every individual game), so
    one player can't flood the board with repeated low scores."""
    top_players = (
        Player.objects.annotate(top_score=Max("scores__value"))
        .filter(top_score__isnull=False)
        .order_by("-top_score")[:20]
    )
    return render(request, "game/leaderboard.html", {"players": top_players})
