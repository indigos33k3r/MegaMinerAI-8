#####
### Missouri S&T ACM SIG-Game Arena (Thunderdome)
#####

# Non-Django 3rd Party Imports
import beanstalkc

# Django Imports
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf

# My Imports
from thunderdome.models import Game, Client, GameData, InjectedGameForm

def index(request):
    # Let's start by having this page show some arena health statistics
    p = dict() # payload for the render_to_response

    c = beanstalkc.Connection()
    c.use('game-requests')
    tube_status = c.stats_tube('game-requests')
    (p['ready_requests'], p['running_requests']) = \
        [tube_status[x] for x in ('current-jobs-ready',
                                  'current-jobs-reserved')]
    c.close()

    (p['new_games'], p['scheduled_games'], p['running_games'], 
     p['complete_games'], p['failed_games']) = \
         [Game.objects.filter(status = x).count 
          for x in ('New', 'Scheduled', 'Running', 'Complete', 'Failed')]

    p['sanity'] = p['ready_requests']  == p['scheduled_games'] \
              and p['running_games'] == p['running_requests']

    return render_to_response('thunderdome/index.html', p)


def inject(request):
    ### Handle manual injection of a game into the system
    if request.method == 'POST':
        form = InjectedGameForm(request.POST)
        if form.is_valid():
            game = Game.objects.create(priority=form.cleaned_data['priority'])
            for client in Client.objects.filter(pk__in = \
                                                form.cleaned_data['clients']):
                GameData(game=game, client=client).save()
            game.schedule()
            payload = {'game': game}
            payload.update(csrf(request))
            return HttpResponseRedirect('view/%s' % game.pk)
    else:
        form = InjectedGameForm()
    
    payload = {'form': form}
    payload.update(csrf(request))
    return render_to_response('thunderdome/inject.html', payload)


def view_game(request, game_id):
    ### View the status of a single game
    return render_to_response('thunderdome/view_game.html', 
                              {'game': get_object_or_404(Game, pk=game_id)})


def view_client(request, client_id):
    ### View the status of a single client
    return render_to_response('thunderdome/view_client.html', 
                              {'client': get_object_or_404(Client, 
                                                           pk=client_id)})


def scoreboard(request):
    clients = Client.objects.all()
    
    # Build the speedy lookup table
    grid = dict()    
    for c1 in clients:
        grid[c1] = dict()
        for c2 in clients:
            if c1 != c2:
                grid[c1][c2] = 0
    
    for game in Game.objects.all():
        winner_set = game.gamedata_set.filter(won=True)
        loser_set  = game.gamedata_set.filter(won=False)
        if( len(winner_set) == 1 and len(loser_set) == 1 ):
            winner = winner_set[0]
            loser  = loser_set[0]
            grid[winner.client][loser.client] += 1
                
    # Sort the clients by winningness
    clients = list(clients)
    clients.sort(key = lambda x: x.gamedata_set.filter(won=True).count(),
                 reverse=True)

    # Load the data in the format the template expects
    for c1 in clients:
        c1.row = list()
        for c2 in clients:
            if c1 in grid and c2 in grid[c1]:
                c1.row.append(grid[c1][c2])
            else:
                c1.row.append(' ')

    payload = {'clients': clients}
    return render_to_response('thunderdome/scoreboard.html', payload)
