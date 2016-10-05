import sys
import random
import re
from pkg_resources import resource_filename, Requirement


def generatePhrase(numWords):
	phrase = re.compile("[0-9]+\t(.*)")

	path_to_diceware = resource_filename("factotum", "diceware.wordlist.asc")

	with open(path_to_diceware, "r") as diceware:
		password = diceware.readlines()
		password = [m.group(1) for l in password for m in [phrase.search(l)] if m]
		random.SystemRandom().shuffle(password)
		return ' '.join(password[0:numWords])
