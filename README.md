# DropboxC2C
DropboxC2C is a post-exploitation agent which uses Dropbox Infrastructure for command and control operations.

DO NOT USE THIS FOR MALICIOUS PURPOSES. THE AUTHOR IS NOT RESPONSIBLE FOR ANY MISUSE OF THIS PROGRAM.

Dropbox-C2C is an old project of mine to use a thirdparty for command and control. Since the guys at Empire implemented dropbox as a C2C i am releasing this.

# Structure


main.py - The "server" part which manages all the agents.

agent.py - The "client" part which does what the server tells.

I have removed the keylogging functions so this doesn't get missused.

# Requirements

Python 2.7


Libraries
dropbox 
psutil
pyinstaller

# Installation

1-) Clone the repository.

2-) Modify the API Key on agent.py and main.py # The api key must be created from the dropbox web interface.

3-) Run setup.bat on a Windows Machine. You will get agent.exe which is the "compiled" agent.

4-) Run main.py and run the agent on the compromised server.

Video Coming Soon

# Screenshots
Screenshot - 1
![ScreenShot](https://raw.github.com/0x09AL/DropboxC2C/master/screenshots/Screenshot-1.png)


Screenshot - 2
![ScreenShot](https://raw.github.com/0x09AL/DropboxC2C/master/screenshots/Screenshot-2.png)


Screenshot - 3
![ScreenShot](https://raw.github.com/0x09AL/DropboxC2C/master/screenshots/Screenshot-3.png)


Screenshot - 4
![ScreenShot](https://raw.github.com/0x09AL/DropboxC2C/master/screenshots/Screenshot-4.png)
