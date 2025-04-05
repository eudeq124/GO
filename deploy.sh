#!/bin/bash

# Variables
APP_NAME="goldeaf_bank"
DEPLOY_PATH="/var/www/$APP_NAME"
REPO_URL="https://github.com/eudeq124/GOLDEAF.git"
PYTHON_VERSION="python3"

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Début du déploiement de $APP_NAME${NC}"

# Vérification des dépendances
echo "Vérification des dépendances..."
command -v $PYTHON_VERSION >/dev/null 2>&1 || { echo -e "${RED}Python3 n'est pas installé${NC}" >&2; exit 1; }
command -v nginx >/dev/null 2>&1 || { echo -e "${RED}Nginx n'est pas installé${NC}" >&2; exit 1; }

# Installation des paquets système nécessaires
echo "Installation des paquets système..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev build-essential libssl-dev libffi-dev

# Création du répertoire de déploiement
echo "Création du répertoire de déploiement..."
sudo mkdir -p $DEPLOY_PATH
sudo chown -R $USER:$USER $DEPLOY_PATH

# Clonage du dépôt
echo "Clonage du dépôt..."
git clone $REPO_URL $DEPLOY_PATH || (cd $DEPLOY_PATH && git pull)

# Configuration de l'environnement virtuel
echo "Configuration de l'environnement virtuel..."
cd $DEPLOY_PATH
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances Python
echo "Installation des dépendances Python..."
pip install -r requirements.txt
pip install gunicorn

# Configuration des permissions
echo "Configuration des permissions..."
sudo chown -R www-data:www-data $DEPLOY_PATH
sudo chmod -R 755 $DEPLOY_PATH

# Configuration de Nginx
echo "Configuration de Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/$APP_NAME
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configuration du service systemd
echo "Configuration du service systemd..."
sudo cp goldeaf.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable goldeaf
sudo systemctl start goldeaf

# Vérification de la configuration Nginx
echo "Vérification de la configuration Nginx..."
sudo nginx -t && sudo systemctl restart nginx

echo -e "${GREEN}Déploiement terminé !${NC}"
echo "L'application devrait être accessible à l'adresse configurée dans Nginx"
echo "Vérifiez les logs avec : sudo journalctl -u goldeaf"
