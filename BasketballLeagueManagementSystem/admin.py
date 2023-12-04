from django.contrib import admin
from .models import *

admin.site.register([SystemUser, Team, Player, Coach, Game, PlayerGame])
