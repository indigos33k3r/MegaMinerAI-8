#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#from subprocess import Popen, PIPE, STDOUT
#import os, shutil
from os.path import isdir, exists, join, split
import traceback
#from bz2 import compress, decompress
import time
#from git import *
import sys
from WebServerInterface import *
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from celery.task import task
import pexpect
from os import remove
from subprocess import Popen

AWS_ACCESS_KEY = 'AKIAICYAQREP6CMTOZ7Q'

AWS_SECRET_KEY = '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'

password = 'blastfromthepast'

webserver=WebServerInterface('megaminerai.com')
s3conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
logbucket = s3conn.get_bucket("megaminer7")

startport = 20000
count = 0
tentacle = "2"
rootdir = '/tmp/'+tentacle+'/'

repositories = dict()

working_copies=dict()

Popen("cp -r "+ "/home/ubuntu/megaminer7/server "+rootdir+"server", shell = True).wait()
Popen("rm -rf "+rootdir+"/*", shell = True).wait()

def getPort():
  global count
  count = count + 1
  return startport+count

def update(program):
  print "updating",program
  webs = webserver.get_ssh_path(program)
  path = webs['path']
  commit = webs['commit_id']
  repositories[program] = split(path)[1][:-4]
  if commit == None or commit == '':
    print "bad request, no commit version"
    return "Git setup wrong for"+program
  working_copies[program]=commit
  if not exists(rootdir+repositories[program]):
    p = pexpect.spawn('rm -rf '+rootdir+split(path)[1][:-4])
    i = p.expect([pexpect.EOF])
    print 'cloning'
    command = "git clone ssh://mmweb@r99acm.device.mst.edu:2222" + path
    cwd = rootdir
  else:
    #first git clean
    p = pexpect.spawn("git checkout master", cwd = rootdir+repositories[program])
    i = p.expect([pexpect.EOF])
    #print p.before
    p = pexpect.spawn("git clean -f", cwd = rootdir+repositories[program])
    i = p.expect([pexpect.EOF])
    #print p.before
    print 'pulling'
    command = "git pull"
    cwd = rootdir+repositories[program]
  p = pexpect.spawn(command, cwd = cwd, timeout = 120) 
  print "spawned a process:",command
  i = p.expect(['Password:',pexpect.EOF], timeout = 120)
  if i == 0:
    p.sendline(password)
    i = p.expect([pexpect.EOF, pexpect.TIMEOUT], timeout = 120)
    if i == 1:
      print "error in git"
      print p.before
      return "Git clone timed out for "+program
  else:
    print "ERROR, can't clone git directory of",program
    print p.before
    return "Git clone timed out for "+program
  if commit != None:
    p = pexpect.spawn("git checkout "+commit,cwd = rootdir+repositories[program])
    i = p.expect(['fatal',pexpect.EOF])
    if i == 0:
      print "failed to get the build",commit
      print p.before
      return "Failed to get commit "+str(commit)+" for "+program
  
  if program != 'server':
    p = pexpect.spawn("make", cwd = rootdir+repositories[program])
    i = p.expect(['Error',pexpect.EOF], timeout = 60)
    if i == 0:
      print "failed to make"
      return "Faild to make "+program
    p = pexpect.spawn("chmod +x run", cwd = rootdir+repositories[program])
    i = p.expect([pexpect.EOF])
  return "good!"

@task
def run_game(client1, client2, name):
  c1_status = update(client1)
  if c1_status != "good!":
    return ("Error", c1_status)
  c2_status = update(client2)
  if c2_status != "good!":
    return ("Error", c2_status)
#  if not update('server'):
#    return -13
  port = getPort()
  startTime = time.time()
  #now start the server...
  serverp = pexpect.spawn('python main.py '+str(port), cwd = rootdir+'server/', timeout = 10)
  #i = serverp.expect(['Starting Server',pexpect.EOF])
  #if i == 0:
  #  print "server started"
  #else:
  #  print "server failed to start"
    #return -1
  time.sleep(2)
  #now client 1...
  client1p = Popen('/bin/bash ./run localhost:'+str(port), cwd = rootdir+repositories[client1], shell = True)
  i = serverp.expect(['Creating game 1',pexpect.EOF,pexpect.TIMEOUT])
  if i == 0:
    print "game created!"
  else:
    print "game failed to create:",i
    return ("Error","Game failed to create")
  #and client 2...
  client2p = Popen('/bin/bash ./run localhost:'+str(port)+' 0', cwd = rootdir+repositories[client2], shell = True)
  print "game started!"
  result = ''
  while time.time() < startTime + 600 and client1p.returncode == None and client2p.returncode == None and len(result) < 5:
    #result = serverp.expect(["Tie game!", "1 Wins!", "2 Wins", pexpect.TIMEOUT], timeout = 5)
    try:
      result = serverp.readline()
      if "win" not in result.lower() and "tie" not in result.lower():
        result = ''
    except:
      pass
  #result = serverp.readlines()
  print result
  print "game completed!"
  c1_score = 0
  c2_score = 0
  if "1" in result:# == "1 Wins!":
    c1_score = 1
    winner = client1
    print client1, "wins"
  elif "2" in result:# == "2 Wins!":
    c2_score = 1
    winner = client2
    print client2, "wins"
  elif "tie" in result.lower():# == "Tie game!":
    print "tie"
    winner = client2
    c2_score = 1
  elif result == '':
    print "someone crashed!"
  else:
    print "wat?",result
    return ("Error","Unknown results from server:"+result)
  serverp.close(True)
  client1p.kill()
  client2p.kill()

  logfile = open(rootdir+'server/logs/1.gamelog.bz2','rb')
  log = logfile.read()
  newkey = Key(logbucket)
  logname = 'logs/arena/'+str(tentacle)+'-'+str(time.time())+'.gamelog.bz2'
  newkey.key = logname
  newkey.set_contents_from_filename(rootdir+"server/logs/1.gamelog.bz2")
  webserver.set_game_stat(client1, client2, c1_score, c2_score, working_copies[client1], working_copies[client2], logname)
  remove(rootdir+"server/logs/1.gamelog")
  remove(rootdir+"server/logs/1.gamelog.bz2")
  
  return (winner, logname)

#run_game('Shell AI','Shell AI', 19000)

