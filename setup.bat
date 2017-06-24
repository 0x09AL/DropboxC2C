@echo off
echo "Installing Required Libraries"
pip install -r requirements.txt
echo "Creating the agent executable"
pyinstaller --onefile --uac-admin agent.py
echo agent.exe can be fond at dist/

