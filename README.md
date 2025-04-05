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

## Installation

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
python app.py
```

L'application sera accessible à :
- http://localhost:5000 (accès direct)
- https://goldeaf.local (via Nginx, nécessite configuration)

## Sécurité

- Support HTTPS complet
- En-têtes de sécurité HTTP
- Protection contre XSS et CSRF
- Limitation de la taille des requêtes
- Certificats SSL/TLS

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT.
