#####
### Missouri S&T ACM SIG-Game Arena (Thunderdome)
#####

# Standard Imports
from datetime import datetime

# Non-Django 3rd Party Imports
import beanstalkc
import time
import json

# Django Imports
from django import forms
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Max

class Client(models.Model):
    ### A competitor in the arena
    name            = models.CharField(max_length=100)
    current_version = models.CharField(max_length=100, default='')
    embargoed       = models.BooleanField(default=False) # fail to compile?
    seed            = models.IntegerField(default=0)
        
    def last_game(self):
        last = self.games_played.all().aggregate(Max('pk'))
        if last['pk__max']:
            return last['pk__max']
        else:
            return -1
    
    def last_visualized(self):
        vis = self.games_played.all().aggregate(Max('visualized'))
        if vis['visualized__max']:
            return vis['visualized__max']
        else:
            return datetime(1970,1,1,0,0)
    
    def fitness(self):
        if self.games_played.count() == 0:
            return 0
        else:
            return self.games_won.count() / float(self.games_played.count())
    
    def __unicode__(self):
        return self.name

    
class Game(models.Model):
    ### A single game
    clients     = models.ManyToManyField(Client, through='GameData',
                                         related_name='games_played')
    winner      = models.ForeignKey(Client, null=True, blank=True,
                                    related_name='games_won')
    loser       = models.ForeignKey(Client, null=True, blank=True,
                                    related_name='games_lost')
    status      = models.CharField(max_length=20, 
                                   default='New')
    priority    = models.IntegerField(default=1000)
    gamelog_url = models.CharField(max_length=200, default='')
    visualized  = models.DateTimeField(default=datetime(1970,1,1),null=True)
    completed   = models.DateTimeField(null=True)
    claimed     = models.BooleanField(default=True)
    tournament  = models.BooleanField(default=False)
    stats       = models.TextField(default='') # holds extra stuff via JSON
    
    def schedule(self):
        if self.status != 'New':
            return False
        if self.pk == None:
            self.save()
        return self.force_schedule()
    
    def force_schedule(self):
        c = beanstalkc.Connection()
        c.use('game-requests')
        payload = json.dumps({'game_id'    : str(self.pk),
                              'entry_time' : str(time.time()) })
        c.put(payload, priority=self.priority)
        c.close()
        self.status='Scheduled'
        self.save()
        return True

    def __unicode__(self):
        return unicode(self.pk)


class GameData(models.Model):
    ### each Match will have one of these for each competitor in that match
    game       = models.ForeignKey(Game)
    client     = models.ForeignKey(Client)
    compiled   = models.NullBooleanField()
    won        = models.NullBooleanField()
    version    = models.CharField(max_length=100, default='')
    stats      = models.TextField(default='') # holds extra stuff via JSON

    def __unicode__(self):
        return u"%s - %s" % (self.game.pk, self.client.name)


class InjectedGameForm(forms.Form):
    ### Used to manually inject a game into the queue
    priority = forms.IntegerField(min_value=0, max_value=1000)
    clients = forms.MultipleChoiceField(widget=CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        super(InjectedGameForm, self).__init__(*args, **kwargs)
        self.fields['clients'].choices = [(x.pk, x.name) for x in 
                                          Client.objects.all()]

    
class Match(models.Model):
    ### A multi-game match
    p0     = models.ForeignKey(Client, null=True, blank=True, 
                               related_name='matches_as_p0')
    p1     = models.ForeignKey(Client, null=True, blank=True,
                               related_name='matches_as_p1')
    winner = models.ForeignKey(Client, null=True, blank=True,
                               related_name='matches_won')
    loser  = models.ForeignKey(Client, null=True, blank=True,
                               related_name='matches_lost')
    father = models.ForeignKey('self', null=True, blank=True,
                               related_name='matches_fathered')
    mother = models.ForeignKey('self', null=True, blank=True,
                               related_name='matches_mothered')
    games  = models.ManyToManyField(Game)
    losses_to_eliminate = models.IntegerField(default=3)
    wins_to_win = models.IntegerField(default=4)
    father_type = models.TextField(default='win')
    mother_type = models.TextField(default='win')
    status      = models.TextField(default='Waiting')
    root        = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s - %s" % (self.p0.name, self.p1.name)
