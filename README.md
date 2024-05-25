# Flask-API-Security

# Flask Security Application

This project is a Flask application that demonstrates the use of Flask-Security for user authentication and role management. It includes routes for user creation, authentication, and data retrieval, as well as public information access.

### Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Models](#database-models)
- [Routes](#routes)
- [One-time Setup](#one-time-setup)
- [Running the Application](#running-the-application)
- [Navigation](#navigation)
- [Example Requests](#example-requests)
- [Note](#note)

### Installation

1. Clone the repository:

```sh
git clone https://github.com/your-repo/flask-security-app.git
```

2. Create a virtual environment and activate it:

```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```sh
    pip install -r requirements.txt
```


### Configuration

The application uses environment variables for configuration. You can set these variables in your environment or create a `.env` file in the root directory.

- `SECRET_KEY`: Secret key for the Flask application.
- `SECURITY_PASSWORD_SALT`: Salt for password hashing.

### Database Models

The application uses SQLAlchemy for ORM and defines the following models:

- **Role**: Represents a user role.

```python
class Role(db.Model, fsqla.FsRoleMixin):
	id = Column(Integer(), primary_key=True)
	name = Column(String(100), unique=True)
	description = Column(String(255))
```


- **User**: Represents a user.

```python
class User(db.Model, fsqla.FsUserMixin):
	id = Column(Integer, primary_key=True)
	email = Column(String(255), unique=True)
	password = Column(String(255))
	active = Column(Boolean())
	confirmed_at = Column(DateTime())
	roles = relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
```


### Routes

- **Home**: Requires authentication.

```python
@app.route("/")
@auth_required()
def home():
    return render_template_string("Hello {{ current_user.email }}")
```


- **Get User Info**: Requires authentication.
```python
    @app.route("/api/user", methods=["GET"])
    @auth_required()
    def get_user_info():
        from flask_security import current_user
        return jsonify({"email": current_user.email})
```


- **Create User**: Public route to create a new user.
```python
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
```


- **Public Info**: Public route to access information without authentication.
```python
    @app.route("/public-info")
    def public_info():
        return jsonify({"message": "This is public information accessible without authentication."})
```


- **Show Data**: Public route to show all users and roles.
```python
    @app.route("/data")
    def show_data():
        users = User.query.all()
        roles = Role.query.all()

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

        return jsonify({'users': users_data, 'roles': roles_data})
```



### One-time Setup

The application includes a one-time setup to create a test user:

```python
with app.app_context():
    db.create_all()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(email="test@me.com", password=hash_password("password"))
    db.session.commit()
```


### Running the Application

To run the application, use the following command:

```sh
python app.py
```

The application will start on `http://127.0.0.1:5000/`. You can access the following routes:
- `GET /`: Home page (requires authentication).
- `GET /api/user`: Retrieve user information (requires authentication).
- `POST /api/user`: Create a new user.
- `GET /public-info`: Access public information.
- `GET /data`: Show all users and roles.

### Navigation
- **Home**: Visit `http://127.0.0.1:5000/` to see the home page after logging in.
- **User Info**: Use tools like `curl` or Postman to send a `GET` request to `http://127.0.0.1:5000/api/user` with authentication headers.
- **Create User**: Send a `POST` request to `http://127.0.0.1:5000/api/user` with a JSON body containing `email` and `password`.
- **Public Info**: Visit `http://127.0.0.1:5000/public-info` to see public information.
- **Show Data**: Visit `http://127.0.0.1:5000/data` to see all users and roles.

### Example Requests

- **Create User**:
```sh
curl -X POST http://127.0.0.1:5000/api/user -H "Content-Type: application/json" -d '{"email":"newuser@example.com", "password":"newpassword"}'
```

- **Get User Info**:
```sh
curl -X GET http://127.0.0.1:5000/api/user -H "Authorization: Bearer <your_token>"
```

### Note
This Flask application demonstrates a simple yet powerful way to manage user authentication and roles using Flask-Security. Feel free to extend the application with more features as needed.