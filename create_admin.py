from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    with app.app_context():
        # Vérifier si l'administrateur existe déjà
        admin = User.query.filter_by(email='admin@goldeaf.com').first()
        if not admin:
            admin = User(
                nom='Admin',
                prenom='GOLDEAF',
                email='admin@goldeaf.com',
                password=generate_password_hash('admin123456'),
                date_naissance=datetime(1990, 1, 1),
                pays='FR',
                is_admin=True,
                email_confirme=True,
                solde=1000000  # 1 million d'euros comme solde initial
            )
            db.session.add(admin)
            db.session.commit()
            print("Compte administrateur créé avec succès!")
        else:
            print("Le compte administrateur existe déjà.")

if __name__ == '__main__':
    create_admin_user()
