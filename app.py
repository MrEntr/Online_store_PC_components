from flask import Flask, jsonify, request, redirect, render_template, session, url_for
from flask_migrate import Migrate
from crud import crud_bp
from config import Config
from models import db, Users, Roles
from views import admin


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
admin.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def home():
    if "user_id" in session:
        user = Users.query.get(session["user_id"])
        if user and user.role.role_id == 2:
            return redirect("/admin")
    return redirect(url_for('log_in'))


@app.route('/log_in', methods=['POST', 'GET'])
def log_in():
    if request.method == 'POST':
        data = request.form
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Invalid request'}), 400

        user = Users.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401

        user.generate_token()
        session['user_id'] = user.user_id

        if user.role.role_id == 2:
            return redirect('/admin')

    return render_template('verification/log_in.html')


@app.route('/sign_in')
def sign_in():
    return render_template('verification/sign_in.html')


# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('first_name') or not data.get('last_name'):
        return jsonify({'message': 'Invalid request'}), 400

    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    user_role = Roles.query.filter_by(role_name="Пользователь").first()
    if not user_role:
        return jsonify({'message': 'Role "Пользователь" does not exist'}), 400

    new_user = Users(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role_id=user_role.role_id
    )

    new_user.set_password(data['password'])
    new_user.generate_token()
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user_id': new_user.user_id}), 201


# Аутентификация пользователя
@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Invalid request'}), 400

    user = Users.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    user.generate_token()
    db.session.commit()

    return jsonify({'message': 'Logged in successfully', 'token': user.token}), 200


app.register_blueprint(crud_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
