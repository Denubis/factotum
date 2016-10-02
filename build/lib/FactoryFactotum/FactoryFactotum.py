#!/usr/bin/env python3
'''
FactoryFactoum -- a CLI for managing the headless linux factorio server
By: Brian Ballsun-Stanton
GPL v3

'''


import time

import click
from daemonocle.cli import DaemonCLI

import os
import tempfile
import subprocess
import time
import json
import codecs
import ptyprocess
import io
import requests
from clint.textui import progress
import tarfile
import sys
import shutil
import datetime
import re
import random
from os.path import expanduser
import circus
import stat
from circus import get_arbiter
import inspect
import asyncio
from factoirc.rcon import RconConnection




FACTORIOPATH = "/opt/factorio"
DOWNLOADURL = "https://www.factorio.com/get-download/latest/headless/linux64"

#http://stackoverflow.com/a/22331852/263449
def copytree(src, dst, symlinks = False, ignore = None):
  if not os.path.exists(dst):
    os.makedirs(dst)
    shutil.copystat(src, dst)
  lst = os.listdir(src)
  if ignore:
    excl = ignore(src, lst)
    lst = [x for x in lst if x not in excl]
  for item in lst:
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if symlinks and os.path.islink(s):
      if os.path.lexists(d):
        os.remove(d)
      os.symlink(os.readlink(s), d)
      try:
        st = os.lstat(s)
        mode = stat.S_IMODE(st.st_mode)
        os.lchmod(d, mode)
      except:
        pass # lchmod not available
    elif os.path.isdir(s):
      copytree(s, d, symlinks, ignore)
    else:
      shutil.copy2(s, d)

#http://stackoverflow.com/a/22881871/263449
def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def generatePhrase(numWords):
	phrase = re.compile("[0-9]+\t(.*)")
	
	__location__ = get_script_dir()

	print(__location__)

	with open(os.path.join(__location__, 'diceware.wordlist.asc')) as diceware:
		password = diceware.readlines()
		password = [m.group(1) for l in password for m in [phrase.search(l)] if m]
		random.SystemRandom().shuffle(password)
		return ' '.join(password[0:numWords])



