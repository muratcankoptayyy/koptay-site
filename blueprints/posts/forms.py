"""
Posts Forms
Flask-WTF forms for creating and editing posts
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from constants import POST_CATEGORIES, URGENCY_LEVELS, TASK_CATEGORY_DEFINITIONS

class PostForm(FlaskForm):
    """Create/Edit post form"""
    # Title otomatik oluşturulacak
    
    job_type = SelectField('Görev Türü', choices=[('', 'Seçiniz...')] + [(k, v['label']) for k, v in TASK_CATEGORY_DEFINITIONS.items()], validators=[
        DataRequired(message='Görev türü seçiniz')
    ])

    law_category = SelectField('Hukuk Dalı', choices=[('', 'Seçiniz...')] + [(c, c) for c in POST_CATEGORIES], validators=[
        DataRequired(message='Hukuk dalı seçiniz')
    ])
    
    description = TextAreaField('Açıklama', validators=[
        DataRequired(message='Açıklama gereklidir'),
        Length(min=10, max=2000, message='Açıklama 10-2000 karakter arası olmalıdır')
    ])
    
    city = SelectField('Şehir', choices=[], validators=[
        DataRequired(message='Şehir gereklidir')
    ])
    
    courthouse = SelectField('Adliye', choices=[], validate_choice=False, validators=[
        DataRequired(message='Adliye seçiniz')
    ])
    
    hearing_date = DateField('Tarih', validators=[
        DataRequired(message='Tarih gereklidir')
    ], format='%Y-%m-%d')
    
    price = IntegerField('Ücret (TL)', validators=[
        DataRequired(message='Ücret gereklidir'),
        NumberRange(min=0, message='Ücret 0 veya daha büyük olmalıdır')
    ])
    
    urgency_level = SelectField('Aciliyet Durumu', choices=[(k, v) for k, v in URGENCY_LEVELS.items()], validators=[
        DataRequired(message='Aciliyet durumu seçiniz')
    ])
    
    is_active = BooleanField('İlan Aktif')
