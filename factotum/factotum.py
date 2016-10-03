"""
FactoryFactoum -- a CLI for managing the headless linux factorio server
By: Brian Ballsun-Stanton
GPL v3
"""

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
from pkg_resources import resource_filename, Requirement
import glob
import stat
from requests.auth import HTTPDigestAuth
import urllib
import getpass



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

	path_to_diceware = resource_filename("factotum", "diceware.wordlist.asc")

	with open(path_to_diceware, "r") as diceware:
		password = diceware.readlines()
		password = [m.group(1) for l in password for m in [phrase.search(l)] if m]
		random.SystemRandom().shuffle(password)
		return ' '.join(password[0:numWords])



def newFactorioMap():
	FACTORIOPATH = getFactorioPath()

	mapFileExamplePath="%s/data/map-gen-settings.example.json" % (FACTORIOPATH)
	mapFilePath="%s/config/mapsettings.json" % (FACTORIOPATH)

	if not os.path.isfile(mapFilePath):		
		with codecs.open(mapFileExamplePath, 'r', encoding='utf-8') as map_file:
			mapJson = json.load(map_file)
	
			mapJson['starting_area'] = "very-high"

			for control in mapJson['autoplace_controls']:
				mapJson['autoplace_controls'][control]['size'] = "high"
				mapJson['autoplace_controls'][control]['richness'] = "very-high"
				mapJson['autoplace_controls'][control]['frequency'] = "low"

		with codecs.open(mapFilePath, 'w', encoding='utf-8') as map_file:
			json.dump(mapJson, map_file, indent=4)


	print(subprocess.check_output(
					["%s/bin/x64/factorio" % (FACTORIOPATH), 
					 "--create", "%s/saves/%s" % (FACTORIOPATH, 'Headless-{:%Y%m%d-%H%M%S}'.format(datetime.datetime.now())),
					 "--map-gen-settings", "%s/config/mapsettings.json" % (FACTORIOPATH)	]
					 ).decode("unicode_escape"))


def getSettingsFile():
	FACTORIOPATH = getFactorioPath()

	if os.path.isfile("%s/config/settings.json" % (FACTORIOPATH)):
		settingsFilePath="%s/config/settings.json" % (FACTORIOPATH)
	else:
		settingsFilePath="%s/data/server-settings.example.json" % (FACTORIOPATH)	
	return settingsFilePath

def updateFactorio():
	FACTORIOPATH = getFactorioPath()

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



def getFactorioPath():
	try:
		with open("%s/.factorioPath" % (expanduser("~")), "r") as data_file:
			path = data_file.readline().strip()
	except:
		print("%s/.factorioPath not found. Using default." % (expanduser("~")))
		if os.path.isdir("/opt/factorio"):
			path = "/opt/factorio"
		elif os.access("/opt", os.W_OK):
			path = "/opt/factorio"
		else:
			path = "%s/factorio" % (expanduser("~"))
	return path



def getPassword():	
	FACTORIOPATH = getFactorioPath()

	try:

		with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r', encoding='utf-8') as settings_file:
			settingsJson = json.load(settings_file)			
			return settingsJson["game_password"]

	except Exception as e:
		return "Unable to read settings.json. Error %s" % (e)


def rconCmd(cmd):
	host = "localhost"
	port = 27015

	
	with open("/tmp/factorioRcon", "r") as phraseFile:
		phrase = phraseFile.readline().strip()

		cmd = ' '.join(cmd)
		loop = asyncio.get_event_loop()
		conn = RconConnection(host, port, phrase)
		resp = loop.run_until_complete(conn.exec_command(cmd))
		print(resp, end='')	


def safeUpdate():
	FACTORIOPATH = getFactorioPath()

	if os.path.isdir("%s" % (FACTORIOPATH) ): 
		updateFactorio()
	else:
		print("Cannot update factorio. %s does not exist." % (FACTORIOPATH))
		sys.exit(1)



