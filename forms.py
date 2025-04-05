from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SelectField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import date

class RegistrationForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    date_naissance = DateField('Date de naissance', validators=[DataRequired()])
    pays = SelectField('Pays', choices=[
        ('FR', 'France'), ('BE', 'Belgique'), ('CH', 'Suisse'),
        ('CA', 'Canada'), ('US', 'États-Unis'), ('GB', 'Royaume-Uni')
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    accept_terms = BooleanField('J\'accepte les conditions d\'utilisation', validators=[DataRequired()])

    def validate_date_naissance(self, field):
        if field.data >= date.today():
            raise ValidationError('La date de naissance doit être dans le passé')
        age = (date.today() - field.data).days / 365
        if age < 18:
            raise ValidationError('Vous devez avoir au moins 18 ans pour ouvrir un compte')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')

class TransferForm(FlaskForm):
    destinataire = StringField('Destinataire', validators=[DataRequired()])
    montant = DecimalField('Montant', validators=[DataRequired()])
    message = TextAreaField('Message')
    type_transfert = SelectField('Type de transfert', choices=[
        ('interne', 'Transfert interne'),
        ('externe', 'Transfert externe')
    ])

class CardRequestForm(FlaskForm):
    montant_initial = DecimalField('Montant initial', validators=[DataRequired()])

class AdminCodeForm(FlaskForm):
    code = StringField('Code administrateur', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Le code doit contenir exactement 6 caractères')
    ])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
