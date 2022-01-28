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
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False

OFFICE_ID = 1
BASE_ROOM_TOPIC = 'rooms'

ALL_USERS = None


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(f'{BASE_ROOM_TOPIC}/+')
    response = requests.get(url=F"http://{CENTRAL_SERVER_HOST}:{CENTRAL_SERVER_PORT}/api/user",
                            headers={'API_KEY': LOCAL_SERVER_API_KEY})
    global ALL_USERS
    ALL_USERS = json.loads(response.text)['users']
    print("USERS ")
    pprint(ALL_USERS)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    body = json.loads(message.payload.decode())

    activity = {
        "card": body['card'],
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "entered",
        'room': message.topic.split('/')[-1],
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


@app.route('/test', methods=['POST'])
def send():
    body = request.get_json()
    x = mqtt.publish(f'{BASE_ROOM_TOPIC}/{body["room"]}', payload=json.dumps(body).encode('utf-8'))

    return {'mqtt_result': x}


if __name__ == '__main__':
    app.run(host=LOCAL_SERVER_HOST, port=LOCAL_SERVER_PORT)
