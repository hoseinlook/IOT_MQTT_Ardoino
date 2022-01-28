import datetime
import json
from pprint import pprint

import requests
from flask import Flask, request
from flask_mqtt import Mqtt

from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, CENTRAL_SERVER_PORT, CENTRAL_SERVER_HOST, LOCAL_SERVER_API_KEY

app = Flask(__name__)
mqtt = Mqtt(app)
app.config['DEBUG'] = True
app.config['FLASK_ENV'] = 'development'
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'admin'
app.config['MQTT_PASSWORD'] = 'hivemq'
app.config['MQTT_KEEPALIVE'] = 600
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLIENT_ID'] = 'qwetyuioasdkljksdkjgzvbmzbajshfdpoweuyUWIQEYTPOAIUDAKLSaAZMVXNZGLJHGMZNXC'
IS_CONNECTED = False

OFFICE_ID = 1
BASE_ROOM_TOPIC = 'login/rooms'
CMD_TOPIC = 'cmd/rooms'
LIGHT_RESULT_TOPIC = 'light/rooms'

ALL_USERS = []


@app.before_request
def xxx():
    global IS_CONNECTED
    if not IS_CONNECTED:
        print(" CONNECT")
        mqtt.subscribe(f'{BASE_ROOM_TOPIC}/+')
        mqtt.subscribe(f'{CMD_TOPIC}/+')
        response = requests.get(url=F"http://{CENTRAL_SERVER_HOST}:{CENTRAL_SERVER_PORT}/api/user",
                                headers={'API_KEY': LOCAL_SERVER_API_KEY})
        global ALL_USERS
        ALL_USERS = json.loads(response.text)['users']
        print("USERS ")
        pprint(ALL_USERS)
        IS_CONNECTED = True


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    body = json.loads(message.payload.decode())
    the_user = None
    for user in ALL_USERS:
        if user['card'] == body['card']:
            the_user = user

    if the_user is None:
        print("BADDDD CARD \n user not found with this card register it ")
        return None
    if the_user.get('type') == 'exited' or the_user.get('type') is None:
        the_user['type'] = 'entered'

    else:
        the_user['type'] = 'exited'

    room_id = message.topic.split('/')[-1]
    activity = {
        "card": body['card'],
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": the_user['type'],
        'room': room_id,
        'office': OFFICE_ID,
    }
    url = F"http://{CENTRAL_SERVER_HOST}:{CENTRAL_SERVER_PORT}/api/admin/activities"
    response = requests.post(url=url,
                             data=json.dumps(activity),
                             headers={
                                 'API_KEY': LOCAL_SERVER_API_KEY,
                                 'Content-Type': 'application/json'
                             })

    print("ADD activity", response)

    mqtt.publish(f"{LIGHT_RESULT_TOPIC}/{room_id}", payload=the_user['light'])


@app.route('/test', methods=['POST'])
def send():
    body = request.get_json()
    x = mqtt.publish(f'{BASE_ROOM_TOPIC}/{body["room"]}', payload=json.dumps(body).encode('utf-8'))

    return {'mqtt_result': x}


#
# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#     print("LOG ", level, buf)


if __name__ == '__main__':
    app.run(host=LOCAL_SERVER_HOST, port=LOCAL_SERVER_PORT)
