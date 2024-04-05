## https://deb.nodesource.com/
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs

npx create-next-app@latest

## Reset for new build
sudo systemctl restart APItektonhome.service
bash stop-nextjs.sh

## Developement (pay attention to ports)
npm run dev
uvicorn app_dev:app --reload --host 0.0.0.0 --port 8001

## Run FastAPI independently
uvicorn app:app --host 0.0.0.0 --port 8000