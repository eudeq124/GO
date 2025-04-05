import random
import string
from datetime import datetime, timedelta
import jwt
from flask import current_app
from flask_mail import Message
from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash

def generate_card_number():
    """Génère un numéro de carte bancaire valide"""
    prefix = "4532"  # Préfixe pour les cartes GOLDEAF
    account = ''.join(random.choices(string.digits, k=12))
    number = prefix + account
    
    # Algorithme de Luhn pour générer le dernier chiffre
    total = 0
    for i, digit in enumerate(reversed(number)):
        d = int(digit)
        if i % 2 == 0:
            d = d * 2
            if d > 9:
                d = d - 9
        total += d
    check_digit = (10 - (total % 10)) % 10
    
    return number + str(check_digit)

def generate_cvv():
    """Génère un code CVV"""
    return ''.join(random.choices(string.digits, k=3))

def generate_expiration_date():
    """Génère une date d'expiration pour la carte (3 ans à partir d'aujourd'hui)"""
    return datetime.now() + timedelta(days=3*365)

def generate_admin_code():
    """Génère un code administrateur pour les transactions"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def send_confirmation_email(user):
    """Envoie un email de confirmation à l'utilisateur"""
    token = generate_confirmation_token(user.email)
    msg = Message('Confirmation de compte GOLDEAF Financial Inc',
                 sender='noreply@goldeaf.com',
                 recipients=[user.email])
    msg.body = f'''Pour confirmer votre compte, cliquez sur le lien suivant:
{url_for('confirm_email', token=token, _external=True)}

Ce lien expire dans 24 heures.

Si vous n'avez pas créé de compte, ignorez simplement cet email.
'''
    current_app.extensions['mail'].send(msg)

def send_reset_password_email(user):
    """Envoie un email de réinitialisation de mot de passe"""
    token = generate_reset_token(user.email)
    msg = Message('Réinitialisation de mot de passe GOLDEAF Financial Inc',
                 sender='noreply@goldeaf.com',
                 recipients=[user.email])
    msg.body = f'''Pour réinitialiser votre mot de passe, cliquez sur le lien suivant:
{url_for('reset_password', token=token, _external=True)}

Ce lien expire dans 1 heure.

Si vous n'avez pas demandé de réinitialisation de mot de passe, ignorez simplement cet email.
'''
    current_app.extensions['mail'].send(msg)

def generate_confirmation_token(email):
    """Génère un token de confirmation d'email"""
    return jwt.encode(
        {'confirm': email, 'exp': datetime.utcnow() + timedelta(days=1)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def generate_reset_token(email):
    """Génère un token de réinitialisation de mot de passe"""
    return jwt.encode(
        {'reset': email, 'exp': datetime.utcnow() + timedelta(hours=1)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token(token, type='confirm'):
    """Vérifie un token (confirmation ou réinitialisation)"""
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return data.get(type)
    except:
        return None

def admin_required(f):
    """Décorateur pour les routes nécessitant des droits administrateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(amount):
    """Formate un montant en euros"""
    return f"{amount:,.2f} €"

def calculate_transfer_fee(amount, transfer_type):
    """Calcule les frais de transfert"""
    if transfer_type == 'interne':
        return 0
    elif transfer_type == 'externe':
        # 1% de frais pour les transferts externes, minimum 1€, maximum 20€
        fee = max(1, min(amount * 0.01, 20))
        return fee
    return 0
