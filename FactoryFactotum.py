#!/usr/bin/env python
from __future__ import print_function

'''
FactoryFactoum -- a CLI for managing the headless linux factorio server
By: Brian Ballsun-Stanton
GPL v3

Usage
'''
'''
import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
			  help='The person to greet.')
def hello(count, name):
	"""Simple program that greets NAME for a total of COUNT times."""
	for x in range(count):
		click.echo('Hello %s!' % name)

if __name__ == '__main__':
	hello()

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
import urllib2
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

FACTORIOPATH = "/opt/factorio"
DOWNLOADURL = "https://www.factorio.com/get-download/latest/headless/linux64"


try:
	with open("%s.factorioPath" % (expanduser("~"))) as data_file:
		FACTORIOPATH = data_file.readline()
except:
	print("%s/.factorioPath not found. Using default." % (expanduser("~")))
	FACTORIOPATH = "/opt/factorio"


print("Factorio path: %s" % (FACTORIOPATH))



try:
	with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r+', encoding='utf-8') as settings_file:
		settingsJson = json.load(settings_file)
		print("The server password is: \"%s\" " % settingsJson["game_password"])

except:
	print("Unable to read settings.json")

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


def generatePhrase(numWords):
	phrase = re.compile("[0-9]+\t(.*)")
	

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


	factorio1 = ptyprocess.PtyProcessUnicode.spawn(["%s/bin/x64/factorio" % (FACTORIOPATH), "--create", os.path.join(FACTORIOPATH,"saves/", 'Headless-{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now())), "--map-gen-settings", os.path.join(FACTORIOPATH, "config/mapsettings.json") ])

	time.sleep(10)

	with codecs.open("%s/factorio-current.log" % (FACTORIOPATH), 'r+', encoding='utf-8') as log: 
		for line in log.readline():
			print(line, end="")


def updateFactorio():
	file_name = "/tmp/latestFactorio.tar.gz"
	print("Downloading %s" % file_name)

	r = requests.get(DOWNLOADURL, stream=True)
	total_length = int(r.headers.get('content-length'))

	if total_length != os.path.getsize(file_name):
		with open(file_name, 'wb') as f:
			for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
				if chunk:
					f.write(chunk)
					f.flush()
	else:
		print("File already exists and file sizes match. Skipping download.")	

	tar = tarfile.open(file_name, "r:gz")
	tar.extractall(path="/tmp")
	tar.close()


	for filename in os.listdir("/tmp/factorio"):
		shutil.move(os.path.join("/tmp/factorio", filename), os.path.join(FACTORIOPATH, filename))
	



@click.group()
def daemonClick():
	pass

@daemonClick.command(cls=DaemonCLI, daemon_params={'pidfile': '/tmp/factorio.pid'})

def factorio():
	"""Factotum for Factorio server stuff. Runs the server. Start with `factorio start`. Help with `factorio --help`."""
	



	from circus import get_arbiter

	myprogram = {"cmd": "%s/bin/x64/factorio --start-server-load-latest --server-settings %s/config/settings.json" % (FACTORIOPATH, FACTORIOPATH) , "numprocesses": 1}

	arbiter = get_arbiter([myprogram])
	try:
	    arbiter.start()
	finally:
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
			os.mkdir(FACTORIOPATH, 0755)
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
	
	print(servername, description, [str(x) for x in tag], visibility, serverpassword, genserverpasswordwords)
	
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
				settingsJson['tags'] = [str(x) for xs in tag]


			settingsJson["game_password"] = password
			settingsJson['visibility'] = visibility
			
			settings_file.seek(0)
			json.dump(settingsJson, settings_file, indent=4)

	except (ValueError, IOError) as e:
		print(e)
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
""" % (servername or "Headless factorio server", description or "Headless factorio server generated by denubis' scripts", "[\"%s\"]" % ('","'.join(tag)), visibility, password)
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
			f = tempfile.NamedTemporaryFile()
			f.write(settings)
			f.seek(0)
			#print f.read()
			print("Settings file: %s" % (f.name))
			factorio1 = ptyprocess.PtyProcessUnicode.spawn(["%s/bin/x64/factorio" % (FACTORIOPATH), "--create", "/opt/factorio/saves/authenticateMap" ])

			time.sleep(10)

			with codecs.open("%s/factorio-current.log" % (FACTORIOPATH), 'r+', encoding='utf-8') as log: 
				for line in log.readline():
					print(line, end="")

			print("Map made.")
			factorio2 = ptyprocess.PtyProcessUnicode.spawn(["%s/bin/x64/factorio" % (FACTORIOPATH), "--start-server-load-latest","--until-tick","100","--no-auto-pause", "--server-settings", f.name ])
			
			time.sleep(5)
			
			factorio2.write("/quit\n")
			time.sleep(5)				
			with codecs.open("%s/factorio-current.log" % (FACTORIOPATH), 'r+', encoding='utf-8') as log: 
				for line in log.readline():
					print(line, end="")
			
			
			
			with open("%s/player-data.json" % (FACTORIOPATH)) as data_file:
				data = json.load(data_file)

			print(data['service-username'], data['service-token'])


			try:
				with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r+', encoding='utf-8') as settings_file:
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
				with open("%s/config/settings.json" % (FACTORIOPATH), 'w') as settings_file:
					settings_file.write(updated_settings)
					settings_file.close()

		finally:
			f.close()



cli = click.CommandCollection(sources=[daemonClick, settingsClick, authClick, installClick, updateClick, mapClick])

if __name__ == '__main__':
	cli()    

