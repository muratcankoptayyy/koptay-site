"""
Posts Forms
Flask-WTF forms for creating and editing posts
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class PostForm(FlaskForm):
    """Create/Edit post form"""
    title = StringField('İlan Başlığı', validators=[
        DataRequired(message='Başlık gereklidir'),
        Length(min=10, max=200, message='Başlık 10-200 karakter arası olmalıdır')
    ])
    
    description = TextAreaField('Açıklama', validators=[
        DataRequired(message='Açıklama gereklidir'),
        Length(min=50, max=2000, message='Açıklama 50-2000 karakter arası olmalıdır')
    ])
    
    law_category = SelectField('Hukuk Dalı', choices=[
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
    ], validators=[DataRequired(message='Hukuk dalı seçiniz')])
    
    case_type = SelectField('Dava Türü', choices=[
        ('', 'Seçiniz...'),
        ('dava', 'Dava'),
        ('icra', 'İcra Takibi'),
        ('sorusturma', 'Soruşturma'),
        ('tahkim', 'Tahkim'),
        ('调解', 'Arabuluculuk'),
        ('danismanlik', 'Hukuki Danışmanlık'),
        ('diger', 'Diğer')
    ], validators=[DataRequired(message='Dava türü seçiniz')])
    
    city = StringField('Şehir', validators=[
        DataRequired(message='Şehir gereklidir')
    ])
    
    district = StringField('İlçe', validators=[
        Optional()
    ])
    
    court_name = StringField('Mahkeme Adı', validators=[
        Optional(),
        Length(max=200)
    ])
    
    file_number = StringField('Dosya No', validators=[
        Optional(),
        Length(max=100)
    ])
    
    hearing_date = DateField('Duruşma Tarihi', validators=[
        Optional()
    ], format='%Y-%m-%d')
    
    budget_min = IntegerField('Minimum Bütçe (TL)', validators=[
        Optional(),
        NumberRange(min=0, message='Bütçe 0 veya daha büyük olmalıdır')
    ])
    
    budget_max = IntegerField('Maksimum Bütçe (TL)', validators=[
        Optional(),
        NumberRange(min=0, message='Bütçe 0 veya daha büyük olmalıdır')
    ])
    
    urgency_level = SelectField('Aciliyet Durumu', choices=[
        ('dusuk', 'Düşük'),
        ('orta', 'Orta'),
        ('yuksek', 'Yüksek'),
        ('acil', 'Acil')
    ], validators=[DataRequired(message='Aciliyet durumu seçiniz')])
    
    is_active = BooleanField('İlan Aktif')
