import json
import random
from datetime import datetime

from flask import Flask
from flask import request, jsonify

from config import STORAGE_PATH, LOCAL_SERVER_API_KEY, CENTRAL_SERVER_HOST, CENTRAL_SERVER_PORT

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['FLASK_ENV'] = 'development'
ADMIN_FILE_PATH = STORAGE_PATH.joinpath('admin.json')
USER_FILE_PATH = STORAGE_PATH.joinpath('user.json')
OFFICE_FILE_PATH = STORAGE_PATH.joinpath('office.json')
ACTIVITIES_FILE_PATH = STORAGE_PATH.joinpath('activities.json')


def generate_random_token():
    return ''.join(
        random.choices('qwetyuioasdkljksdkjgzvbmzbajshfdpoweuyUWIQEYTPOAIUDAKLSaAZMVXNZGLJHGMZNXC' * 3, k=50))


def save_to_file(path, objects):
    with open(path, 'w') as file:
        file.write(json.dumps(objects))


def load_from_file(path):
    try:
        with open(path, 'r') as file:
            objects = json.loads(file.read())
    except:
        objects = []
    return objects


def check_admin_auth() -> bool:
    if "api_key" not in request.headers:
        return False
    token = request.headers['api_key']
    admins = load_from_file(ADMIN_FILE_PATH)
    if token == LOCAL_SERVER_API_KEY: return True
    if token not in [a.get('token') for a in admins]: return False
    return True


def check_user_auth() -> bool:
    if "api_key" not in request.headers:
        return False
    token = request.headers['api_key']
    admins = load_from_file(USER_FILE_PATH)
    if token not in [a.get('token') for a in admins]: return False
    return True


@app.route('/api/office/register', methods=['POST'])
def register_office():
    offices = load_from_file(OFFICE_FILE_PATH)
    now_time = datetime.now()
    new_office = {
        "id": len(offices) + 1,
        "lightsOnTime": f"{now_time.hour}:{now_time.minute}",
        "lightsOffTime": f"{now_time.hour}:{now_time.minute}",
    }
    offices += [new_office]
    save_to_file(OFFICE_FILE_PATH, offices)
    return jsonify(
        {
            "new_office": new_office
        }
    ), 201


@app.route('/api/admin/register', methods=['POST'])
def register_admin():
    body = request.get_json()
    if body is None or 'username' not in body or 'password' not in body or 'office_id' not in body:
        return jsonify({
            "message": 'bad body'
        }), 400

    admins = load_from_file(str(ADMIN_FILE_PATH))
    new_admin = {
        "id": len(admins) + 1,
        "username": body['username'],
        "password": body['password'],
        "office_id": body['office_id'],
    }
    admins += [new_admin]
    save_to_file(str(ADMIN_FILE_PATH), admins)
    return jsonify(
        {
            "new_admin": new_admin
        }
    ), 201


@app.route('/api/admin/')
def get_all_admins():
    return jsonify(load_from_file(ADMIN_FILE_PATH))


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    body = request.get_json()
    if body is None or 'username' not in body or 'password' not in body:
        return jsonify({
            "message": 'bad body'
        }), 400

    admins = load_from_file(str(ADMIN_FILE_PATH))
    the_admin = None
    for item in admins:
        if item.get('username') == body.get('username') and item.get('password') == body.get('password'):
            the_admin = item
    if the_admin is None:
        return jsonify({
            "message": "no any admin with this username or password is wrong!"
        }), 401

    the_admin['token'] = generate_random_token()

    save_to_file(ADMIN_FILE_PATH, admins)

    return jsonify(the_admin), 200


@app.route('/api/admin/user/register', methods=['POST'])
def register_user():
    if not check_admin_auth():
        return jsonify({'message': 'auth failed'}), 401

    body = request.get_json()
    if body is None or 'card' not in body or 'password' not in body or 'office' not in body or 'room' not in body:
        return jsonify({
            "message": 'bad body'
        }), 400
    users = load_from_file(USER_FILE_PATH)
    new_user = {
        "id": len(users) + 1,
        "card": body['card'],
        "password": body['password'],
        "office": body['office'],
        "room": body['room'],
    }
    users += [new_user]
    save_to_file(USER_FILE_PATH, users)

    return jsonify({
        'new_user': new_user
    }), 201


@app.route('/api/admin/activities', methods=['GET'])
def all_activities():
    if not check_admin_auth():
        return jsonify({'message': 'auth failed'}), 401

    return jsonify({'activities': load_from_file(ACTIVITIES_FILE_PATH)})


@app.route('/api/admin/activities', methods=['POST'])
def add_activity():
    if not check_admin_auth():
        return jsonify({'message': 'local_server auth failed'}), 401

    body = request.get_json()
    if body is None or 'card' not in body or 'datetime' not in body or 'office' not in body or 'room' not in body or 'type' not in body:
        return jsonify({
            "message": 'bad body'
        }), 400
    acts = load_from_file(ACTIVITIES_FILE_PATH)
    new_act = {
        "id": len(acts) + 1,
        "card": body['card'],
        "datetime": body['datetime'],
        "office": body['office'],
        "room": body['room'],
        "type": body['type'],
    }
    acts += [new_act]
    save_to_file(ACTIVITIES_FILE_PATH, acts)

    return jsonify({
        'new_act': new_act
    }), 201


# users endpoints
@app.route('/api/user', methods=['GET'])
def get_all_users():
    if not check_admin_auth():
        return jsonify({"message": "auth failed"}), 401
    return jsonify({'users': load_from_file(USER_FILE_PATH)}), 200


@app.route('/api/user/login', methods=['POST'])
def user_login():
    body = request.get_json()
    if body is None or 'card' not in body or 'password' not in body:
        return jsonify({
            "message": 'bad body'
        }), 400
    users = load_from_file(USER_FILE_PATH)
    the_user = None
    for item in users:
        if item.get('card') == body.get('card') and item.get('password') == body.get('password'):
            the_user = item
    if the_user is None:
        return jsonify({
            "message": "no any user with this card or password is wrong!"
        }), 401

    the_user['token'] = generate_random_token()

    save_to_file(USER_FILE_PATH, users)

    return jsonify(the_user), 200


@app.route('/api/user/<int:user_id>', methods=['POST'])
def user_set_light(user_id):
    if not check_user_auth():
        return jsonify({'message': 'auth failed'}), 401
    light = request.args.get('light')
    if light is None:
        return jsonify({'message': 'no  light param'}), 400
    light = int(light)
    users = load_from_file(USER_FILE_PATH)
    the_user = None
    for item in users:
        if item.get('token') == request.headers.get('api_key'):
            the_user = item
    if the_user is None:
        return jsonify({
            "message": "no any user with this token"
        }), 401

    the_user['light'] = light

    save_to_file(USER_FILE_PATH, users)

    return jsonify({
        'user': the_user
    }), 200


if __name__ == '__main__':
    app.run(host=CENTRAL_SERVER_HOST, port=CENTRAL_SERVER_PORT)
