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
    required_fields = ['email', 'password', 'name', 'age', 'gender', 'location', 'profile_photo']
    if not all(k in data for k in required_fields):
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

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=user.email)
    return jsonify({'access_token': access_token, 'user_id': user.id, 'is_admin': user.is_admin}), 200

# Get All Users (Admin Only)
@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'age': user.age,
        'gender': user.gender,
        'location': user.location,
        'profile_photo': user.profile_photo
    } for user in users]), 200

# Get User Profile
@app.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'age': user.age,
        'gender': user.gender,
        'location': user.location,
        'profile_photo': user.profile_photo
    }), 200
@app.route('/users/all', methods=['GET'])
@jwt_required()
def get_other_users():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    # Fetch all users except the currently logged-in user
    other_users = User.query.filter(User.id != current_user.id).all()

    return jsonify([{
        'id': user.id,
        'name': user.name,
        'age': user.age,
        'gender': user.gender,
        'location': user.location,
        'profile_photo': user.profile_photo
    } for user in other_users]), 200
# Update Own Profile
@app.route('/user', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    for key, value in data.items():
        if hasattr(current_user, key) and key != 'id' and key != 'password_hash':
            setattr(current_user, key, value)
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

# Delete Own Profile
@app.route('/user', methods=['DELETE'])
@jwt_required()
def delete_own_profile():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(current_user)
    db.session.commit()
    return jsonify({'message': 'Your account has been deleted'}), 200

# Admin Delete User
@app.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_user(user_id):
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user_to_delete)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created
    app.run(debug=True)
