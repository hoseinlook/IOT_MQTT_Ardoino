from flask import Flask
from flask_mqtt import Mqtt

app = Flask(__name__)
mqtt = Mqtt(app)
app.config['DEBUG'] = True
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'admin'
app.config['MQTT_PASSWORD'] = 'hivemq'
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('rooms/+')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    print("DATAA", data)
    print("DATAA", client, userdata)


@app.route('/rooms/<int:room_id>', methods=['GET'])
def send(room_id):
    print(room_id)
    x = mqtt.publish(f'rooms/{room_id}', payload=b"asd")
    print(x)
    return {'x': x}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
