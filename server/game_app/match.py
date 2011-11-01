from base import *
from matchUtils import *
from objects import *
import networking.config.config
from collections import defaultdict
from networking.sexpr.sexpr import *
import os
import itertools
import scribe
import random
import math

Scribe = scribe.Scribe

def loadClassDefaults(cfgFile = "config/defaults.cfg"):
  cfg = networking.config.config.readConfig(cfgFile)
  for className in cfg.keys():
    for attr in cfg[className]:
      setattr(eval(className), attr, cfg[className][attr])

class Match(DefaultGameWorld):
  def __init__(self, id, controller):
    self.id = int(id)
    self.controller = controller
    DefaultGameWorld.__init__(self)
    self.scribe = Scribe(self.logPath())
    self.addPlayer(self.scribe, "spectator")

    #Initializes some variables
    self.turnNumber = -1
    self.playerID = -1
    self.gameNumber = id

  def addPlayer(self, connection, type="player"):
    connection.type = type
    if len(self.players) >= 2 and type == "player":
      return "Game is full"
    if type == "player":
      self.players.append(connection)
    elif type == "spectator":
      self.spectators.append(connection)
      #If the game has already started, send them the ident message
      if (self.turn is not None):
        self.sendIdent([connection])
    return True

  def removePlayer(self, connection):
    if connection in self.players:
      if self.turn is not None:
        winner = self.players[1 - self.getPlayerIndex(connection)]
        self.declareWinner(winner)
      self.players.remove(connection)
    else:
      self.spectators.remove(connection)

  def start(self):
    if len(self.players) < 2:
      return "Game is not full"
    if self.winner is not None or self.turn is not None:
      return "Game has already begun"
    
    #START STUFF 
    self.turn = self.players[-1]
    self.turnNumber = -1
    for p in self.players:
      self.addObject(Player, [p.screenName, 0, self.startingCycles, self.startTime])
    self.startMap()
    self.nextTurn()
    return True
    
    
    
  def startMap (self):
    mapFilenames = []
    #look through the list of map files, for every .map file, add to mapfilename list
    for filename in os.listdir("maps/"):
      if ".map" in filename:
        mapFilenames.append(filename)
        
      #choose a random map, open it as f, then get rid of all whitespace in file, save that file as mapdata, close f
    with open(("maps/" + mapFilenames[self.gameNumber % len(mapFilenames)]),'r') as f:
      mapdata = f.read().replace(' ','').split()
    self.width = len(mapdata[0])
    self.height = len(mapdata)
    #Need to get the attributes for the game objects before we parse the file
    #self.grid is for our benefit, so that we can look things up by location

    self.grid = [[None]*self.height for _ in range(self.width)]

    #saves y data as a enumeration called row, iterates through
    #does the same for x, saved as mapSquare. mapsquare points at map[x][y]
    for y, row in enumerate(mapdata):
      for x, mapSquare in enumerate(row):
        #if mapSquare is an X then it is a wall, owned by 3
        if mapSquare == 'X':
          self.grid[x][y] = self.addObject(Tile, [x,y,3])
        #if mapSquare is a . then it is a neutral tile owned by 2
        elif mapSquare == '.':
          self.grid[x][y] = self.addObject(Tile, [x,y,2])
        #if mapSquare is 1, then it is a tile owned by player 1, which means 
        #there's a base on top, so we add a base too
        elif mapSquare == '1':
         self.grid[x][y] = self.addObject(Tile, [x,y,1])
         self.addObject(Base,[x, y, 1, 0])
        #same as previous, only it is player 0's base/tile combo
        elif mapSquare =='0':
          self.grid[x][y] = self.addObject(Tile, [x,y,0])
          self.addObject(Base,[x, y, 0, 0])

  def nextTurn(self):
    self.turnNumber += 1
    if self.turn == self.players[0]:
      self.turn = self.players[1]
      self.playerID = 1
    elif self.turn == self.players[1]:
      self.turn = self.players[0]
      self.playerID = 0

    else:
      return "Game is over."

    for obj in self.objects.values():
      obj.nextTurn()

    self.checkWinner()
    if self.winner is None:
      self.sendStatus([self.turn] +  self.spectators)
    else:
      self.sendStatus(self.spectators)
    self.animations = ["animations"]
    return True

  def virusCost(self, level):
    # Calcuate the cost of a virus
    return int(self.baseCost*self.scaleCost**level)

  def worth(self, id):
    # Calculate the worth of a player
    total = self.objects.players[id].cycles
    for virus in self.objects.viruses:
      if virus.owner == id:
        total += self.virusCost(virus.level)
    return total
  
  def getScore(self, id):
    path = []
    connect = {} 
    closed = [[False]*self.height for _ in range(self.width)]
    offsets = [(0,1),(1,0),(0,-1),(-1,0)]
    score = 0
    for base in self.objects.bases:
      if base.owner == id:
        score+=1
        path.append(self.grid[base.x][base.y])
        closed[base.x][base.y] = True
    while len(path)>0:
      working = path.pop()
      for offset in offsets:
        dx, dy = working.x+offset[0], working.y+offset[1]
        if 0 <= dx < self.width and 0 <= dy < self.height and not closed[dx][dy] and self.grid[dx][dy].owner == id:
          score+=1
          path.append(self.grid[dx][dy])
          closed[dx][dy] = True
    return score

  def getIncome(self, id):
    possible = self.startingCycles + self.turnNumber / 2 * self.cyclesPerTurn
    return int(math.ceil((possible - self.worth(id))*self.returnAmount) + self.cyclesPerTurn)

  def checkWinner(self):
    player1 = self.objects.players[0]
    player2 = self.objects.players[1]
    if self.turnNumber >= self.turnLimit:
      if player1.byteDollars > player2.byteDollars:
        self.declareWinner(self.players[0], 'Victory through Bytedollar superiority!!')
        print "0 Wins!"
      elif player2.byteDollars > player1.byteDollars:
        self.declareWinner(self.players[1], 'Victory through Bytedollar superiority!!')
        print "1 Wins!"
      else:
        p0Worth, p1Worth = self.worth(0), self.worth(1)
        if p0Worth > p1Worth:
          self.declareWinner(self.players[0], 'Victory through more usable cycles')
          print("0 Wins!")
        elif p0Worth > p1Worth:
          print("1 Wins!")
          self.declareWinner(self.players[1], 'Victory through more usuable cycles')
        else:
          print("0 Wins!")
          self.declareWinner(self.players[0],'Victory because I said so, why did you build the same army?')       
    return

  def declareWinner(self, winner, reason=''):
    self.winner = winner

    msg = ["game-winner", self.id, self.winner.user, self.getPlayerIndex(self.winner), reason]
    self.scribe.writeSExpr(msg)
    self.scribe.finalize()
    self.removePlayer(self.scribe)

    for p in self.players + self.spectators:
      p.writeSExpr(msg)

    self.sendStatus([self.turn])
    self.playerID ^= 1
    self.sendStatus([self.players[self.playerID]])
    self.playerID ^= 1
    self.turn = None
    
  def logPath(self):
    return "logs/" + str(self.id) + ".glog"

  @derefArgs(Base, None)
  def spawn(self, object, Level):
    return object.spawn(Level, )

  @derefArgs((Player, Virus), None)
  def talk(self, object, message):
    return object.talk(message, )

  @derefArgs(Virus, None, None)
  def move(self, object, x, y):
    return object.move(x, y, )


  def sendIdent(self, players):
    if len(self.players) < 2:
      return False
    list = []
    for i in itertools.chain(self.players, self.spectators):
      list += [[self.getPlayerIndex(i), i.user, i.screenName, i.type]]
    for i in players:
      i.writeSExpr(['ident', list, self.id, self.getPlayerIndex(i)])

  def getPlayerIndex(self, player):
    try:
      playerIndex = self.players.index(player)
    except ValueError:
      playerIndex = -1
    return playerIndex

  def sendStatus(self, players):
    for i in players:
      i.writeSExpr(self.status())
      i.writeSExpr(self.animations)
    return True


  def status(self):
    msg = ["status"]
    msg.append(["game", self.turnNumber, self.playerID, self.gameNumber, self.baseCost, self.scaleCost, self.width, self.height])

    typeLists = []
    typeLists.append(["Base"] + [i.toList() for i in self.objects.values() if i.__class__ is Base])
    typeLists.append(["Player"] + [i.toList() for i in self.objects.values() if i.__class__ is Player])
    typeLists.append(["Tile"] + [i.toList() for i in self.objects.values() if i.__class__ is Tile])
    typeLists.append(["Virus"] + [i.toList() for i in self.objects.values() if i.__class__ is Virus])

    msg.extend(typeLists)

    return msg


loadClassDefaults()

