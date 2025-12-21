from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, IntegerField, BooleanField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional

class OfficePostForm(FlaskForm):
    title = StringField('İlan Başlığı', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Açıklama', validators=[DataRequired(), Length(min=20)])
    category = SelectField('Kategori', choices=[
        ('rent_office', 'Kiralık Ofis'),
        ('rent_room', 'Kiralık Oda'),
        ('share_office', 'Paylaşımlı Ofis'),
        ('sell_furniture', 'Satılık Mobilya')
    ], validators=[DataRequired()])
    
    price = FloatField('Fiyat', validators=[DataRequired()])
    currency = SelectField('Para Birimi', choices=[('TRY', 'TL'), ('USD', 'USD'), ('EUR', 'EUR')], default='TRY')
    
    city = StringField('Şehir', validators=[DataRequired()])
    district = StringField('İlçe', validators=[DataRequired()])
    address = TextAreaField('Adres', validators=[Optional()])
    
    latitude = FloatField('Enlem', validators=[Optional()])
    longitude = FloatField('Boylam', validators=[Optional()])
    
    square_meters = IntegerField('Metrekare (m²)', validators=[Optional()])
    room_count = StringField('Oda Sayısı', validators=[Optional()])
    floor = StringField('Bulunduğu Kat', validators=[Optional()])
    heating_type = StringField('Isıtma Tipi', validators=[Optional()])
    is_furnished = BooleanField('Eşyalı')
    
    images = MultipleFileField('Resimler', validators=[Optional()])
