from django.db import models
from django.contrib.auth.models import User


class SystemUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_logged_in = models.BooleanField()
    logged_in_count = models.IntegerField()
    time_spent_online = models.IntegerField()

    def __str__(self):
        return self.user.username


class Team(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(SystemUser, on_delete=models.CASCADE)
    height = models.CharField(max_length=6)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)

    def __str__(self):
        return self.user.user.username


class Coach(models.Model):
    user = models.OneToOneField(SystemUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)

    def __str__(self):
        return self.user.user.username


class Game(models.Model):
    team_1 = models.ForeignKey(Team, on_delete=models.RESTRICT, related_name='team_1')
    team_1_score = models.IntegerField()
    team_2 = models.ForeignKey(Team, on_delete=models.RESTRICT, related_name='team_2')
    team_2_score = models.IntegerField()
    winner = models.ForeignKey(Team, on_delete=models.RESTRICT, related_name='winner')
    type = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.type} - {self.team_1.name} vs {self.team_2.name}'


class PlayerGame(models.Model):
    player = models.ForeignKey(Player, on_delete=models.RESTRICT)
    game = models.ForeignKey(Game, on_delete=models.RESTRICT)
    player_score = models.IntegerField()

    def __str__(self):
        return f'{self.player.user.user.username} - {self.player.team.name}'
