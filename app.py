
import os
import logging
from flask import Flask, request, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_security.models import fsqla_v3 as fsqla

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-default-secret-key")
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT", "your-default-salt")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database connection
db = SQLAlchemy(app)
fsqla.FsModels.set_db_info(db)

from sqlalchemy.orm import relationship
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
    extend_existing=True
)

# Define models
class Role(db.Model, fsqla.FsRoleMixin):
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String(255))

class User(db.Model, fsqla.FsUserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

# Routes
@app.route("/")
@auth_required()
def home():
    return render_template_string("Hello {{ current_user.email }}")

@app.route("/api/user", methods=["GET"])
@auth_required()
def get_user_info():
    from flask_security import current_user
    return jsonify({"email": current_user.email})

@app.route("/api/user", methods=["POST"])
def create_user():
    try:
        data = request.json
        user = user_datastore.create_user(email=data["email"], password=hash_password(data["password"]))
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to create user: {e}")
        return jsonify({"error": "Failed to create user"}), 400

@app.route("/public-info")
def public_info():
    return jsonify({"message": "This is public information accessible without authentication."})

@app.route("/data")
def show_data():
    # Query all users and roles from the database
    users = User.query.all()
    roles = Role.query.all()

    # Serialize the data to JSON format
    users_data = [{
        'id': user.id,
        'email': user.email,
        'active': user.active,
        'confirmed_at': user.confirmed_at.isoformat() if user.confirmed_at else None,
        'roles': [role.name for role in user.roles]
    } for user in users]

    roles_data = [{
        'id': role.id,
        'name': role.name,
        'description': role.description
    } for role in roles]

    # Return the data as a JSON response
    return jsonify({'users': users_data, 'roles': roles_data})

# One-time setup
with app.app_context():
    db.create_all()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(email="test@me.com", password=hash_password("password"))
    db.session.commit()

# Run the app
if __name__ == "__main__":
    app.run()