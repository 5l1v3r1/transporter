import time
start = time.time()

import sys
import netifaces
import os
import socket
from datetime import datetime
import codecs

def basic():
	print("Transporter v1.0 ( github.com/ivan-sincek/transporter )")
	print("")
	print("Usage:   python transporter.py -i interface -p protocol -f file")
	print("Example: python transporter.py -i eth0      -p 0        -f packet.txt")

def advanced():
	basic()
	print("")
	print("DESCRIPTION")
	print("   Send packets through raw sockets")
	print("INTERFACE")
	print("   Specify a network interface to use")
	print("   -i <interface> - eth0 | wlan0 | etc.")
	print("PROTOCOL")
	print("   Specify a network protocol")
	print("   Use '0' for ICMP")
	print("   Use '6' for TCP")
	print("   Use '7' for UDP")
	print("   Search web for additional network protocol numbers")
	print("   -p <protocol> - 0 | 6 | 17 | etc.")
	print("FILE")
	print("   Specify an input file with packet you want to send")
	print("   -f <file> - packet.txt | etc.")

interface = ""
protocol = ""
file = ""
abort = False

def validate(key, value):
	global interface
	global protocol
	global file
	global abort
	if key == "-i" and interface == "":
		interface = value
		try:
			netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]["addr"]
		except:
			abort = True
			print("ERROR: Interface is not valid")
	elif key == "-p" and protocol == "":
		protocol = value
		if not protocol.isdigit():
			abort = True
			print("ERROR: Protocol is not valid")
	elif key == "-f" and file == "":
		file = value
		if not os.path.isfile(file):
			abort = True
			print("ERROR: File does not exists")
		elif not os.stat(file).st_size > 0:
			abort = True
			print("ERROR: File is empty")

missing = False

def check(key):
	global interface
	global protocol
	global file
	global missing
	if key != "-i" and key != "-p" and key != "-f" or interface == "" or protocol == "" or file == "":
		missing = True

def timestamp(text):
	print(("{0} -- {1}").format(text, datetime.now().strftime("%H:%M:%S %m-%d-%Y")))

def send(interface, protocol, file):
	s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
	s.settimeout(1)
	error = False
	try:
		s.bind((interface, int(protocol)))
	except socket.error as ex:
		error = True
		print(("ERROR: {0}").format(ex))
	if not error:
		timestamp("Sending packets has started")
		packet = open(file, "rb").read()
		packet = (b"").join(packet.split())
		packet = codecs.encode(packet.decode("unicode_escape"), "raw_unicode_escape")
		count = 0
		try:
			s.send(packet)
			count = count + 1
		except socket.timeout:
			print("Timed out")
		except socket.error as ex:
			print(("ERROR: {0}").format(ex))
		timestamp("Sending packets has ended")
		print(("Total packets sent {0}").format(count))
		if count:
			print("")
			timestamp("Waiting for response has started")
			response = ""
			try:
				while True:
					data = s.recv(1024)
					if not data:
						break
					response += data.decode("unicode_escape")
			except socket.timeout:
				print("Timed out")
			except socket.error as ex:
				print(("ERROR: {0}").format(ex))
			timestamp("Waiting for response has ended")
			if response:
				file = "transporter_response.txt"
				open(file, "w").write(response)
				print(("Response has been saved in '{0}' file").format(file))
			else:
				print("No response recieved")
	s.close()

argc = len(sys.argv)

if argc == 1:
	abort = True
	advanced()
elif argc == 2:
	abort = True
	if sys.argv[1] == "-h":
		basic()
	elif sys.argv[1] == "--help":
		advanced()
	else:
		print("ERROR: Incorrect usage")
		print("Use -h for basic and --help for advanced info")
elif argc == 7:
	validate(sys.argv[1], sys.argv[2])
	validate(sys.argv[3], sys.argv[4])
	validate(sys.argv[5], sys.argv[6])
	check(sys.argv[1])
	check(sys.argv[3])
	check(sys.argv[5])
	if missing:
		abort = True
		print("ERROR: Missing a mandatory option (-i, -p, -f)")
		print("Use -h for basic and --help for advanced info")
else:
	abort = True
	print("ERROR: Incorrect usage")
	print("Use -h for basic and --help for advanced info")

if not abort:
	print("#######################################################################")
	print("#                                                                     #")
	print("#                             Transporter                             #")
	print("#                                    by Ivan Sincek                   #")
	print("#                                                                     #")
	print("# Send packets through raw sockets.                                   #")
	print("# GitHub repository at github.com/ivan-sincek/transporter.            #")
	print("# Feel free to donate bitcoin at 1BrZM6T7G9RN8vbabnfXu4M6Lpgztq6Y14.  #")
	print("#                                                                     #")
	print("#######################################################################")
	send(interface, protocol, file)
	end = time.time()
	print("")
	print(("Script has finished in {0:0.9f}").format(end - start))
