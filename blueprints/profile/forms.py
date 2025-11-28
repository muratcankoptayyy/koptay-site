"""
Profile Forms
Flask-WTF forms for profile editing
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class ProfileForm(FlaskForm):
    """Edit profile form"""
    first_name = StringField('Ad', validators=[
        DataRequired(message='Ad gereklidir'),
        Length(min=2, max=50)
    ])
    
    last_name = StringField('Soyad', validators=[
        DataRequired(message='Soyad gereklidir'),
        Length(min=2, max=50)
    ])
    
    phone = StringField('Telefon', validators=[
        DataRequired(message='Telefon gereklidir'),
        Length(min=10, max=15)
    ])
    
    bio = TextAreaField('Hakkımda', validators=[
        Optional(),
        Length(max=500)
    ])
    
    law_specialization = SelectField('Uzmanlık Alanı', choices=[
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
    ])
    
    experience_years = SelectField('Deneyim (Yıl)', choices=[
        ('0-2', '0-2 yıl'),
        ('3-5', '3-5 yıl'),
        ('6-10', '6-10 yıl'),
        ('11-15', '11-15 yıl'),
        ('16+', '16+ yıl')
    ])
    
    city = StringField('Şehir', validators=[
        DataRequired(message='Şehir gereklidir')
    ])
    
    district = StringField('İlçe', validators=[Optional()])
    
    address = TextAreaField('Adres', validators=[
        Optional(),
        Length(max=200)
    ])
