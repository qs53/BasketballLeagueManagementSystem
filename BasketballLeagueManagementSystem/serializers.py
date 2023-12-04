from rest_framework import serializers
from .models import Game, SystemUser


class GameSerializer(serializers.ModelSerializer):
    team1 = serializers.StringRelatedField(source='team_1')
    team1Score = serializers.IntegerField(source='team_1_score')
    team2 = serializers.StringRelatedField(source='team_2')
    team2Score = serializers.IntegerField(source='team_2_score')
    winner = serializers.StringRelatedField()

    class Meta:
        model = Game
        fields = ['team1', 'team1Score', 'team2', 'team2Score', 'winner', 'type']


class SystemUserSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source='user.username')
    name = serializers.SerializerMethodField()
    isLoggedIn = serializers.CharField(source='is_logged_in')
    loggedInCount = serializers.CharField(source='logged_in_count')
    timeSpentOnline = serializers.CharField(source='time_spent_online')

    class Meta:
        model = SystemUser
        fields = ['name', 'username', 'isLoggedIn', 'loggedInCount', 'timeSpentOnline']

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