def safeInstall():
	FACTORIOPATH = getFactorioPath()

	try:
		if not os.path.isdir("%s" % (FACTORIOPATH) ):		

			if os.access("%s/.." % (FACTORIOPATH), os.W_OK):
				os.mkdir(FACTORIOPATH, 0o755)
			else:
				subprocess.call(['sudo', 'mkdir', '-p', FACTORIOPATH])
				subprocess.call(['sudo', 'chown', getpass.getuser(), FACTORIOPATH])
							

			os.mkdir(os.path.join(FACTORIOPATH, "saves"))
			os.mkdir(os.path.join(FACTORIOPATH, "config"))
			with open("%s/.bashrc" % (expanduser("~")), "r+") as bashrc:
				lines = bashrc.read()
				
				if lines.find("eval \"$(_FACTOTUM_COMPLETE=source factotum)\"\n") == -1:
					bashrc.write("eval \"$(_FACTOTUM_COMPLETE=source factotum)\"\n")
					print("You'll want to restart your shell for command autocompletion. Tab is your friend.")
		updateFactorio()
	except IOError as e:
		print("Cannot make %s. Please check permissions. Error %s" % (FACTORIOPATH, e))
		sys.exit(1)
	


def configSetup(servername, description, tag, visibility, serverpassword, genserverpasswordwords, admins, ignoreplayerlimit, afk, uploadrate, updatepassword):
	FACTORIOPATH = getFactorioPath()
	
	
	if updatepassword:
		if serverpassword:
			password=serverpassword
		elif genserverpasswordwords > 0:
			password=generatePhrase(genserverpasswordwords)
		else:
			password=""

		

	try:
		with codecs.open(getSettingsFile(), 'r', encoding='utf-8') as settings_file:

			settingsJson = json.load(settings_file)
			if servername:
				settingsJson['name'] = servername
			if description:
				settingsJson['description'] = description
			if tag:
				settingsJson['tags'] = tag
			if admins:
				settingsJson['admins'] = admins
			if ignoreplayerlimit:
				settingsJson['ignore_player_limit_for_returning_players'] = ignoreplayerlimit
			if afk:
				settingsJson['afk_autokick_interval'] = afk
			if uploadrate:
				settingsJson['max_upload_in_kilobytes_per_second'] = uploadrate
			if updatepassword:
				settingsJson["game_password"] = password
			settingsJson['visibility'] = visibility
			
			
		with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'w', encoding='utf-8') as settingsFile:
			json.dump(settingsJson, settingsFile, indent=4)

		print("The server password is: \"%s\" " % getPassword())

	except:
		print("Cannot write settings file.")

def configAuthenticate(username, password):
	FACTORIOPATH = getFactorioPath()

	url = "https://auth.factorio.com/api-login"
	params = {'username': username, 'password': password, 'apiVersion': 2}


	if not os.path.isfile("%s/bin/x64/factorio" % (FACTORIOPATH) ):
		print("Could not find factorio at %s" % (FACTORIOPATH))
		sys.exit(1)


	print("Fetching token for %s" %  (username))
	myResponse = requests.post(url,data=params, verify=True)
	if(myResponse.ok):

	    jData = json.loads(myResponse.text)
	    print("Writing %s to settings.json" % (jData[0]))
	    
	else:
	  # If response code is not ok (200), print the resulting http error code with description
	    myResponse.raise_for_status()
	    sys.exit(1)
	

	try:
		with codecs.open(getSettingsFile(), 'r', encoding='utf-8') as settings_file:
			settingsJson = json.load(settings_file)
			settingsJson['token'] = jData[0]
			settingsJson['username'] = username
				


		with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'w', encoding='utf-8') as settings_file:
			json.dump(settingsJson, settings_file, indent=4)
	except Exception as e:
		print(e)
		print("Help! Can't deal with the settings file!")		

@click.group()
def cli():
	pass


@click.command(cls=DaemonCLI, daemon_params={'pidfile': '/tmp/factorio.pid'})
def factorio():
	"""Factotum for Factorio server stuff. Runs the server. Start with `factorio start`. Help with `factorio --help`."""
	FACTORIOPATH = getFactorioPath()

	phrase = generatePhrase(6)
	with open("/tmp/factorioRcon", "w") as phraseFile:
		phraseFile.write(phrase)

	with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r+', encoding='utf-8') as settings_file:
		try:
			settingsJson = json.load(settings_file)
		except Exception as e:
			print("Problem with settings file.")
			print(e)
			sys.exit(1)


	if not filter(os.path.isfile, glob.glob('%s/saves/*.zip' % (FACTORIOPATH))):
		print("Cannot find a save file. Exiting.")
		sys.exit(1)

	myprogram = {"cmd": "%s/bin/x64/factorio --rcon-port 27015 --rcon-password \"%s\" --start-server-load-latest --server-settings %s/config/settings.json" % (FACTORIOPATH, phrase, FACTORIOPATH) , "numprocesses": 1}

	arbiter = get_arbiter([myprogram])
	try:
			arbiter.start()
	finally:
		os.remove("/tmp/factorioRcon")
		arbiter.stop()


