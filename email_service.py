from flask_mail import Message
from flask import current_app, render_template
from extensions import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        subject=f"{app.config['APP_NAME']} - {subject}",
        recipients=[to],
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    # msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template, **kwargs)
    
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
