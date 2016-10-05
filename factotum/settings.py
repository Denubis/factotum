import os
import requests
import json
import codecs

from .factoriopath import getFactorioPath
from .diceware import generatePhrase

def getSettingsFile():
	FACTORIOPATH = getFactorioPath()

	if os.path.isfile("%s/config/settings.json" % (FACTORIOPATH)):
		settingsFilePath="%s/config/settings.json" % (FACTORIOPATH)
	else:
		settingsFilePath="%s/data/server-settings.example.json" % (FACTORIOPATH)	
	return settingsFilePath


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



def getPassword():	
	FACTORIOPATH = getFactorioPath()

	try:

		with codecs.open("%s/config/settings.json" % (FACTORIOPATH), 'r', encoding='utf-8') as settings_file:
			settingsJson = json.load(settings_file)			
			return settingsJson["game_password"]

	except Exception as e:
		return "Unable to read settings.json. Error %s" % (e)		