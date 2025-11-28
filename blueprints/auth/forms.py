"""
Authentication Forms
Flask-WTF forms for login and registration
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    password = PasswordField('Şifre', validators=[
        DataRequired(message='Şifre gereklidir')
    ])
    remember = BooleanField('Beni Hatırla')

class RegisterForm(FlaskForm):
    """Registration form"""
    # Kişisel Bilgiler
    first_name = StringField('Ad', validators=[
        DataRequired(message='Ad gereklidir'),
        Length(min=2, max=50, message='Ad 2-50 karakter arası olmalıdır')
    ])
    last_name = StringField('Soyad', validators=[
        DataRequired(message='Soyad gereklidir'),
        Length(min=2, max=50, message='Soyad 2-50 karakter arası olmalıdır')
    ])
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    phone = StringField('Telefon', validators=[
        DataRequired(message='Telefon numarası gereklidir'),
        Length(min=10, max=15, message='Geçerli bir telefon numarası giriniz')
    ])
    
    # Avukatlık Bilgileri
    bar_association = StringField('Baro', validators=[
        DataRequired(message='Baro bilgisi gereklidir')
    ])
    bar_number = StringField('Sicil No', validators=[
        DataRequired(message='Sicil numarası gereklidir')
    ])
    law_specialization = SelectField('Uzmanlık Alanı', choices=[
        ('', 'Seçiniz...'),
        ('ceza', 'Ceza Hukuku'),
        ('medeni', 'Medeni Hukuku'),
        ('ticaret', 'Ticaret Hukuku'),
        ('idare', 'İdare Hukuku'),
        ('icra_iflas', 'İcra İflas Hukuku'),
        ('aile', 'Aile Hukuku'),
        ('is', 'İş Hukuku'),
        ('tazminat', 'Tazminat Hukuku'),
        ('gayrimenkul', 'Gayrimenkul Hukuku'),
        ('bilisim', 'Bilişim Hukuku'),
        ('diger', 'Diğer')
    ], validators=[DataRequired(message='Uzmanlık alanı seçiniz')])
    
    experience_years = SelectField('Deneyim (Yıl)', choices=[
        ('', 'Seçiniz...'),
        ('0-2', '0-2 yıl'),
        ('3-5', '3-5 yıl'),
        ('6-10', '6-10 yıl'),
        ('11-15', '11-15 yıl'),
        ('16+', '16+ yıl')
    ], validators=[DataRequired(message='Deneyim süresi seçiniz')])
    
    bio = TextAreaField('Kısa Tanıtım', validators=[
        Length(max=500, message='Tanıtım en fazla 500 karakter olabilir')
    ])
    
    # Adres Bilgileri
    city = StringField('Şehir', validators=[
        DataRequired(message='Şehir gereklidir')
    ])
    district = StringField('İlçe', validators=[
        DataRequired(message='İlçe gereklidir')
    ])
    address = TextAreaField('Adres', validators=[
        Length(max=200, message='Adres en fazla 200 karakter olabilir')
    ])
    
    # Şifre
    password = PasswordField('Şifre', validators=[
        DataRequired(message='Şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    password_confirm = PasswordField('Şifre Tekrar', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('password', message='Şifreler eşleşmiyor')
    ])
    
    terms = BooleanField('Kullanım koşullarını kabul ediyorum', validators=[
        DataRequired(message='Kullanım koşullarını kabul etmelisiniz')
    ])
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor')
    
    def validate_bar_number(self, field):
        """Check if bar number already exists"""
        if User.query.filter_by(bar_registration_number=field.data).first():
            raise ValidationError('Bu sicil numarası zaten kayıtlı')
