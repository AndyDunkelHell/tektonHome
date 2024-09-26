
## Virtual enviroment SetUp

- Create your own virtual enviroment and Run `pip install -r requirements.txt` to install all required packages on each board. 


## https://deb.nodesource.com/
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs

npx create-next-app@latest

## Reset for new build
- sudo systemctl restart APItektonhome.service
- bash stop-nextjs.sh
- and/or sudo reboot

# FOR Developement (pay attention to ports in app.py)
### `activate python env for dev in venv folder`

in Server and client Pi, to see updates live:
- source bin/activate
- sudo systemctl stop APItektonhome.service
- uvicorn app:app --reload --host 0.0.0.0 --port 8000
when finished: 
- sudo systemctl start APItektonhome.service

in Server (if previous version already running): 
- ps -ef | grep next-server (Result with only next-server) **Look for proces ID (PID) second number from the left**
- kill -9 *yourPID*
- npm run dev

### `in nextJs folder`
- npm run dev 


# Run FastAPI independently
uvicorn app:app --host 0.0.0.0 --port 8000


# TO DO: 
- change tab title and implement logo on tab
- Update version number
- Improve README Instructiuons
- Add  Video and images
- Make tabs always different colors from a set of colors
