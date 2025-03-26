from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from models import db, init_db, User

# Initialize Flask app
app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://smash_app:smash_dating001@localhost:5432/smash_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

# Initialize Extensions
jwt = JWTManager(app)
CORS(app)  # Enable CORS for frontend integration
init_db(app)  # Initialize database

# Root Route
@app.route('/')
def home():
    return {'message': 'Welcome to Smash Dating App API!'}

# Register Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ('email', 'password', 'name', 'age', 'gender', 'location', 'profile_photo')):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Create new user
    new_user = User(
        email=data['email'],
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        location=data['location'],
        profile_photo=data['profile_photo']
    )
    new_user.set_password(data['password'])  # Hash password
    
    # Save user to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

# Admin-only user count endpoint
@app.route('/user_count', methods=['GET'])
@jwt_required()
def user_count():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()

    if not current_user or not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    count = User.query.count()
    return jsonify({'user_count': count}), 200

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created
    app.run(debug=True)
