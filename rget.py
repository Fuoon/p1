import socket as s
import os

# rget -o test1.txt www.w3.org

#get users input
print "Format: rget -o <output file> http://someurl.domain[:port]/path/to/file"
print "Example: rget -o test.txt http://www.google.com/, [:port] is optional"
inputCommand = raw_input("Enter command: ")

name = inputCommand.split(" ")[2]
fileName = name.split(".")[0]
fileExt = "." + name.split(".")[1]
fileTmpExt = ".tmp"
filePath = 'files/'
trackerPath = 'tracker/'
trackerName = "tracker.txt"

serverSocket = s.socket(s.AF_INET, s.SOCK_STREAM)

url = inputCommand.split(" ")[3]
if url.find(".com") != -1:
	if url.split(".com")[0].find("//") != -1:
		host = url.split(".com")[0].split("//")[1] + ".com"
	else:
		host = url.split(".com")[0] + ".com"
	if url.split(".com")[1].find(":") != -1:
		path = url.split(".com")[1].split(":")[1]
		serverPort = int(url.split(".com")[1].split(":")[0])
	else:
		path = url.split(".com")[1]
		serverPort = 80	
	remote_ip = s.gethostbyname( host )
	# Connect to the server
	serverSocket.connect((remote_ip, serverPort))
elif url.find(".org") != -1:
	if url.split(".org")[0].find("//") != -1:
		host = url.split(".org")[0].split("//")[1] + ".org"
	else:
		host = url.split(".org")[0] + ".org"
	if url.split(".org")[1].find(":") != -1:
		path = url.split(".org")[1].split(":")[1]
		serverPort = int(url.split(".org")[1].split(":")[0])
	else:
		path = url.split(".org")[1]
		serverPort = 80
	remote_ip = s.gethostbyname( host )
	# Connect to the server
	serverSocket.connect((remote_ip, serverPort))

def getTracker(fileName, host, path, size):
	f = open(os.path.join(trackerPath, trackerName), 'r')
	trackFile = f.read()
	trackList = trackFile.split("\n")
	trackChecker = fileName + " " + host + " " + path + "_" + size
	for i in trackList:
		if i == trackChecker:
			track = trackChecker.split("_")[1]
			return int(track)

def resume(size):
	track = getTracker(fileName+fileTmpExt, host, path, size)
	message = "GET " + path + " HTTP/1.1\r\n" + "Host: " + host + "\r\n" + "Range: bytes=%i-\r\nConnection: close\r\n\r\n" %(track)
	serverSocket.send(message)

def download():
	message = "GET " + path + " HTTP/1.1\r\n" + "Host: " + host + "\r\n" + "Connection: close\r\n\r\n"
	serverSocket.send(message) 

def tracker(fileName, host, path, size):
	if os.path.isfile(os.path.join(trackerPath, trackerName)):
		f = open(os.path.join(trackerPath, trackerName), 'r')
		trackChecker = fileName + " " + host + " " + path
		trackFile = f.read()
		f.close()
		if trackFile.find(trackChecker) == -1:
			f = open(os.path.join(trackerPath, trackerName), 'a')
			f.write(trackChecker + "_" + size)

		f = open(os.path.join(trackerPath, trackerName), 'r')
		trackChecker = fileName + " " + host + " " + path
		trackFile = f.read()
		f.close()
		trackList = trackFile.split("\n")
		open(os.path.join(trackerPath, trackerName), 'w').close()
		f = open(os.path.join(trackerPath, trackerName), 'w')
		for line in trackList:
			if line.split("_")[0] == trackChecker:
				line = line.replace(line.split("_")[1], str(size))
				f.write(line + "\n")
			elif line != "":
				if trackFile.find(line) != -1 or trackFile.find(trackChecker) != -1:
					f.write(line + "\n")
				else:
					f.write(fileName + " " + host + " " + path + "_" + size + "\n")
		f.close
	else:
		f = open(os.path.join(trackerPath, trackerName), 'a')
		f.write(fileName + " " + host + " " + path + "_" + size + "\n")
		f.close()

def resetTracker():
	f = open(os.path.join(trackerPath, trackerName), 'r')
	trackFile = f.read()
	f.close()
	trackList = trackFile.split("\n")
	open(os.path.join(trackerPath, trackerName), 'w').close()
	f = open(os.path.join(trackerPath, trackerName), 'w')
	for line in trackList:
		if line != "":
			line = line.replace(line.split("_")[1], str(0))
			f.write(line + "\n")
	f.close()
		
def filesWriter(reply):
	f = open(os.path.join(filePath, fileName+fileTmpExt), 'a')
	f.write(reply)
	f.close()

def fileStore():
	os.rename(os.path.join(filePath, fileName+fileTmpExt), os.path.join(filePath, fileName+fileExt))
	resetTracker()

if os.path.isfile(os.path.join(filePath, fileName+fileTmpExt)):
	size = str(os.path.getsize(os.path.join(filePath, fileName+fileTmpExt)))
	f = open(os.path.join(trackerPath, trackerName), 'r')
	trackFile = f.read()
	trackChecker = fileName + fileTmpExt + " " + host + " " + path
	if trackFile.find(trackChecker) != -1:
		resume(size)
	else:
		os.remove(os.path.join(filePath, fileName+fileTmpExt))
		download()
else:
	download()

while True:
	# Recieved Data
	reply = serverSocket.recv(1024)

	if len(reply) <= 0:
		fileStore()
		break
	if reply.find('\r\n\r\n') == -1:
		filesWriter(reply)
		tracker(fileName+fileTmpExt, host, path, str(os.path.getsize(os.path.join(filePath, fileName+fileTmpExt))))
	else:
		data = reply.split('\r\n\r\n')[1]
		filesWriter(data)
		tracker(fileName+fileTmpExt, host, path, str(os.path.getsize(os.path.join(filePath, fileName+fileTmpExt))))







