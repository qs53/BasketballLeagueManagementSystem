from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from BasketballLeagueManagementSystem.models import *
from itertools import chain
import json
import os


class Command(BaseCommand):
    help = 'Populate database with seed data'

    def handle(self, *args, **kwargs):
        system_user_content_type = ContentType.objects.get_for_model(SystemUser)
        system_user_permissions = Permission.objects.filter(content_type=system_user_content_type)
        coach_content_type = ContentType.objects.get_for_model(Coach)
        coach_permissions = Permission.objects.filter(content_type=coach_content_type)
        player_content_type = ContentType.objects.get_for_model(Player)
        player_permissions = Permission.objects.filter(content_type=player_content_type)
        league_admin_group = Group.objects.create(name='League Admin')
        coach_group = Group.objects.create(name='Coach')
        player_group = Group.objects.create(name='Player')
        league_admin_group_permissions = list(chain(system_user_permissions, coach_permissions, player_permissions))
        league_admin_group.permissions.set(league_admin_group_permissions)
        coach_group_permissions = list(chain(coach_permissions, player_permissions))
        coach_group.permissions.set(coach_group_permissions)
        player_group.permissions.set(player_permissions)

        league_admin = {'first_name': 'Kenzo', 'last_name': 'Patterson',
                        'username': 'kenzo.patterson', 'password': 'kenzo.patterson', 'last_login': None}
        league_admin_user = User.objects.create_user(**league_admin)
        league_admin_system_user = SystemUser.objects.create(user=league_admin_user, is_logged_in=False,
                                                             logged_in_count=0, time_spent_online=0)
        league_admin_system_user.save()

        current_dir_path = 'BasketballLeagueManagementSystem/management/commands/'
        teams = []
        teams_dict = {}
        player_system_users = []
        player_users = []
        players = []
        players_dict = {}
        coach_system_users = []
        coach_users = []
        coaches = []
        games = []
        games_dict = {}
        player_games = []
        teams_json = json.load(open(os.path.join(os.path.abspath(
            os.path.dirname('manage.py')), current_dir_path + 'teams.json')))
        for team_dict in teams_json:
            team = Team.objects.create(**team_dict)
            teams.append(team)
            teams_dict[team_dict['name']] = team

        players_json = json.load(open(os.path.join(os.path.abspath(
            os.path.dirname('manage.py')), current_dir_path + 'players.json')))
        for player_dict in players_json:
            player_user = User.objects.create_user(first_name=player_dict['first_name'],
                                                   last_name=player_dict['last_name'],
                                                   username=player_dict['username'], password=player_dict['username'],
                                                   last_login=None)
            player_users.append(player_user)
            player_system_user = SystemUser.objects.create(user=player_user, is_logged_in=False,
                                                           logged_in_count=0, time_spent_online=0)
            player = Player.objects.create(user=player_system_user, height=player_dict['height'],
                                           team=teams_dict[player_dict['team']])
            player_system_users.append(player_system_user)
            players.append(player)
            players_dict[player_dict['username']] = player

        coaches_json = json.load(open(os.path.join(os.path.abspath(
            os.path.dirname('manage.py')), current_dir_path + 'coaches.json')))
        for coach_dict in coaches_json:
            coach_user = User.objects.create_user(first_name=coach_dict['first_name'],
                                                  last_name=coach_dict['last_name'],
                                                  username=coach_dict['username'], password=coach_dict['username'],
                                                  last_login=None)
            coach_users.append(coach_user)
            coach_system_user = SystemUser.objects.create(user=coach_user, is_logged_in=False,
                                                          logged_in_count=0, time_spent_online=0)
            coach = Coach.objects.create(user=coach_system_user,
                                         team=teams_dict[coach_dict['team']])
            coach_system_users.append(coach_system_user)
            coaches.append(coach)

        games_json = json.load(open(os.path.join(os.path.abspath(
            os.path.dirname('manage.py')), current_dir_path + 'games.json')))
        for game_dict in games_json:
            game = Game.objects.create(team_1=teams_dict[game_dict['team_1']], team_1_score=game_dict['team_1_score'],
                                       team_2=teams_dict[game_dict['team_2']], team_2_score=game_dict['team_2_score'],
                                       winner=teams_dict[game_dict['winner']], type=game_dict['type'])
            games.append(game)
            games_dict[game_dict['team_1'] + game_dict['team_2']] = game

        player_games_json = json.load(open(os.path.join(os.path.abspath(
            os.path.dirname('manage.py')), current_dir_path + 'player_games.json')))
        for player_game_dict in player_games_json:
            game = games_dict[player_game_dict['team_1'] + player_game_dict['team_2']]
            for i, player in enumerate(player_game_dict['players']):
                player_game = PlayerGame.objects.create(game=game, player=players_dict[player],
                                                        player_score=player_game_dict['player_scores'][i])
                player_games.append(player_game)

        league_admin_group.user_set.add(league_admin_user)
        coach_group.user_set.add(*coach_users)
        player_group.user_set.add(*player_users)

        for team in teams:
            team.save()
        for coach in coaches:
            coach.save()
        for player in players:
            player.save()
        for game in games:
            game.save()
        for player_game in player_games:
            player_game.save()

        self.stdout.write(self.style.SUCCESS('Data populated successfully'))
