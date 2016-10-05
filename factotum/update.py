import os
import shutil
import stat
import requests
import tarfile
import subprocess
import getpass
from clint.textui import progress

from .factoriopath import getFactorioPath

DOWNLOADURL = "https://www.factorio.com/get-download/latest/headless/linux64"
FACTORIOPATH = getFactorioPath()





def safeUpdate():
	FACTORIOPATH = getFactorioPath()

	if os.path.isdir("%s" % (FACTORIOPATH) ): 
		updateFactorio()
	else:
		print("Cannot update factorio. %s does not exist." % (FACTORIOPATH))
		sys.exit(1)

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
			with open("%s/.bashrc" % (os.path.expanduser("~")), "r+") as bashrc:
				lines = bashrc.read()
				
				if lines.find("eval \"$(_FACTOTUM_COMPLETE=source factotum)\"\n") == -1:
					bashrc.write("eval \"$(_FACTOTUM_COMPLETE=source factotum)\"\n")
					print("You'll want to restart your shell for command autocompletion. Tab is your friend.")
		updateFactorio()
	except IOError as e:
		print("Cannot make %s. Please check permissions. Error %s" % (FACTORIOPATH, e))
		sys.exit(1)
