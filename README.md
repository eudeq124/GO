# GOLDEAF Bank

Application bancaire multilingue moderne développée avec Flask.

## Fonctionnalités

- Interface utilisateur moderne et réactive
- Support multilingue (11 langues)
- Authentification sécurisée
- Gestion des comptes
- Transactions en temps réel
- Design adaptatif pour tous les appareils
- Support HTTPS avec SSL/TLS
- Configuration Nginx sécurisée

## Technologies utilisées

- Flask
- Flask-Babel pour l'internationalisation
- Bootstrap 5
- Select2 pour le sélecteur de langue
- SQLite pour la base de données
- Nginx comme proxy inverse
- SSL/TLS pour la sécurité
- Gunicorn comme serveur WSGI

## Installation locale

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-username/goldeaf_bank.git
cd goldeaf_bank
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configuration Nginx (optionnel) :
```bash
sudo cp nginx.conf /etc/nginx/sites-available/goldeaf
sudo ln -sf /etc/nginx/sites-available/goldeaf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. Lancer l'application :
```bash
python app.py  # Pour le développement
# ou
gunicorn --bind 127.0.0.1:5000 app:app  # Pour la production
```

L'application sera accessible à :
- http://localhost:5000 (accès direct)
- https://goldeaf.local (via Nginx, nécessite configuration)

## Déploiement en production

1. Prérequis serveur :
- Python 3.8+
- Nginx
- Git

2. Déploiement automatique :
```bash
# Cloner le dépôt
git clone https://github.com/votre-username/goldeaf_bank.git
cd goldeaf_bank

# Rendre le script de déploiement exécutable
chmod +x deploy.sh

# Lancer le déploiement
sudo ./deploy.sh
```

3. Vérification :
```bash
# Vérifier le statut du service
sudo systemctl status goldeaf

# Vérifier les logs
sudo journalctl -u goldeaf

# Vérifier la configuration Nginx
sudo nginx -t
```

## Sécurité

- Support HTTPS complet
- En-têtes de sécurité HTTP
- Protection contre XSS et CSRF
- Limitation de la taille des requêtes
- Certificats SSL/TLS
- Serveur WSGI Gunicorn

## Maintenance

- Logs d'application : `/var/log/goldeaf/`
- Logs Nginx : `/var/log/nginx/`
- Fichiers de l'application : `/var/www/goldeaf_bank/`
- Service systemd : `goldeaf.service`

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT.