def newFactorioMap():
	if not os.path.isfile("%s/config/mapsettings.json" % (FACTORIOPATH) ):
		with open("%s/config/mapsettings.json" % (FACTORIOPATH), 'w') as mapsettingsfile:
			map="""{
  "_comment": "Sizes can be specified as none, very-low, low, normal, high, very-high",

  "terrain_segmentation": "normal",
  "water": "normal",
  "width": 0,
  "height": 0,
  "starting_area": "high",
  "peaceful_mode": false,
  "autoplace_controls":
  {
	"coal": {"frequency": "low", "size": "high", "richness": "very-high"},
	"copper-ore": {"frequency": "low", "size": "high", "richness": "very-high"},
	"crude-oil": {"frequency": "low", "size": "high", "richness": "very-high"},
	"enemy-base": {"frequency": "low", "size": "very-high", "richness": "very-high"},
	"iron-ore": {"frequency": "low", "size": "high", "richness": "very-high"},
	"stone": {"frequency": "low", "size": "high", "richness": "very-high"}
  }
}"""
			mapsettingsfile.write(map)
			mapsettingsfile.close()



	print(subprocess.check_output(
					["%s/bin/x64/factorio" % (FACTORIOPATH), 
					 "--create", "%s/%s" % (FACTORIOPATH, 'Headless-{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now())),
					 "--map-gen-settings", "%s/config/mapsettings.json" % (FACTORIOPATH)	]
					 ).decode("unicode_escape"))


	

def updateFactorio():
	file_name = "/tmp/latestFactorio.tar.gz"
	print("Downloading %s" % file_name)

	r = requests.get(DOWNLOADURL, stream=True)
	total_length = int(r.headers.get('content-length'))

	if not os.path.isfile(file_name) or total_length != os.path.getsize(file_name):
		with open(file_name, 'wb') as f:
			for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
				if chunk:
					f.write(chunk)
					f.flush()
	else:
		print("File already exists and file sizes match. Skipping download.")	

	if os.path.isfile(file_name) and os.access(FACTORIOPATH, os.W_OK):
		tar = tarfile.open(file_name, "r:gz")
		tar.extractall(path="/tmp")
		tar.close()

		copytree("/tmp/factorio", FACTORIOPATH)
		print("Success.")
	else:
		print("Help! Can't find %s, but I should have!" % (file_name))
		sys.exit(1)






try:
	with open("%s/.factorioPath" % (expanduser("~")), "r") as data_file:
		FACTORIOPATH = data_file.readline().strip()
except:
	print("%s/.factorioPath not found. Using default." % (expanduser("~")))
	FACTORIOPATH = "/opt/factorio"




@click.group()
def passwordClick():
	pass

@passwordClick.command()
def password():
	"""Get the server game password"""
	try:
		with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r+', encoding='utf-8') as settings_file:
			settingsJson = json.load(settings_file)
			print("The server password is: \"%s\" " % settingsJson["game_password"])

	except Exception as e:
		print("Unable to read settings.json. Error %s" % (e))


@click.group()
def rconClick():
	pass

@click.argument("cmd", nargs=-1)	

@rconClick.command()
def rcon(cmd):
	"""Pass an rcon command to the server. Find out possible by saying rcon /help"""
	host = "localhost"
	port = 27015

	
	with open("/tmp/factorioRcon", "r") as phraseFile:
		phrase = phraseFile.readline().strip()

		cmd = ' '.join(cmd)
		loop = asyncio.get_event_loop()
		conn = RconConnection(host, port, phrase)
		resp = loop.run_until_complete(conn.exec_command(cmd))
		print(resp, end='')	
		


@click.group()
def daemonClick():
	pass

@daemonClick.command(cls=DaemonCLI, daemon_params={'pidfile': '/tmp/factorio.pid'})

def factorio():
	"""Factotum for Factorio server stuff. Runs the server. Start with `factorio start`. Help with `factorio --help`."""

	phrase = generatePhrase(6)
	with open("/tmp/factorioRcon", "w") as phraseFile:
		phraseFile.write(phrase)

	myprogram = {"cmd": "%s/bin/x64/factorio --rcon-port 27015 --rcon-password \"%s\" --start-server-load-latest --server-settings %s/config/settings.json" % (FACTORIOPATH, phrase, FACTORIOPATH) , "numprocesses": 1}

	arbiter = get_arbiter([myprogram])
	try:
	    arbiter.start()
	finally:
		os.remove("/tmp/factorioRcon")
		arbiter.stop()


@click.group()
def updateClick():
	pass

@updateClick.command()
def update():
	"""Download and unpack latest factorio."""
	if os.path.isdir("%s" % (FACTORIOPATH) ): 
		updateFactorio()
	else:
		print("Cannot update factorio. %s does not exist." % (FACTORIOPATH))
		sys.exit(1)
		


@click.group()
def mapClick():
	pass

@mapClick.command()
def newMap():
	"""Generate a new map."""
	newFactorioMap()
		


@click.group()
def installClick():
	pass

@updateClick.command()
def install():
	"""Create the FACTORIOPATH directory, then download and unpack factorio.""" 
	try:
		if not os.path.isdir("%s" % (FACTORIOPATH) ):
			os.mkdir(FACTORIOPATH, 0o755)
			os.mkdir(os.path.join(FACTORIOPATH, "saves"))
		updateFactorio()
	except IOError as e:
		print("Cannot make %s. Please check permissions. Error %s" % (FACTORIOPATH, e))
		sys.exit(1)
	


@click.group()
def settingsClick():
	pass

@settingsClick.command()
@click.option('--servername', prompt=True, help="Name of the server for public listings.")
@click.option('--description', prompt=True,  help="Description of the server for public listings.")
@click.option('--visibility', default="public", help="Default: public. public/lan/hidden")
@click.option('--serverpassword', help='To set the server password')
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')
@click.option('--tag','-t', help="Tags for the server list.", multiple=True)

def setup(servername, description, tag, visibility, serverpassword, genserverpasswordwords):
	"""Setup tasks for deploying a server."""
	
	
	tags = [str(x) for x in tag]
	print(servername, description, tags, visibility, serverpassword, genserverpasswordwords)

	if serverpassword:
		password=serverpassword
	elif genserverpasswordwords > 0:
		password=generatePhrase(genserverpasswordwords)
	else:
		password=""

	print("The server password is: \"%s\" " % password)

	try:
		with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r+', encoding='utf-8') as settings_file:

			settingsJson = json.load(settings_file)
			if servername:
				settingsJson['name'] = servername
			if description:
				settingsJson['description'] = description
			if tag:
				settingsJson['tags'] = tags


			settingsJson["game_password"] = password
			settingsJson['visibility'] = visibility
			
			settings_file.seek(0)
			json.dump(settingsJson, settings_file, indent=4)

	except (ValueError, IOError) as e:
		
		updated_settings="""{
  "name": "%s",
  "description": "%s",
  "tags": %s,
  "max_players": "0",

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server - test",
						  "lan: Game will be broadcast on LAN",
						  "hidden: Game will not be published anywhere"],
  "visibility": "%s",

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "",
  "password": "",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "",

  "game_password": "%s",

  "_comment_verify_user_identity": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "verify_user_identity": true,
  "_commend_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0
}
""" % (servername or "Headless factorio server", description or "Headless factorio server generated by denubis' scripts", "[\"%s\"]" % ('","'.join(tags)), visibility, password)
		with open("%s/config/settings.json" % (FACTORIOPATH), 'w') as settings_file:
			settings_file.write(updated_settings)
			settings_file.close()

@click.group()
def authClick():
	pass

@authClick.command()
@click.option('--username', prompt=True,  help="Name of the server for public listings.")
@click.option('--password', prompt=True, hide_input=True, help="Description of the server for public listings.")

def authenticate(username, password):
	"""Save an authentication token from factorio"""
	print("Fetching token for %s" %  (username))
	if not os.path.isfile("%s/bin/x64/factorio" % (FACTORIOPATH) ):
		print("Could not find factorio at %s" % (FACTORIOPATH))
		sys.exit(1)
	else:
		settings="""{
  "name": "Name of the game as it will appear in the game listing",
  "description": "Description of the game that will appear in the listing",
  "tags": ["game", "tags"],
  "max_players": "0",

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server",
						  "lan: Game will be broadcast on LAN",
						  "hidden: Game will not be published anywhere"],
  "visibility": "hidden",

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "%s",
  "password": "%s",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "",

  "game_password": "",

  "_comment_verify_user_identity": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "verify_user_identity": true,
  "_commend_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0
}
""" % (username, password)
		try:
			f = tempfile.NamedTemporaryFile(mode='w')
			f.write(settings)
			f.seek(0)
			#print f.read()
			print("Settings file: %s" % (f.name))

			print(subprocess.check_output(
					["%s/bin/x64/factorio" % (FACTORIOPATH), 
					 "--create", "%s/saves/AuthenticateMap" % (FACTORIOPATH)]
					 ).decode("unicode_escape"))


			print("Briefly loading server...")



			auth = subprocess.Popen(
					["%s/bin/x64/factorio" % (FACTORIOPATH), 
					 "--start-server", "%s/saves/AuthenticateMap.zip" % (FACTORIOPATH),
					 "--server-settings", f.name
					 ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True
					 )

			
			time.sleep(5)
			outs, errs = auth.communicate(input="/quit\n")
			print(outs)
		
			
			
			with open("%s/player-data.json" % (FACTORIOPATH), 'r+') as data_file:
				data = json.load(data_file)

			print(data['service-username'], data['service-token'])


			try:
				with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'a+', encoding='utf-8') as settings_file:
					settingsJson = json.load(settings_file)
					settingsJson['token'] = data['service-token']
					settingsJson['username'] = data['service-username']
					settings_file.seek(0)
					json.dump(settingsJson, settings_file, indent=4)
			except (ValueError, IOError):
				updated_settings="""{
  "name": "Name of the game as it will appear in the game listing",
  "description": "Description of the game that will appear in the listing",
  "tags": ["game", "tags"],
  "max_players": "0",

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server",
						  "lan: Game will be broadcast on LAN",
						  "hidden: Game will not be published anywhere"],
  "visibility": "hidden",

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "%s",
  "password": "",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "%s",

  "game_password": "",

  "_comment_verify_user_identity": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "verify_user_identity": true,
  "_commend_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0
}
""" % (data['service-username'], data['service-token'])
				with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'a+') as settings_file:
					settings_file.write(updated_settings)
					settings_file.close()

		finally:
			f.close()



cli= click.CommandCollection(sources=[daemonClick, settingsClick, authClick, installClick, updateClick, mapClick, rconClick, passwordClick])



if __name__ == '__main__':
	cli()    