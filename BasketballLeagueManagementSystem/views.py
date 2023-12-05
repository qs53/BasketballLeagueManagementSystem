from datetime import datetime, timezone

import numpy as np
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import GameSerializer, SystemUserSerializer


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def login_user(request):
    """
    Log in a user and return a JWT token.
    Throws a 404 if invalid credentials
    """
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return JsonResponse({"error": "Invalid login credentials"}, status=status.HTTP_404_NOT_FOUND)
    user.last_login = datetime.now(timezone.utc)
    user.save()
    system_user = SystemUser.objects.get(user=user)
    system_user.is_logged_in = True
    system_user.logged_in_count = system_user.logged_in_count + 1
    system_user.save()
    token, created = Token.objects.get_or_create(user=user)
    return JsonResponse({"token": token.key}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Log out a user and delete the JWT token in request headers.
    """
    system_user = SystemUser.objects.get(user=request.user)
    system_user.is_logged_in = False
    time_spent_online = (datetime.now(timezone.utc) - request.user.last_login).total_seconds()
    system_user.time_spent_online = time_spent_online
    system_user.save()
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        return JsonResponse({"error": "Error while deleting token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse({"success": "Successfully logged out"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def scoreboard(request):
    """
    Get details and scores of all games played
    """
    games = Game.objects.all()
    serializer = GameSerializer(games, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def team_details(request, team_id):
    """
    Get details of team (and percentile if provided). Coach can only access his team's data.
    """
    team = get_object_or_404(Team, pk=team_id)
    if not coach_authorized(request.user, team):
        return JsonResponse({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
    percentile = request.GET.get("percentile")
    players = Player.objects.filter(team=team)
    if percentile is not None:
        response = get_team_details_for_percentile(team, players, percentile)
    else:
        response = get_team_details(team, players)
    return JsonResponse(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def player_details(request, player_id):
    """
    Get details of player. Player can only access his data.
    """
    player = get_object_or_404(Player, pk=player_id)
    if not player_authorized(request.user, player.team, player):
        return JsonResponse({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
    number_of_games_played, avg_score = get_player_details(player)
    return JsonResponse({"name": player.user.user.get_full_name(), "height": player.height,
                         "numberOfGamesPlayed": number_of_games_played, "avgScore": avg_score},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def stats(request):
    """
    Get user stats. Only accessible by league admin. Time spent online is in seconds
    """
    if not league_admin_authorized(request.user):
        return JsonResponse({"error": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)
    system_users = SystemUser.objects.all()
    serializer = SystemUserSerializer(system_users, many=True)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)


def get_team_details_for_percentile(team, players, percentile):
    percentile = int(percentile)
    if not 0 <= percentile <= 100:
        return JsonResponse({'error': 'Percentile value should be between 0 and 100'},
                            status=status.HTTP_400_BAD_REQUEST)
    team_players = []
    avg_scores = []
    for player in players:
        number_of_games_played, avg_score = get_player_details(player)
        team_player_dict = {"player": player, "number_of_games_played": number_of_games_played,
                            "avg_score": avg_score}
        team_players.append(team_player_dict)
        if number_of_games_played > 0:
            avg_scores.append(avg_score)
    avg_scores = np.array(avg_scores)
    avg_score_percentile = round(np.percentile(avg_scores, percentile))
    players_in_percentile = []
    for team_player in team_players:
        if team_player['avg_score'] >= avg_score_percentile:
            players_in_percentile.append({"player_name": team_player['player'].user.user.get_full_name(),
                                          "avg_score": team_player['avg_score']})
    return {"team": team.name, "percentile": percentile, "percentileScore": avg_score_percentile,
            "playersInPercentile": [{"name": player["player_name"], "avgScore": player['avg_score']}
                                    for player in players_in_percentile]}


def get_team_details(team, players):
    avg_score_1 = Game.objects.filter(team_1=team).aggregate(avg_score=Avg('team_1_score'))['avg_score']
    avg_score_2 = Game.objects.filter(team_2=team).aggregate(avg_score=Avg('team_2_score'))['avg_score']
    if avg_score_1 is None:
        avg_score = round(avg_score_2)
    elif avg_score_2 is None:
        avg_score = round(avg_score_1)
    else:
        avg_score = round((avg_score_1 + avg_score_2) / 2)
    players_names = [f'{player.user.user.get_full_name()}' for player in players]
    return {"team": team.name, "avgScore": avg_score, "players": players_names}


def get_player_details(player):
    player_games = PlayerGame.objects.filter(player=player)
    number_of_games_played = player_games.count()
    avg_score = 0
    if player_games.count() > 0:
        avg_score = round(player_games.aggregate(player_score=Avg('player_score'))['player_score'])
    return number_of_games_played, avg_score


def league_admin_authorized(user):
    for permission in user.get_group_permissions():
        if permission.split('.')[1] == 'view_systemuser':
            return True
    return False


def coach_authorized(user, team):
    if league_admin_authorized(user):
        return True
    coach = Coach.objects.get(team=team)
    for permission in user.get_group_permissions():
        if permission.split('.')[1] == 'view_coach' and coach.user.user.username == user.username:
            return True
    return False


def player_authorized(user, team, player):
    if coach_authorized(user, team):
        return True
    for permission in user.get_group_permissions():
        if permission.split('.')[1] == 'view_player' and player.user.user.username == user.username:
            return True
    return False