@click.command()
def password():
	"""Get the server game password"""
	print("The server password is: \"%s\" " % (getPassword()))


@click.argument("cmd", nargs=-1)	

@click.command()
def rcon(cmd):
	"""Pass an rcon command to the server. Find out possible by saying rcon /help"""
	rconCmd(cmd)


@click.command()
def update():
	"""Download and unpack latest factorio."""
	safeUpdate()
		

@click.command()
def newMap():
	"""Generate a new map."""
	newFactorioMap()
		


@click.command()
def install():
	"""Create the FACTORIOPATH directory, then download and unpack factorio.""" 
	safeInstall()


@click.command()
@click.option('--servername', help="Name of the server for public listings.")
@click.option('--description',  help="Description of the server for public listings.")
@click.option('--visibility', default="public", help="Default: public. public/lan/hidden")
@click.option('--serverpassword', help='To set the server password')
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')
@click.option('--tag','-t', help="Tags for the server list.", multiple=True)
@click.option('--admins','-a', help="Set default admin names.", multiple=True)
@click.option('--ignorePlayerLimit/--noIgnorePlayerLimit', help="Enable/Disable ignore Player Limit for returing players.")
@click.option('--afk', help='Set the afk timeout in minutes')
@click.option('--uploadrate', help='Upload limit in kbps', type=click.INT)
@click.option('--UpdatePassword/--noUpdatePassword', '-u/-n', help="Don't change the json password", default=True)


def setup(servername, description, tag, visibility, serverpassword, genserverpasswordwords, admins, ignoreplayerlimit, afk, uploadrate, updatepassword):
	"""Setup tasks for deploying a server."""
	configSetup(servername, description, tag, visibility, serverpassword, genserverpasswordwords, admins, ignoreplayerlimit, afk, uploadrate, updatepassword)

@click.command()
@click.option('--username', prompt=True,  help="Name of the server for public listings.")
@click.option('--password', prompt=True, hide_input=True, help="Description of the server for public listings.")

def authenticate(username, password):
	"""Save an authentication token from factorio"""
	configAuthenticate(username, password)



@click.command()
@click.option('--genServerPasswordWords','-g', default=4, help='Default 4. Generate a random password with this many words.')
def diceware(genserverpasswordwords):
	"""Generates a diceware password for the user."""
	print(generatePhrase(genserverpasswordwords))

@click.command()
@click.option('--username', prompt=True,  help="Name of the server for public listings.")
@click.option('--password', prompt=True, hide_input=True, help="Description of the server for public listings.")
@click.option('--servername', prompt=True, help="Name of the server for public listings.")
@click.option('--description', prompt=True, help="Description of the server for public listings.")
@click.option('--tag','-t', prompt=True, help="Tag for the server list. (You can deploy multiple with factotum setup")
@click.option('--admin','-a',prompt=True, help="Set default admin (You can deploy multiple with factotum setup).")


def fulldeploy(username, password, servername, description, tag, admin):
	"""Completely deploy a factorio server. Prompt for install, authenticate, setup, and newmap"""
	safeInstall()
	configAuthenticate(username, password)
	newFactorioMap()
	configSetup(servername=servername, 
				description=description, 
				tag=tag, 
				visibility="public", 
				serverpassword=None, 
				genserverpasswordwords=4, 
				admins=admin, 
				ignoreplayerlimit=True, 
				afk=5, 
				uploadrate=None, 
				updatepassword=True)
	
	
	print("Now run: factotum start")

cli.add_command(password)
cli.add_command(factorio)
cli.add_command(rcon)
cli.add_command(update)
cli.add_command(newMap)
cli.add_command(install)
cli.add_command(setup)
cli.add_command(authenticate)
cli.add_command(fulldeploy)
cli.add_command(diceware)




if __name__ == '__main__':
	cli()    
