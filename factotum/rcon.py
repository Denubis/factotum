from factoirc.rcon import RconConnection
import asyncio
import sys

def rconCmd(cmd):
	host = "localhost"
	port = 27015

	try:
		with open("/tmp/factorioRcon", "r") as phraseFile:
			phrase = phraseFile.readline().strip()

			cmd = ' '.join(cmd)
			loop = asyncio.get_event_loop()
			conn = RconConnection(host, port, phrase)
			resp = loop.run_until_complete(conn.exec_command(cmd))
			print(resp, end='')	
	except FileNotFoundError:
		print("Cannot find the rcon password. Is the server running?")
		sys.exit(1)