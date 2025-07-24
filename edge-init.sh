set -e
apt-get update -qq
apt-get install -y docker.io docker-compose-plugin git
rm -rf /opt/bridge || true
sudo git clone https://github.com/QuietXO/smart-home-bridge.git /opt/bridge
cd /opt/bridge
docker compose up -d mosquitto edge-sim
