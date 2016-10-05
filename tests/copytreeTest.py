import unittest
from factotum import factotum
import random
import re
from pkg_resources import resource_filename, Requirement


class TestCopytree(fake_filesystem_unittest.TestCase):
	def setUp(self):
        self.setUpPyfakefs()

	def tearDown(self):
        # It is no longer necessary to add self.tearDownPyfakefs()
        pass       