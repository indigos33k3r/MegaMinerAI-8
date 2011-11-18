#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
offsets = [(0,1), (1,0), (0,-1), (-1,0)]
import random
from collections import deque
def makeDict(mappable, test = lambda X: True):
  ret = {}
  for obj in mappable:
    if test(obj):
      ret[obj.getX(),obj.getY()] = obj
  return ret

def connect(openList, available):
  # Given a list of starting points and a set of valid points, find how many are connected to the start
  connected = set()
  while len(openList) > 0:
    working = openList.pop()
    connected.add(working)
    for offset in offsets:
      next = working[0] + offset[0], working[1] + offset[1]
      if next in available:
        available.remove(next)
        openList.append(next)
  return connected

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "mst00120"

  @staticmethod
  def password():
    return "aegoaf5Y"

  def biggestArea(self):
    p1, p2 = set(), set()
    # Builds a dictionary of all controlled tiles for both players
    for tile in self.tiles:
      if tile.getOwner() == 0:
        p1.add((tile.getX(), tile.getY()))
      elif tile.getOwner() == 1:
        p2.add((tile.getX(), tile.getY()))

    def maxArea(available):
      # Given a dictionary of valid tiles
      largest = 0
      ret = set()
      while len(available) > 0:
        next = available.pop()
        blob = connect([next], available)
        if largest < len(blob):
          largest = len(blob)
          ret = blob
      return ret
    p1blob, p2blob = maxArea(p1), maxArea(p2)
    # Convert the score to be a single point
    if self.playerID() == 0:
      return p1blob, p2blob
    else:
      return p2blob, p1blob

  def shortestNext(self, moves, virus, closest, test = lambda X: True, goal = lambda X: True):
    searched = set(moves)
    openList = deque([])
    for move in moves:
      openList.append(move+(move,))
    count = 0
    while len(openList) > 0:
      count+=1
      if count == 200:
        break
      x, y, move = openList.pop()
      if goal((x, y)):
        if move is None:
          if closest:
            self.shortestNext(moves, virus, False, test, goal)
          else:
            return moves
        else:
          return [move]
      for offset in offsets:
        next = x+offset[0], y+offset[1]
        if test(next) and next not in searched:
          if closest and next in self.units and self.units[next].getLevel() >= virus.getLevel():
            openList.appendleft(next + (None,))
          else:
            openList.appendleft(next + (move,))
          searched.add(next)
    return moves


  def init(self):
    self.blocked = makeDict(self.bases)    
    self.valid = makeDict(self.tiles, lambda tile: (tile.getX(), tile.getY()) not in self.blocked and tile.getOwner()!=3)
    self.enemyID = 0 if self.playerID() == 1 else 1

  def end(self):
    pass
  
  def danger(self, virus, move):
    for offset in offsets:
      adj = move[0]+offset[0], move[1]+offset[1]
      if adj in self.units and self.units[adj].getOwner() != self.playerID() and self.units[adj].getLevel() > virus.getLevel():
        return True
    return False

  def run(self):
    print self.turnNumber()
    self.units = makeDict(self.viruses)
    self.myblob, self.enemyblob = self.biggestArea()
    self.myunconnected, self.enemyunconnected = set(), set()
    for at, tile in self.valid.iteritems():
      if tile.getOwner() == self.playerID() and at not in self.myblob:
        self.myunconnected.add(at)
      elif tile.getOwner() == self.enemyID and at not in self.enemyblob:
        self.enemyunconnected.add(at)

    # loop through all of the viruses
    for virus in self.viruses:
      # if you own that virus
      if virus.getOwner() == self.playerID() and virus.getMovesLeft() > 0:
        moves = [(virus.getX()+offset[0], virus.getY()+offset[1]) for offset in offsets] + [virus.getX(),virus.getY()]
        # only valid moves
        moves = filter(lambda move: move in self.valid, moves)
        # No running into other guys
        moves = filter(lambda move: move not in self.units or 
                      (self.units[move].getOwner() != self.playerID() and self.units[move].getLevel() <= virus.getLevel()) or
                      (self.units[move].getOwner() == self.playerID() and self.units[move].getLevel() == virus.getLevel()), moves)
                      
        moves = filter(lambda move: not self.danger(virus, move), moves)
        # From here down, moves become optional
        
        kills = filter(lambda move: move in self.units and self.units[move].getOwner() != self.playerID(), moves)
        if len(kills) > 0:
          moves = kills
        
        enemySpace = filter(lambda move: self.valid[move].getOwner() == self.enemyID, moves)
        if len(enemySpace) > 0:
          moves = enemySpace
        neutralSpace = filter(lambda move: self.valid[move].getOwner() == 2, moves)
        if len(neutralSpace) > 0:
          moves = neutralSpace
        
        if len(moves) > 1 and (virus.getX(), virus.getY()) not in self.myblob:
          moves = self.shortestNext(moves, virus, True, test = lambda X: X in self.valid, goal = lambda X: X in self.myblob)
        elif len(self.myunconnected) > 0:
          moves = self.shortestNext(moves, virus, True, test = lambda X: X in self.valid, goal = lambda X: X in self.myunconnected)
        
        if len(moves) > 1:
          # Part 6
          moves = self.shortestNext(moves, virus, True, test = lambda X: X in self.valid, goal = lambda X: X in self.valid and self.valid[X].getOwner() != self.playerID())
        
        if len(moves) > 0:
          action = random.choice(moves)
          self.updateMove(virus, action)
        
    
    # loop through all of the bases
    for base in sorted(self.bases, key=lambda base: 
                       sum(abs(virus.getX()-base.getX())+abs(virus.getY()-base.getY()) for virus in self.viruses if virus.getOwner()==self.playerID()), reverse=True):
      # check if you own that base
      if base.getOwner() == self.playerID():
        # check to see if you have enough cycles to spawn a level 0 virus
        if self.baseCost() <= self.players[self.playerID()].getCycles():
          # spawn a level 0 virus at that base
          base.spawn(0)

    # End your turn
    return True;
  
  def updateMove(self, virus, action):
    if action != (virus.getX(), virus.getY()):
      del self.units[virus.getX(), virus.getY()]
      virus.move(*action)
      if action not in self.units or self.units[action].getOwner() != self.playerID():
        self.units[action] = virus
    
  def __init__(self, conn):
      BaseAI.__init__(self, conn)