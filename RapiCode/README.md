## https://deb.nodesource.com/
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs

npx create-next-app@latest

## Reset for new build
sudo systemctl restart APItektonhome.service
bash stop-nextjs.sh

# FOR Developement (pay attention to ports)
## activate python env for dev in venv folder
source bin/activate
uvicorn app_dev:app --reload --host 0.0.0.0 --port 8001
## in nextJs folder
npm run dev 


# Run FastAPI independently
uvicorn app:app --host 0.0.0.0 --port 8000