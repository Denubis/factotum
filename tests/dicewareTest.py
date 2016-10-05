import unittest
from factotum.diceware import generatePhrase
import random
import re
from pkg_resources import resource_filename, Requirement



class TestDiceware(unittest.TestCase):	

	def setUp(self):
		self.path_to_diceware = resource_filename("factotum", "diceware.wordlist.asc")
		self.phrase = re.compile("[0-9]+\t(.*)")

		with open(self.path_to_diceware, "r") as diceware:
			passwordList = diceware.readlines()
			self.passwordArray = ([m.group(1) for l in passwordList for m in [self.phrase.search(l)] if m])

	def test_lenArray(self):
		self.assertEqual(len(self.passwordArray), 7776)

	def test_numWords(self):
		for numWords in range (0,20,2):
			with self.subTest(i=numWords):
				phrase = generatePhrase(numWords).split(" ")		
				matchedWords = 0		
				for word in phrase:
					if word in self.passwordArray:
						matchedWords = matchedWords + 1
				
				self.assertEqual(matchedWords, numWords)

if __name__ == '__main__':
    unittest.main()	