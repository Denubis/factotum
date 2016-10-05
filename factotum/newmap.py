"""
This is the newmap module.
Calling this will make a new map in FACTORIOPATH/saves/Headless-YYMMDD-HHMMSS.zip

"""

import os
import codecs
import json
import subprocess
import datetime
from .factoriopath import getFactorioPath

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
