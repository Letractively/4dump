import os, re, sys, urllib
from time import sleep
from shutil import move

# Disable traceback
sys.tracebacklimit = 0

# Global for finding images
htmldl = '<a href="//images.4chan.org/'
htmlboardfind = '[<a href="res/[0-9]+" class="replylink">Reply</a>]'

# Dynamic Print Function
def dynamic_print(msg):	
    sys.stdout.write("\r"+msg)
    sys.stdout.flush()

# Puts html content into a variable
def geturl(url):
	f = urllib.urlopen(url)
	fread = f.read()
	return fread
	
def countfiles(path):
	number_of_files = sum(1 for item in os.listdir(path) if os.path.isfile(os.path.join(path, item)))
	return number_of_files
	
# Check url to know if it's a board, a thread or an invalid link
def checkurl(argurl):
	rthread = re.findall('http://boards.4chan.org/[a-z]+/res/', argurl)
	rboard = re.findall('http://boards.4chan.org/[a-z]+/$', argurl)
	if rthread:
		return 'thread'
	elif rboard:
		return 'board'
	else:
		return 'error'

# Returns thread number
def threadnumber(argurl):
	thread = 'http://boards.4chan.org/[a-z]+/res/'
	rthread = argurl.split('/res/')
	return rthread[1]

# Returns board letter.
def boardletter(argurl):
	board = 'http://boards.4chan.org/[a-z]+'
	rboard = re.findall(board, argurl)
	return rboard[0].split('.org/')[1]

# Resolves the path to put the images based on "board/thread_number"
def path(threadnumber):
	board = boardletter(argurl)
	if os.path.isdir(board+'/'+threadnumber):
		return True
	elif os.path.isdir(board):
		os.path.join(board)
		os.mkdir(os.path.expanduser(board+'/'+threadnumber))
	else:
		os.mkdir(board)
		os.mkdir(os.path.expanduser(board+'/'+threadnumber))

# Dump the thread.
def dump_thread(url, boardletter, threadnumber):
	print url
	fread = geturl(url)
	x = 1
	p = 1
	if fread.count(htmldl) > 0:
		while x <= fread.count(htmldl):
			p = fread.find(htmldl, p)
			concatenate = ''
			filename = ''
			
			# Set concatenate and filename
			for i in range(p+11, len(htmldl)+p+30):
				if fread[i] == '"':
					break
				concatenate = concatenate + fread[i]
				if fread[i] == '/':
					filename = ''
				else:
					filename = filename + fread[i]
			
			# Print status
			msg = "[%i/%i] %s" % (x,fread.count(htmldl),str(filename))
			if x == fread.count(htmldl):
				dynamic_print(msg)
				dynamic_print("")
			else:
				dynamic_print(msg)
			
			# Download and handle file/folders
			# If already downloaded, jump
			if os.path.isfile(boardletter+'/'+threadnumber+'/'+filename):
				jump = True
			# If incomplete, remove it, download and move
			elif os.path.isfile(filename):
				os.remove(filename)
				urllib.urlretrieve('http://'+concatenate, str(filename)) 
				move(filename, boardletter+'/'+threadnumber)
			# Download and move
			else:
				urllib.urlretrieve('http://'+concatenate, str(filename)) 
				move(filename, boardletter+'/'+threadnumber)
			p += 1
			x += 1
	else:
		return False

def dump_board(argurl):
	page = 1
	board = str(boardletter(argurl))
	result = []
	x = 0
	print 'Dumping /'+board+'/'
	while page > 0:
		fread = geturl(argurl+'/'+str(page))
		threads = re.findall(htmlboardfind, fread)
		for t in threads:
			url = 'http://boards.4chan.org/'+board+'/res/'+t.split('res/')[1].split('"')[0]
			result.append(url)
			x += 1
		if len(threads) == 0:
			break
		page += 1
	return result
		
def update():
	for dirname, dirnames, filenames in os.walk('.'):
		if len(dirname.split('\\')) > 2:
			dirurl = 'http://boards.4chan.org/'+dirname.split('\\')[1]+'/res/'+dirname.split('\\')[2]
			if countfiles(dirname.split('\\')[1]+'/'+dirname.split('\\')[2]) != geturl(dirurl).count(htmldl):
				print dirurl
				dump_thread(geturl(dirurl), boardletter(dirurl), threadnumber(dirurl))
			else:
				print dirurl
	
def doupdate(continuous=False, timer=60):
	if continuous == False:
		update()
	while continuous != False:
		update()
		print 'Waiting '+str(timer)+' seconds to refresh...'	
		sleep(timer)

###### Program execution starts here #####
# Get url from argument
try:
	arguments = sys.argv[1:]
except IndexError:
	print "I've failed, master."


# Threat the given url/command.
if len(arguments) > 0:
	noarg = False
	for argurl in arguments:
		if checkurl(argurl) == 'thread':
			path(threadnumber(argurl))
			dump_thread(argurl, boardletter(argurl), threadnumber(argurl))
		elif checkurl(argurl) == 'board':
			for i in dump_board(argurl):
				path(threadnumber(i))
				dump_thread(i, boardletter(i), threadnumber(i))
		elif argurl == '--update':
			doupdate()
		elif argurl == '-u':
			doupdate(True, 120)
		else:
			print "This does not seem to be valid link or option."
else:
	noarg = True

if noarg == True:
	print ''
	print ' ================================================='
	print ' usage: %s url     | Download all threads' % sys.argv[0]
	print ' usage: %s -u      | Update' % sys.argv[0]
	print ' -------------------------------------------------'
	print ' Note:'
	print '   if you use a board for the url, it will get'
	print '   all the threads available at the moment.'
	print ' ================================================='
	sys.exit(1)