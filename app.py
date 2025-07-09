from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from forms import (RegistrationForm, LoginForm, TransferForm, CardRequestForm,
                  AdminCodeForm, ResetPasswordRequestForm, ResetPasswordForm)
from utils import (generate_card_number, generate_cvv, generate_expiration_date,
                  generate_admin_code, send_confirmation_email, send_reset_password_email,
                  verify_token, admin_required, format_currency, calculate_transfer_fee)
from flask_babel import Babel, _, get_locale

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

# Configuration Babel pour l'internationalisation
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
app.config['LANGUAGES'] = ['fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar']
babel = Babel(app)

def get_locale():
    # Essaie d'obtenir la langue depuis les paramètres de l'URL
    lang = request.args.get('lang')
    if lang and lang in app.config['LANGUAGES']:
        return lang
    # Sinon, utilise la langue du navigateur
    return request.accept_languages.best_match(app.config['LANGUAGES'])

babel.init_app(app, locale_selector=get_locale)

@app.before_request
def before_request():
    g.lang_code = str(get_locale())

# Initialisation des extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    pays = db.Column(db.String(100), nullable=False)
    solde = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirme = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Carte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(16), unique=True, nullable=False)
    date_expiration = db.Column(db.Date, nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    solde = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50), nullable=False)
    expediteur_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destinataire_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    statut = db.Column(db.String(20), default='en_attente')
    code_admin = db.Column(db.String(6), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes pour l'authentification
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(_('Cet email est déjà utilisé.'), 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            nom=form.nom.data,
            prenom=form.prenom.data,
            email=form.email.data,
            password=hashed_password,
            date_naissance=form.date_naissance.data,
            pays=form.pays.data
        )
        db.session.add(new_user)
        db.session.commit()

        send_confirmation_email(new_user)
        flash(_('Un email de confirmation a été envoyé à votre adresse.'), 'info')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.email_confirme:
                flash(_('Veuillez confirmer votre email avant de vous connecter.'), 'warning')
                return redirect(url_for('login'))
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash(_('Email ou mot de passe incorrect.'), 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/confirm/<token>')
def confirm_email(token):
    email = verify_token(token)
    if not email:
        flash(_('Le lien de confirmation est invalide ou a expiré.'), 'danger')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash(_('Utilisateur non trouvé.'), 'danger')
        return redirect(url_for('login'))
    
    if user.email_confirme:
        flash(_('Votre compte est déjà confirmé.'), 'info')
    else:
        user.email_confirme = True
        db.session.commit()
        flash(_('Votre compte a été confirmé avec succès !'), 'success')
    
    return redirect(url_for('login'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)
            flash(_('Un email avec les instructions pour réinitialiser votre mot de passe a été envoyé.'), 'info')
            return redirect(url_for('login'))
        else:
            flash(_('Adresse email non trouvée.'), 'danger')
    return render_template('reset_password_request.html', title=_('Réinitialisation du mot de passe'), form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    email = verify_token(token)
    if not email:
        flash(_('Le lien de réinitialisation est invalide ou a expiré.'), 'danger')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash(_('Utilisateur non trouvé.'), 'danger')
        return redirect(url_for('login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash(_('Votre mot de passe a été réinitialisé.'), 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', title=_('Réinitialisation du mot de passe'), form=form)

# Routes principales
@app.route('/')
def index():
    return render_template('index.html', title=_('Accueil'))

@app.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter(
        (Transaction.expediteur_id == current_user.id) |
        (Transaction.destinataire_id == current_user.id)
    ).order_by(Transaction.date.desc()).limit(10).all()

    cartes = Carte.query.filter_by(user_id=current_user.id).all()

    return render_template('dashboard.html',
                         transactions=transactions,
                         cartes=cartes)

# Routes pour les transferts
@app.route('/transfer', methods=['POST'])
@login_required
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        montant = float(form.montant.data)
        if montant <= 0:
            return jsonify({'success': False, 'error': _('Le montant doit être positif')})

        if montant > current_user.solde:
            return jsonify({'success': False, 'error': _('Solde insuffisant')})

        # Générer un code admin pour les transferts > 1000€
        code_admin = None
        if montant > 1000:
            code_admin = generate_admin_code()

        transaction = Transaction(
            montant=montant,
            type=form.type_transfert.data,
            expediteur_id=current_user.id,
            destinataire=form.destinataire.data,
            code_admin=code_admin
        )
        db.session.add(transaction)
        
        if not code_admin:  # Si pas besoin de code admin
            current_user.solde -= montant
            transaction.statut = 'complete'
        
        db.session.commit()

        return jsonify({
            'success': True,
            'transaction_id': transaction.id,
            'need_admin_code': bool(code_admin)
        })

    return jsonify({'success': False, 'error': _('Formulaire invalide')})

@app.route('/verify-admin-code', methods=['POST'])
@login_required
def verify_admin_code():
    data = request.get_json()
    transaction = Transaction.query.get_or_404(data['transferId'])
    
    if transaction.code_admin == data['code']:
        transaction.statut = 'complete'
        transaction.expediteur.solde -= transaction.montant
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': _('Code incorrect')})

# Routes pour les cartes
@app.route('/request-card', methods=['POST'])
@login_required
def request_card():
    form = CardRequestForm()
    if form.validate_on_submit():
        montant = float(form.montant_initial.data)
        if montant <= 0:
            return jsonify({'success': False, 'error': _('Le montant doit être positif')})

        if montant > current_user.solde:
            return jsonify({'success': False, 'error': _('Solde insuffisant')})

        carte = Carte(
            numero=generate_card_number(),
            date_expiration=generate_expiration_date(),
            cvv=generate_cvv(),
            solde=montant,
            user_id=current_user.id
        )
        
        current_user.solde -= montant
        db.session.add(carte)
        db.session.commit()

        return jsonify({'success': True})

    return jsonify({'success': False, 'error': _('Formulaire invalide')})

# Routes administrateur
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'clients_actifs': User.query.filter_by(is_admin=False).count(),
        'cartes_actives': Carte.query.count(),
        'transactions_jour': Transaction.query.filter(
            Transaction.date >= datetime.now().date()
        ).count()
    }
    
    clients = User.query.filter_by(is_admin=False).all()
    transactions_attente = Transaction.query.filter_by(statut='en_attente').all()
    solde_total = sum(user.solde for user in User.query.all())

    return render_template('admin_dashboard.html',
                         stats=stats,
                         clients=clients,
                         transactions_attente=transactions_attente,
                         solde_total=solde_total)

@app.route('/admin/update-bank-balance', methods=['POST'])
@login_required
@admin_required
def update_bank_balance():
    nouveau_solde = float(request.form.get('nouveau_solde', 0))
    if nouveau_solde < 0:
        return jsonify({'success': False, 'error': _('Le solde ne peut pas être négatif')})

    # Mettre à jour le solde global de la banque
    # Cette fonctionnalité dépend de votre logique métier
    return jsonify({'success': True})

@app.route('/admin/deposit', methods=['POST'])
@login_required
@admin_required
def admin_deposit():
    client_id = int(request.form.get('client_id'))
    montant = float(request.form.get('montant'))
    
    if montant <= 0:
        return jsonify({'success': False, 'error': _('Le montant doit être positif')})

    client = User.query.get_or_404(client_id)
    client.solde += montant
    
    transaction = Transaction(
        montant=montant,
        type='depot_admin',
        destinataire_id=client_id,
        statut='complete'
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/admin/withdraw', methods=['POST'])
@login_required
@admin_required
def admin_withdraw():
    client_id = int(request.form.get('client_id'))
    montant = float(request.form.get('montant'))
    
    if montant <= 0:
        return jsonify({'success': False, 'error': _('Le montant doit être positif')})

    client = User.query.get_or_404(client_id)
    if client.solde < montant:
        return jsonify({'success': False, 'error': _('Solde insuffisant')})

    client.solde -= montant
    
    transaction = Transaction(
        montant=-montant,
        type='retrait_admin',
        expediteur_id=client_id,
        statut='complete'
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'success': True})

# Initialisation de la base de données
with app.app_context():
    db.create_all()

def init_db():
    with app.app_context():
        db.create_all()

@app.before_request
def initialize_database():
    if not hasattr(g, '_initialized'):
        init_db()
        g._initialized = True

if __name__ == '__main__':
    init_db()
    # Modification pour que l'application écoute sur le port défini par Vercel
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
