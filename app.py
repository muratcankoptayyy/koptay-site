"""
Tevkil Platform - Main Application
"""
import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv
from config import config
from models import db, User
from extensions import mail

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

@app.before_request
def log_request_info():
    from flask import request
    try:
        print(f"REQUEST: {request.method} {request.url}")
        # print(f"   Headers: {request.headers}") # Disable header logging to prevent encoding errors
    except Exception:
        pass

@app.errorhandler(500)
def internal_error(error):
    import traceback
    print("!!! INTERNAL SERVER ERROR (500) !!!")
    print(traceback.format_exc())
    return "Sunucu hatası oluştu. Lütfen sayfayı yenileyin.", 500

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize database
db.init_app(app)

# Initialize Mail
mail.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bu sayfayı görüntülemek için giriş yapmalısınız.'
login_manager.login_message_category = 'warning'

# Register blueprints
from blueprints.auth import auth_bp
from blueprints.posts import posts_bp
from blueprints.applications import applications_bp
from blueprints.messages import messages_bp
from blueprints.profile import profile_bp
from blueprints.settings import settings_bp
from blueprints.api import api_bp
from blueprints.jobs import jobs_bp
from blueprints.office import office_bp
from blueprints.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(api_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(office_bp)
app.register_blueprint(main_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# CSP Header - Allow Alpine.js to work
@app.after_request
def set_csp_header(response):
    """Set Content Security Policy header - Very permissive for development"""
    if app.config.get('DEBUG'):
        # Development: Disable CSP completely for Alpine.js
        # Remove any existing CSP headers
        response.headers.pop('Content-Security-Policy', None)
        response.headers.pop('Content-Security-Policy-Report-Only', None)
        # Set ultra-permissive CSP
        response.headers['Content-Security-Policy'] = (
            "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; "
            "script-src * 'unsafe-inline' 'unsafe-eval'; "
            "style-src * 'unsafe-inline'; "
            "img-src * data: blob:; "
            "font-src * data:; "
            "connect-src *; "
            "frame-src *;"
        )
    else:
        # Production: Stricter CSP
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdn.tailwindcss.com https://www.googletagmanager.com https://*.googletagmanager.com https://www.google-analytics.com https://ssl.google-analytics.com https://www.clarity.ms https://*.clarity.ms https://c.bing.com https://*.bing.com https://www.googleadservices.com https://googleads.g.doubleclick.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: https://www.google-analytics.com https://*.google-analytics.com https://analytics.google.com https://www.googletagmanager.com https://*.googletagmanager.com https://www.google.com https://*.google.com https://www.googleadservices.com https://googleads.g.doubleclick.net; "
            "connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://analytics.google.com https://*.analytics.google.com https://stats.g.doubleclick.net https://www.googletagmanager.com https://*.googletagmanager.com https://www.clarity.ms https://*.clarity.ms https://c.bing.com https://*.bing.com https://www.google.com https://*.google.com https://www.googleadservices.com https://googleads.g.doubleclick.net; "
            "frame-src 'self' https://googleads.g.doubleclick.net https://www.google.com; "
            "worker-src 'self' blob:;"
        )
    return response

# Context processor - add global variables to all templates
@app.context_processor
def inject_globals():
    """Add global variables to all templates"""
    unread_messages = 0
    notifications_count = 0
    
    if current_user.is_authenticated:
        notifications_count = current_user.notifications_unread_count
        # Mesaj sayısını hesapla (şimdilik 0)
        unread_messages = 0
        
        stats = {
            'active_posts': current_user.total_posts_created,
            'new_applications': current_user.total_applications_received,
            'unread_messages': unread_messages
        }
    else:
        stats = {
            'active_posts': 0,
            'new_applications': 0,
            'unread_messages': 0
        }
    
    return {
        'stats': stats,
        'notifications_count': notifications_count,
        'config': app.config
    }

# Routes
@app.route('/')
def index():
    """Ana sayfa - Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('hub'))
    return render_template('index.html')

@app.route('/hub')
@login_required
def hub():
    """Platform Seçim Ekranı"""
    return render_template('pages/hub.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard"""
    # DEV MODE: Otomatik login
    if not current_user.is_authenticated and app.config['DEV_MODE']:
        first_user = User.query.first()
        if first_user:
            from flask_login import login_user
            login_user(first_user, remember=True)
            print(f"DEV MODE: Auto-logged in as {first_user.email}")
    
    # Login kontrolü
    if not current_user.is_authenticated:
        return render_template('pages/login.html')
    
    from models import TevkilPost, Application, Conversation
    
    # Gerçek istatistikleri hesapla
    active_posts_count = TevkilPost.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).count()
    
    # Gelen başvuru sayısı
    received_apps_count = db.session.query(Application)\
        .join(TevkilPost, Application.post_id == TevkilPost.id)\
        .filter(TevkilPost.user_id == current_user.id)\
        .filter(Application.status == 'pending')\
        .count()
    
    # Okunmamış mesaj sayısı - Conversation bazlı hesaplama
    from models import Conversation
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id)
    ).all()
    
    unread_messages_count = 0
    for conv in conversations:
        if conv.user1_id == current_user.id:
            unread_messages_count += conv.unread_count_user1
        else:
            unread_messages_count += conv.unread_count_user2
    
    # Dashboard stats
    stats = {
        'active_posts': active_posts_count,
        'applications': received_apps_count,
        'messages': unread_messages_count,
        'rating': current_user.rating_average or 5.0
    }
    
    # Son ilanlar
    recent_posts = TevkilPost.query.filter_by(
        user_id=current_user.id
    ).order_by(TevkilPost.created_at.desc()).limit(5).all()
    
    # Son başvurular
    recent_applications = db.session.query(Application)\
        .join(TevkilPost, Application.post_id == TevkilPost.id)\
        .filter(TevkilPost.user_id == current_user.id)\
        .order_by(Application.created_at.desc())\
        .limit(5)\
        .all()
    
    return render_template('pages/dashboard.html', 
                         stats=stats,
                         recent_posts=recent_posts,
                         recent_applications=recent_applications)

# Custom template filters
@app.template_filter('nl2br')
def nl2br(value):
    """Converts newlines to <br> tags."""
    if not value:
        return ""
    from markupsafe import Markup, escape
    return Markup(str(escape(value)).replace('\n', '<br>\n'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
