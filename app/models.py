from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSON

# Initialize database & encryption
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)  # <-- Add this line
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    interests = db.Column(JSON, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=False)
    subscription_plan = db.Column(db.String(20), default='free')


    # Password methods
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_match = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan = db.Column(db.String(20), nullable=False)  # 'free', 'premium'
    payment_method = db.Column(db.String(50), nullable=False)  # 'M-Pesa', 'Stripe', 'Crypto'
    amount = db.Column(db.Float, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    participants = db.relationship('EventParticipant', backref='event', lazy=True)

class EventParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method = db.Column(db.String(50), nullable=False)  # 'M-Pesa', 'Stripe', 'Crypto'
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(255), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database function
def init_db(app):
    db.init_app(app)
    bcrypt.init_app(app)
    with app.app_context():
        db.create_all()
